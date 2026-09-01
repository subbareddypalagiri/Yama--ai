use reqwest::Client;
use serde_json::json;
use std::env;
use futures_util::Stream;
use std::pin::Pin;

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
        let api_key = custom_api_key.unwrap_or_else(|| self.default_api_key.clone());
        let model = custom_model.unwrap_or_else(|| self.default_model.clone());

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
