import numpy
from typing import TypedDict, Literal

__all__ = [
    '_AppCSS',
]

_AppRunningCss = TypedDict('_AppRunningCss', {
    'cssname': Literal['normal', 'hover', 'active']
})

_AppCSS = TypedDict('_AppCSS', {
    'win-title': str,
    'win-pos': tuple[int, int] | Literal['unset'],
    'win-size': tuple[int, int] | Literal['unset'],
    'win-icon': str,
    'win-visible': bool,
    'win-opacity': float,
    'win-caption-theme': Literal['active', 'blur', 'toggle'],
    'win-ask-close': bool,
    'win-cursor': Literal['arrow', 'ibeam', 'wait', 'cross', 'uparrow', 'sizenwse', 'sizenesw', 'sizewe', 'sizens', 'sizeall', 'no', 'hand', 'appstarting', 'help'],

    'bk-color': int,

    'bk-image': numpy.ndarray | Literal['none'],
    'bk-image-pos': tuple[int, int],
    'bk-image-crop-start': tuple[int, int],
    'bk-image-crop-size': tuple[int, int] | Literal['auto'],

    'bk-text': str,
    'bk-text-color': int,
    'bk-text-align': Literal['LT', 'LM', 'LB', 'RT', 'RM', 'RB', 'MT', 'MM', 'MB'],
    'bk-text-offset': tuple[int, int],
    'bk-text-overflow': Literal['clip', 'ellipsis', 'wrap'],

    'bk-font': str,
    'bk-font-size': int,
    'bk-font-weight': Literal['normal', 'thin', 'heavy'],
    'bk-font-italic': bool,
    'bk-font-strike': bool,
    'bk-font-underline': bool,
}, total=False)
