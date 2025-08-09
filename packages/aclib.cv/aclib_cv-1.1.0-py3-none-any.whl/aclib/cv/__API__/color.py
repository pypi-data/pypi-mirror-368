from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal, Iterator

import re
import numpy as np

from typing import Union

Uint8, Uhex8 = int, str
TupColor = Union[ tuple[Uint8], tuple[Uint8, Uint8, Uint8], tuple[Uint8, Uint8, Uint8, Uint8]]
HexColor = str          # see TypeError in matchHexColor()
HexColorRange = str     # see TypeError in matchHexColorRange()


def matchHexColor(color: HexColor):
    uhex8 = r'([0-9a-fA-F]{2})'
    match = re.search(f'^{uhex8}(?:{uhex8}{uhex8}{uhex8}?)?$', color)
    if not match: raise TypeError(
        f"HexColor shuold be a string like '0f', '0f0f0f' or '0f0f0fff'. got '{color}'")
    return match.groups()   # (r, g, b, a), None will replace blank

def matchHexColorRange(colorrange: HexColorRange):
    uhex8 = r'([0-9a-fA-F]{2})'
    match = re.search(f'^(-)?{uhex8}{uhex8}{uhex8}(?:(-{{1,2}}){uhex8}{uhex8}{uhex8})?$', colorrange)
    if not match: raise TypeError(
        "HexColorRange should be a string like '-?0e0e0e|-?0e0e0e(mid)-010101(diff)|-0d0d0d(min)--0f0f0f(max)', ")
    return match.groups()   # (sign, r1, g1, b1, sep, r2, g2, b2), None will replace blank

def hextup2inttup(uhex8tuple: tuple[Uhex8, ...]) -> tuple[Uint8, ...]:
    return tuple(int(uhex8, 16) for uhex8 in uhex8tuple if uhex8)


def rgb2gray(r: Uint8, g: Uint8, b: Uint8) -> Uint8:
    return int(0.114 * b + 0.587 * g + 0.299 * r + 0.5)

def translateRgb(rgbcolor: HexColor | TupColor, dstnchannel: Literal[1,3,4] = None) -> np.ndarray:
    if isinstance(rgbcolor, HexColor):
        rgbcolor = hextup2inttup(matchHexColor(rgbcolor))
    if dstnchannel and dstnchannel != len(rgbcolor):
        if dstnchannel == 1:
            rgbcolor = (rgb2gray(*rgbcolor[:3]),)
        else: rgbcolor = (*rgbcolor, *rgbcolor[:1]*(len(rgbcolor)==1)*2, 255)[:dstnchannel]
    bgrcolor = (*rgbcolor[2::-1], *rgbcolor[3:4])
    return np.array(bgrcolor, dtype=np.uint8)

def translateRgbrange(rgbrange: HexColorRange, graymode=False) -> Iterator[tuple[bool, TupColor, TupColor]]:
    mid_diff, min_max = 1, 2
    for rgbrange in rgbrange.split('|'):
        sign, r1, g1, b1, sep, r2, g2, b2 = matchHexColorRange(rgbrange)
        include, rangemode = sign != '-', len(sep or '--')
        lbgr, rbgr = hextup2inttup((b1, g1, r1)), hextup2inttup((b2, g2, r2))
        if rangemode == min_max:
            minbgr, maxbgr = lbgr, rbgr or lbgr
        if rangemode == mid_diff:
            midbgr, difbgr = lbgr, rbgr or (0, 0, 0)
            minbgr = tuple(max(midbgr[i] - difbgr[i], 0x00) for i in range(3))
            maxbgr = tuple(min(midbgr[i] + difbgr[i], 0xff) for i in range(3))
        if graymode:
            minbgr, maxbgr = (max(minbgr),), (min(maxbgr),)
        yield include, minbgr, maxbgr


def isColorsInRgbrange(immat: np.ndarray, rgbrange: HexColorRange) -> np.ndarray:
    isInRanges, graymode = None, immat.ndim == 2
    if not graymode: immat = immat[:,:,:3]
    for include, minbgr, maxbgr in translateRgbrange(rgbrange, graymode):
        isInRange = (immat >= minbgr) * (immat <= maxbgr)
        if not graymode:
            isInRange = isInRange.all(2)
        if not include:
            isInRange = ~isInRange
        isInRanges = isInRange if isInRanges is None else np.bitwise_or(isInRanges, isInRange)
    return isInRanges
