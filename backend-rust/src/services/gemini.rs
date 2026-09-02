use reqwest::Client;
use serde_json::json;
use std::env;
use futures_util::Stream;
use std::pin::Pin;

fn normalize_model_name(raw: &str) -> String {
    let clean = raw.trim().to_lowercase();
    if clean.is_empty() {
        return "gemini-2.5-flash".to_string();
    }

    if clean.contains("flash-lite") || clean.contains("flash lite") {
        "gemini-2.0-flash-lite".to_string()
    } else if clean.contains("2.0") && clean.contains("flash") {
        "gemini-2.0-flash".to_string()
    } else if clean.contains("2.5") && clean.contains("pro") {
        "gemini-2.5-pro".to_string()
    } else if clean.contains("1.5") && clean.contains("pro") {
        "gemini-1.5-pro".to_string()
    } else if clean.contains("pro") {
        "gemini-2.5-pro".to_string()
    } else if clean.contains("2.5") || clean.contains("flash") {
        "gemini-2.5-flash".to_string()
    } else {
        let slug = clean.replace(' ', "-");
        if slug.starts_with("gemini-") {
            slug
        } else {
            "gemini-2.5-flash".to_string()
        }
    }
}

pub struct GeminiClient {
    client: Client,
    default_api_key: String,
    default_model: String,
}

impl GeminiClient {
    pub fn new() -> Self {
        let api_key = env::var("GOOGLE_API_KEY").unwrap_or_else(|_| "".to_string());
        Self {
            client: Client::new(),
            default_api_key: api_key,
            default_model: "gemini-2.5-flash".to_string(),
        }
    }

    pub async fn generate_response_stream(
        &self,
        prompt: String,
        custom_api_key: Option<String>,
        custom_model: Option<String>,
    ) -> Result<impl Stream<Item = Result<bytes::Bytes, String>> + use<>, String> {
        let api_key = match custom_api_key {
            Some(ref k) if !k.trim().is_empty() => k.trim().to_string(),
            _ => {
                if !self.default_api_key.trim().is_empty() {
                    self.default_api_key.clone()
                } else {
                    std::env::var("GOOGLE_API_KEY").unwrap_or_else(|_| "AIzaSyDuUX9eeFapUJMgmckRUy_wUxNMI_p3CME".to_string())
                }
            }
        };

        let raw_model = match custom_model {
            Some(ref m) if !m.trim().is_empty() => m.trim().to_string(),
            _ => {
                if !self.default_model.trim().is_empty() {
                    self.default_model.clone()
                } else {
                    "gemini-2.5-flash".to_string()
                }
            }
        };

        let model = normalize_model_name(&raw_model);

        if api_key.is_empty() {
            return Err("No API key provided".to_string());
        }

        let url = format!(
            "https://generativelanguage.googleapis.com/v1beta/models/{}:streamGenerateContent?alt=sse&key={}",
            model, api_key
        );

        let payload = json!({
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        });

        let response = self.client.post(&url).json(&payload).send().await.map_err(|e| e.to_string())?;

        if !response.status().is_success() {
            let status = response.status();
            let text = response.text().await.unwrap_or_default();
            return Err(format!("Gemini API error ({}): {}", status, text));
        }

        use futures_util::StreamExt;
        
        let byte_stream = response.bytes_stream().map(|res| res.map_err(|e| e.to_string()));

        Ok(byte_stream)
    }
}
