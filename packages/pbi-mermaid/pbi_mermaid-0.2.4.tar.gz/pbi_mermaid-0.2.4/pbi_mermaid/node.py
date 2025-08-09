from dataclasses import dataclass
from enum import Enum


@dataclass
class Shape:
    start: str
    end: str


class NodeShape(Enum):
    normal = Shape("[", "]")
    round_edge = Shape("(", ")")
    stadium_shape = Shape("([", "])")
    subroutine_shape = Shape("[[", "]]")
    cylindrical = Shape("[(", ")]")
    circle = Shape("((", "))")
    label_shape = Shape(">", "]")
    rhombus = Shape("{", "}")
    hexagon = Shape("{{", "}}")
    parallelogram = Shape("[/", "/]")
    parallelogram_alt = Shape("[\\", "\\]")
    trapezoid = Shape("[/", "\\]")
    trapezoid_alt = Shape("[\\", "/]")
    double_circle = Shape("(((", ")))")


class Node:
    id: str
    shape: Shape
    content: str
    style: str

    def __init__(self, id: str, shape: NodeShape = NodeShape.normal, content: str = "", style: str = "") -> None:
        self.id = id
        self.shape = shape.value
        self.content = content
        self.style = style

    def to_markdown(self) -> str:
        ret = f'{self.id}{self.shape.start}"{self.content or self.id}"{self.shape.end}'
        if self.style:
            ret += f"\nstyle {self.id} {self.style}"
        return ret

    def __repr__(self) -> str:
        return f"Node({self.id})"
