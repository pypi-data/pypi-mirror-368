from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self, Sequence, Literal, Callable, TypeVar, Generator
    from ._typing import _Area, _Areas
    from aclib.cv._typing import HexColorRange
    T = TypeVar('T')

from aclib.builtins import MatTarget
from aclib.cv import Image, FontLib, DotsetLib, TargetList
from aclib.winlib import winapi

from .window import Window


class CvWindow(Window):

    def __init__(self):
        super().__init__()
        self.__cvflib = FontLib()
        self.__cvdlib = DotsetLib()

    FontLib = FontLib
    DotsetLib = DotsetLib

    def cvset(self, dlib: DotsetLib|None=..., flib: FontLib|None=...) -> Self:
        """传入None删除已设置的库，不传(或传入...)则不修改"""
        if isinstance(flib, FontLib):
            self.__cvflib = flib
        if isinstance(dlib, DotsetLib):
            self.__cvdlib = dlib
        if flib is None:
            self.__cvflib = FontLib()
        if dlib is None:
            self.__cvdlib = DotsetLib()
        return self

    def cvcapture(self, area: _Area=None, savepath='') -> Image | None:
        if area and not isinstance(area[0], int):
            area = tuple(map(int, area))
        size, buffer = winapi.CaptureWindow(self.handle, area)
        screenshot = Image.frombuffer(buffer, size)
        if savepath:
            screenshot.tofile(savepath)
        return screenshot


    def __cviter_target(self, capareas: _Area|_Areas|None, capscale: float, func: Callable[[Image], T]) -> Generator[tuple[tuple[int,int], T], None, None]:
        if capareas is None:
            capareas = [(0, 0, *self.clientsize)]
        if hasattr(capareas[0], '__index__'):
            capareas = [capareas]
        for caparea in capareas:
            capstart = caparea[:2]
            screenshot = self.cvcapture(caparea)
            if not screenshot:
                continue
            if capscale != 1:
                screenshot = screenshot.scale(capscale)
            yield capstart, func(screenshot)

    def __cvfind_target(self, capareas: _Area|_Areas|None, capscale: float, func: Callable[[Image], MatTarget]) -> MatTarget:
        for start, target in self.__cviter_target(capareas, capscale, func):
            if target:
                return target.scale(1/capscale).offset(*start)
        return MatTarget()

    def __cvfind_targets(self, capareas: _Area|_Areas|None, capscale: float, func: Callable[[Image], TargetList]) -> list[MatTarget]:
        found = []
        for start, targets in self.__cviter_target(capareas, capscale, func):
            found.extend(target.scale(1/capscale).offset(*start) for target in targets)
        return found


    def cvfindcolor(self, rgbranges: HexColorRange, areas: _Area|_Areas=None) -> MatTarget:
        return self.__cvfind_target(areas, 1, lambda cap: cap.findcolor(rgbranges))

    def cvfindcolors(self, rgbranges: HexColorRange, areas: _Area|_Areas=None) -> list[MatTarget]:
        return self.__cvfind_targets(areas, 1, lambda cap: cap.findcolors(rgbranges))

    def cvfinddotset(self,
        dotsets: str|Sequence[str],
        areas: _Area|_Areas=None,
        matchcolor: Literal[0,1]|HexColorRange=None,
        similarity = 0.9,
        capscale = 1.0,
        usedlib: DotsetLib|None=None,
    ) -> MatTarget:
        if len(_dlib := usedlib or self.__cvdlib) == 0:
            return MatTarget()
        return self.__cvfind_target(
            areas, capscale, lambda cap: cap.finddotset(_dlib, dotsets, matchcolor, similarity))

    def cvfinddotsets(self,
        dotsets: str|Sequence[str],
        areas: _Area|_Areas=None,
        matchcolor: Literal[0,1]|HexColorRange=None,
        similarity = 0.9,
        capscale = 1.0,
        ignore_overlaps = False,
        usedlib: DotsetLib|None=None,
    ) -> list[MatTarget]:
        if len(_dlib := usedlib or self.__cvdlib) == 0:
            return []
        return self.__cvfind_targets(
            areas, capscale, lambda cap: cap.finddotsets(_dlib, dotsets, matchcolor, similarity, 1, ignore_overlaps))

    def cvfindtext(self,
        texts: str|Sequence[str],
        areas: _Area|_Areas=None,
        matchcolor: Literal[0,1]|HexColorRange=None,
        similarity = 0.9,
        txtdir: Literal[0,1]=0,
        txtwrap = True,
        capscale = 1.0,
        charset: str|Literal['']=None,
        useflib: FontLib|None=None,
    ) -> MatTarget:
        if len(_flib := useflib or self.__cvflib) == 0:
            return MatTarget()
        return self.__cvfind_target(
            areas, capscale, lambda cap: cap.findtext(_flib, texts, matchcolor, similarity, txtdir, txtwrap, 1, charset))

    def cvfindtexts(self,
        texts: str|Sequence[str],
        areas: _Area|_Areas=None,
        matchcolor: Literal[0,1]|HexColorRange=None,
        similarity = 0.9,
        txtdir: Literal[0,1]=0,
        txtwrap = True,
        capscale = 1.0,
        charset: str|Literal['']=None,
        ignore_overlaps = False,
        useflib: FontLib|None=None,
    ) -> list[MatTarget]:
        if len(_flib := useflib or self.__cvflib) == 0:
            return []
        return self.__cvfind_targets(
            areas, capscale, lambda cap: cap.findtexts(_flib, texts, matchcolor, similarity, txtdir, txtwrap, 1, charset, ignore_overlaps))

    def cvocr(self,
        areas: _Area|_Areas=None,
        matchcolor: Literal[0,1]|HexColorRange=None,
        similarity = 0.9,
        txtdir: Literal[0,1]=0,
        txtwrap = True,
        capscale = 1.0,
        charset: str|Literal['']=None,
        useflib: FontLib|None=None,
    ) -> list[MatTarget]:
        if len(_flib := useflib or self.__cvflib) == 0:
            return []
        texts = []
        for start, ocrgroups in self.__cviter_target(
            areas, capscale, lambda cap: cap.ocr(_flib, matchcolor, similarity, txtdir, txtwrap, 1, charset)
        ):
            texts.extend(ocrgroup.join().scale(1/capscale).offset(*start) for ocrgroup in ocrgroups)
        return texts
