from dataclasses import dataclass

from tidipy import composer, Resolver, auto_compose


@dataclass
class Point:
    x: int
    y: int


@composer
def point() -> Point:
    return Point(x=1, y=2)


@dataclass
class PointWrapper:
    point: Point


@composer
def point_wrapper() -> PointWrapper:
    return PointWrapper(Point(x=3, y=4))


class PointWrapperWrapper:
    def __init__(self, point_wrapper: PointWrapper):
        self.point_wrapper = point_wrapper


class EmptyInit:
    def hey(self) -> str:
        return 'hey'