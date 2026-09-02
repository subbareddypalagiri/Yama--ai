use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::sync::Arc;
use uuid::Uuid;
use crate::routes::chat::AppState;

#[derive(Debug, Deserialize)]
pub struct CaseListParams {
    pub status: Option<String>,
    pub category: Option<String>,
    pub search: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CaseDTO {
    pub id: i64,
    pub case_uid: String,
    pub title: String,
    pub description: Option<String>,
    pub category: Option<String>,
    pub status: String,
    pub priority: String,
    pub client_name: Option<String>,
    pub opponent_name: Option<String>,
    pub court_name: Option<String>,
    pub case_number: Option<String>,
    pub next_hearing_date: Option<String>,
    pub ai_summary: Option<String>,
    pub relevant_laws: Option<String>,
    pub risk_assessment: Option<String>,
    pub created_at: String,
    pub updated_at: Option<String>,
    pub document_count: i64,
    pub event_count: i64,
}

#[derive(Debug, Deserialize)]
pub struct CreateCaseRequest {
    pub title: String,
    pub description: Option<String>,
    pub category: Option<String>,
    pub priority: Option<String>,
    pub client_name: Option<String>,
    pub opponent_name: Option<String>,
    pub court_name: Option<String>,
    pub case_number: Option<String>,
    pub next_hearing_date: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct UpdateCaseRequest {
    pub title: Option<String>,
    pub description: Option<String>,
    pub category: Option<String>,
    pub status: Option<String>,
    pub priority: Option<String>,
    pub client_name: Option<String>,
    pub opponent_name: Option<String>,
    pub court_name: Option<String>,
    pub case_number: Option<String>,
    pub next_hearing_date: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CaseEventDTO {
    pub id: i64,
    pub event_type: String,
    pub title: String,
    pub description: Option<String>,
    pub event_date: String,
    pub created_at: String,
}

#[derive(Debug, Deserialize)]
pub struct CreateCaseEventRequest {
    pub event_type: String,
    pub title: String,
    pub description: Option<String>,
    pub event_date: String,
}

// GET /api/v1/cases
pub async fn list_cases_handler(
    State(state): State<Arc<AppState>>,
    Query(params): Query<CaseListParams>,
) -> impl IntoResponse {
    let mut cases = Vec::new();
    let conn_guard = state.legal_db.get_conn().await;
    if let Some(conn) = conn_guard.as_ref() {
        let mut query = String::from(
            "SELECT id, case_uid, title, description, category, status, priority, \
             client_name, opponent_name, court_name, case_number, next_hearing_date, \
             ai_summary, relevant_laws, risk_assessment, created_at, updated_at \
             FROM cases WHERE 1=1"
        );

        let search_pattern = params.search.as_ref().map(|s| format!("%{}%", s.to_lowercase()));
        if search_pattern.is_some() {
            query.push_str(" AND (LOWER(title) LIKE ?1 OR LOWER(client_name) LIKE ?1 OR LOWER(case_number) LIKE ?1)");
        }
        if let Some(ref st) = params.status {
            query.push_str(&format!(" AND LOWER(status) = '{}'", st.to_lowercase()));
        }
        if let Some(ref cat) = params.category {
            query.push_str(&format!(" AND LOWER(category) = '{}'", cat.to_lowercase()));
        }
        query.push_str(" ORDER BY created_at DESC");

        if let Ok(mut stmt) = conn.prepare(&query) {
            if let Some(ref sp) = search_pattern {
                if let Ok(iter) = stmt.query_map([sp], |row| map_case_row(row, conn)) {
                    for item in iter.flatten() {
                        cases.push(item);
                    }
                }
            } else if let Ok(iter) = stmt.query_map([], |row| map_case_row(row, conn)) {
                for item in iter.flatten() {
                    cases.push(item);
                }
            }
        }
    }
    Json(cases)
}

// POST /api/v1/cases
pub async fn create_case_handler(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<CreateCaseRequest>,
) -> impl IntoResponse {
    let case_uid = Uuid::new_v4().to_string();
    let priority = payload.priority.unwrap_or_else(|| "medium".to_string());
    let status = "active".to_string();

    let conn_guard = state.legal_db.get_conn().await;
    if let Some(conn) = conn_guard.as_ref() {
        let insert_res = conn.execute(
            "INSERT INTO cases (case_uid, title, description, category, status, priority, \
             client_name, opponent_name, court_name, case_number, next_hearing_date) \
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11)",
            rusqlite::params![
                case_uid,
                payload.title,
                payload.description,
                payload.category,
                status,
                priority,
                payload.client_name,
                payload.opponent_name,
                payload.court_name,
                payload.case_number,
                payload.next_hearing_date
            ],
        );

        if insert_res.is_ok() {
            if let Some(case_dto) = get_case_by_uid_internal(conn, &case_uid) {
                return (StatusCode::CREATED, Json(case_dto)).into_response();
            }
        }
    }
    (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"error": "Failed to create case"}))).into_response()
}

