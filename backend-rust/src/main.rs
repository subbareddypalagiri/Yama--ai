mod routes;
mod services;
mod models;

use axum::{
    routing::post,
    Router,
};
use routes::chat::{chat_handler, AppState};
use services::gemini::GeminiClient;
use std::sync::Arc;
use tokio::sync::RwLock;
use std::collections::HashMap;
use models::chat::ChatMessage;
use tower_http::cors::{Any, CorsLayer};
use dotenv::dotenv;
use std::path::Path;

#[tokio::main]
async fn main() {
    // Try to load the .env file from local or backend folder
    dotenv::dotenv().ok();
    dotenv::from_filename("../backend/.env").ok();
    dotenv::from_filename("backend/.env").ok();
    dotenv::from_filename(".env").ok();
    
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_headers(Any)
        .allow_methods(Any);

    let state = Arc::new(AppState {
        gemini_client: GeminiClient::new(),
        history_cache: RwLock::new(HashMap::new()),
        legal_db: services::legal_db::LegalDatabase::new(),
    });

    let app = Router::new()
        .route("/api/v1/chat/", post(chat_handler))
        .route("/api/v1/lawyer/", post(chat_handler))
        .route("/api/v1/laws/search", axum::routing::get(routes::laws::search_laws_handler))
        .route("/api/v1/laws/state", axum::routing::get(routes::laws::search_state_laws_handler))
        .route("/api/v1/laws/supreme-court", axum::routing::get(routes::laws::search_supreme_court_handler))
        .route("/api/v1/laws/high-courts", axum::routing::get(routes::laws::search_high_courts_handler))
        .route("/api/v1/laws/stats", axum::routing::get(routes::laws::get_enterprise_stats_handler))
        .route("/api/v1/laws/acts", axum::routing::get(routes::laws::get_acts_handler))
        .route("/api/v1/laws/categories", axum::routing::get(routes::laws::get_categories_handler))
        .route("/api/v1/laws/sections/:act_name", axum::routing::get(routes::laws::get_sections_by_act_handler))
        .route("/api/v1/laws/:id", axum::routing::get(routes::laws::get_law_by_id_handler))
        // Cases (Case Diary & Client Case Manager)
        .route("/api/v1/cases", axum::routing::get(routes::cases::list_cases_handler).post(routes::cases::create_case_handler))
        .route("/api/v1/cases/:case_uid", axum::routing::get(routes::cases::get_case_handler).patch(routes::cases::update_case_handler).delete(routes::cases::delete_case_handler))
        .route("/api/v1/cases/:case_uid/events", axum::routing::get(routes::cases::get_case_events_handler).post(routes::cases::create_case_event_handler))
        .route("/api/v1/health", axum::routing::get(|| async { axum::Json(serde_json::json!({ "status": "ok", "backend": "rust-axum" })) }))
        .layer(cors)
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("127.0.0.1:8080").await.unwrap();
    println!("🚀 Rust Server running on http://127.0.0.1:8080");
    
    axum::serve(listener, app).await.unwrap();
}
