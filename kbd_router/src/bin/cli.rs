use kbd_router::astar::route;
use kbd_router::{RouteResult, RoutingRequest};
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    if let Err(e) = io::stdin().read_to_string(&mut input) {
        let err_result = RouteResult {
            success: false,
            traces: vec![],
            vias: vec![],
            unrouted_nets: vec![],
            diagnostics: format!("Failed to read stdin: {}", e),
        };
        println!("{}", serde_json::to_string(&err_result).unwrap());
        std::process::exit(1);
    }

    let request: RoutingRequest = match serde_json::from_str(&input) {
        Ok(req) => req,
        Err(e) => {
            let err_result = RouteResult {
                success: false,
                traces: vec![],
                vias: vec![],
                unrouted_nets: vec![],
                diagnostics: format!("Failed to parse JSON: {}", e),
            };
            println!("{}", serde_json::to_string(&err_result).unwrap());
            std::process::exit(1);
        }
    };

    let result = route(&request);
    println!("{}", serde_json::to_string(&result).unwrap());
}