// GET /api/v1/cases/:case_uid
pub async fn get_case_handler(
    State(state): State<Arc<AppState>>,
    Path(case_uid): Path<String>,
) -> impl IntoResponse {
    let conn_guard = state.legal_db.get_conn().await;
    if let Some(conn) = conn_guard.as_ref() {
        if let Some(case_dto) = get_case_by_uid_internal(conn, &case_uid) {
            return Json(case_dto).into_response();
        }
    }
    (StatusCode::NOT_FOUND, Json(json!({"error": "Case not found"}))).into_response()
}

// PATCH /api/v1/cases/:case_uid
pub async fn update_case_handler(
    State(state): State<Arc<AppState>>,
    Path(case_uid): Path<String>,
    Json(payload): Json<UpdateCaseRequest>,
) -> impl IntoResponse {
    let conn_guard = state.legal_db.get_conn().await;
    if let Some(conn) = conn_guard.as_ref() {
        if let Some(mut existing) = get_case_by_uid_internal(conn, &case_uid) {
            if let Some(t) = payload.title { existing.title = t; }
            if let Some(d) = payload.description { existing.description = Some(d); }
            if let Some(c) = payload.category { existing.category = Some(c); }
            if let Some(s) = payload.status { existing.status = s; }
            if let Some(p) = payload.priority { existing.priority = p; }
            if let Some(cn) = payload.client_name { existing.client_name = Some(cn); }
            if let Some(on) = payload.opponent_name { existing.opponent_name = Some(on); }
            if let Some(ct) = payload.court_name { existing.court_name = Some(ct); }
            if let Some(num) = payload.case_number { existing.case_number = Some(num); }
            if let Some(date) = payload.next_hearing_date { existing.next_hearing_date = Some(date); }

            let _ = conn.execute(
                "UPDATE cases SET title=?1, description=?2, category=?3, status=?4, priority=?5, \
                 client_name=?6, opponent_name=?7, court_name=?8, case_number=?9, next_hearing_date=?10, \
                 updated_at=CURRENT_TIMESTAMP WHERE case_uid=?11",
                rusqlite::params![
                    existing.title,
                    existing.description,
                    existing.category,
                    existing.status,
                    existing.priority,
                    existing.client_name,
                    existing.opponent_name,
                    existing.court_name,
                    existing.case_number,
                    existing.next_hearing_date,
                    case_uid
                ],
            );
            return Json(existing).into_response();
        }
    }
    (StatusCode::NOT_FOUND, Json(json!({"error": "Case not found"}))).into_response()
}

// DELETE /api/v1/cases/:case_uid
pub async fn delete_case_handler(
    State(state): State<Arc<AppState>>,
    Path(case_uid): Path<String>,
) -> impl IntoResponse {
    let conn_guard = state.legal_db.get_conn().await;
    if let Some(conn) = conn_guard.as_ref() {
        let _ = conn.execute("DELETE FROM cases WHERE case_uid=?1", rusqlite::params![case_uid]);
        return StatusCode::NO_CONTENT.into_response();
    }
    (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"error": "Failed to delete case"}))).into_response()
}

