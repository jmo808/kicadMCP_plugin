use crate::{Point, RouteResult, RoutingRequest, TraceSegment, Via};
use std::collections::{BinaryHeap, HashMap, HashSet};

#[derive(Debug, PartialEq)]
struct AStarNode {
    point: Point,
    g_cost: f64,
    f_cost: f64,
}

impl Eq for AStarNode {}

impl PartialOrd for AStarNode {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for AStarNode {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        // Reverse ordering for min-heap
        other.f_cost.partial_cmp(&self.f_cost).unwrap_or(std::cmp::Ordering::Equal)
    }
}

fn heuristic(a: Point, b: Point) -> f64 {
    let dx = (a.x - b.x).abs() as f64;
    let dy = (a.y - b.y).abs() as f64;
    let dz = if a.layer != b.layer { 15.0 } else { 0.0 };
    dx + dy + dz
}

fn to_grid_coord(coord: f64, pitch: f64) -> i32 {
    (coord / pitch).round() as i32
}

fn to_phys(p: Point, pitch: f64) -> (f64, f64) {
    (p.x as f64 * pitch, p.y as f64 * pitch)
}

fn get_layer_name(layer: u8) -> String {
    if layer == 0 {
        "F.Cu".to_string()
    } else {
        "B.Cu".to_string()
    }
}

fn find_path(
    start: Point,
    goal: Point,
    x_max: i32,
    y_max: i32,
    blocked: &HashSet<Point>,
) -> Option<Vec<Point>> {
    if start == goal {
        return Some(vec![start]);
    }

    let mut open_set = BinaryHeap::new();
    let mut g_score = HashMap::new();
    let mut came_from = HashMap::new();
    let mut closed_set = HashSet::new();

    g_score.insert(start, 0.0);
    open_set.push(AStarNode {
        point: start,
        g_cost: 0.0,
        f_cost: heuristic(start, goal),
    });

    while let Some(current_node) = open_set.pop() {
        let current = current_node.point;

        if current == goal {
            let mut path = vec![current];
            let mut curr = current;
            while let Some(&prev) = came_from.get(&curr) {
                path.push(prev);
                curr = prev;
            }
            path.reverse();
            return Some(path);
        }

        if !closed_set.insert(current) {
            continue;
        }

        // Neighbors
        let mut neighbors = Vec::new();
        let moves = [(1, 0), (-1, 0), (0, 1), (0, -1)];
        for &(dx, dy) in &moves {
            let nx = current.x + dx;
            let ny = current.y + dy;
            if nx >= 0 && nx <= x_max && ny >= 0 && ny <= y_max {
                neighbors.push((Point { x: nx, y: ny, layer: current.layer }, 1.0));
            }
        }
        // Via layer transition
        let other_layer = 1 - current.layer;
        neighbors.push((Point { x: current.x, y: current.y, layer: other_layer }, 15.0));

        for (nbr, step_cost) in neighbors {
            if closed_set.contains(&nbr) {
                continue;
            }

            if nbr != goal && blocked.contains(&nbr) {
                continue;
            }

            // Via check: both layers must be clear
            if nbr.x == current.x && nbr.y == current.y {
                let p0 = Point { x: nbr.x, y: nbr.y, layer: 0 };
                let p1 = Point { x: nbr.x, y: nbr.y, layer: 1 };
                if (p0 != start && p0 != goal && blocked.contains(&p0))
                    || (p1 != start && p1 != goal && blocked.contains(&p1))
                {
                    continue;
                }
            }

            let tentative_g = g_score.get(&current).unwrap_or(&f64::INFINITY) + step_cost;
            if tentative_g < *g_score.get(&nbr).unwrap_or(&f64::INFINITY) {
                g_score.insert(nbr, tentative_g);
                came_from.insert(nbr, current);
                open_set.push(AStarNode {
                    point: nbr,
                    g_cost: tentative_g,
                    f_cost: tentative_g + heuristic(nbr, goal),
                });
            }
        }
    }

    None
}

