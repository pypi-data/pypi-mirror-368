from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self, Callable, Any
    from ._typing import _AppCSS, _AppRunningCss

import ctypes, inspect
from time import sleep
from typing import overload
from aclib.builtins import decorator
from aclib.winlib import winapi, wincon, wintype
from aclib.winlib.wincon import *
from aclib.winlib.__API__._windll import user32, gdi32, kernel32
from .background import BackgroundBuffer
from .pytypes import reactive_dict, apptask

from ..__API__.basewindow import BaseWindow


__all__ = [
    'AppWindow',
]

WM_APP_REDRAW = WM_APP + 0x0080


class AppWindow(BaseWindow):

    @classmethod
    def __newappwin(cls, wtype: int, wparent: Self | int, wclass: str) -> Self:
        window = cls()
        window.__create_params = (wtype, wparent, wclass)
        return window

    @decorator.instance_classmethod
    def newoverlapped(parent: Self | int = 0, wnd_class='aclib.winapp') -> Self:
        return parent.cls.__newappwin(WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX, parent.self, wnd_class)

    @decorator.instance_classmethod
    def newpopup(parent: Self | int, wnd_class='aclib.winapp') -> Self:
        return parent.cls.__newappwin(WS_POPUP|WS_MINIMIZEBOX, parent.self, wnd_class)

    @decorator.instance_classmethod
    def newchild(parent: Self | int, wnd_class='aclib.winapp') -> Self:
        return parent.cls.__newappwin(wincon.WS_CHILD, parent.self, wnd_class)

    @decorator.instance_classmethod
    def new_button(parent: Self | int) -> Self:
        ...

    @decorator.instance_classmethod
    def new_sys_static(parent: Self | int) -> Self:
        ...

    @decorator.instance_classmethod
    def new_sys_edit(parent: Self | int) -> Self:
        ...

    def __init__(self):
        super().__init__()
        self.__listener: dict[int, dict[Callable, None]] = {}
        self.__trackingmouse = False
        self.__rect_dsize = 0
        self.__sys_control = BaseWindow()
        self.__css_calculated: _AppCSS = reactive_dict(on_update=self.__on_css_using_update__)
        self.__css_normal: _AppCSS = reactive_dict(on_update=self.__on_css_base_update__)
        self.__css_hover: _AppCSS = reactive_dict(on_update=self.__on_css_base_update__)
        self.__css_active: _AppCSS = reactive_dict(on_update=self.__on_css_base_update__)
        self.__css_usename: _AppRunningCss = reactive_dict({'cssname': 'normal'}, on_update=self.__on_css_base_update__)
        self.css()

    def __repr__(self):
        wndid = self.handle or hex(id(self))
        wndsummary = self.title or self.classname if self.handle else 'UNCREATED'
        return f'<{self.__class__.__name__}-{wndid} {wndsummary}>'

    def css(self, css: _AppCSS={
        'win-title': '',
        'win-pos': 'unset',
        'win-size': 'unset',
        'win-visible': True,
        'win-opacity': 1.0,
        'win-caption-theme': 'toggle',
        'win-ask-close': False,
        'win-cursor': 'arrow',
        'win-icon': '',
        'bk-color': 0xffffff,
        'bk-image': 'none',
        'bk-image-pos': (0,0),
        'bk-image-crop-start': (0,0),
        'bk-image-crop-size': 'auto',
        'bk-text': '',
        'bk-text-color': 0x0,
        'bk-text-align': 'MM',
        'bk-text-offset': (0,0),
        'bk-text-overflow': 'clip',
        'bk-font': '微软雅黑',
        'bk-font-size': 18,
        'bk-font-weight': 'normal',
        'bk-font-italic': False,
        'bk-font-strike': False,
        'bk-font-underline': False,
    }) -> Self:
        """
        - 此方法可多次、链式地调用。不传参数，样式表将被重置为默认值；传入参数，同名属性将被更新
        - 窗口被创建后，配置 win-pos 和 win-size 只会修改子窗口的位置和大小，对于非子窗口，请使用 app.setpos 和 app.setsize
        - bk-text-overflow 设为 wrap 时，bk-text-align 指定的纵向对齐方式将无效
        - bk-color 目前仅支持十进制 BGR 颜色值，如 0xffffff
        """
        return self.__css_normal.update(css) or self

    def csshover(self, css: _AppCSS) -> Self:
        """鼠标悬停在窗口上时生效，此方法可多次、链式地调用，新的样式表将会更新原来的样式表"""
        return self.__css_hover.update(css) or self

    def cssactive(self, css: _AppCSS) -> Self:
        """鼠标在窗口上按下时生效，此方法可多次、链式地调用，新的样式表将会更新原来的样式表"""
        return self.__css_active.update(css) or self

    def cssget(self, name: str):
        return self.__css_calculated.get(name)

    def create(self) -> Self:
        assert self.handle == 0, 'AppWindow could be created only once.'
        wtype, wparent, wclass = self.__create_params
        hparent = getattr(wparent, 'handle', wparent)
        if not winapi.GetWindowClassInfo(wclass).hInstance:
            winapi.RegisterWindowClass(wclass, self.__wndproc)
        self.__checkthread()
        if wclass == 'listbox':
            wtype |= WS_VSCROLL | LBS_NOTIFY
        h = apptask(winapi.CreateWindow, self.__appthread)(
            hparent, wclass, '', 0, 0, wtype|ES_AUTOHSCROLL, wincon.WS_EX_LAYERED, id(self))
        if h and winapi.IsWindowClassInSystem(wclass):
            self._sethandle_(h)
            self._ctl_hbkclr = 0
            self._bk = BackgroundBuffer()
            self.__css_usename.update(cssname='normal')
            self.__appwindows[h] = self
            winapi.RedrawWindow(h)
        self.__checkwindow()
        return self

    def loop(self):
        while winapi.IsWindowExistent(self.handle):
            sleep(1)


    def __on_css_base_update__(self, old: _AppCSS, new: _AppCSS, _):
        if self.handle == 0:
            return
        usename = self.__css_usename['cssname']
        calculated = {} | self.__css_normal
        if usename in ['hover', 'active']:
            calculated |= self.__css_hover
        if usename == 'active':
            calculated |= self.__css_active
        self.__css_calculated.update(calculated)

    def __on_css_using_update__(self, old: _AppCSS, new: _AppCSS, diffkeys: str):
        if 'win-title' in diffkeys:
            self.settitle(new['win-title'])
            self.__sys_control.settitle(new['win-title'])
        if 'win-pos' in diffkeys or 'win-size' in diffkeys \
        and winapi.GetWindowLong(self.handle, wincon.GWL_STYLE) & wincon.WS_CHILDWINDOW:
            pos, size = new['win-pos'], new['win-size']
            pos, size = 0 if pos == 'unset' else pos, 0 if size == 'unset' else size
            self.setpossizeR(pos, size)
            self.__sys_control.setsize(size)
        if 'win-icon' in diffkeys:
            winapi.SendMessage(self.handle, wincon.WM_SETICON, 0, 0)
        if 'win-opacity' in diffkeys:
            self.settransparency(new['win-opacity'])
        if 'win-caption-theme' in diffkeys and (_wct := new['win-caption-theme']) in ('active', 'blur'):
            winapi.SendMessage(self.handle, wincon.WM_NCACTIVATE, _wct == 'active', 0)
        if 'win-cursor' in diffkeys:
            winapi.PostMessage(self.handle, wincon.WM_SETCURSOR, self.handle, winapi.MakeLong(wincon.HTCLIENT, wincon.WM_MOUSEMOVE))
        if 'bk-' in diffkeys:
            winapi.SendMessage(self.handle, WM_APP_REDRAW, 0, 'bk-font' in diffkeys)
        if 'bk-font' in diffkeys:
            winapi.PostMessage(self.handle, wincon.WM_SETFONT, self._bk._canvas._font, 1)
        if 'win-visible' in diffkeys:
            user32.ShowWindow(self.handle, new['win-visible'])
            user32.ShowWindow(self.__sys_control.handle, new['win-visible'])
        if diffkeys:
            winapi.RedrawWindow(self.handle)

    def minimize(self):
        for c in winapi.IterDescendantWindows(self.handle):
            self.__appwindows[c].__css_usename.update(cssname='normal')
        super().minimize()

    def __on_message__(self, h, m, w, l):
        if m == wincon.WM_CREATE:
            self._sethandle_(h)
            self._bk = BackgroundBuffer()
            self.__css_usename.update(cssname='normal')
        if m in [0x0133, 0x0134, 0x0135, 0x0138] and (control := self.__appwindows.get(l, None)):
            gdi32.SetTextColor(w, control.__css_calculated['bk-text-color'])
            gdi32.SetBkColor(w, control.__css_calculated['bk-color'])
            gdi32.DeleteObject(control._ctl_hbkclr)
            control._ctl_hbkclr = gdi32.CreateSolidBrush(control.__css_calculated['bk-color'])
            return control._ctl_hbkclr
        if m == wincon.WM_MOUSEHOVER:
            self.__css_usename.update(cssname='hover')
        if m == wincon.WM_MOUSELEAVE:
            self.__css_usename.update(cssname='normal')
        if m == wincon.WM_LBUTTONDOWN:
            user32.SetFocus(self.handle)
            self.capturemouse()
            self.__css_usename.update(cssname='active')
        if m == wincon.WM_LBUTTONUP:
            self.releasecapture()
            self.__css_usename.update(cssname='hover')
        if m == wincon.WM_NCCALCSIZE:
            new_rect, old_rect, old_client = ctypes.cast(l, ctypes.POINTER(wintype.NCCALCSIZE_PARAMS)).contents.rgrc
            dw, dh = old_rect.size[0] - old_client.size[0], old_rect.size[1] - old_client.size[1]
            if self.isminimized:
                self.__rect_dsize = dw, dh
            elif self.__rect_dsize:
                dw, dh = self.__rect_dsize
                self.__rect_dsize = 0
            new_clientsize = new_rect.size[0] - dw, new_rect.size[1] - dh
            self._bk.resize(new_clientsize)
            self._bk.redraw(self.__css_calculated, False)
        if m == WM_APP_REDRAW:
            self._bk.redraw(self.__css_calculated, h)
        if m == wincon.WM_PAINT and not self.classname.endswith('.wrapper'):
            self._bk.repaint(h)

        if m == wincon.WM_MOUSEMOVE and not self.__trackingmouse:
            winapi.TrackMouseEvent(h)
            self.__trackingmouse = True
        if m == wincon.WM_MOUSELEAVE:
            self.__trackingmouse = False

        if m == wincon.WM_COMMAND and (control := self.__appwindows.get(l, None)):
            for callback in control.__listener.get(-winapi.ParseLong(w)[1], []):
                callback(*(h, m, w, l)[:len(inspect.signature(callback).parameters)])
        for callback in self.__listener.get(m, []):
            callback(*(h, m, w, l)[:len(inspect.signature(callback).parameters)])

        if m == wincon.WM_SETCURSOR and w == h and winapi.ParseLong(l)[0] == wincon.HTCLIENT:
            cursor = self.__css_calculated['win-cursor']
            hcursor = cursor if isinstance(cursor, int) else getattr(wincon, f"IDC_{cursor.upper()}")
            winapi.SetCursor(hcursor)
        if m == wincon.WM_ERASEBKGND:
            return 1
        if m == wincon.WM_SETICON \
        and (hicon := user32.LoadImageW(0, self.__css_calculated['win-icon'], wincon.IMAGE_ICON, 0, 0, wincon.LR_LOADFROMFILE)):
            return user32.DestroyIcon(user32.DefWindowProcW(h, m, wincon.ICON_SMALL, hicon))
        if m == wincon.WM_NCACTIVATE \
        and winapi.ParseLong(w)[0] == {'active': 1, 'blur': 0}.get(self.__css_calculated['win-caption-theme'], -1) ^ 1:
            return 1
        if m == wincon.WM_CLOSE and self.__css_calculated['win-ask-close'] \
        and not winapi.MessageBox('确定要退出吗？', '提示', h, True, wincon.MB_YESNO) == wincon.IDYES:
            return 0

        if m == wincon.WM_NCDESTROY:
            self._bk._canvas.__del__()
            self.__listener.clear()
            self.__css_normal.unref()
            self.__css_hover.unref()
            self.__css_active.unref()
            self.__css_calculated.unref()
            self.__css_usename.unref()


    __appthread = 0
    __appwindows: dict[int, Self] = {}

    @classmethod
    def __wndproc(cls, hwnd, message, wparam, lparam):
        ret = None
        # if message == WM_PARENTNOTIFY and winapi.IsWindowClassInSystem(winapi.GetWindowClassName(lparam)):
        #     print(hwnd, message, wparam, lparam)
        #     message, hwnd, wparam, lparam = wparam, lparam, 0, 0
        if message == wincon.WM_CREATE:
            lpApp = ctypes.cast(lparam, ctypes.POINTER(wintype.CREATESTRUCTW)).contents.lpCreateParams
            cls.__appwindows[hwnd] = ctypes.cast(lpApp, ctypes.py_object).value
        if (app := cls.__appwindows.get(hwnd, None)) is not None:
            ret = app.__on_message__(hwnd, message, wparam, lparam)
        if message == wincon.WM_NCDESTROY:
            cls.__appwindows.pop(hwnd, None)
            cls.__checkwindow()
        return ret

    @classmethod
    def __checkthread(cls):
        if not cls.__appthread:
            cls.__appthread = winapi.CreateMsgloopThread()

    @classmethod
    def __checkwindow(cls):
        if not cls.__appwindows and cls.__appthread:
            cls.__appthread = winapi.DestroyMsgloopThread(cls.__appthread)


    @staticmethod
    def __parse_msg(msg: int | str):
        if isinstance(msg, str):
            _, sign, msg = msg.rpartition('-')
            msg = msg.upper() if msg.count('_') else f'WM_{msg}'.upper()
            msg = (-1) ** sign.count('-') * getattr(wincon, msg)
        return msg

    def addmsglistener(self, msg: int | str, callback: Callable[[int, int, int, int], Any]) -> Self:
        """
        - 回调函数按添加顺序执行
        - msg 为字符串时消息名称不区分大小写，WM_前缀可以省略： WM_LBUTTONUP == 0x0202 == 'lbuttonup' == 'WM_LBUTTONUP'
        - 如需处理win32预设控件的消息，整数参数请使用负数，字符串参数也请使用'-'前缀： -BM_CLICK == '-BM_CLICK'; -WM_CUT == '-cut'
        """
        msg = self.__parse_msg(msg)
        if msg not in self.__listener:
            self.__listener[msg] = {}
        self.__listener[msg][callback] = None
        return self

    @overload
    def removemsglistener(self, msg: int | str) -> Self:
        """remove all listener on msg"""
    @overload
    def removemsglistener(self, msg: int | str, callback: Callable[[int, int, int, int], Any]) -> Self:
        """remove specified listener"""
    def removemsglistener(self, msg: int | str, callback: Callable[[int, int, int, int], Any] = None) -> Self:
        msg = self.__parse_msg(msg)
        self.__listener.get(msg, {}).pop(callback, None)
        if not callback or not self.__listener.get(msg):
            self.__listener.pop(msg, None)
        return self


    @apptask
    def capturemouse(self):
        winapi.SetCapture(self.handle)

    @apptask
    def releasecapture(self):
        winapi.ReleaseCapture()
