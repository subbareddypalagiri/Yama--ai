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
        .layer(cors)
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("127.0.0.1:8080").await.unwrap();
    println!("🚀 Rust Server running on http://127.0.0.1:8080");
    
    axum::serve(listener, app).await.unwrap();
}