fn convert_path_to_traces(
    path: &[Point],
    pitch: f64,
    width: f64,
) -> (Vec<TraceSegment>, Vec<Via>) {
    let mut traces = Vec::new();
    let mut vias = Vec::new();

    if path.is_empty() {
        return (traces, vias);
    }

    let mut segment_start = path[0];
    for i in 1..path.len() {
        let prev = path[i - 1];
        let curr = path[i];

        if prev.layer != curr.layer {
            if segment_start != prev {
                traces.push(TraceSegment {
                    start: to_phys(segment_start, pitch),
                    end: to_phys(prev, pitch),
                    layer: get_layer_name(segment_start.layer),
                    width,
                });
            }
            vias.push(Via {
                position: to_phys(curr, pitch),
                drill: 0.3,
                diameter: 0.6,
                layers: ("F.Cu".to_string(), "B.Cu".to_string()),
            });
            segment_start = curr;
        } else if i > 1 {
            let prev_prev = path[i - 2];
            let dx1 = prev.x - prev_prev.x;
            let dy1 = prev.y - prev_prev.y;
            let dx2 = curr.x - prev.x;
            let dy2 = curr.y - prev.y;
            if prev_prev.layer != prev.layer || dx1 != dx2 || dy1 != dy2 {
                traces.push(TraceSegment {
                    start: to_phys(segment_start, pitch),
                    end: to_phys(prev, pitch),
                    layer: get_layer_name(segment_start.layer),
                    width,
                });
                segment_start = prev;
            }
        }
    }

    let last = *path.last().unwrap();
    if segment_start != last {
        traces.push(TraceSegment {
            start: to_phys(segment_start, pitch),
            end: to_phys(last, pitch),
            layer: get_layer_name(segment_start.layer),
            width,
        });
    }

    (traces, vias)
}

