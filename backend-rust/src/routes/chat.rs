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

    // Retrieve verified statutes from Legal Database
    let retrieved_laws = state.legal_db.search_laws(&payload.message, 6).await;
    let mut legal_context = String::new();
    if !retrieved_laws.is_empty() {
        legal_context.push_str("### 📚 VERIFIED INDIAN STATUTORY LAW & PRECEDENT CONTEXT (Use for absolute accuracy):\n");
        for law in retrieved_laws {
            let old_ref = law.old_law_reference.map(|r| format!(" (Old Law Ref: {})", r)).unwrap_or_default();
            let punishment = law.punishment.map(|p| format!("\n  - Punishment: {}", p)).unwrap_or_default();
            legal_context.push_str(&format!(
                "- **{} Section {}**{}: {}\n  - Summary: {}{}\n",
                law.act_name, law.section_number, old_ref, law.title, law.description, punishment
            ));
        }
    }

    let system_prompt = format!(
        "You are **Advocate YAMA**, a highly knowledgeable, empathetic, and strategic legal friend.\n{}",
        legal_context
    );

    let format_instruction = if !is_stage_2 {
        r#"
### 🛑 CRITICAL RULE: SOCRATIC STAGE 1 (DISCOVERY ONLY)
The user is asking a new legal query or initial situation (`SITUATION`). DO NOT give a robotic, default essay of laws, precedents, and action steps right now (`anni okesari ivva koodadhu`). Giving everything at once feels unnatural and confusing.
Instead, act like a smart, supportive legal buddy. Your job right now is strictly **STAGE 1: CASE DISCOVERY & CLARIFYING QUESTIONS**. Speak naturally, show empathy, and ask a few targeted questions to understand their exact situation before advising.

You MUST structure your response strictly using this friendly, rhythmic Stage 1 format:

# 🤝 YAMA's Initial Check-In

Hey there! I'm YAMA, your legal buddy. I'm really sorry you're dealing with this. Don't worry, I'm here to help you figure this out step-by-step. Before we jump into sending notices or filing complaints, let's get a clear picture of what's going on.

### ❓ A Few Quick Questions to Build Your Case:
1. **[Question 1 - E.g., Do you have this in writing? When did it happen?]**
2. **[Question 2 - E.g., What exactly did the other person say or do recently?]**
3. **[Question 3 - E.g., Do you have any proof of payment or communication?]**

---

### 📑 Things You Should Start Gathering (Keep These Handy):
- ✅ **[Primary Document - e.g., The original agreement or offer letter]**
- ✅ **[Payment Proof - e.g., Screenshots of UPI/Bank transfers]**
- ✅ **[Communication Proof - e.g., WhatsApp chats or emails]**

👉 *Just reply with quick answers to these (or upload any screenshots/documents using the 📎 icon or voice 🎙️). Once you tell me this, I'll give you the exact laws that protect you, past court decisions that support you, and a clear step-by-step plan on what to do next!*
"#
    } else {
        r#"
### 🎯 STAGE 2: STRATEGIC COUNSEL & ACTION PLAN
The user has now provided answers/context (`user icchina ans batti`). DO NOT repeat basic questions. Act like a smart, supportive legal buddy who is now laying out the exact plan of action in a natural, easy-to-follow rhythm.

You MUST structure your response strictly using this friendly, action-oriented Stage 2 format:

# 🤝 YAMA's Game Plan & Solution

Thanks for sharing those details! Based on what you've told me (`[Brief 1-sentence friendly summary of their situation]`), we definitely have a path forward. Here is the exact plan on how we handle this under Indian Law, step-by-step:

### ⚖️ 1. The Laws On Your Side
- **[Exact Act & Section - e.g., BNS 2023 Section 316 / IT Act Sec 66C]:** [Explain simply, like a friend, how this law protects them based on their answers]
- **[Evidence Strategy - e.g., under BSA 2023 Sec 61/63]:** [Explain how the proof they mentioned will help them win]

---

### 🏛️ 2. Proof That You Can Win (Court Precedents)
1. **[Supreme Court/High Court Case Name]:** [Briefly explain how this past case proves the other party is wrong and protects the user]
2. **[Supporting Citation]:** [Optional extra support]

---

### 💡 3. What You Need To Do Now (Action Plan)
*Here is what we do next, step-by-step:*
1. **🚀 Step 1 (Immediate Action):** [E.g., Send a formal legal demand notice via Registered Post. Give them 15 days to reply.]
2. **🛡️ Step 2 (Filing a Complaint):** [E.g., If they don't reply, here is the exact portal or police procedure to use, like E-Daakhil or CyberCrime 1930.]
3. **⚔️ Step 3 (Escalation):** [E.g., Moving to the Consumer Court or filing a civil recovery suit.]

---
⚖️ *Tip: Feel free to use the buttons below (`📊 Case Scorecard`, `🏛️ Courtroom Simulator`, `🚨 SOS Shield`, `⚖️ Litigation Estimator`) to run the numbers on your case based on what we just discussed!*
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
            use axum::http::StatusCode;
            (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"error": e}))).into_response()
        }
    }
}
