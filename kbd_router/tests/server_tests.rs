use axum::{body::Body, http::{self, Request, StatusCode}, routing::post, Json, Router};
use kbd_router::astar::route;
use kbd_router::{RouteResult, RoutingRequest};
use tower::ServiceExt; // for `oneshot`

async fn handle_route(Json(req): Json<RoutingRequest>) -> Json<RouteResult> {
    Json(route(&req))
}

fn app() -> Router {
    Router::new().route("/route", post(handle_route))
}

#[tokio::test]
async fn test_route_endpoint() {
    let app = app();

    let request_json = r#"{
        "width": 10.0,
        "height": 10.0,
        "grid_pitch": 1.0,
        "nets": [
            {
                "name": "NET_1",
                "pins": [
                    {"x": 1, "y": 1, "layer": 0},
                    {"x": 5, "y": 1, "layer": 0}
                ],
                "track_width": 0.2,
                "clearance": 0.2
            }
        ],
        "obstacles": []
    }"#;

    let response = app
        .oneshot(
            Request::builder()
                .method(http::Method::POST)
                .uri("/route")
                .header(http::header::CONTENT_TYPE, "application/json")
                .body(Body::from(request_json))
                .unwrap(),
        )
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::OK);

    let body = axum::body::to_bytes(response.into_body(), usize::MAX).await.unwrap();
    let result: RouteResult = serde_json::from_slice(&body).unwrap();
    assert!(result.success);
}
