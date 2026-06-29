from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Key:
    x: float
    y: float
    width: float = 1.0
    height: float = 1.0
    rotation: float = 0.0
    matrix_row: int | None = None
    matrix_col: int | None = None

    @property
    def logical_key_id(self) -> str:
        if self.matrix_row is not None and self.matrix_col is not None:
            return f"SW_{self.matrix_row}_{self.matrix_col}"
        return f"SW_{self.x}_{self.y}"


@dataclass(frozen=True)
class KeyMatrix:
    keys: list[Key] = field(default_factory=list)

    @property
    def rows(self) -> int:
        rows_list = [k.matrix_row for k in self.keys if k.matrix_row is not None]
        return max(rows_list) + 1 if rows_list else 0

    @property
    def cols(self) -> int:
        cols_list = [k.matrix_col for k in self.keys if k.matrix_col is not None]
        return max(cols_list) + 1 if cols_list else 0

    def get_key_at(self, row: int, col: int) -> Key | None:
        for k in self.keys:
            if k.matrix_row == row and k.matrix_col == col:
                return k
        return None


@dataclass(frozen=True)
class PlacementResult:
    placements: dict[str, dict[str, Any]]
    valid: bool
    errors: list[str] = field(default_factory=list)
