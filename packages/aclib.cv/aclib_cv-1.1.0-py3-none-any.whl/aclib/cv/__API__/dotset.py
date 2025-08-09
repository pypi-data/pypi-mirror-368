from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal, Self
    from .color import HexColorRange

from typing import overload
from random import randint
from aclib.builtins import Str

from .image import Image

class Dotset(object):

    def __new__(cls):
        raise TypeError(
            f"cannot create {cls.__name__} instances")

    @classmethod
    def __new(cls, name: str, bintmpl: Image, binmask: Image | None, rgbmatchcolor: Literal[0,1] | HexColorRange) -> Self:
        self = super().__new__(cls)
        self.__init(name, bintmpl, binmask, rgbmatchcolor)
        return self

    def __init(self, name, bintmpl, binmask, rgbmatchcolor):
        self.__name = name
        self.__tmpl = bintmpl
        self.__mask = binmask
        self.__matchcolor = rgbmatchcolor

    def __repr__(self) -> str:
        npixelinfo = f'{self.tmpl.npixel}' + f'-{self.npixel}' * (self.mask is not None)
        return f'<Dotset:{self.name} {self.matchcolor}|{self.width}x{self.height}={npixelinfo}>'


    @classmethod
    def fromimage(cls,
        asname:              str,
        image:               Image,
        tmplExtractColor:    Literal[0,1] | HexColorRange,
        maskExtractColor:    Literal[0,1] | HexColorRange = None,
        matchcolor:          Literal[0,1] | HexColorRange = None,
        cropmode:            Literal[0,1,2] = 0,
        cropmargin:          int = 0,
    ) -> Self:
        uncroppedBintmpl = image.binarize(tmplExtractColor)
        if maskExtractColor is not None:
            uncroppedBinmask = image.binarize(maskExtractColor).bitwise_or(uncroppedBintmpl)
            cropStart, cropEnd = uncroppedBinmask.border(cropmode, cropmargin)
            bintmpl = uncroppedBintmpl.crop(cropStart, cropEnd)
            binmask = uncroppedBinmask.crop(cropStart, cropEnd)
        else: bintmpl, binmask = uncroppedBintmpl.crop(*uncroppedBintmpl.border(cropmode, cropmargin)), None
        if matchcolor is None:
            matchcolor = tmplExtractColor
        return cls.__new(asname, bintmpl, binmask, matchcolor)

    @classmethod
    def fromdata(cls, data: str) -> Self | None:
        try:
            def decode(zippedhexim: Str) -> Image | None:
                binim = zippedhexim.unzip('GHIJKLMNOP').toBin(16).data[-w*h:]
                return Image.fromiter(binim, (w,h)) * 255 if binim else None
            b64name, b64color, strw, strh, hextmpl, hexmask = tuple(Str(data).split('|'))   # to tuple to get type hint
            name, color = b64name.base64decode().tostr(), b64color.base64decode().tostr()
            if color in ['0', '1']: color = int(color)
            w, h = strw.toint(), strh.toint()
            tmpl, mask = decode(hextmpl), decode(hexmask)
            if mask: mask = mask.bitwise_or(tmpl)
            return cls.__new(name, tmpl, mask, color)
        except: return None

    def todata(self) -> str:
        def encode(mat) -> Str:
            return Str().join((mat/255).reshape(mat.size).astype(int).astype(str)).toHex(2).toStr().zip('GHIJKLMNOP')
        hextmpl = encode(self.tmpl.toarray())
        hexmask = encode(self.mask.bitwise_xor(self.tmpl).toarray()) if self.mask else chr(randint(ord('Q'), ord('Z')))
        b64name = Str(self.name).base64encode()
        b64color = Str(self.matchcolor).base64encode()
        return f'{b64name}|{b64color}|{self.width}|{self.height}|{hextmpl}|{hexmask}'


    @property
    def name(self) -> str:
        return self.__name

    @property
    def tmpl(self) -> Image:
        return self.__tmpl

    @property
    def mask(self) -> Image | None:
        return self.__mask

    @property
    def matchcolor(self) -> Literal[0,1] | HexColorRange:
        return self.__matchcolor

    @property
    def size(self) -> tuple[int,int]:
        return self.__tmpl.size

    @property
    def width(self) -> int:
        return self.__tmpl.width

    @property
    def height(self) -> int:
        return self.__tmpl.height

    @property
    def npixel(self) -> int:
        if self.mask:
            maskmat = self.mask._immat
            return maskmat[maskmat == 255].__len__()
        else: return self.tmpl.npixel


    def asname(self, name: str) -> Self:
        return self.__class__.__new(name, self.tmpl, self.mask, self.matchcolor)

    def asmatchcolor(self, rgbmatchcolor: Literal[0,1] | HexColorRange) -> Self:
        return self.__class__.__new(self.name, self.tmpl, self.mask, rgbmatchcolor)


    @overload
    def scale(self, scale: int | float) -> Self: ...

    @overload
    def scale(self, scaleX: int | float, scaleY: int | float) -> Self: ...

    def scale(self, scaleX: int | float, scaleY: int | float = None) -> Self:
        if scaleY is None: scaleY = scaleX
        if scaleX == scaleY == 1:
            return self
        scaledtmpl = self.tmpl.scale(scaleX, scaleY).binarize(1)
        scaledmask = self.mask and self.mask.bitwise_xor(self.tmpl).scale(scaleX, scaleY).binarize(1).bitwise_or(scaledtmpl)
        return self.__class__.__new(self.name, scaledtmpl, scaledmask, self.matchcolor)


    def print(self):
        print(self)
        self.__tmpl.printbinimg(self.mask)

    def show(self, usebrowser=True):
        displaymat = self.tmpl.toarray()
        if self.mask:
            displaymat[self.mask.toarray()[:,:] == 0] = 0xa0
        Image.fromarray(displaymat).show(usebrowser)
