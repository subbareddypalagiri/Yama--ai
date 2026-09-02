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

    // Retrieve verified statutes & court precedents from Enterprise Legal Database with State Code filter
    let unified_results = state.legal_db.unified_search(&payload.message, payload.state_code.as_deref(), 8).await;
    let mut legal_context = String::new();
    let mut matched_sections_summary = Vec::new();
    
    if !unified_results.central_laws.is_empty() || !unified_results.state_laws.is_empty() || !unified_results.precedents.is_empty() {
        legal_context.push_str("### 📚 VERIFIED INDIAN STATUTORY LAW & COURT PRECEDENT CONTEXT (Use for absolute accuracy):\n");
        
        for law in &unified_results.central_laws {
            let old_ref = law.old_law_reference.as_ref().map(|r| format!(" (Old Law Ref: {})", r)).unwrap_or_default();
            let punishment = law.punishment.as_ref().map(|p| format!(" | Punishment: {}", p)).unwrap_or_default();
            matched_sections_summary.push(format!("{} Section {}{}", law.act_name, law.section_number, old_ref));
            legal_context.push_str(&format!(
                "- [Central Law] **{} Section {}**{}: {} - {}{}\n",
                law.act_name, law.section_number, old_ref, law.title, law.description, punishment
            ));
        }

        for slaw in &unified_results.state_laws {
            let punishment = slaw.punishment.as_ref().map(|p| format!(" | Relief: {}", p)).unwrap_or_default();
            matched_sections_summary.push(format!("{} Section {} ({})", slaw.act_name, slaw.section_number, slaw.state_name));
            legal_context.push_str(&format!(
                "- [State Law: {}] **{} Section {}**: {} - {}{}\n",
                slaw.state_name, slaw.act_name, slaw.section_number, slaw.title, slaw.description, punishment
            ));
        }

        for prec in &unified_results.precedents {
            let disp = prec.disposition.as_ref().map(|d| format!(" | Outcome: {}", d)).unwrap_or_default();
            legal_context.push_str(&format!(
                "- [{} Landmark Precedent] **{} ({})**: Holding: {}{}\n",
                prec.court_name, prec.case_name, prec.citation, prec.ratio_decidendi, disp
            ));
        }
    }

    let mode_str = payload.mode.as_deref().unwrap_or("default");

    let system_prompt = format!(
        "You are **Advocate YAMA**, an elite, empathetic, and strategic Indian Legal Advisor and courtroom strategist.\n\
        Client Mode: {}\nState Jurisdiction: {}\n{}\n\
        Always cite the exact Section numbers, Act names, and landmark court rulings. Maintain a confident, protective, and reassuring tone.",
        mode_str,
        payload.state_code.as_deref().unwrap_or("All India"),
        legal_context
    );

    let user_msg_lower = payload.message.trim().to_lowercase();
    let is_simple_greeting = ["hi", "hii", "hello", "hlo", "hey", "namaste", "good morning", "good evening"].contains(&user_msg_lower.as_str());

    let format_instruction = if is_simple_greeting && history_text.is_empty() {
        r#"
### 🤝 GREETING MODE:
Reply warmly and concisely in under 3 lines:
- Greet the client as **Advocate YAMA**.
- Ask what legal matter, notice, or dispute they are facing today.
- Mention 3 quick areas: *(e.g., 💻 Cyber Fraud & Hacking, 🏠 Tenancy & Land, 💼 Salary & Employment)*.
"#
    } else if mode_str == "quick" {
        r#"
### ⚡ QUICK ADVICE MODE:
Provide a punchy, high-impact 3-step action plan in under 120 words:
1. **Immediate Protection / Counter-Action:** What to do right now.
2. **Applicable Laws & Penalties:** Cite exact sections (IT Act, BNS, State laws).
3. **Official Reporting / Remedy:** Exact police/portal helpline (e.g. 1930 / cybercrime.gov.in / Rent Controller).
"#
    } else if mode_str == "rights" {
        r#"
### 🛡️ KNOW YOUR RIGHTS MODE:
Detail the client's statutory rights and protections under Indian law:
- **Your Legal Rights:** Exactly what protection the Constitution, BNS/IPC, and IT Act guarantee you.
- **Opponent's Violations:** Why the opponent's actions are criminal/illegal and what penalties they face.
- **Evidence Protection:** What screenshots, chats, and records you must preserve under BSA Section 63 (Sec 65B).
"#
    } else if mode_str == "document" {
        r#"
### 📄 DRAFT / COMPLAINT GENERATOR MODE:
Generate a court-standard, formal Written Complaint / FIR Application ready for submission:
- To: The Station House Officer / Competent Authority
- Subject: Formal Criminal Complaint
- Brief Facts of the Offence
- Applicable Sections of Law
- Prayer / Relief Requested
"#
    } else if !is_stage_2 {
        r#"
### 🛑 CRISP SOCRATIC DISCOVERY (STAGE 1):
Be concise, strategic, and punchy. Keep under 110 words:
### 🤝 **Advocate YAMA Check-In**
[1 confident sentence acknowledging their situation].

#### ❓ **Key Facts Needed:**
1. **[Question 1]:** [Short direct question].
2. **[Question 2]:** [Short question on evidence or financial loss].

#### 📑 **Quick Proof to Keep Ready:**
- 📄 [Essential proofs: Screenshots, URLs, transaction IDs, chats].

👉 *Reply with answers above, and I'll immediately give your complete legal action plan!*
"#
    } else {
        r#"
### 🎯 CRISP STRATEGIC GAME PLAN (STAGE 2):
Keep response under 160 words:
### ⚖️ **Your Legal Strategy & Action Plan**
[1 punchy sentence summarizing your legal leverage].

#### 🛡️ **Applicable Laws on Your Side:**
- **[Exact Section & Act]:** [How this penalizes the perpetrator or protects you].

#### 🏛️ **Precedent Leverage:**
- **[Court Ruling / Holding]:** [How judges rule in similar cases].

#### 🚀 **Next Steps (Action Plan):**
1. **Immediate Step:** [Helpline 1930 / Formal Notice].
2. **Filing Complaint:** [Cyber Crime / Police FIR].
3. **Escalation:** [Court remedy if needed].
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
            
            let mut guidance_text = String::new();

            if !matched_sections_summary.is_empty() {
                guidance_text.push_str("### ⚖️ **Advocate YAMA - Strategic Legal Assessment**\n\n");
                guidance_text.push_str("Based on your situation, here is the immediate legal protection and penal liability under Indian Law:\n\n");
                
                guidance_text.push_str("#### 🛡️ **Applicable Indian Statutes on Your Side:**\n");
                for s in matched_sections_summary.iter().take(4) {
                    guidance_text.push_str(&format!("- 📌 **{}**\n", s));
                }

                guidance_text.push_str("\n#### 🚨 **Immediate Emergency Battle Plan:**\n");
                guidance_text.push_str("1. **Preserve Evidence (BSA Sec 63 / IEA 65B):** Take complete screenshots of the account, extortion chats, payment handles/QR codes, and profile URLs with exact timestamps.\n");
                guidance_text.push_str("2. **Dial National Cyber Crime Helpline (1930):** Immediately call **1930** or report online at [cybercrime.gov.in](https://cybercrime.gov.in) to flag extortion and freeze recipient bank/UPI accounts.\n");
                guidance_text.push_str("3. **File Police Complaint / FIR:** Submit a formal written complaint under **IT Act Sections 66C/66D** and **BNS Section 308 (Extortion)** at your nearest Cyber Crime Police Station.\n");
                guidance_text.push_str("4. **Do NOT Transfer Money:** Extortionists continue demanding money after initial payment. Block, preserve evidence, and let the cyber cell trace the IP/device.\n\n");
            }

            if e.contains("leaked") || e.contains("API key") || e.contains("403") || e.contains("PERMISSION_DENIED") || e.contains("No API key") {
                guidance_text.push_str("---\n💡 *Note: To activate deep generative conversational reasoning, add your free Gemini API Key via the **⚙️ Settings icon** in the header.*");
            } else {
                guidance_text.push_str(&format!("\n---\n*(AI Service Notice: {})*", e));
            }

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
