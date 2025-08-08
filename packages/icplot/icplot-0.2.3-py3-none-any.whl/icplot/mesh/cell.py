from dataclasses import dataclass


@dataclass(frozen=True)
class Cell:
    """
    A mesh cell
    """

    vertices: tuple[int, ...]
    type: str = ""

    def get_edges(self) -> tuple:
        raise NotImplementedError()


@dataclass(frozen=True)
class HexCell(Cell):
    """
    A hex mesh element - used in openfoam meshing
    """

    cell_counts: tuple[int, ...] = (1, 1, 1)
    grading: str = "simpleGrading"
    grading_ratios: tuple[int, ...] = (1, 1, 1)
    type = "hex"

    def get_top_edges(self) -> tuple:
        return (
            (self.vertices[0], self.vertices[1]),
            (self.vertices[1], self.vertices[2]),
            (self.vertices[2], self.vertices[3]),
            (self.vertices[3], self.vertices[0]),
        )

    def get_bottom_edges(self) -> tuple:
        return (
            (self.vertices[4], self.vertices[5]),
            (self.vertices[5], self.vertices[6]),
            (self.vertices[6], self.vertices[7]),
            (self.vertices[7], self.vertices[4]),
        )

    def get_side_edges(self) -> tuple:
        return (
            (self.vertices[0], self.vertices[4]),
            (self.vertices[1], self.vertices[5]),
            (self.vertices[2], self.vertices[6]),
            (self.vertices[3], self.vertices[7]),
        )

    def get_edges(self) -> tuple:
        return self.get_bottom_edges() + self.get_top_edges() + self.get_side_edges()
