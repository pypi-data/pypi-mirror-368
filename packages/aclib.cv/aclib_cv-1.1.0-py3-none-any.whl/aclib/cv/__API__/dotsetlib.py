from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self, Literal
    from .color import HexColorRange

import os
from typing import overload

from .dotset import Dotset


class DotsetLib(object):

    def __new__(cls):
        return cls.__new(())

    @classmethod
    def __new(cls, libdata: tuple[Dotset, ...]) -> Self:
        self = super().__new__(cls)
        self.__init(libdata)
        return self

    def __init(self, libdata: tuple[Dotset, ...]):
        self.__libdata = libdata
        self.__groups = {}
        isfontlib = isinstance(self, FontLib)
        for dotset in libdata:
            if isfontlib and len(dotset.name) != 1:
                raise KeyError(
                    f'Only dotset with 1-length-name can be stored in FontLib, "{dotset.name}" got')
            self.__groups[dotset.name] = self.__groups.get(dotset.name, ()) + (dotset,)
        if isfontlib: self.__charset = ''.join(self.__groups)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}({self.ngroup}/{self.ndotset}) at {hex(id(self))}>'

    def __len__(self) -> int:
        return self.__libdata.__len__()

    def __getitem__(self, item) -> Dotset:
        return self.__libdata[item]


    @classmethod
    def fromfile(cls, filepath: str) -> Self:
        with open(filepath, 'r') as f:
            datas = f.read().strip().split('\n')
        return cls.__new(tuple(filter(lambda item:item, (Dotset.fromdata(data) for data in datas))))

    def tofile(self, filepath: str) -> str:
        savedata = '\n'.join([dotset.todata() for dotset in self.__libdata])
        with open(filepath, 'w') as f:
            f.write(savedata)
        return os.path.abspath(filepath)


    @property
    def ndotset(self):
        return self.__libdata.__len__()

    @property
    def ngroup(self):
        return self.__groups.__len__()

    def group(self, name: str) -> tuple[Dotset, ...]:
        return self.__groups.get(name, ())

    def groups(self) -> dict[str, tuple[Dotset, ...]]:
        return self.__groups.copy()


    @overload
    def scale(self, scale: int | float) -> Self: ...

    @overload
    def scale(self, scaleX: int | float, scaleY: int | float) -> Self: ...

    def scale(self, scaleX: int | float, scaleY: int | float = None) -> Self:
        return self.__class__.__new(tuple(dotset.scale(scaleX, scaleY) for dotset in self.__libdata))


    def list(self) -> None:
        maxLabelLen = (self.ndotset-1).__str__().__len__()
        seperator = "=" * 60
        print(f'\n{seperator}')
        for i, dotset in enumerate(self.__libdata):
            print(f'{i:{maxLabelLen}}: {dotset}')
        print(f'{seperator}\n')

    def sort(self) -> None:
        self.__init(tuple(sorted(self.__libdata, key=lambda dotset: dotset.name)))

    def add(self, dotset: Dotset, toindex: int = None) -> None:
        if toindex is None:
            toindex = self.ndotset
        self.__init((*self.__libdata[:toindex], dotset, *self.__libdata[toindex:]))

    def delete(self, index: int) -> None:
        self.__init((*self.__libdata[:index], *self.__libdata[index+1 or self.ndotset:]))

    def __replace(self, index: int, dotset: Dotset) -> None:
        self.__init((*self.__libdata[:index], dotset, *self.__libdata[index+1 or self.ndotset:]))

    def rename(self, index: int, name: str) -> None:
        self.__replace(index, self[index].asname(name))

    def recolor(self, index: int, rgbrange: Literal[0,1] | HexColorRange) -> None:
        self.__replace(index, self[index].asmatchcolor(rgbrange))


class FontLib(DotsetLib):
    @property
    def charset(self): return self._DotsetLib__charset
