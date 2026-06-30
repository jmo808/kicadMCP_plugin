use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Point {
    pub x: i32,
    pub y: i32,
    pub layer: u8, // 0 = F.Cu, 1 = B.Cu
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Obstacle {
    pub x_min: i32,
    pub y_min: i32,
    pub x_max: i32,
    pub y_max: i32,
    pub layer: Option<u8>, // None means all layers
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Net {
    pub name: String,
    pub pins: Vec<Point>,
    pub track_width: f64, // in mm
    pub clearance: f64,   // in mm
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RoutingRequest {
    pub width: f64,
    pub height: f64,
    pub grid_pitch: f64,
    pub nets: Vec<Net>,
    pub obstacles: Vec<Obstacle>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct TraceSegment {
    pub start: (f64, f64),
    pub end: (f64, f64),
    pub layer: String,
    pub width: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Via {
    pub position: (f64, f64),
    pub drill: f64,
    pub diameter: f64,
    pub layers: (String, String),
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct RouteResult {
    pub success: bool,
    pub traces: Vec<TraceSegment>,
    pub vias: Vec<Via>,
    pub unrouted_nets: Vec<String>,
    pub diagnostics: String,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_serialization_deserialization() {
        let request = RoutingRequest {
            width: 100.0,
            height: 100.0,
            grid_pitch: 0.5,
            nets: vec![Net {
                name: "ROW_0".to_string(),
                pins: vec![
                    Point { x: 10, y: 10, layer: 0 },
                    Point { x: 20, y: 10, layer: 0 },
                ],
                track_width: 0.2,
                clearance: 0.2,
            }],
            obstacles: vec![Obstacle {
                x_min: 15,
                y_min: 5,
                x_max: 16,
                y_max: 15,
                layer: Some(0),
            }],
        };

        let serialized = serde_json::to_string(&request).unwrap();
        let deserialized: RoutingRequest = serde_json::from_str(&serialized).unwrap();

        assert_eq!(deserialized.width, 100.0);
        assert_eq!(deserialized.nets.len(), 1);
        assert_eq!(deserialized.nets[0].name, "ROW_0");
        assert_eq!(deserialized.nets[0].pins.len(), 2);
        assert_eq!(deserialized.obstacles.len(), 1);
    }
}
