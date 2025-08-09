from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self, Literal
    from ._typing import _Area, _Areas

import os, itertools
from aclib.dm import DM, DmDotsetLib
from aclib.builtins import MatTarget

from .window import Window


class DmWindow(Window):

    def __init__(self):
        super().__init__()
        self.__dmbind = False
        self.__dmwordlock = False
        self.__dmdlib: DmDotsetLib = None

    @property
    def __dm(self) -> DM:
        del DmWindow.__dm
        self.__dm = DM()
        self.__dm.SetShowErrorMsg(0)
        return self.__dm

    def dmset(self,
        displaymode: Literal['dx', 'dx2', 'dx3', 'gdi', 'gdi2'] | None = '',
        flib: str | None = '',
        dlib: str | None = '',
        dlibscale: float = 1.0
    ) -> Self:
        """传入空字符串时对应参数不做更改，传入None时清除已设置的值"""
        if displaymode:
            self.__dm.UnBindWindow()
            self.__dm.BindWindow(self.handle, displaymode, 'windows', 'windows', 0)
            self.__dmbind = True
        if flib:
            if not os.path.isfile(flib):
                raise FileNotFoundError(
                    f'No such file or directory: {flib}')
            self.__dm.SetDict(0, flib)
        if dlib:
            self.__dmdlib = DmDotsetLib.fromfile(dlib).scale(dlibscale)
        if displaymode is None:
            self.__dm.UnBindWindow()
            self.__dmbind = False
        if flib is None:
            self.__dm.ClearDict()
            self.__dmwordlock = False
        if dlib is None:
            self.__dmdlib = None
        return self


    def __dmassert_bind(self):
        assert self.__dmbind, 'please call dmset() first'

    def __dmtransfer_areas(self, areas: _Area|_Areas|None) -> _Areas:
        self.__dmassert_bind()
        if areas is None:
            return [(0, 0, *self.clientsize)]
        if hasattr(areas[0], '__index__'):
            return [areas]
        return areas


    def dmcapture(self, area: _Area=None, savepath: str=''):
        self.__dmassert_bind()
        area = area or (0, 0, *self.clientsize)
        self.__dm.Capture(*area, savepath)

    def dmfindcolor(self, color: str, areas: _Area|_Areas=None) -> MatTarget:
        areas = self.__dmtransfer_areas(areas)
        for area, color in itertools.product(areas, color.split('|')):
            x, y, success = self.__dm.FindColor(*area, color, 1, 0)
            if success:
                return MatTarget(x, y, x+1, y+1, color, 1.0)
        return MatTarget()

    def dmfindcolors(self, color: str, areas: _Area|_Areas=None) -> list[MatTarget]:
        found, areas = [], self.__dmtransfer_areas(areas)
        for area, color in itertools.product(areas, color.split('|')):
            res = self.__dm.FindColorEx(*area, color, 1, 0)
            if not res: continue
            xs, ys = [[int(coor) for coor in coors.split(',')] for coors in res.split('|')]
            for i in range(min(len(xs), len(ys))):
                x, y = xs[i], ys[i]
                found.append(MatTarget(x, y, x+1, y+1, color, 1.0))
        return found

    def dmfindcolorblock(self, colorBlock: str, areas: _Area|_Areas=None, similarity=1, scale=1) -> MatTarget:
        """ colorBlock: '{w}x{h}x{color}|{w}x{h}x{color}' like '3x5xefefef-101010' """
        areas = self.__dmtransfer_areas(areas)
        for area, colorBlock in itertools.product(areas, colorBlock.split('|')):
            w,h,color = [(round(int(w)*scale), round(int(h)*scale), color) for w,h,color in [(info for info in colorBlock.split('x'))]][0]
            dmColorBlock = ','.join([f'{i%w}|{i//w}|{color}' for i in range(w*h)])
            x, y, success = self.__dm.FindMultiColor(*area, color, dmColorBlock, similarity, 0)
            if success:
                return MatTarget.frompossize((x, y), (w, h), f'{w}x{h}x{color}', similarity)
        return MatTarget()

    def dmfindcolorblocks(self, colorBlock: str, areas: _Area|_Areas=None, similarity=1, scale=1) -> list[MatTarget]:
        """ colorBlock: '{w}x{h}x{color}|{w}x{h}x{color}' like '3x5xefefef-101010' """
        found, areas = [], self.__dmtransfer_areas(areas)
        for area, colorBlock in itertools.product(areas, colorBlock.split('|')):
            w,h,color = [(round(int(w)*scale), round(int(h)*scale), color) for w,h,color in [(info for info in colorBlock.split('x'))]][0]
            dmColorBlock = ','.join([f'{i%w}|{i//w}|{color}' for i in range(w*h)])
            res = self.__dm.FindMultiColorEx(*area, color, dmColorBlock, similarity, 0)
            if not res: continue
            xs, ys = [[int(coor) for coor in coors.split(',')] for coors in res.split('|')]
            for i in range(min(len(xs), len(ys))):
                found.append(MatTarget.frompossize((xs[i], ys[i]), (w, h), f'{w}x{h}x{color}', similarity))
        return found

    def dmfinddotset(self, dotsetname: str, areas: _Area|_Areas=None, color: str=None, similarity=1, scale=1) -> MatTarget:
        if not self.__dmdlib:
            return MatTarget()
        areas = self.__dmtransfer_areas(areas)
        for area, dotsetname in itertools.product(areas, dotsetname.split('|')):
            for dotset in self.__dmdlib.group(dotsetname):
                dotset = dotset.scale(scale).asmatchcolor(color)
                x, y, success = self.__dm.FindMultiColor(*area, dotset.matchcolor, dotset.tmpl, similarity, 0)
                if success:
                    start = dotset.getrealpos((x, y))
                    end = start[0] + dotset.width, start[1] + dotset.height
                    return MatTarget(*start, *end, dotsetname, similarity)
        return MatTarget()

    def dmfinddotsets(self, dotsetname: str, areas: _Area|_Areas=None, color: str=None, similarity=1, scale=1) -> list[MatTarget]:
        if not self.__dmdlib:
            return []
        found, areas = [], self.__dmtransfer_areas(areas)
        for area, dotsetname in itertools.product(areas, dotsetname.split('|')):
            for dotset in self.__dmdlib.group(dotsetname):
                dotset = dotset.scale(scale).asmatchcolor(color)
                res = self.__dm.FindMultiColorEx(*area, dotset.matchcolor, dotset.tmpl, similarity, 0)
                if not res: continue
                xs, ys = [[int(coor) for coor in coors.split(',')] for coors in res.split('|')]
                for i in range(min(len(xs), len(ys))):
                    x, y = xs[i], ys[i]
                    start = dotset.getrealpos((x, y))
                    end = start[0] + dotset.width, start[1] + dotset.height
                    found.append(MatTarget(*start, *end, dotsetname, similarity))
        return found

    def dmfindword(self, texts: str, areas: _Area|_Areas, color: str, similarity=0.9) -> MatTarget:
        while self.__dmwordlock: pass
        self.__dmwordlock = True
        found = MatTarget()
        for area in self.__dmtransfer_areas(areas):
            x, y, index = self.__dm.FindStrFast(*area, texts, color, similarity)
            if index > -1:
                found = MatTarget(x, y, x, y, texts.split('|')[index], similarity)
                break
        self.__dmwordlock = False
        return found

    def dmfindwords(self, texts: str, areas: _Area|_Areas, color: str, similarity=0.9) -> list[MatTarget]:
        while self.__dmwordlock: pass
        self.__dmwordlock = True
        found = []
        textList = texts.split('|')
        for area in self.__dmtransfer_areas(areas):
            res = self.__dm.FindStrFastEx(*area, texts, color, similarity)
            if not res: continue
            for info in res.split('|'):
                index, x, y = info.split(',')
                word = textList[int(index)]
                pos = int(x), int(y)
                found.append(MatTarget(*pos, *pos, word, similarity))
        self.__dmwordlock = False
        return found
