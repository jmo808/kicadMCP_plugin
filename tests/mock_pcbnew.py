# Mock implementation of pcbnew for unit testing without KiCad installed.


class VECTOR2I:
    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y

    def GetX(self) -> int:
        return self.x

    def GetY(self) -> int:
        return self.y


class EDA_ANGLE:
    def __init__(self, value: float = 0.0, unit: int = 0) -> None:
        self.value = value
        self.unit = unit

    def AsDegrees(self) -> float:
        return self.value


DEGREES_T = 1


class PAD:
    def __init__(self, name: str = "") -> None:
        self.name = name


class FOOTPRINT:
    def __init__(self, board: "BOARD" = None) -> None:
        self.board = board
        self.position = VECTOR2I(0, 0)
        self.reference = ""
        self.orientation = EDA_ANGLE(0.0)
        self.pads = []

    def SetPosition(self, pos: VECTOR2I) -> None:
        self.position = pos

    def GetPosition(self) -> VECTOR2I:
        return self.position

    def SetReference(self, ref: str) -> None:
        self.reference = ref

    def GetReference(self) -> str:
        return self.reference

    def SetOrientation(self, angle: EDA_ANGLE) -> None:
        self.orientation = angle

    def GetOrientation(self) -> EDA_ANGLE:
        return self.orientation

    def GetPads(self) -> list[PAD]:
        return self.pads


class TRACK:
    def __init__(self, board: "BOARD" = None) -> None:
        self.board = board
        self.start = VECTOR2I(0, 0)
        self.end = VECTOR2I(0, 0)
        self.layer = 0
        self.width = 0

    def SetStart(self, pos: VECTOR2I) -> None:
        self.start = pos

    def SetEnd(self, pos: VECTOR2I) -> None:
        self.end = pos

    def SetLayer(self, layer: int) -> None:
        self.layer = layer

    def SetWidth(self, width: int) -> None:
        self.width = width


class BOARD_DESIGN_SETTINGS:
    def __init__(self) -> None:
        pass


class BOARD:
    def __init__(self) -> None:
        self.footprints = []
        self.tracks = []
        self.settings = BOARD_DESIGN_SETTINGS()

    def GetFootprints(self) -> list[FOOTPRINT]:
        return self.footprints

    def Add(self, item: FOOTPRINT | TRACK) -> None:
        if isinstance(item, FOOTPRINT):
            self.footprints.append(item)
        elif isinstance(item, TRACK):
            self.tracks.append(item)

    def GetDesignSettings(self) -> BOARD_DESIGN_SETTINGS:
        return self.settings

    def Save(self, filename: str) -> bool:
        return True


def GetBoard() -> BOARD:
    return BOARD()


def LoadBoard(filename: str) -> BOARD:
    return BOARD()


def FootprintLoad(library_path: str, footprint_name: str) -> FOOTPRINT:
    fp = FOOTPRINT()
    fp.reference = footprint_name
    return fp
