use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct ChatMessage {
    pub role: String,
    pub content: String,
}

#[derive(Debug, Deserialize)]
pub struct ChatRequest {
    pub message: String,
    pub session_id: Option<String>,
    pub response_style: Option<String>,
    pub response_language: Option<String>,
    pub custom_api_key: Option<String>,
    pub custom_model: Option<String>,
    pub state_code: Option<String>,
    pub mode: Option<String>,
    pub lawyer_context: Option<String>,
    pub client_profile: Option<serde_json::Value>,
}

#[derive(Debug, Serialize)]
pub struct ChatResponse {
    pub session_id: String,
    pub analysis: String,
    pub relevant_sections: Vec<String>,
    pub timestamp: String,
    pub detected_input_language: Option<String>,
    pub response_language: Option<String>,
}
