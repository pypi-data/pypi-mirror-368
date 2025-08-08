__all__ = ["WindowIcon"]

from dataclasses import dataclass

from emath import IVector2
from emath import U8Vector4Array


@dataclass
class WindowIcon:
    pixels: U8Vector4Array
    size: IVector2
