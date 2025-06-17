from typing import Annotated

Coord = tuple[int, int] | Annotated[list[int], 2] | tuple[int, int, int, int] | Annotated[list[int], 4]
Ratios = tuple[float | int, float | int] | Annotated[list[float | int], 2] | tuple[float | int, float | int, float | int, float | int] | Annotated[list[float | int], 4]
PixelColor = tuple[int, int, int] | Annotated[list[int], 3]
