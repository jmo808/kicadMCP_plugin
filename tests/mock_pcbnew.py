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


class NETCLASS:
    def __init__(self, name: str) -> None:
        self.name = name
        self.clearance = 0
        self.track_width = 0
        self.via_dia = 0
        self.via_drill = 0

    def GetName(self) -> str:
        return self.name

    def SetClearance(self, val: int) -> None:
        self.clearance = val

    def GetClearance(self) -> int:
        return self.clearance

    def SetTrackWidth(self, val: int) -> None:
        self.track_width = val

    def GetTrackWidth(self) -> int:
        return self.track_width

    def SetViaDiameter(self, val: int) -> None:
        self.via_dia = val

    def GetViaDiameter(self) -> int:
        return self.via_dia

    def SetViaDrill(self, val: int) -> None:
        self.via_drill = val

    def GetViaDrill(self) -> int:
        return self.via_drill


class NETCLASSES:
    def __init__(self) -> None:
        self.classes = {}

    def Add(self, netclass: NETCLASS) -> None:
        self.classes[netclass.GetName()] = netclass

    def Find(self, name: str) -> NETCLASS | None:
        return self.classes.get(name)


class NET_SETTINGS:
    def __init__(self) -> None:
        self.assignments = {}

    def SetNetclass(self, net_name: str, class_name: str) -> None:
        self.assignments[net_name] = class_name

    def GetNetClassByName(self, net_name: str) -> str:
        return self.assignments.get(net_name, "Default")


class BOARD:
    def __init__(self) -> None:
        self.footprints = []
        self.tracks = []
        self.settings = BOARD_DESIGN_SETTINGS()
        self.netclasses = NETCLASSES()
        self.net_settings = NET_SETTINGS()

    def GetFootprints(self) -> list[FOOTPRINT]:
        return self.footprints

    def Add(self, item: FOOTPRINT | TRACK) -> None:
        if isinstance(item, FOOTPRINT):
            self.footprints.append(item)
        elif isinstance(item, TRACK):
            self.tracks.append(item)

    def GetDesignSettings(self) -> BOARD_DESIGN_SETTINGS:
        return self.settings

    def GetNetClasses(self) -> NETCLASSES:
        return self.netclasses

    def GetNetSettings(self) -> NET_SETTINGS:
        return self.net_settings

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
