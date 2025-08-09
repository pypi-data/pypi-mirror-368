from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import numpy as np
    from ._typing import _AppCSS

import ctypes
from aclib.winlib import wintype, wincon
from aclib.winlib.wincon import *
from aclib.winlib.__API__._windll import user32, gdi32


class BackgroundBuffer:

    def __init__(self):
        self._canvas = Canvas()

    def resize(self, size: tuple[int,int]):
        self._canvas.resize(size)

    def redraw(self, c: _AppCSS, refont: bool):
        self._canvas.draw_rect(c['bk-color'])
        if not isinstance(im := c['bk-image'], str):
            srcpos = c['bk-image-crop-start']
            destx, desty = c['bk-image-pos']
            destsize = c['bk-image-crop-size']
            destw, desth = im.shape[:2][::-1] if destsize == 'auto' else destsize
            imcanvas = Canvas(im.shape[:2][::-1])
            imcanvas.draw_image(im)
            imcanvas.copy_tocanvas(self._canvas, (destx, desty, destx+destw, desty+desth), srcpos)
        if refont:
            fw = getattr(wincon, f'FW_{c["bk-font-weight"].upper()}')
            self._canvas.refont(c['bk-font'], c['bk-font-size'], fw, c['bk-font-italic'], c['bk-font-underline'], c['bk-font-strike'])
        if text := c['bk-text']:
            color = c['bk-text-color']
            _dx, _dy = c['bk-text-offset']
            _overflow = c['bk-text-overflow']
            _xalign, _yalign = c['bk-text-align']
            area = (_dx, _dy, self._canvas._size[0] + _dx, self._canvas._size[1] + _dy)
            dtformat = DT_WORDBREAK if _overflow == 'wrap' else DT_SINGLELINE
            if _overflow == 'ellipsis':
                dtformat |= DT_END_ELLIPSIS
            _xalign = {'L': DT_LEFT, 'R': DT_RIGHT, 'M': DT_CENTER}[_xalign]
            _yalign = {'T': DT_TOP, 'B': DT_BOTTOM, 'M': DT_VCENTER}[_yalign]
            dtformat |= _xalign | _yalign
            self._canvas.draw_text(text, color, area, dtformat)

    def repaint(self, hwnd: int):
        ps = wintype.PAINTSTRUCT()
        hdc = user32.BeginPaint(hwnd, ps.ref)
        self._canvas.copy_todc(hdc)
        user32.EndPaint(hwnd, ps.ref)
        user32.ReleaseDC(hwnd, hdc)


class Canvas:
    def __init__(self, size = (1, 1)):
        self._size = size
        self._mem = gdi32.CreateCompatibleDC(0)
        self._bmp = self._oldbmp = 0
        self._font = self._oldfont = 0
        self.resize(size)
        gdi32.SetBkMode(self._mem, TRANSPARENT)

    def __del__(self):
        self.refont(None)
        self.resize(None)
        gdi32.DeleteDC(self._mem)

    def resize(self, size: tuple[int,int]|None):
        gdi32.SelectObject(self._mem, self._oldbmp)
        gdi32.DeleteObject(self._bmp)
        self._size = (1,1)
        if size is not None:
            self._size = size
            self._bmp = gdi32.CreateBitmap(*size, 1, 32, 0)
            self._oldbmp = gdi32.SelectObject(self._mem, self._bmp)

    def refont(self, font: str|None, size=18, weight=400, italic=False, underline=False, strikeout=False):
        gdi32.SelectObject(self._mem, self._oldfont)
        gdi32.DeleteObject(self._font)
        if font is not None:
            self._font = gdi32.CreateFontW(size, 0,0,0, weight, italic, underline, strikeout, 0,0,0,0,0, font)
            self._oldfont = gdi32.SelectObject(self._mem, self._font)

    def draw_rect(self, color: int, area: tuple[int,int,int,int] = ...):
        area  = (0, 0, *self._size) if area is ... else area
        hb = gdi32.CreateSolidBrush(color)
        user32.FillRect(self._mem, wintype.RECT(*area).ref, hb)
        gdi32.DeleteObject(hb)

    def draw_image(self, im: np.ndarray):
        bmi = wintype.BITMAPINFO()
        bmi.bmiHeader.biSize = bmi.bmiHeader.sizeof()
        bmi.bmiHeader.biWidth = im.shape[1]
        bmi.bmiHeader.biHeight = -im.shape[0]
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = BI_RGB
        gdi32.SetDIBits(0, self._bmp, 0, im.shape[0], im.ctypes.data_as(wintype.PBYTE), bmi.ref, DIB_RGB_COLORS)

    def draw_text(self, text: str, color = 0x000000, area: tuple[int,int,int,int] = ..., format = 0):
        rect = wintype.RECT(*area if area is not ... else (0, 0, *self._size))
        gdi32.SetTextColor(self._mem, color)
        user32.DrawTextW(self._mem, text, -1, rect.ref, format)

    def copy_todc(self, tohdc: int, toarea: tuple[int,int,int,int] = ..., copystart: tuple[int,int] = (0,0)):
        area = (0, 0, *self._size) if toarea is ... else toarea
        gdi32.BitBlt(tohdc, *area[:2], *self._size, self._mem, *copystart, SRCCOPY)

    def copy_tocanvas(self, canvas: Canvas, toarea: tuple[int,int,int,int] = ..., copystart: tuple[int,int] = (0,0)):
        self.copy_todc(canvas._mem, toarea, copystart)

    def copy_towindow(self, hwnd: int, toarea: tuple[int,int,int,int] = ..., copystart: tuple[int,int] = (0,0)):
        hdc = user32.GetDC(hwnd)
        self.copy_todc(hdc, toarea, copystart)
        user32.ReleaseDC(hwnd, hdc)

    def to_bytes(self) -> bytearray:
        total_bytes = self._size[0] * self._size[1] * 4
        buffer = bytearray(total_bytes)
        byte_array = ctypes.c_ubyte * total_bytes
        gdi32.GetBitmapBits(self._bmp, total_bytes, byte_array.from_buffer(buffer))
        return buffer