/// Route the nets using a 3D A* grid-based pathfinder.
pub fn route(request: &RoutingRequest) -> RouteResult {
    let x_max = to_grid_coord(request.width, request.grid_pitch);
    let y_max = to_grid_coord(request.height, request.grid_pitch);

    let mut blocked = HashSet::new();

    // Populate initial obstacles
    for obs in &request.obstacles {
        for x in obs.x_min..=obs.x_max {
            for y in obs.y_min..=obs.y_max {
                if let Some(l) = obs.layer {
                    blocked.insert(Point { x, y, layer: l });
                } else {
                    blocked.insert(Point { x, y, layer: 0 });
                    blocked.insert(Point { x, y, layer: 1 });
                }
            }
        }
    }

    let mut traces = Vec::new();
    let mut vias = Vec::new();
    let mut unrouted_nets = Vec::new();
    let mut success = true;

    for net in &request.nets {
        if net.pins.is_empty() {
            continue;
        }

        // Temporarily remove this net's pins from blocked set during its routing
        for pin in &net.pins {
            blocked.remove(pin);
        }

        let mut net_path = Vec::new();
        let mut net_success = true;

        for i in 1..net.pins.len() {
            let start = net.pins[i - 1];
            let goal = net.pins[i];

            if let Some(path) = find_path(start, goal, x_max, y_max, &blocked) {
                if i == 1 {
                    net_path.extend(path);
                } else {
                    // Avoid duplicating the connection pin
                    net_path.extend(path.into_iter().skip(1));
                }
            } else {
                net_success = false;
                break;
            }
        }

        if net_success {
            // Convert to physical trace segments and vias
            let (net_traces, net_vias) = convert_path_to_traces(&net_path, request.grid_pitch, net.track_width);
            traces.extend(net_traces);
            vias.extend(net_vias);

            // Add routed path to blocked set for subsequent nets
            for pt in &net_path {
                blocked.insert(*pt);
            }
        } else {
            success = false;
            unrouted_nets.push(net.name.clone());
        }

        // Re-add this net's pins to blocked set to prevent other nets from routing through them
        for pin in &net.pins {
            blocked.insert(*pin);
        }
    }

    let diagnostics = if success {
        "All nets routed successfully".to_string()
    } else {
        format!("Failed to route nets: {}", unrouted_nets.join(", "))
    };

    RouteResult {
        success,
        traces,
        vias,
        unrouted_nets,
        diagnostics,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{Net, Obstacle};

    #[test]
    fn test_route_single_net_empty_grid() {
        let request = RoutingRequest {
            width: 10.0,
            height: 10.0,
            grid_pitch: 1.0,
            nets: vec![Net {
                name: "NET_1".to_string(),
                pins: vec![
                    Point { x: 1, y: 1, layer: 0 },
                    Point { x: 5, y: 1, layer: 0 },
                ],
                track_width: 0.2,
                clearance: 0.2,
            }],
            obstacles: vec![],
        };

        let result = route(&request);
        assert!(result.success, "Failed: {}", result.diagnostics);
        assert_eq!(result.traces.len(), 1);
        assert_eq!(result.traces[0].start, (1.0, 1.0));
        assert_eq!(result.traces[0].end, (5.0, 1.0));
        assert_eq!(result.vias.len(), 0);
    }

    #[test]
    fn test_route_around_obstacle() {
        let request = RoutingRequest {
            width: 10.0,
            height: 10.0,
            grid_pitch: 1.0,
            nets: vec![Net {
                name: "NET_1".to_string(),
                pins: vec![
                    Point { x: 1, y: 2, layer: 0 },
                    Point { x: 5, y: 2, layer: 0 },
                ],
                track_width: 0.2,
                clearance: 0.2,
            }],
            // Rectangular obstacle blocking the direct route at x=3, y=1..3
            obstacles: vec![Obstacle {
                x_min: 3,
                y_min: 1,
                x_max: 3,
                y_max: 3,
                layer: Some(0),
            }],
        };

        let result = route(&request);
        assert!(result.success, "Failed: {}", result.diagnostics);
        // Check that none of the trace segments cross the obstacle (x=3, y=1..3, layer 0)
        for segment in &result.traces {
            if segment.layer == "F.Cu" {
                let x_min = segment.start.0.min(segment.end.0);
                let x_max = segment.start.0.max(segment.end.0);
                let y_min = segment.start.1.min(segment.end.1);
                let y_max = segment.start.1.max(segment.end.1);
                if x_min <= 3.0 && x_max >= 3.0 && y_min <= 3.0 && y_max >= 1.0 {
                    assert!(!(y_min == y_max && y_min >= 1.0 && y_min <= 3.0 && x_min != x_max));
                }
            }
        }
    }

    #[test]
    fn test_route_via_layer_transition() {
        let request = RoutingRequest {
            width: 10.0,
            height: 10.0,
            grid_pitch: 1.0,
            nets: vec![Net {
                name: "NET_1".to_string(),
                pins: vec![
                    Point { x: 1, y: 2, layer: 0 },
                    Point { x: 5, y: 2, layer: 1 },
                ],
                track_width: 0.2,
                clearance: 0.2,
            }],
            obstacles: vec![],
        };

        let result = route(&request);
        assert!(result.success, "Failed: {}", result.diagnostics);
        assert_eq!(result.vias.len(), 1);
        assert_eq!(result.vias[0].layers, ("F.Cu".to_string(), "B.Cu".to_string()));
    }

    #[test]
    fn test_route_failure_no_path() {
        let request = RoutingRequest {
            width: 10.0,
            height: 10.0,
            grid_pitch: 1.0,
            nets: vec![Net {
                name: "NET_1".to_string(),
                pins: vec![
                    Point { x: 1, y: 2, layer: 0 },
                    Point { x: 5, y: 2, layer: 0 },
                ],
                track_width: 0.2,
                clearance: 0.2,
            }],
            // Wall blocking all layers at x=3
            obstacles: vec![Obstacle {
                x_min: 3,
                y_min: 0,
                x_max: 3,
                y_max: 10,
                layer: None,
            }],
        };

        let result = route(&request);
        assert!(!result.success);
        assert_eq!(result.unrouted_nets, vec!["NET_1".to_string()]);
    }

    #[test]
    fn test_route_multi_net_ordering() {
        let request = RoutingRequest {
            width: 10.0,
            height: 10.0,
            grid_pitch: 1.0,
            nets: vec![
                Net {
                    name: "NET_1".to_string(),
                    pins: vec![
                        Point { x: 1, y: 2, layer: 0 },
                        Point { x: 5, y: 2, layer: 0 },
                    ],
                    track_width: 0.2,
                    clearance: 0.2,
                },
                Net {
                    name: "NET_2".to_string(),
                    pins: vec![
                        Point { x: 3, y: 1, layer: 0 },
                        Point { x: 3, y: 3, layer: 0 },
                    ],
                    track_width: 0.2,
                    clearance: 0.2,
                },
            ],
            obstacles: vec![],
        };

        let result = route(&request);
        assert!(result.success, "Failed: {}", result.diagnostics);
        // NET_1 should be straight: (1,2) -> (5,2)
        // NET_2 should either route around NET_1 on F.Cu or use B.Cu.
        // If it routes on F.Cu, it cannot cross (3,2).
        for segment in &result.traces {
            if segment.layer == "F.Cu" {
                // Assert no vertical trace of NET_2 goes straight through y=2 at x=3
                // Wait, if start and end are on F.Cu:
                let x_min = segment.start.0.min(segment.end.0);
                let x_max = segment.start.0.max(segment.end.0);
                let y_min = segment.start.1.min(segment.end.1);
                let y_max = segment.start.1.max(segment.end.1);
                if x_min == 3.0 && x_max == 3.0 && y_min <= 1.0 && y_max >= 3.0 {
                    panic!("NET_2 crossed NET_1 straight through on the same layer!");
                }
            }
        }
    }
}
