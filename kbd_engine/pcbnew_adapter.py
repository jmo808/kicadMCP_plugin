from typing import Any

import pcbnew


class PcbnewAdapter:
    """Thin adapter layer over the KiCad pcbnew API to allow mockability."""

    def __init__(self, board: Any = None) -> None:
        if board is not None:
            self.board = board
        else:
            try:
                self.board = pcbnew.GetBoard()
                if self.board is None:
                    self.board = pcbnew.BOARD()
            except AttributeError:
                self.board = pcbnew.BOARD()

    def load(self, filepath: str) -> None:
        self.board = pcbnew.LoadBoard(filepath)

    def save(self, filepath: str) -> None:
        self.board.Save(filepath)

    def add_footprint(
        self,
        library_path: str,
        footprint_name: str,
        reference: str,
        x: float,
        y: float,
        rotation: float,
    ) -> Any:
        fp = pcbnew.FootprintLoad(library_path, footprint_name)
        if not fp:
            raise ValueError(f"Could not load footprint '{footprint_name}' from '{library_path}'")

        fp.SetReference(reference)

        # Convert position from mm to internal units (1 mm = 1,000,000 nanometers)
        iu_x = int(x * 1000000)
        iu_y = int(y * 1000000)
        fp.SetPosition(pcbnew.VECTOR2I(iu_x, iu_y))

        # Set orientation
        degrees_t = getattr(pcbnew, "DEGREES_T", 1)
        fp.SetOrientation(pcbnew.EDA_ANGLE(rotation, degrees_t))

        self.board.Add(fp)
        return fp

    def add_track(
        self,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        layer: str,
        width: float,
    ) -> Any:
        track = pcbnew.TRACK(self.board)

        iu_start_x = int(start_x * 1000000)
        iu_start_y = int(start_y * 1000000)
        iu_end_x = int(end_x * 1000000)
        iu_end_y = int(end_y * 1000000)

        track.SetStart(pcbnew.VECTOR2I(iu_start_x, iu_start_y))
        track.SetEnd(pcbnew.VECTOR2I(iu_end_x, iu_end_y))

        # Resolve layer ID from name if supported by board
        layer_id = 0
        if hasattr(self.board, "GetLayerID"):
            layer_id = self.board.GetLayerID(layer)
        track.SetLayer(layer_id)

        iu_width = int(width * 1000000)
        track.SetWidth(iu_width)

        self.board.Add(track)
        return track

    def get_footprints(self) -> list[dict[str, Any]]:
        results = []
        for fp in self.board.GetFootprints():
            pos = fp.GetPosition()
            rot = fp.GetOrientation()

            # Convert back to mm
            mm_x = pos.GetX() / 1000000.0
            mm_y = pos.GetY() / 1000000.0
            deg_rot = rot.AsDegrees()

            results.append(
                {
                    "reference": fp.GetReference(),
                    "x": mm_x,
                    "y": mm_y,
                    "rotation": deg_rot,
                }
            )
        return results

    def create_net_class(
        self,
        name: str,
        track_width: float,
        clearance: float,
        via_diameter: float,
        via_drill: float,
    ) -> None:
        """Create a new net class with specified parameters.

        All parameters are specified in mm.
        """
        netclass = pcbnew.NETCLASS(name)

        netclass.SetTrackWidth(int(track_width * 1000000))
        netclass.SetClearance(int(clearance * 1000000))
        netclass.SetViaDiameter(int(via_diameter * 1000000))
        netclass.SetViaDrill(int(via_drill * 1000000))

        self.board.GetNetClasses().Add(netclass)

    def set_net_class(self, net_name: str, class_name: str) -> None:
        """Assign a net to a net class.

        Args:
            net_name: Name of the net to assign.
            class_name: Name of the net class.
        """
        self.board.GetNetSettings().SetNetclass(net_name, class_name)

    def find_footprint_by_reference(self, ref: str) -> Any:
        """Find a footprint by its reference designator.

        Args:
            ref: Reference designator (e.g. SW_0_0)

        Returns:
            The footprint object, or None if not found.
        """
        if hasattr(self.board, "FindFootprintByReference"):
            return self.board.FindFootprintByReference(ref)
        return None

    def get_pad_position(self, footprint_ref: str, pad_name: str) -> tuple[float, float] | None:
        """Get the absolute coordinates of a pad on the board in mm.

        Args:
            footprint_ref: Reference designator of the footprint.
            pad_name: Name/number of the pad.

        Returns:
            A tuple of (x, y) coordinates in mm, or None if not found.
        """
        fp = self.find_footprint_by_reference(footprint_ref)
        if fp is None:
            return None

        pad = None
        if hasattr(fp, "FindPadByNumber"):
            pad = fp.FindPadByNumber(pad_name)
        elif hasattr(fp, "FindPad"):
            pad = fp.FindPad(pad_name)

        if pad is None:
            return None

        pos = pad.GetPosition()
        return (pos.GetX() / 1000000.0, pos.GetY() / 1000000.0)

    def add_via(
        self,
        x: float,
        y: float,
        drill: float,
        diameter: float,
    ) -> Any:
        """Add a via at specified coordinates with given drill and diameter.

        All parameters are specified in mm.
        """
        via = pcbnew.VIA(self.board)
        iu_x = int(x * 1000000)
        iu_y = int(y * 1000000)
        via.SetStart(pcbnew.VECTOR2I(iu_x, iu_y))
        via.SetEnd(pcbnew.VECTOR2I(iu_x, iu_y))
        via.SetDrill(int(drill * 1000000))
        via.SetWidth(int(diameter * 1000000))
        self.board.Add(via)
        return via

