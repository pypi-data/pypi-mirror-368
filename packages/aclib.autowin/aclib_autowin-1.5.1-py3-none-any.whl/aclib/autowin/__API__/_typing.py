from __future__ import annotations
from typing import Sequence

__all__ = [
    '_Pos',
    '_Size',
    '_Area',
    '_Areas'
]

_Pos = _Size = tuple[int, int]
_Area = tuple[int, int, int, int]
_Areas = Sequence[_Area]
