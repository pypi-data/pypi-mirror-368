from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

from aclib.winlib.winapi import *

from .basewindow import BaseWindow


__all__ = [
    'Window'
]


class Window(BaseWindow):


    @classmethod
    def fromhandle(cls, hwnd: int) -> Self:
        return cls()._sethandle_(hwnd)

    def __repr__(self):
        alias = ''
        if self.handle == GetDesktopWindow():
            alias = '.desktopwindow'
        if self.handle == GetDesktopView():
            alias = '.desktop'
        if self.handle == GetTaskbarWindow():
            alias = '.taskbar'
        return super().__repr__().replace(self.__class__.__name__, f'{self.__class__.__name__}{alias}', 1)


    @classmethod
    def findwindow(cls, title='', classname='', visible: bool=None) -> Self:
        return cls.fromhandle(FilterWindow(IterDescendantWindows(0), title, classname, visible))

    @classmethod
    def findwindows(cls, title='', classname='', visible: bool=None) -> list[Self]:
        return [cls.fromhandle(h) for h in FilterWindows(IterDescendantWindows(0), title, classname, visible)]


    @classmethod
    def desktopwindow(cls) -> Self:
        """winapi中定义的DesktopWindow"""
        return cls.fromhandle(GetDesktopWindow())

    @classmethod
    def desktop(cls) -> Self:
        """显示桌面图标的窗口"""
        return cls.fromhandle(GetDesktopView())

    @classmethod
    def taskbar(cls) -> Self:
        return cls.fromhandle(GetTaskbarWindow())


    @classmethod
    def pointwindow(cls, pos: tuple[int, int] = None) -> Self:
        return cls.fromhandle(GetPointWindow(pos or GetCursorPos()))

    @classmethod
    def foregroundwindow(cls) -> Self:
        return cls.fromhandle(GetForegroundWindow())


    def parent(self) -> Self:
        return self.fromhandle(GetParentWindow(self.handle))

    def root(self) -> Self:
        return self.fromhandle(GetRootWindow(self.handle))

    def rootowner(self) -> Self:
        return self.fromhandle(GetRootOwnerWindow(self.handle))


    def prevbrother(self) -> Self:
        return self.fromhandle(GetPrevWindow(self.handle))

    def nextbrother(self) -> Self:
        return self.fromhandle(GetNextWindow(self.handle))

    def brother(self, title='', classname='', visible: bool=None) -> Self:
        return self.fromhandle(FilterWindow(IterBrotherWindows(self.handle), title, classname, visible))

    def brothers(self, title='', classname='', visible: bool=None) -> list[Self]:
        return [self.fromhandle(h) for h in FilterWindows(IterBrotherWindows(self.handle), title, classname, visible)]


    def child(self, title='', classname='', visible: bool=None) -> Self:
        return self.fromhandle(FilterWindow(IterChildWindows(self.handle), title, classname, visible))

    def children(self, title='', classname='', visible: bool=None) -> list[Self]:
        return [self.fromhandle(h) for h in FilterWindows(IterChildWindows(self.handle), title, classname, visible)]


    def descendant(self, title='', classname='', visible: bool=None) -> Self:
        return self.fromhandle(FilterWindow(IterDescendantWindows(self.handle), title, classname, visible))

    def descendants(self, title='', classname='', visible: bool=None) -> list[Self]:
        return [self.fromhandle(h) for h in FilterWindows(IterDescendantWindows(self.handle), title, classname, visible)]