// GET /api/v1/cases/:case_uid/events
pub async fn get_case_events_handler(
    State(state): State<Arc<AppState>>,
    Path(case_uid): Path<String>,
) -> impl IntoResponse {
    let mut events = Vec::new();
    let conn_guard = state.legal_db.get_conn().await;
    if let Some(conn) = conn_guard.as_ref() {
        let query = "SELECT e.id, e.event_type, e.title, e.description, e.event_date, e.created_at \
                     FROM case_events e JOIN cases c ON c.id = e.case_id \
                     WHERE c.case_uid = ?1 ORDER BY e.event_date ASC";
        if let Ok(mut stmt) = conn.prepare(query) {
            let rows = stmt.query_map([case_uid], |row| {
                Ok(CaseEventDTO {
                    id: row.get(0)?,
                    event_type: row.get(1)?,
                    title: row.get(2)?,
                    description: row.get(3)?,
                    event_date: row.get(4)?,
                    created_at: row.get(5)?,
                })
            });
            if let Ok(iter) = rows {
                for item in iter.flatten() {
                    events.push(item);
                }
            }
        }
    }
    Json(events)
}

// POST /api/v1/cases/:case_uid/events
pub async fn create_case_event_handler(
    State(state): State<Arc<AppState>>,
    Path(case_uid): Path<String>,
    Json(payload): Json<CreateCaseEventRequest>,
) -> impl IntoResponse {
    let conn_guard = state.legal_db.get_conn().await;
    if let Some(conn) = conn_guard.as_ref() {
        if let Ok(case_id) = conn.query_row("SELECT id FROM cases WHERE case_uid=?1", [&case_uid], |r| r.get::<_, i64>(0)) {
            let res = conn.execute(
                "INSERT INTO case_events (case_id, event_type, title, description, event_date) \
                 VALUES (?1, ?2, ?3, ?4, ?5)",
                rusqlite::params![
                    case_id,
                    payload.event_type,
                    payload.title,
                    payload.description,
                    payload.event_date
                ],
            );
            if res.is_ok() {
                let event_id = conn.last_insert_rowid();
                return (
                    StatusCode::CREATED,
                    Json(json!({
                        "id": event_id,
                        "event_type": payload.event_type,
                        "title": payload.title,
                        "description": payload.description,
                        "event_date": payload.event_date,
                    }))
                ).into_response();
            }
        }
    }
    (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"error": "Failed to create event"}))).into_response()
}

fn map_case_row(row: &rusqlite::Row, conn: &rusqlite::Connection) -> rusqlite::Result<CaseDTO> {
    let id: i64 = row.get(0)?;
    let doc_count = conn.query_row("SELECT count(*) FROM documents WHERE case_id=?1", [id], |r| r.get::<_, i64>(0)).unwrap_or(0);
    let evt_count = conn.query_row("SELECT count(*) FROM case_events WHERE case_id=?1", [id], |r| r.get::<_, i64>(0)).unwrap_or(0);

    Ok(CaseDTO {
        id,
        case_uid: row.get(1)?,
        title: row.get(2)?,
        description: row.get(3)?,
        category: row.get(4)?,
        status: row.get(5)?,
        priority: row.get(6)?,
        client_name: row.get(7)?,
        opponent_name: row.get(8)?,
        court_name: row.get(9)?,
        case_number: row.get(10)?,
        next_hearing_date: row.get(11)?,
        ai_summary: row.get(12)?,
        relevant_laws: row.get(13)?,
        risk_assessment: row.get(14)?,
        created_at: row.get(15)?,
        updated_at: row.get(16)?,
        document_count: doc_count,
        event_count: evt_count,
    })
}

fn get_case_by_uid_internal(conn: &rusqlite::Connection, uid: &str) -> Option<CaseDTO> {
    let query = "SELECT id, case_uid, title, description, category, status, priority, \
                 client_name, opponent_name, court_name, case_number, next_hearing_date, \
                 ai_summary, relevant_laws, risk_assessment, created_at, updated_at \
                 FROM cases WHERE case_uid=?1";
    conn.query_row(query, [uid], |row| map_case_row(row, conn)).ok()
}
