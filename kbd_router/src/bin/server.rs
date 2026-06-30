use axum::{routing::post, Json, Router};
use kbd_router::astar::route;
use kbd_router::{RouteResult, RoutingRequest};
use std::net::SocketAddr;

async fn handle_route(Json(req): Json<RoutingRequest>) -> Json<RouteResult> {
    let res = route(&req);
    Json(res)
}

#[tokio::main]
async fn main() {
    let app = Router::new().route("/route", post(handle_route));
    let addr = SocketAddr::from(([127, 0, 0, 1], 8080));
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
