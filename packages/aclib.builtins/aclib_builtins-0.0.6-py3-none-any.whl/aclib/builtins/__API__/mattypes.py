from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

from .pytypes import Object


class Rect(Object):

    @classmethod
    def frompossize(cls, pos: tuple[int, int] = (0, 0), size: tuple[int, int] = (0, 0)) -> Self:
        return cls(*pos, pos[0] + size[0], pos[1] + size[1])

    def copy(self) -> Self:
        return self.__class__(*self.border)

    def __init__(self, left=0, top=0, right=0, bottom=0):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def __repr__(self, *key: str) -> str:
        if not self:
            return f'<{self.__class__.__name__} empty>'
        return super().__repr__( * key or ('start', 'center', 'end'))

    def __bool__(self) -> bool:
        return any(it for it in self.__dict__.values())


    @property
    def border(self) -> tuple[int, int, int, int]:
        return self.left, self.top, self.right, self.bottom


    def ratiopos(self, ratio: float | tuple[float, float]) -> tuple[int, int]:
        ratio = ratio if hasattr(ratio, '__getitem__') else (ratio, ratio)
        return self.left + int(self.width * ratio[0]), self.top + int(self.height * ratio[1])

    @property
    def start(self) -> tuple[int, int]:
        return self.left, self.top

    @property
    def end(self) -> tuple[int, int]:
        return self.right, self.bottom

    @property
    def center(self) -> tuple[int, int]:
        return self.ratiopos(0.5)


    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top

    @property
    def size(self) -> tuple[int, int]:
        return self.width, self.height


    def offset(self, dx: int, dy: int) -> Self:
        self.left += dx
        self.right += dx
        self.top += dy
        self.bottom += dy
        return self

    def resize(self, w: int, h: int) -> Self:
        self.right = self.left + w
        self.bottom = self.top + h
        return self

    def scale(self, ratio: float | tuple[float, float], center: tuple[int, int] = (0, 0)) -> Self:
        sx, sy = ratio if hasattr(ratio, '__getitem__') else (ratio, ratio)
        cx, cy = center
        self.left   = int(cx + (self.left   - cx) * sx)
        self.right  = int(cx + (self.right  - cx) * sx)
        self.top    = int(cy + (self.top    - cy) * sy)
        self.bottom = int(cy + (self.bottom - cy) * sy)
        return self


class MatTarget(Rect):

    @classmethod
    def frompossize(cls, pos: tuple[int, int] = (0, 0), size: tuple[int, int] = (0, 0), name='', similarity=0.0) -> Self:
        return cls(*pos, pos[0] + size[0], pos[1] + size[1], name, similarity)

    def copy(self) -> Self:
        return self.__class__(*self.border, self.name, self.similarity)

    def __init__(self, left=0, top=0, right=0, bottom=0, name='', similarity=0.0):
        super().__init__(left, top, right, bottom)
        self.name = name
        self.similarity = similarity

    def __repr__(self) -> str:
        return super().__repr__('name', 'start', 'center', 'end', 'similarity')
