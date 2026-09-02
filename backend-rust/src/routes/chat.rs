use axum::{Json, response::{IntoResponse, sse::{Event, Sse}}};
use serde_json::json;
use crate::models::chat::{ChatMessage, ChatRequest, ChatResponse};
use crate::services::gemini::GeminiClient;
use std::sync::Arc;
use tokio::sync::RwLock;
use std::collections::HashMap;
use axum::extract::State;
use uuid::Uuid;
use futures_util::stream::Stream;
use futures_util::StreamExt;
use std::convert::Infallible;

pub struct AppState {
    pub gemini_client: GeminiClient,
    pub history_cache: RwLock<HashMap<String, Vec<ChatMessage>>>,
    pub legal_db: crate::services::legal_db::LegalDatabase,
}

pub async fn chat_handler(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<ChatRequest>,
) -> impl IntoResponse {
    let session_id = payload.session_id.unwrap_or_else(|| Uuid::new_v4().to_string());
    let mut history_text = String::new();
    let mut is_stage_2 = false;
    
    // Fetch history & save current user message
    {
        let mut cache = state.history_cache.write().await;
        let messages = cache.entry(session_id.clone()).or_insert_with(Vec::new);
        
        for m in messages.iter() {
            let role = if m.role == "user" { "User" } else { "Advocate YAMA" };
            history_text.push_str(&format!("{}: {}\n", role, m.content));
        }
        
        if messages.len() >= 2 || history_text.to_lowercase().contains("discovery") || history_text.to_lowercase().contains("❓") {
            is_stage_2 = true;
        }

        messages.push(ChatMessage {
            role: "user".to_string(),
            content: payload.message.clone(),
        });
    }

    // Retrieve verified statutes & court precedents from Enterprise Legal Database
    let unified_results = state.legal_db.unified_search(&payload.message, None, 6).await;
    let mut legal_context = String::new();
    
    if !unified_results.central_laws.is_empty() || !unified_results.state_laws.is_empty() || !unified_results.precedents.is_empty() {
        legal_context.push_str("### 📚 VERIFIED INDIAN STATUTORY LAW & COURT PRECEDENT CONTEXT (Use for absolute accuracy):\n");
        
        for law in unified_results.central_laws {
            let old_ref = law.old_law_reference.map(|r| format!(" (Old Law Ref: {})", r)).unwrap_or_default();
            let punishment = law.punishment.map(|p| format!(" | Punishment: {}", p)).unwrap_or_default();
            legal_context.push_str(&format!(
                "- [Central Law] **{} Section {}**{}: {} - {}{}\n",
                law.act_name, law.section_number, old_ref, law.title, law.description, punishment
            ));
        }

        for slaw in unified_results.state_laws {
            let punishment = slaw.punishment.map(|p| format!(" | Relief: {}", p)).unwrap_or_default();
            legal_context.push_str(&format!(
                "- [State Law: {}] **{} Section {}**: {} - {}{}\n",
                slaw.state_name, slaw.act_name, slaw.section_number, slaw.title, slaw.description, punishment
            ));
        }

        for prec in unified_results.precedents {
            let disp = prec.disposition.map(|d| format!(" | Outcome: {}", d)).unwrap_or_default();
            legal_context.push_str(&format!(
                "- [{} Landmark Precedent] **{} ({})**: Holding: {}{}\n",
                prec.court_name, prec.case_name, prec.citation, prec.ratio_decidendi, disp
            ));
        }
    }

    let system_prompt = format!(
        "You are **Advocate YAMA**, a highly knowledgeable, empathetic, and strategic legal friend.\n{}",
        legal_context
    );

    let user_msg_lower = payload.message.trim().to_lowercase();
    let is_simple_greeting = ["hi", "hii", "hello", "hlo", "hey", "namaste", "good morning", "good evening"].contains(&user_msg_lower.as_str());

    let format_instruction = if is_simple_greeting && history_text.is_empty() {
        r#"
### 🤝 GREETING MODE:
The user just sent a simple greeting. DO NOT dump any questionnaire, checklists, or long essays.
Reply warmly and concisely in under 3 lines:
- Introduce yourself as **Advocate YAMA**, their personal AI legal strategist.
- Ask them in 1 line what legal issue, dispute, or notice they need help with today.
- End with 3 quick example areas: *(e.g., 🏠 Landlord/Tenant, 💼 Employment & Salary, 💳 Fraud & Money Recovery)*.
"#
    } else if !is_stage_2 {
        r#"
### 🛑 CRISP SOCRATIC DISCOVERY (STAGE 1):
Be concise, strategic, and punchy. DO NOT write long paragraphs, giant checklists, or redundant essays. Keep the entire response under 90-110 words.

Structure your response strictly as:
### 🤝 **Advocate YAMA Check-In**
[1 warm, confident sentence acknowledging their situation].

#### ❓ **Key Facts Needed:**
1. **[Question 1]:** [Short, direct question on what happened & when].
2. **[Question 2]:** [Short question on written agreements or payment/communication proof].

#### 📑 **Quick Proof to Keep Ready:**
- 📄 [Primary proof: Agreement / Contract / WhatsApp chats / Bank receipts].

👉 *Reply with quick answers above, and I'll immediately pull the exact legal sections and your step-by-step action plan!*
"#
    } else {
        r#"
### 🎯 CRISP STRATEGIC GAME PLAN (STAGE 2):
The user provided answers. Be direct, authoritative, and concise. No fluff or repetitive text. Keep response under 150-180 words.

Structure your response strictly as:
### ⚖️ **Your Legal Strategy & Action Plan**
[1 punchy sentence summarizing their legal leverage].

#### 🛡️ **Applicable Laws on Your Side:**
- **[Exact Section & Act]:** [1 concise line explaining how this statute protects them or penalizes the opponent].

#### 🏛️ **Precedent & Court Leverage:**
- **[Landmark Landmark Case / Principle]:** [1 line showing how past rulings support the user].

#### 🚀 **Next Steps (Action Plan):**
1. **Send Formal Notice:** [15-day Demand Notice / Legal Warning].
2. **Filing Complaint:** [Exact Portal / Police / Consumer Forum remedy].
3. **Escalation:** [Court remedy if non-compliant].
"#
    };

    let combined_prompt = format!(
        "{}\n\n{}\n\n### Conversation History:\n{}\n\n### User Query: {}\n\nResponse:",
        system_prompt,
        format_instruction,
        history_text,
        payload.message
    );

    let result = state.gemini_client.generate_response_stream(
        combined_prompt,
        payload.custom_api_key,
        payload.custom_model,
    ).await;

    match result {
        Ok(stream) => {
            use axum::body::Body;
            use axum::response::Response;
            
            let body = Body::from_stream(stream);
            
            Response::builder()
                .header("Content-Type", "text/event-stream")
                .header("Cache-Control", "no-cache")
                .header("Connection", "keep-alive")
                .body(body)
                .unwrap()
        },
        Err(e) => {
            use axum::body::Body;
            use axum::response::Response;
            
            let guidance_text = if e.contains("leaked") || e.contains("API key") || e.contains("403") || e.contains("PERMISSION_DENIED") {
                "⚠️ **Google Gemini API Key Alert:**\nThe system API key was reported as leaked/revoked by Google.\n\n👉 **To activate live AI responses instantly:**\n1. Click the **⚙️ Settings icon** in the top-right header.\n2. Paste your free **Gemini API Key** (from [Google AI Studio](https://aistudio.google.com/app/apikey)).\n3. Click Save — it stores securely in your browser and starts streaming responses immediately!\n\n*(In the meantime, you can explore all 12,036+ verified laws, High Courts, and Supreme Court rulings in the **Laws** tab above!)*".to_string()
            } else {
                format!("⚠️ **AI Service Notice:** {}\n\nPlease check your internet connection or update your Gemini API key in Settings (⚙️).", e)
            };

            let sse_chunk = format!("data: {}\n\n", json!({
                "candidates": [{
                    "content": {
                        "parts": [{ "text": guidance_text }]
                    }
                }]
            }));
            let done_chunk = "data: [DONE]\n\n".to_string();

            let stream = futures_util::stream::iter(vec![
                Ok::<_, Infallible>(bytes::Bytes::from(sse_chunk)),
                Ok::<_, Infallible>(bytes::Bytes::from(done_chunk)),
            ]);

            let body = Body::from_stream(stream);

            Response::builder()
                .header("Content-Type", "text/event-stream")
                .header("Cache-Control", "no-cache")
                .header("Connection", "keep-alive")
                .body(body)
                .unwrap()
        }
    }
}
