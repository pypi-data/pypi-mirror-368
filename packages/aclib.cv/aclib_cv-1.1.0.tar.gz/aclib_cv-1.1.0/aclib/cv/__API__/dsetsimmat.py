from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self, Iterable
    from .dotset import Dotset

import cv2 as cv
import numpy as np

from aclib.builtins import MatTarget
from .target import TargetList


class DsetSimMat(object):

    def __new__(cls):
        raise TypeError(
            'cannot create DsetSimMat instances')

    @classmethod
    def _new_(cls, dsetlist: Iterable[Dotset], simmat: np.ndarray, indexmat: np.ndarray = None) -> Self:
        self = super().__new__(cls)
        self._init_(dsetlist, simmat, indexmat)
        return self

    def _init_(self, dsetlist: Iterable[Dotset], simmat: np.ndarray, indexmat: np.ndarray = None):
        simmat[simmat == np.inf] = -np.inf
        self._dsetlist = tuple(dsetlist)
        self._simmat = simmat
        self._indexmat = np.zeros(simmat.shape, dtype=int) if indexmat is None else indexmat

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.size[0]}x{self.size[1]} at {hex(id(self))}>'


    @classmethod
    def merge(cls, dsetsimmat: Self, *dsetsimmats: Self) -> Self:
        if not dsetsimmats:
            return dsetsimmat
        in_dsetsimmats = (dsetsimmat, *dsetsimmats)
        out_dsetlist = ()
        out_matshape = max(mat.size[1] for mat in in_dsetsimmats), max(mat.size[0] for mat in in_dsetsimmats)
        out_simmat, out_indexmat = np.zeros(out_matshape), np.zeros(out_matshape, dtype=int)
        for dsetsimmat in in_dsetsimmats:
            dsetlist, simmat, indexmat = dsetsimmat._dsetlist, dsetsimmat._simmat, dsetsimmat._indexmat
            viewslice = slice(None, simmat.shape[0]), slice(None, simmat.shape[1])
            out_simmat_view, out_indexmat_view = out_simmat[viewslice], out_indexmat[viewslice]
            _filter = out_simmat_view < simmat
            out_simmat_view[_filter] = simmat[_filter]
            out_indexmat_view[_filter] = indexmat[_filter] + len(out_dsetlist)
            out_dsetlist += dsetlist
        return cls._new_(out_dsetlist, out_simmat, out_indexmat)


    @property
    def size(self) -> tuple[int, int]:
        return self._simmat.shape[1::-1]

    def get(self, x, y) -> tuple[Dotset, float]:
        return self.getdotset(x,y), self.getsim(x,y)

    def getsim(self, x, y) -> float:
        return self._simmat[y,x]

    def getdotset(self, x, y) -> Dotset:
        return self._dsetlist[self._indexmat[y,x]]

    def gettarget(self, x, y) -> MatTarget:
        d = self.getdotset(x,y)
        return MatTarget.frompossize((x,y), d.size, d.name, self.getsim(x,y))


    def print_sims(self):
        for line in self._simmat:
            print(line.tolist())

    def print_dotsets(self):
        for line in self._indexmat:
            print([self._dsetlist[i] for i in line])


    def __filter(self, similarity, ignore_overlaps=False, direction=0) -> tuple[np.ndarray, np.ndarray]:
        _filter = self._simmat >= similarity
        if direction==0: ylist, xlist = np.where(_filter)
        if direction==1: xlist, ylist = np.where(_filter.T)
        if ignore_overlaps:
            _ends: list[tuple[ tuple[int, int], tuple[int, int], float ]] = []
            for x0, y0 in zip(xlist, ylist):
                if not _filter[y0, x0]: continue
                dsetw, dseth = self.getdotset(x0, y0).size
                x1, y1 = x0 + dsetw, y0 + dseth
                localmaxX, localmaxY = cv.minMaxLoc(self._simmat[y0:y1, x0:x1] * _filter[y0:y1, x0:x1])[-1]
                _filter[y0:y1, x0:x1] = False
                _filter[y0+localmaxY, x0+localmaxX] = True
                if localmaxX == localmaxY == 0:
                    _ends.append(( (x0,y0), (x1,y1), self.getsim(x0, y0) ))
            i = 0
            samedir, crossdir = direction, ~direction + 2
            while i < len(_ends):
                pos, end, sim = _ends[i]
                todelete = []
                for comppos, compend, compsim in _ends[i+1:]:
                    if comppos[crossdir] >= end[crossdir]:
                        break
                    if not (comppos[samedir] < pos[samedir] < compend[samedir]):
                        continue
                    if compsim > sim:
                        todelete = [(pos, end, sim)]
                        break
                    todelete.append((comppos, compend, compsim))
                for el in todelete:
                    _filter[el[0][1], el[0][0]] = False
                    _ends.remove(el)
                if todelete != [(pos, end, sim)]:
                    i += 1
            if direction == 0: ylist, xlist = np.where(_filter)
            if direction == 1: xlist, ylist = np.where(_filter.T)
        return xlist, ylist

    def filter(self, similarity, ignore_overlaps=False, direction=0) -> TargetList:
        xlist, ylist = self.__filter(similarity, ignore_overlaps, direction)
        return TargetList._new_((xlist, ylist, self.gettarget))

    def separate(self, similarity, ignore_overlaps=False, direction=0) -> list[TargetList]:
        xlist, ylist = self.__filter(similarity, ignore_overlaps, direction)
        groups, groupBorderEnd = [], -1
        for pos in zip(xlist, ylist):
            dotset, sim = self.getdotset(*pos), self.getsim(*pos)
            if pos[not direction] > groupBorderEnd:
                groups.append([])
            groups[-1].append(MatTarget.frompossize(pos, dotset.size, dotset.name, sim))
            groupBorderEnd = max(groupBorderEnd, pos[not direction] + dotset.size[not direction])
        for i in range(len(groups)):
            groups[i].sort(key=lambda target: target.start[direction])
            groups[i] = TargetList._new_((groups[i],))
        return groups
