
from kbd_engine.routing_models import RoutingResult, Via


class ViaInserter:
    """Engine that automatically inserts vias at layer transition points in a RoutingResult."""

    def __init__(
        self,
        drill: float = 0.3,
        diameter: float = 0.6,
        merge_tolerance: float = 0.1,
    ) -> None:
        """Initialize the via inserter.

        Args:
            drill: Default drill diameter of inserted vias in mm.
            diameter: Default outer diameter of inserted vias in mm.
            merge_tolerance: Tolerance in mm within which nearby vias are merged.
        """
        self.drill = drill
        self.diameter = diameter
        self.merge_tolerance = merge_tolerance

    def insert_vias(self, result: RoutingResult) -> RoutingResult:
        """Analyze trace segments for layer transition coordinates, insert vias,

        and merge transition points that are within merge_tolerance.
        """
        # Map each coordinate to the set of layers present at that coordinate
        coord_layers: dict[tuple[float, float], set[str]] = {}

        for trace in result.traces:
            start = (round(trace.start[0], 6), round(trace.start[1], 6))
            end = (round(trace.end[0], 6), round(trace.end[1], 6))

            for pt in (start, end):
                if pt not in coord_layers:
                    coord_layers[pt] = set()
                coord_layers[pt].add(trace.layer)

        # Collect raw transition points (where 2 or more layers meet)
        transition_points = [
            pt for pt, layers in coord_layers.items() if len(layers) >= 2
        ]

        # Merge transition points that are close to each other
        merged_points = self._merge_points(transition_points, self.merge_tolerance)

        # Existing vias in the result
        vias = list(result.vias)
        existing_via_positions = {
            (round(v.position[0], 6), round(v.position[1], 6)) for v in vias
        }

        # Add new vias
        for pt in merged_points:
            # Check if there is already a via close to this transition point
            already_has_via = False
            for v_pos in existing_via_positions:
                dist = ((pt[0] - v_pos[0]) ** 2 + (pt[1] - v_pos[1]) ** 2) ** 0.5
                if dist < self.merge_tolerance:
                    already_has_via = True
                    break

            if not already_has_via:
                vias.append(
                    Via(
                        position=pt,
                        drill=self.drill,
                        diameter=self.diameter,
                        layers=("F.Cu", "B.Cu"),
                    )
                )
                existing_via_positions.add(pt)

        return RoutingResult(
            traces=result.traces,
            vias=vias,
            unrouted_nets=result.unrouted_nets,
            success=result.success,
            diagnostics=result.diagnostics,
        )

    def _merge_points(
        self, points: list[tuple[float, float]], tolerance: float
    ) -> list[tuple[float, float]]:
        merged = []
        used = set()
        for i, pt1 in enumerate(points):
            if i in used:
                continue
            cluster = [pt1]
            used.add(i)
            for j in range(i + 1, len(points)):
                if j in used:
                    continue
                pt2 = points[j]
                dist = ((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** 0.5
                if dist < tolerance:
                    cluster.append(pt2)
                    used.add(j)
            # Compute centroid of cluster
            cx = sum(p[0] for p in cluster) / len(cluster)
            cy = sum(p[1] for p in cluster) / len(cluster)
            merged.append((round(cx, 6), round(cy, 6)))
        return merged
