from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self
    from aclib.winlib import wintype
    from ._typing import _Pos, _Size, _Area

import time, getpass
from aclib.winlib.winapi import *
from aclib.winlib.wincon import *


__all__ = [
    'BaseWindow'
]


class BaseWindow(object):

    def __init__(self):
        self.__handle = 0

    def _sethandle_(self, hwnd: int) -> Self:
        self.__handle = hwnd
        return self

    def __bool__(self):
        return bool(self.handle)

    def __repr__(self):
        summary = self.title.replace('\n', '\\n') or self.classname
        return f'<{self.__class__.__name__}-{self.handle} {summary}>'


    @property
    def handle(self) -> int:
        return self.__handle

    @property
    def classname(self) -> str:
        return GetWindowClassName(self.handle)

    @property
    def title(self) -> str:
        return GetWindowTitle(self.handle)

    def settitle(self, title: str) -> bool:
        return SetWindowTitle(self.handle, title)


    @property
    def threadid(self) -> int:
        return GetWindowThreadProcessId(self.handle)[0]

    @property
    def processid(self) -> int:
        return GetWindowThreadProcessId(self.handle)[1]

    @property
    def threadprocessid(self) -> tuple[int, int]:
        return GetWindowThreadProcessId(self.handle)

    @property
    def creationtime(self) -> int:
        hthread = OpenThreadHandle(self.threadid)
        ctime = GetThreadTimes(hthread)[0]
        CloseHandle(hthread)
        return ctime

    @property
    def exittime(self) -> int:
        hthread = OpenThreadHandle(self.threadid)
        etime = GetThreadTimes(hthread)[1]
        CloseHandle(hthread)
        return etime


    def tolayeredwindow(self):
        LayerWindow(self.handle)

    def tounlayeredwindow(self):
        UnlayerWindow(self.handle)


    @property
    def isexistent(self) -> bool:
        return IsWindowExistent(self.handle)

    @property
    def isenabled(self) -> bool:
        return IsWindowEnabled(self.handle)

    @property
    def isvisible(self) -> bool:
        return IsWindowVisible(self.handle)

    @property
    def isviewable(self) -> bool:
        (l, t, r, b), (sw, sh) = self.rect.values(), GetScreenSize()
        return l < sw and t < sh and r > 0 and b > 0

    @property
    def ismaximized(self) -> bool:
        return IsWindowMaximized(self.handle)

    @property
    def isminimized(self) -> bool:
        return IsWindowMinimized(self.handle)

    @property
    def isnormalized(self) -> bool:
        return IsWindowNormalized(self.handle)

    @property
    def isforeground(self) -> bool:
        return self.handle == GetForegroundWindow()

    @property
    def istopmost(self) -> bool:
        return IsWindowTopMost(self.handle)


    def close(self):
        CloseWindow(self.handle)

    def destroy(self):
        DestroyWindow(self.handle)

    def enable(self):
        EnableWindow(self.handle)

    def disable(self):
        DisableWindow(self.handle)

    def show(self):
        ShowWindow(self.handle)

    def hide(self):
        HideWindow(self.handle)

    def maximize(self):
        MaximizeWindow(self.handle)

    def minimize(self):
        MinimizeWindow(self.handle)

    def normalieze(self):
        NormalizeWindow(self.handle)

    def settopmost(self, topmost: bool):
        SetWindowTopMost(self.handle, topmost)


    @property
    def rect(self) -> wintype.RECT:
        return GetWindowRect(self.handle)

    @property
    def rectR(self) -> wintype.RECT:
        return GetWindowRectR(self.handle)

    @property
    def pos(self) -> _Pos:
        return self.rect.start

    @property
    def posR(self) -> _Pos:
        return self.rectR.start

    @property
    def size(self) -> _Size:
        return self.rect.size

    def setpossize(self, newpos: _Pos, newsize: _Size):
        SetWindowPosSize(self.handle, newpos, newsize)

    def setpossizeR(self, newposR: _Pos, newsize: _Size):
        SetWindowPosSizeR(self.handle, newposR, newsize)

    def setpos(self, newpos: _Pos):
        SetWindowPosSize(self.handle, newpos)

    def setposR(self, newposR: _Pos):
        SetWindowPosSizeR(self.handle, newposR)

    def setsize(self, newsize: _Size):
        SetWindowPosSize(self.handle, None, newsize)


    @property
    def clientrect(self) -> wintype.RECT:
        return GetClientRect(self.handle)

    @property
    def clientrectR(self) -> wintype.RECT:
        return GetClientRectR(self.handle)

    @property
    def clientpos(self) -> _Pos:
        return self.clientrect.start

    @property
    def clientposR(self) -> _Pos:
        return self.clientrectR.start

    @property
    def clientsize(self) -> _Size:
        return self.clientrect.size

    def setclientpossize(self, newclientpos: _Pos, newclientsize: _Size):
        SetClientPosSize(self.handle, newclientpos, newclientsize)

    def setclientpossizeR(self, newclientposR: _Pos, newclientsize: _Size):
        SetClientPosSizeR(self.handle, newclientposR, newclientsize)

    def setclientpos(self, newclientpos: _Pos):
        SetClientPosSize(self.handle, newclientpos)

    def setclientposR(self, newclientposR: _Pos):
        SetClientPosSizeR(self.handle, newclientposR)

    def setclientsize(self, newclientsize: _Size):
        SetClientPosSize(self.handle, None, newclientsize)


    @property
    def transparency(self) -> float:
        return GetWindowTransparency(self.handle)

    def settransparency(self, transparency: float):
        SetWindowTransparency(self.handle, transparency)


    def getcolor(self, pos: _Pos) -> int:
        """get decimal bgr color at given pos"""
        return GetPixel(self.handle, pos)

    def capture(self, area: _Area) -> tuple[_Size, bytearray]:
        return CaptureWindow(self.handle, area)


    def movemouse(self, topos: _Pos):
        PostMessage(self.handle, WM_MOUSEMOVE, 0, MakeLong(*topos))


    def leftdown(self, pos: _Pos):
        PostMessage(self.handle, WM_LBUTTONDOWN, MK_LBUTTON, MakeLong(*pos))

    def leftup(self, pos: _Pos):
        PostMessage(self.handle, WM_LBUTTONUP, MK_LBUTTON, MakeLong(*pos))

    def leftclick(self, pos: _Pos):
        self.leftdown(pos)
        self.leftup(pos)

    def leftdbclick(self, pos: _Pos):
        self.leftclick(pos)
        self.leftclick(pos)

    def leftdrag(self, pos: _Pos, topos: _Pos):
        self.leftdown(pos)
        self.movemouse(topos)
        self.leftup(topos)

    def leftdragR(self, pos: _Pos, dpos: _Pos):
        self.leftdrag(pos, (pos[0] + dpos[0], pos[1] + dpos[1]))


    def rightdown(self, pos: _Pos):
        PostMessage(self.handle, WM_RBUTTONDOWN, MK_RBUTTON, MakeLong(*pos))

    def rightup(self, pos: _Pos):
        PostMessage(self.handle, WM_RBUTTONUP, MK_RBUTTON, MakeLong(*pos))

    def rightclick(self, pos: _Pos):
        self.rightdown(pos)
        self.rightup(pos)

    def rightdbclick(self, pos: _Pos):
        self.rightclick(pos)
        self.rightclick(pos)

    def rightdrag(self, pos: _Pos, topos: _Pos):
        self.rightdown(pos)
        self.movemouse(topos)
        self.rightup(topos)

    def rightdragR(self, pos: _Pos, dpos: _Pos):
        self.rightdrag(pos, (pos[0] + dpos[0], pos[1] + dpos[1]))


    def middown(self, pos: _Pos):
        PostMessage(self.handle, WM_MBUTTONDOWN, MK_MBUTTON, MakeLong(*pos))

    def midup(self, pos: _Pos):
        PostMessage(self.handle, WM_MBUTTONUP, MK_MBUTTON, MakeLong(*pos))

    def midclick(self, pos: _Pos):
        self.middown(pos)
        self.midup(pos)

    def middrag(self, pos: _Pos, topos: _Pos):
        self.middown(pos)
        self.movemouse(topos)
        self.midup(topos)

    def middragR(self, pos: _Pos, dpos: _Pos):
        self.middrag(pos, (pos[0] + dpos[0], pos[1] + dpos[1]))

    def wheelup(self, pos, times=1):
        self.movemouse(pos)
        lParam = MakeLong(*ClientToScreen(self.handle, *pos))
        for i in range(times):
            PostMessage(self.handle, WM_MOUSEWHEEL, WHEEL_DELTA, lParam)

    def wheeldown(self, pos, times=1):
        self.movemouse(pos)
        lParam = MakeLong(*ClientToScreen(self.handle, *pos))
        for i in range(times):
            PostMessage(self.handle, WM_MOUSEWHEEL, -WHEEL_DELTA, lParam)


    def keydown(self, key: int | str):
        PostMessage(self.handle, WM_IME_KEYDOWN, *MakeKeyMessageParam(key)[0])

    def keyup(self, key:int|str):
        PostMessage(self.handle, WM_IME_KEYUP, *MakeKeyMessageParam(key)[1])

    def keypress(self, key: int | str):
        self.keydown(key)
        self.keyup(key)

    def waitkey(self, *keys: int | str, msg='', cmdmode=False) -> int | str:
        vkmap = {}
        for key in keys:
            vkcode = MakeKeyCode(key)
            if not vkcode:
                raise ValueError(f'invalid key <- {key} ->')
            vkmap[vkcode] =  key
        vkmap = vkmap or VK_MAP_KEYBOARD
        print(msg)
        while True:
            for vkcode in vkmap:
                if GetAsyncKeyState(vkcode):
                    if cmdmode:
                        if vkcode != 13: self.keypress('enter')
                        getpass.getpass('')
                    return vkmap[vkcode]
            time.sleep(.001)

    def sendtext(self, text: str):
        for char in text:
            PostMessage(self.handle, WM_CHAR, ord(char), 0)
