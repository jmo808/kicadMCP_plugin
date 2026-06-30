use crate::astar::route;
use crate::RoutingRequest;
use pyo3::prelude::*;

#[pyfunction]
fn route_board(request_json: &str) -> PyResult<String> {
    // 1. Deserialize the RoutingRequest
    let request: RoutingRequest = serde_json::from_str(request_json).map_err(|e| {
        pyo3::exceptions::PyValueError::new_err(format!("Invalid JSON request: {}", e))
    })?;

    // 2. Run the routing algorithm
    let result = route(&request);

    // 3. Serialize the RouteResult
    let result_json = serde_json::to_string(&result).map_err(|e| {
        pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to serialize result: {}", e))
    })?;

    Ok(result_json)
}

/// A Python module implemented in Rust.
#[pymodule]
fn kbd_router(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(route_board, m)?)?;
    Ok(())
}
