from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self, Callable

from aclib.builtins import MatTarget


class TargetList(object):

    def __new__(cls):
        return cls._new_(([],))

    @classmethod
    # TargetList 存储原始数据, 只有在需要的时候才读取或遍历 Target, 在项目较多时可以显著提升速度和节省资源
    def _new_(cls, *logicgroups: tuple[list[MatTarget]] | tuple[ list[int], list[int], Callable[[int,int], MatTarget] ]) -> Self:

        """ logicgroup: ([Target, ...], ) | ( [x1, x2, ...], [y1, y2, ...], (x,y)=>Target ) """

        self = super().__new__(cls)
        self._init_(*logicgroups)
        return self

    def _init_(self, *logicgroups):
        self._logicgroups = [*logicgroups]

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} x{self.__len__()} {list(self)}>'

    def __bool__(self) -> bool:
        return bool(self.__len__())

    def __len__(self) -> int:
        return sum(len(logicgroup[0]) for logicgroup in self._logicgroups)

    def __getitem__(self, index) -> MatTarget:
        if index < 0:
            index = self.__len__() + index
        if index >= 0:
            for logicgroup in self._logicgroups:
                targetnum = len(logicgroup[0])
                if index < targetnum:
                    if len(logicgroup) == 1:
                        return logicgroup[0][index]
                    return logicgroup[2](logicgroup[0][index], logicgroup[1][index])
                index -= targetnum
        raise IndexError(
            'targetlist index out of range')

    def __add__(self, other) -> Self:
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"unsupported operand type(s) for +: '{self.__class__.__name__}' and '{type(other).__name__}'")
        return self.__class__._new_(*self._logicgroups, *other._logicgroups)


    def append(self, target: MatTarget):
        if len(self._logicgroups[-1]) == 3:
            self._logicgroups.append(([],))
        self._logicgroups[-1][0].append(target)

    def join(self, start: int = 0, end: int = None) -> MatTarget:
        selflen = len(self)
        if end is None:
            end = selflen
        if start < 0:
            start = max(0, selflen + start)
        if end < 0:
            end = max(0, selflen + end)
        start, end = min(start, selflen), min(end, selflen)
        if start < end:
            targets = [self[i] for i in range(start, end)]
            name = ''.join(map(lambda t: t.name, targets))
            avgsim = sum(map(lambda t: t.similarity, targets)) / len(targets)
            return MatTarget(*targets[0].start, *targets[-1].end, name, avgsim)
        else: return MatTarget()
