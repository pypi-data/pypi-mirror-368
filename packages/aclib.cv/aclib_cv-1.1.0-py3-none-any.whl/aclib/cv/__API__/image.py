from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal, Iterable, Self, Sequence
    from .dotset import Dotset
    from .dotsetlib import DotsetLib, FontLib
    from .color import TupColor, HexColor, HexColorRange

import re, os, tempfile
import cv2 as cv, numpy as np

from typing import overload

from aclib.builtins import MatTarget
from .dsetsimmat import DsetSimMat
from .target import TargetList
from .color import translateRgb, isColorsInRgbrange, rgb2gray

class Image(object):

    def __new__(cls):
        raise TypeError(
            "to create a 'Image' instance, please use Image.fromxxx method")

    @classmethod
    def __new(cls, immat: np.ndarray, imsize: tuple[int,int] = None) -> Self | None:
        if not immat.size: return None
        self = super().__new__(cls)
        self.__init(immat, imsize)
        return self

    def __init(self, immat: np.ndarray, imsize: tuple[int,int] = None):
        if imsize:
            npixel = imsize[0] * imsize[1]
            nchannel = npixel and immat.size // npixel
            ndim = 2 + nchannel // 3
            immat = immat.reshape((*imsize[1::-1], nchannel)[:ndim])
        if immat.ndim not in [2, 3]:
            raise TypeError('demensions of the array which describes the image must be 2 or 3')
        if immat.ndim == 3 and immat.shape[2] not in [1,3,4]:
            raise TypeError('image channels must be 1, 3, or 4')
        if immat.ndim == 3 and immat.shape[2] == 1:
            immat = immat.reshape((immat.shape[:2]))
        self._immat = immat

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.width}x{self.height}#{self.nchannel} at {hex(id(self))}>'

    def __mul__(self, other) -> Image:
        return self.__class__.__new(self._immat * other)


    @classmethod
    @overload
    def fromarray(cls, immat) -> Self | None: ...

    @classmethod
    @overload
    def fromarray(cls, array, imsize: tuple[int,int]) -> Self | None: ...

    @classmethod
    def fromarray(cls, array, imsize: tuple[int,int] = None) -> Self | None:
        return cls.__new(np.array(array, dtype=np.uint8), imsize)

    @classmethod
    def frombuffer(cls, buffer: bytes | bytearray, imsize: tuple[int,int]) -> Self | None:
        return cls.__new(np.frombuffer(buffer, dtype=np.uint8), imsize)

    @classmethod
    def fromiter(cls, data: Iterable, imsize: tuple[int,int]) -> Self | None:
        return cls.__new(np.fromiter(data, dtype=np.uint8), imsize)

    @classmethod
    def fromcolor(cls, rgbcolor: HexColor | TupColor, imsize: tuple[int,int]) -> Self | None:
        color = translateRgb(rgbcolor)
        ndim = 2 + len(color) // 3
        return cls.__new(np.tile(color, (imsize[1], imsize[0], 1)[:ndim]))

    @classmethod
    def fromfile(cls, imgpath: str) -> Self | None:
        imbuffer, immat = np.fromfile(imgpath, dtype=np.uint8), None
        if imbuffer.size:
            immat = cv.imdecode(imbuffer, cv.IMREAD_UNCHANGED)
        if immat is None:
            raise TypeError('invallid image file')
        return cls.__new(immat)

    def copy(self) -> Self:
        return self.__class__.__new(self._immat.copy())

    def tofile(self, savepath: str) -> str:
        cv.imencode(f'.{savepath.rsplit(".",1)[-1]}', self._immat)[1].tofile(savepath)
        return os.path.abspath(savepath)

    def toarray(self) -> np.ndarray:
        return self._immat.copy()

    def tolist(self) -> list:
        return self._immat.tolist()

    def todotset(self,
        asname:              str,
        tmplExtractColor:    Literal[0,1] | HexColorRange,
        maskExtractColor:    Literal[0,1] | HexColorRange = None,
        matchcolor:          Literal[0,1] | HexColorRange = None,
        cropmode:            Literal[0,1,2] = 0,
        cropmargin:          int = 0,
    ) -> Dotset:
        from .dotset import Dotset
        return Dotset.fromimage(asname, self, tmplExtractColor, maskExtractColor, matchcolor, cropmode, cropmargin)


    @property
    def width(self) -> int:
        return self._immat.shape[1]

    @property
    def height(self) -> int:
        return self._immat.shape[0]

    @property
    def nchannel(self):
        if self._immat.ndim == 2: return 1
        return self._immat.shape[2]

    @property
    def npixel(self):
        return self._immat.shape[1] * self._immat.shape[0]

    @property
    def size(self) -> tuple[int,int]:
        return self._immat.shape[1::-1]

    @property
    def shape(self) -> tuple[int,int] | tuple[int,int,Literal[3,4]]:
        return self._immat.shape


    def show(self, usebrowser=True):
        if usebrowser:
            htmp, tmpfname = tempfile.mkstemp(suffix='.png')
            os.close(htmp)
            self.tofile(tmpfname)
            os.system(tmpfname)
            os.remove(tmpfname)
        else:
            cv.imshow(str(self), self._immat)
            cv.waitKey()
            cv.destroyAllWindows()

    def printsrc(self):
        displaymat = self._immat.astype(str)
        print('[')
        if displaymat.ndim == 2:
            for line in displaymat:
                print(f' [{", ".join([v.rjust(3) for v in line])}]')
        if displaymat.ndim == 3:
            for line in displaymat:
                print(' [', end='')
                for col in line:
                    print(f'[{",".join([v.rjust(3) for v in col])}]', end=', ')
                print('\b\b]')
        print(']')

    def printbinimg(self, mask: Image = None):
        assert self.nchannel==1 and ((self._immat==0)+(self._immat==255)).all(), 'Image must be binarized'
        displaymat = self._immat.astype(str)
        displaymat[displaymat[:,:]=='0'] = '··'
        displaymat[displaymat[:,:]=='255'] = '##'
        if mask: displaymat[mask._immat[:,:]==0] = '  '
        sep = '==' * (self.width+1)
        print(sep)
        for line in displaymat: print('|' + "".join(["".join(color) for color in line]) + '|')
        print(f'{sep}\n')


    def swapchannel(self) -> Self:
        nchannel = self.nchannel
        if nchannel == 1:
            return self.copy()
        return self.__class__.__new(self._immat[:,:,(2,1,0,*[3]*(nchannel==4))])

    def tonchannel(self, nchannel: Literal[1,3,4]) -> Self:
        modes = {1: 'GRAY', 3: 'BGR', 4: 'BGRA'}
        frommode = modes.get(self.nchannel)
        tomode = modes.get(nchannel) or f'channel{nchannel}'
        if frommode != tomode:
            transmode = getattr(cv, f'COLOR_{frommode}2{tomode}')
            return self.__class__.__new(cv.cvtColor(self._immat, transmode))
        return self.copy()

    def binarize(self, rgbrange: Literal[0,1] | HexColorRange) -> Self:
        if rgbrange == 0 or rgbrange == 1:
            grayscale = self._immat if self._immat.ndim==2 else cv.cvtColor(self._immat[:,:,:3], cv.COLOR_BGR2GRAY)
            binmat = cv.threshold(grayscale, 0, 255, ~rgbrange+2 | cv.THRESH_OTSU)[1]
        if isinstance(rgbrange, str):
            binmat = isColorsInRgbrange(self._immat, rgbrange).astype(np.uint8) * 255
        return self.__class__.__new(binmat)


    @overload
    def scale(self, scale: int | float) -> Self: ...

    @overload
    def scale(self, scaleX: int | float, scaleY: int | float) -> Self: ...

    def scale(self, scaleX: int | float, scaleY: int | float = None) -> Self:
        if scaleY is None: scaleY = scaleX
        assert scaleX > 0 and scaleY > 0, 'scale argument must be a positive number'
        if not self: return self.copy()
        return self.__class__.__new(cv.resize(self._immat, None, None, scaleX, scaleY, cv.INTER_AREA))


    def __bitoperation(self, method, *imgs):
        dstmat = self._immat
        for im in imgs: dstmat = method(dstmat, im._immat)
        return self.__class__.__new(dstmat)

    def bitwise_or(self, img: Self, *imgs: Self) -> Self:
        return self.__bitoperation(cv.bitwise_or, img, *imgs)

    def bitwise_xor(self, img: Self, *imgs: Self) -> Self:
        return self.__bitoperation(cv.bitwise_xor, img, *imgs)


    def minrgb(self) -> np.ndarray:
        if self.nchannel == 1:
            return np.repeat(self._immat.min(), 3)
        return self._immat[::3].min(0).min(0)[2::-1]

    def maxrgb(self) -> np.ndarray:
        if self.nchannel == 1:
            return np.repeat(self._immat.max(), 3)
        return self._immat[::3].max(0).max(0)[2::-1]

    def mainrgbrange(self, uint8offset: int = 0) -> HexColorRange:
        firstrgb = np.repeat(self._immat[0,0], 3) if self.nchannel==1 else self._immat[0,0][2::-1]
        diffrgb = np.repeat(uint8offset, 3)
        minrgb = self.minrgb()
        maxrgb = self.maxrgb()
        if rgb2gray(*firstrgb) <= rgb2gray(*minrgb)/2 + rgb2gray(*maxrgb)/2:
            minrgb = [max(minrgb[i], maxrgb[i] - diffrgb[i]) for i in range(3)]
        else: maxrgb = [min(maxrgb[i], minrgb[i] + diffrgb[i]) for i in range(3)]
        hexrgbs = ''.join(hex(v)[2:].zfill(2) for v in (*minrgb, *maxrgb))
        return f'{hexrgbs[:6]}--{hexrgbs[-6:]}'

    def border(self, objtype: Literal[0,1,2] = 0, objmargin: int = 0, bodrrgbrange: HexColorRange = '000000') \
            -> tuple[tuple[int,int], tuple[int,int]]:
        """
        提取图像中对象的边界
        :param objtype: 0:最小矩阵 1:全角矩阵 2:半角矩阵
        :param objmargin: 在对象四周保留的边距
        :param bodrrgbrange: 在图像四周与bodrcolor颜色相同的区域将被视为对象边框，以此判定对象的最小边界
        """
        srcH, srcW = self._immat.shape[:2]
        for col in range(srcW):
            if not isColorsInRgbrange(self._immat[:,col:col+1], bodrrgbrange).all(): break
        srcObjL = col
        for col in range(srcW - 1, srcObjL - 1, -1):
            if not isColorsInRgbrange(self._immat[:,col:col+1], bodrrgbrange).all(): break
        srcObjR = col + 1
        for line in range(srcH):
            if not isColorsInRgbrange(self._immat[line:line+1,:], bodrrgbrange).all(): break
        srcObjT = line
        for line in range(srcH - 1, srcObjT - 1, -1):
            if not isColorsInRgbrange(self._immat[line:line+1,:], bodrrgbrange).all(): break
        srcObjB = line + 1
        if objtype == 0:
            dstObjL, dstObjR, dstObjT, dstObjB = srcObjL, srcObjR, srcObjT, srcObjB
        if objtype in [1, 2]:
            srcObjW, srcObjH = srcObjR - srcObjL, srcObjB - srcObjT
            srcObjHWRatio = srcObjH / srcObjW
            dstObjHWRatio = objtype
            dstObjW = int(srcObjH / dstObjHWRatio) if srcObjHWRatio >= dstObjHWRatio else srcObjW
            dstObjH = srcObjH                      if srcObjHWRatio >= dstObjHWRatio else srcObjW * dstObjHWRatio
            paddingX, paddingY = int(dstObjW / 2 - srcObjW / 2), int(dstObjH / 2 - srcObjH / 2)
            if srcObjL < paddingX:
                dstObjL, dstObjR = srcObjL, min(srcObjL+dstObjW, srcW)
            else:
                dstObjR = min(srcObjR + paddingX, srcW)
                dstObjL = max(dstObjR-dstObjW, 0)
            if srcObjT < paddingY:
                dstObjT, dstObjB = srcObjT, min(srcObjT+dstObjH, srcH)
            else:
                dstObjB = min(srcObjB+paddingY, srcH)
                dstObjT = max(dstObjB-dstObjH, 0)
        if objmargin >= 0:
            dstL = max(dstObjL - objmargin, 0)
            dstR = min(dstObjR + objmargin, srcW)
            dstT = max(dstObjT - objmargin, 0)
            dstB = min(dstObjB + objmargin, srcH)
        return (dstL, dstT), (dstR, dstB)


    @classmethod
    def __concat(cls, imgs: Sequence[Self], fillrgb: HexColor | TupColor, axis: Literal[0,1]) -> Self:
        maxnchannel = max(im.nchannel for im in imgs)
        maxsize_onvaxis = max(im.shape[not axis] for im in imgs)
        imgs = map(lambda im:im if im.nchannel==maxnchannel else im.tonchannel(maxnchannel), imgs)
        fillcolor, fillndim = translateRgb(fillrgb, maxnchannel), 2 + maxnchannel // 3
        def fillmatof(im):
            imh, imw = im.shape[:2]
            reps = [(imh, maxsize_onvaxis - imw, 1), (maxsize_onvaxis-imh, imw, 1)][axis][:fillndim]
            return np.tile(fillcolor, reps)
        imgs = [np.concatenate([im._immat, fillmatof(im)], ~axis+2) for im in imgs]
        return cls.__new(np.concatenate(imgs, axis))

    @classmethod
    def concatH(cls, himgs: Sequence[Self], fillrgb: HexColor | TupColor = (0,)) -> Self:
        return cls.__concat(himgs, fillrgb, 1)

    @classmethod
    def concatV(cls, vimgs: Sequence[Self], fillrgb: HexColor | TupColor = (0,)) -> Self:
        return cls.__concat(vimgs, fillrgb, 0)

    @classmethod
    def concatHV(cls, himgslist: Sequence[Sequence[Self]], fillrgb: HexColor | TupColor = (0,)) -> Self:
        return cls.__concat([cls.__concat(himgs, fillrgb, 1) for himgs in himgslist], fillrgb, 0)

    @classmethod
    def concatVH(cls, vimgslist: Sequence[Sequence[Self]], fillrgb: HexColor | TupColor = (0,)) -> Self:
        return cls.__concat([cls.__concat(vimgs, fillrgb, 0) for vimgs in vimgslist], fillrgb, 1)

    def crop(self, start: tuple[int,int], end: tuple[int,int]) -> Self:
        l = max(start[0], 0)
        t = max(start[1], 0)
        r = min(end[0], self.width)
        b = min(end[1], self.height)
        return self.__class__.__new(self._immat[t:b, l:r].copy())

    def removeborder(self, bodrrgbrange: HexColorRange = '000000--303030') -> Self:
        return self.crop(*self.border(0, 0, bodrrgbrange))

    @overload
    def addborder(self, bodrwidth: int, rgbbodrcolor: HexColor | TupColor = (0,)) -> Self: ...

    @overload
    def addborder(self, bodrX: int, bodrY: int, rgbbodrcolor: HexColor | TupColor = (0,)) -> Self: ...

    @overload
    def addborder(self, bodrL: int, bodrY: int, bodrR: int, rgbbodrcolor: HexColor | TupColor = (0,)) -> Self: ...

    @overload
    def addborder(self, bodrL: int, bodrT: int, bodrR: int, bodrB: int, rgbbodrcolor: HexColor | TupColor = (0,)) -> Self: ...

    def addborder(self, *args) -> Self:
        if args and not hasattr(args[-1], '__index__'):
            args, rgbbodrcolor = args[:-1], args[-1]
        else: rgbbodrcolor = (0,)
        if not 1 <= len(args) <= 4:
            raise TypeError(
                'addborder() takes only 1-4 bodrwidth and 1 bodrcolor')
        lw, tw, rw, bw = [*args*(4//len(args)), *args[1:2]][:4]
        bodrcolor = translateRgb(rgbbodrcolor, self.nchannel)
        selfw, selfh = self.size
        selfndim = self._immat.ndim
        bodrmat = lambda h,w: np.tile(bodrcolor, (h,w,1)[:selfndim])
        lmat, rmat = bodrmat(selfh, lw), bodrmat(selfh, rw)
        tmat, bmat = bodrmat(tw, selfw+lw+rw), bodrmat(bw, selfw+lw+rw)
        return self.__class__.__new(np.concatenate([tmat, np.concatenate([lmat, self._immat, rmat], 1), bmat], 0))


    def findcolor(self, rgbrange: HexColorRange) -> MatTarget:
        for rgbrange in rgbrange.split('|'):
            ylist, xlist = np.where(isColorsInRgbrange(self._immat, rgbrange))
            if len(xlist):
                pos = xlist[0], ylist[0]
                return MatTarget.frompossize(pos, (1,1), rgbrange, 1.0)
        return MatTarget()

    def findcolors(self, rgbrange: HexColorRange) -> TargetList:
        targets = TargetList()
        for rgbrange in rgbrange.split('|'):
            ylist, xlist = np.where(isColorsInRgbrange(self._immat, rgbrange))
            targets += TargetList._new_((xlist, ylist, lambda x,y: MatTarget.frompossize((x,y), (1,1), rgbrange, 1.0)))
        return targets


    def __matchdotset(self, dotset, matchcolor, dsetscale, cache) -> DsetSimMat:
        # 在 ocr 和 finddotset 中调用，每次调用除了 dotset 外，其它参数是相同的
        # cache: {color: binimage, dotset: matchresult}
        # 点阵缩放后的宽和高不应大于图片，即使其宽高同时大于图片时不会抛错，但那样的匹配结果应该是毫无意义的
        if dotset not in cache:
            if matchcolor is None:
                matchcolor = dotset.matchcolor
            if matchcolor not in cache:
                cache[matchcolor] = self.binarize(matchcolor)
            scaleddset = dotset.scale(dsetscale)
            simmat = cv.matchTemplate(
                cache[matchcolor]._immat,
                scaleddset.tmpl._immat,
                cv.TM_CCOEFF_NORMED, None,
                scaleddset.mask and scaleddset.mask._immat
            )[:self.height, :self.width]
            cache[dotset] = DsetSimMat._new_([scaleddset], simmat)
        return cache[dotset]

    def finddotset(self,
        dotsetlib: DotsetLib,
        dotsets: str | Sequence[str],
        matchcolor: Literal[0,1] | HexColorRange = None,
        similarity = 0.95,
        dsetscale = 1.0
    ) -> MatTarget:
        cache = {}
        if isinstance(dotsets, str): dotsets = [dotsets]
        for name in dict.fromkeys(dotsets):
            for dotset in dotsetlib.group(name):
                targets = self.__matchdotset(dotset, matchcolor, dsetscale, cache).filter(similarity)
                if targets: return targets[0]
        return MatTarget()

    def finddotsets(self,
        dotsetlib: DotsetLib,
        dotsets: str | Sequence[str],
        matchcolor: Literal[0,1] | HexColorRange = None,
        similarity = 0.95,
        dsetscale = 1.0,
        ignore_overlaps = False
    ) -> TargetList:
        cache = {}
        targets = TargetList()
        if isinstance(dotsets, str): dotsets = [dotsets]
        for name in dict.fromkeys(dotsets):
            dsetsimmats = []
            for dotset in dotsetlib.group(name):
                dsetsimmats.append(self.__matchdotset(dotset, matchcolor, dsetscale, cache))
            if dsetsimmats:
                targets += DsetSimMat.merge(*dsetsimmats).filter(similarity, ignore_overlaps)
        return targets

    def __ocr(self, fontlib, matchcolor, similarity, txtdir, txtwrap, charscale, charset, cache) -> list[TargetList]:
        dsetsimmats = []
        if charset != fontlib.charset:
            charset = dict.fromkeys(charset)
        for char in charset:
            for dotset in fontlib.group(char):
                dsetsimmats.append(self.__matchdotset(dotset, matchcolor, charscale, cache))
        if dsetsimmats:
            chargroups = DsetSimMat.merge(*dsetsimmats).separate(similarity, True, txtdir)
            if not txtwrap: chargroups = [sum(chargroups, TargetList())]
            return chargroups
        return []

    def ocr(self,
        fontlib: FontLib,
        matchcolor: Literal[0,1] | HexColorRange = None,
        similarity = 0.95,
        txtdir: Literal[0,1] = 0,
        txtwrap = True,
        charscale = 1.0,
        charset: str | Literal[''] = None
    ) -> list[TargetList]:
        cache = {}
        return self.__ocr(fontlib, matchcolor, similarity, txtdir, txtwrap, charscale, charset or fontlib.charset, cache)

    def findtext(self,
        fontlib: FontLib,
        texts: str | Sequence[str],
        matchcolor: Literal[0,1] | HexColorRange = None,
        similarity = 0.95,
        txtdir: Literal[0,1] = 0,
        txtwrap = True,
        charscale = 1.0,
        charset: str | Literal[''] = None
    ) -> MatTarget:
        cache = {}
        ocr = lambda _charset: self.__ocr(fontlib, matchcolor, similarity, txtdir, txtwrap, charscale, _charset, cache)
        if charset != '': chargroups = ocr(charset or fontlib.charset)
        if isinstance(texts, str): texts = [texts]
        for text in texts:
            if charset == '': chargroups = ocr(text)
            for charlist in chargroups:
                index = charlist.join().name.find(text)
                if index >= 0: return charlist.join(index, index + len(text))
        return MatTarget()

    def findtexts(self,
        fontlib: FontLib,
        texts: str | Sequence[str],
        matchcolor: Literal[0,1] | HexColorRange = None,
        similarity = 0.95,
        txtdir: Literal[0,1] = 0,
        txtwrap = True,
        charscale = 1.0,
        charset: str | Literal[''] = None,
        ignore_overlaps = False
    ) -> TargetList:
        cache, found = {}, TargetList()
        ocr = lambda _charset: self.__ocr(fontlib, matchcolor, similarity, txtdir, txtwrap, charscale, _charset, cache)
        if charset != '': chargroups = ocr(charset or fontlib.charset)
        if isinstance(texts, str): texts = [texts]
        for text in texts:
            if text == '': continue
            if charset == '': chargroups = ocr(text)
            txtlen, txtreg = len(text), re.escape(text)
            regex = txtreg if ignore_overlaps else f'(?=({txtreg}))'
            for charlist in chargroups:
                for match in re.finditer(regex, charlist.join().name):
                    index = match.start()
                    found.append(charlist.join(index, index + txtlen))
        return found
