use axum::{
    extract::{Query, State},
    Json,
    response::IntoResponse,
};
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::sync::Arc;
use crate::routes::chat::AppState;

#[derive(Debug, Deserialize)]
pub struct SearchParams {
    pub q: Option<String>,
    pub category: Option<String>,
    pub act_name: Option<String>,
    pub state_code: Option<String>,
    pub court_code: Option<String>,
    pub page: Option<usize>,
    pub limit: Option<usize>,
}

#[derive(Debug, Serialize)]
pub struct LawSectionDTO {
    pub id: i64,
    pub act_name: String,
    pub section_number: String,
    pub title: String,
    pub description: String,
    pub category: String,
    pub punishment: Option<String>,
    pub old_law_reference: Option<String>,
    pub keywords: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct StateLawDTO {
    pub id: i64,
    pub state_name: String,
    pub state_code: String,
    pub act_name: String,
    pub section_number: String,
    pub title: String,
    pub description: String,
    pub category: String,
    pub punishment: Option<String>,
    pub keywords: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct SupremeCourtDTO {
    pub id: i64,
    pub case_name: String,
    pub citation: String,
    pub year: i64,
    pub bench: Option<String>,
    pub headnotes: Option<String>,
    pub ratio_decidendi: String,
    pub sections_referred: Option<String>,
    pub verdict: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct HighCourtDTO {
    pub id: i64,
    pub high_court_name: String,
    pub court_code: String,
    pub state_code: String,
    pub case_name: String,
    pub citation: String,
    pub year: i64,
    pub bench: Option<String>,
    pub summary: String,
    pub ratio_decidendi: String,
    pub sections_referred: Option<String>,
    pub disposition: Option<String>,
}

// 1. Central Laws Search Handler - Perfectly Ordered by Act & Section Number
pub async fn search_laws_handler(
    State(state): State<Arc<AppState>>,
    Query(params): Query<SearchParams>,
) -> impl IntoResponse {
    let q = params.q.unwrap_or_default().trim().to_string();
    let cat = params.category.unwrap_or_default().trim().to_string();
    let act = params.act_name.unwrap_or_default().trim().to_string();
    let page = params.page.unwrap_or(1).max(1);
    let limit = params.limit.unwrap_or(30).min(200);
    let offset = (page - 1) * limit;

    let mut results: Vec<LawSectionDTO> = Vec::new();
    let mut total: i64 = 0;

    let conn_guard = state.legal_db.get_conn().await;
    if let Some(conn) = conn_guard.as_ref() {
        let q_pattern = format!("%{}%", q.to_lowercase());
        let cat_pattern = format!("%{}%", cat.to_lowercase());
        let act_pattern = format!("%{}%", act.to_lowercase());

        if !act.is_empty() && !q.is_empty() {
            if let Ok(mut c_stmt) = conn.prepare("SELECT count(*) FROM central_acts WHERE LOWER(act_name) LIKE ?1 AND (LOWER(title) LIKE ?2 OR LOWER(description) LIKE ?2 OR section_number = ?3)") {
                total = c_stmt.query_row(rusqlite::params![act_pattern, q_pattern, q], |r| r.get::<_, i64>(0)).unwrap_or(0);
            }
            if let Ok(mut stmt) = conn.prepare("SELECT id, act_name, section_number, title, description, category, punishment, old_law_reference, keywords FROM central_acts WHERE LOWER(act_name) LIKE ?1 AND (LOWER(title) LIKE ?2 OR LOWER(description) LIKE ?2 OR section_number = ?3) ORDER BY CAST(section_number AS INTEGER) ASC, id ASC LIMIT ?4 OFFSET ?5") {
                if let Ok(rows) = stmt.query_map(rusqlite::params![act_pattern, q_pattern, q, limit as i64, offset as i64], |row| {
                    Ok(LawSectionDTO {
                        id: row.get(0)?, act_name: row.get(1)?, section_number: row.get(2)?, title: row.get(3)?,
                        description: row.get(4)?, category: row.get(5)?, punishment: row.get(6).ok(),
                        old_law_reference: row.get(7).ok(), keywords: row.get(8).ok(),
                    })
                }) {
                    for item in rows.flatten() { results.push(item); }
                }
            }
        } else if !act.is_empty() {
            if let Ok(mut c_stmt) = conn.prepare("SELECT count(*) FROM central_acts WHERE LOWER(act_name) LIKE ?1") {
                total = c_stmt.query_row(rusqlite::params![act_pattern], |r| r.get::<_, i64>(0)).unwrap_or(0);
            }
            if let Ok(mut stmt) = conn.prepare("SELECT id, act_name, section_number, title, description, category, punishment, old_law_reference, keywords FROM central_acts WHERE LOWER(act_name) LIKE ?1 ORDER BY CAST(section_number AS INTEGER) ASC, id ASC LIMIT ?2 OFFSET ?3") {
                if let Ok(rows) = stmt.query_map(rusqlite::params![act_pattern, limit as i64, offset as i64], |row| {
                    Ok(LawSectionDTO {
                        id: row.get(0)?, act_name: row.get(1)?, section_number: row.get(2)?, title: row.get(3)?,
                        description: row.get(4)?, category: row.get(5)?, punishment: row.get(6).ok(),
                        old_law_reference: row.get(7).ok(), keywords: row.get(8).ok(),
                    })
                }) {
                    for item in rows.flatten() { results.push(item); }
                }
            }
        } else if !cat.is_empty() && !q.is_empty() {
            if let Ok(mut c_stmt) = conn.prepare("SELECT count(*) FROM central_acts WHERE LOWER(category) LIKE ?1 AND (LOWER(title) LIKE ?2 OR LOWER(description) LIKE ?2 OR section_number = ?3)") {
                total = c_stmt.query_row(rusqlite::params![cat_pattern, q_pattern, q], |r| r.get::<_, i64>(0)).unwrap_or(0);
            }
            if let Ok(mut stmt) = conn.prepare("SELECT id, act_name, section_number, title, description, category, punishment, old_law_reference, keywords FROM central_acts WHERE LOWER(category) LIKE ?1 AND (LOWER(title) LIKE ?2 OR LOWER(description) LIKE ?2 OR section_number = ?3) ORDER BY act_name ASC, CAST(section_number AS INTEGER) ASC LIMIT ?4 OFFSET ?5") {
                if let Ok(rows) = stmt.query_map(rusqlite::params![cat_pattern, q_pattern, q, limit as i64, offset as i64], |row| {
                    Ok(LawSectionDTO {
                        id: row.get(0)?, act_name: row.get(1)?, section_number: row.get(2)?, title: row.get(3)?,
                        description: row.get(4)?, category: row.get(5)?, punishment: row.get(6).ok(),
                        old_law_reference: row.get(7).ok(), keywords: row.get(8).ok(),
                    })
                }) {
                    for item in rows.flatten() { results.push(item); }
                }
            }
        } else if !cat.is_empty() {
            if let Ok(mut c_stmt) = conn.prepare("SELECT count(*) FROM central_acts WHERE LOWER(category) LIKE ?1") {
                total = c_stmt.query_row(rusqlite::params![cat_pattern], |r| r.get::<_, i64>(0)).unwrap_or(0);
            }
            if let Ok(mut stmt) = conn.prepare("SELECT id, act_name, section_number, title, description, category, punishment, old_law_reference, keywords FROM central_acts WHERE LOWER(category) LIKE ?1 ORDER BY act_name ASC, CAST(section_number AS INTEGER) ASC LIMIT ?2 OFFSET ?3") {
                if let Ok(rows) = stmt.query_map(rusqlite::params![cat_pattern, limit as i64, offset as i64], |row| {
                    Ok(LawSectionDTO {
                        id: row.get(0)?, act_name: row.get(1)?, section_number: row.get(2)?, title: row.get(3)?,
                        description: row.get(4)?, category: row.get(5)?, punishment: row.get(6).ok(),
                        old_law_reference: row.get(7).ok(), keywords: row.get(8).ok(),
                    })
                }) {
                    for item in rows.flatten() { results.push(item); }
                }
            }
        } else if !q.is_empty() {
            if let Ok(mut c_stmt) = conn.prepare("SELECT count(*) FROM central_acts WHERE (LOWER(title) LIKE ?1 OR LOWER(description) LIKE ?1 OR LOWER(keywords) LIKE ?1 OR section_number = ?2)") {
                total = c_stmt.query_row(rusqlite::params![q_pattern, q], |r| r.get::<_, i64>(0)).unwrap_or(0);
            }
            if let Ok(mut stmt) = conn.prepare("SELECT id, act_name, section_number, title, description, category, punishment, old_law_reference, keywords FROM central_acts WHERE (LOWER(title) LIKE ?1 OR LOWER(description) LIKE ?1 OR LOWER(keywords) LIKE ?1 OR section_number = ?2) ORDER BY act_name ASC, CAST(section_number AS INTEGER) ASC LIMIT ?3 OFFSET ?4") {
                if let Ok(rows) = stmt.query_map(rusqlite::params![q_pattern, q, limit as i64, offset as i64], |row| {
                    Ok(LawSectionDTO {
                        id: row.get(0)?, act_name: row.get(1)?, section_number: row.get(2)?, title: row.get(3)?,
                        description: row.get(4)?, category: row.get(5)?, punishment: row.get(6).ok(),
                        old_law_reference: row.get(7).ok(), keywords: row.get(8).ok(),
                    })
                }) {
                    for item in rows.flatten() { results.push(item); }
                }
            }
        } else {
            if let Ok(mut c_stmt) = conn.prepare("SELECT count(*) FROM central_acts") {
                total = c_stmt.query_row([], |r| r.get::<_, i64>(0)).unwrap_or(0);
            }
            if let Ok(mut stmt) = conn.prepare("SELECT id, act_name, section_number, title, description, category, punishment, old_law_reference, keywords FROM central_acts ORDER BY act_name ASC, CAST(section_number AS INTEGER) ASC LIMIT ?1 OFFSET ?2") {
                if let Ok(rows) = stmt.query_map(rusqlite::params![limit as i64, offset as i64], |row| {
                    Ok(LawSectionDTO {
                        id: row.get(0)?, act_name: row.get(1)?, section_number: row.get(2)?, title: row.get(3)?,
                        description: row.get(4)?, category: row.get(5)?, punishment: row.get(6).ok(),
                        old_law_reference: row.get(7).ok(), keywords: row.get(8).ok(),
                    })
                }) {
                    for item in rows.flatten() { results.push(item); }
                }
            }
        }
    }

    let total_pages = if limit > 0 { (total as usize + limit - 1) / limit } else { 1 };

    Json(json!({
        "query": q,
        "category": if cat.is_empty() { None } else { Some(cat) },
        "act_name": if act.is_empty() { None } else { Some(act) },
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "results": results,
    }))
}

// 2. State Laws Search Handler - Ordered by State & Section Number
pub async fn search_state_laws_handler(
    State(state): State<Arc<AppState>>,
    Query(params): Query<SearchParams>,
) -> impl IntoResponse {
    let q = params.q.unwrap_or_default().trim().to_string();
    let state_filter = params.state_code.unwrap_or_default().trim().to_uppercase();
    let page = params.page.unwrap_or(1).max(1);
    let limit = params.limit.unwrap_or(30).min(200);
    let offset = (page - 1) * limit;

    let mut results: Vec<StateLawDTO> = Vec::new();
    let mut total: i64 = 0;
    let conn_guard = state.legal_db.get_conn().await;
    if let Some(conn) = conn_guard.as_ref() {
        let q_pattern = format!("%{}%", q.to_lowercase());
        
        if !state_filter.is_empty() && !q.is_empty() {
            if let Ok(mut c_stmt) = conn.prepare("SELECT count(*) FROM state_acts WHERE state_code = ?1 AND (LOWER(title) LIKE ?2 OR LOWER(keywords) LIKE ?2 OR LOWER(act_name) LIKE ?2)") {
                total = c_stmt.query_row(rusqlite::params![state_filter, q_pattern], |r| r.get::<_, i64>(0)).unwrap_or(0);
            }
            if let Ok(mut stmt) = conn.prepare("SELECT id, state_name, state_code, act_name, section_number, title, description, category, punishment, keywords FROM state_acts WHERE state_code = ?1 AND (LOWER(title) LIKE ?2 OR LOWER(keywords) LIKE ?2 OR LOWER(act_name) LIKE ?2) ORDER BY act_name ASC, CAST(section_number AS INTEGER) ASC LIMIT ?3 OFFSET ?4") {
                if let Ok(rows) = stmt.query_map(rusqlite::params![state_filter, q_pattern, limit as i64, offset as i64], |row| {
                    Ok(StateLawDTO {
                        id: row.get(0)?, state_name: row.get(1)?, state_code: row.get(2)?, act_name: row.get(3)?,
                        section_number: row.get(4)?, title: row.get(5)?, description: row.get(6)?, category: row.get(7)?,
                        punishment: row.get(8).ok(), keywords: row.get(9).ok(),
                    })
                }) {
                    for item in rows.flatten() { results.push(item); }
                }
            }
        } else if !state_filter.is_empty() {
            if let Ok(mut c_stmt) = conn.prepare("SELECT count(*) FROM state_acts WHERE state_code = ?1") {
                total = c_stmt.query_row(rusqlite::params![state_filter], |r| r.get::<_, i64>(0)).unwrap_or(0);
            }
            if let Ok(mut stmt) = conn.prepare("SELECT id, state_name, state_code, act_name, section_number, title, description, category, punishment, keywords FROM state_acts WHERE state_code = ?1 ORDER BY act_name ASC, CAST(section_number AS INTEGER) ASC LIMIT ?2 OFFSET ?3") {
                if let Ok(rows) = stmt.query_map(rusqlite::params![state_filter, limit as i64, offset as i64], |row| {
                    Ok(StateLawDTO {
                        id: row.get(0)?, state_name: row.get(1)?, state_code: row.get(2)?, act_name: row.get(3)?,
                        section_number: row.get(4)?, title: row.get(5)?, description: row.get(6)?, category: row.get(7)?,
                        punishment: row.get(8).ok(), keywords: row.get(9).ok(),
                    })
                }) {
                    for item in rows.flatten() { results.push(item); }
                }
            }
        } else if !q.is_empty() {
            if let Ok(mut c_stmt) = conn.prepare("SELECT count(*) FROM state_acts WHERE (LOWER(title) LIKE ?1 OR LOWER(keywords) LIKE ?1 OR LOWER(act_name) LIKE ?1 OR LOWER(state_name) LIKE ?1)") {
                total = c_stmt.query_row(rusqlite::params![q_pattern], |r| r.get::<_, i64>(0)).unwrap_or(0);
            }
            if let Ok(mut stmt) = conn.prepare("SELECT id, state_name, state_code, act_name, section_number, title, description, category, punishment, keywords FROM state_acts WHERE (LOWER(title) LIKE ?1 OR LOWER(keywords) LIKE ?1 OR LOWER(act_name) LIKE ?1 OR LOWER(state_name) LIKE ?1) ORDER BY state_name ASC, act_name ASC, CAST(section_number AS INTEGER) ASC LIMIT ?2 OFFSET ?3") {
                if let Ok(rows) = stmt.query_map(rusqlite::params![q_pattern, limit as i64, offset as i64], |row| {
                    Ok(StateLawDTO {
                        id: row.get(0)?, state_name: row.get(1)?, state_code: row.get(2)?, act_name: row.get(3)?,
                        section_number: row.get(4)?, title: row.get(5)?, description: row.get(6)?, category: row.get(7)?,
                        punishment: row.get(8).ok(), keywords: row.get(9).ok(),
                    })
                }) {
                    for item in rows.flatten() { results.push(item); }
                }
            }
        } else {
            if let Ok(mut c_stmt) = conn.prepare("SELECT count(*) FROM state_acts") {
                total = c_stmt.query_row([], |r| r.get::<_, i64>(0)).unwrap_or(0);
            }
            if let Ok(mut stmt) = conn.prepare("SELECT id, state_name, state_code, act_name, section_number, title, description, category, punishment, keywords FROM state_acts ORDER BY state_name ASC, act_name ASC, CAST(section_number AS INTEGER) ASC LIMIT ?1 OFFSET ?2") {
                if let Ok(rows) = stmt.query_map(rusqlite::params![limit as i64, offset as i64], |row| {
                    Ok(StateLawDTO {
                        id: row.get(0)?, state_name: row.get(1)?, state_code: row.get(2)?, act_name: row.get(3)?,
                        section_number: row.get(4)?, title: row.get(5)?, description: row.get(6)?, category: row.get(7)?,
                        punishment: row.get(8).ok(), keywords: row.get(9).ok(),
                    })
                }) {
                    for item in rows.flatten() { results.push(item); }
                }
            }
        }
    }

    let total_pages = if limit > 0 { (total as usize + limit - 1) / limit } else { 1 };
    Json(json!({ "query": q, "state_code": if state_filter.is_empty() { None } else { Some(state_filter) }, "page": page, "total": total, "total_pages": total_pages, "results": results }))
}

// 3. Supreme Court Judgments Handler - Ordered Chronologically (Year DESC)
pub async fn search_supreme_court_handler(
    State(state): State<Arc<AppState>>,
    Query(params): Query<SearchParams>,
) -> impl IntoResponse {
    let q = params.q.unwrap_or_default().trim().to_string();
    let page = params.page.unwrap_or(1).max(1);
    let limit = params.limit.unwrap_or(30).min(200);
    let offset = (page - 1) * limit;

    let mut results: Vec<SupremeCourtDTO> = Vec::new();
    let mut total: i64 = 0;
    let conn_guard = state.legal_db.get_conn().await;
    if let Some(conn) = conn_guard.as_ref() {
        let q_pattern = format!("%{}%", q.to_lowercase());
        
        if !q.is_empty() {
            if let Ok(mut c_stmt) = conn.prepare("SELECT count(*) FROM supreme_court_judgments WHERE (LOWER(case_name) LIKE ?1 OR LOWER(headnotes) LIKE ?1 OR LOWER(ratio_decidendi) LIKE ?1 OR LOWER(sections_referred) LIKE ?1 OR LOWER(citation) LIKE ?1)") {
                total = c_stmt.query_row(rusqlite::params![q_pattern], |r| r.get::<_, i64>(0)).unwrap_or(0);
            }
            if let Ok(mut stmt) = conn.prepare("SELECT id, case_name, citation, year, bench, headnotes, ratio_decidendi, sections_referred, verdict FROM supreme_court_judgments WHERE (LOWER(case_name) LIKE ?1 OR LOWER(headnotes) LIKE ?1 OR LOWER(ratio_decidendi) LIKE ?1 OR LOWER(sections_referred) LIKE ?1 OR LOWER(citation) LIKE ?1) ORDER BY year DESC, case_name ASC LIMIT ?2 OFFSET ?3") {
                if let Ok(rows) = stmt.query_map(rusqlite::params![q_pattern, limit as i64, offset as i64], |row| {
                    Ok(SupremeCourtDTO {
                        id: row.get(0)?, case_name: row.get(1)?, citation: row.get(2)?, year: row.get(3)?,
                        bench: row.get(4).ok(), headnotes: row.get(5).ok(), ratio_decidendi: row.get(6)?,
                        sections_referred: row.get(7).ok(), verdict: row.get(8).ok(),
                    })
                }) {
                    for item in rows.flatten() { results.push(item); }
                }
            }
        } else {
            if let Ok(mut c_stmt) = conn.prepare("SELECT count(*) FROM supreme_court_judgments") {
                total = c_stmt.query_row([], |r| r.get::<_, i64>(0)).unwrap_or(0);
            }
            if let Ok(mut stmt) = conn.prepare("SELECT id, case_name, citation, year, bench, headnotes, ratio_decidendi, sections_referred, verdict FROM supreme_court_judgments ORDER BY year DESC, case_name ASC LIMIT ?1 OFFSET ?2") {
                if let Ok(rows) = stmt.query_map(rusqlite::params![limit as i64, offset as i64], |row| {
                    Ok(SupremeCourtDTO {
                        id: row.get(0)?, case_name: row.get(1)?, citation: row.get(2)?, year: row.get(3)?,
                        bench: row.get(4).ok(), headnotes: row.get(5).ok(), ratio_decidendi: row.get(6)?,
                        sections_referred: row.get(7).ok(), verdict: row.get(8).ok(),
                    })
                }) {
                    for item in rows.flatten() { results.push(item); }
                }
            }
        }
    }

    let total_pages = if limit > 0 { (total as usize + limit - 1) / limit } else { 1 };
    Json(json!({ "query": q, "page": page, "total": total, "total_pages": total_pages, "results": results }))
}

// 4. 25 State High Courts Judgments Handler - Ordered Alphabetically by High Court Name
pub async fn search_high_courts_handler(
    State(state): State<Arc<AppState>>,
    Query(params): Query<SearchParams>,
) -> impl IntoResponse {
    let q = params.q.unwrap_or_default().trim().to_string();
    let court_filter = params.court_code.unwrap_or_default().trim().to_uppercase();
    let state_filter = params.state_code.unwrap_or_default().trim().to_uppercase();
    let page = params.page.unwrap_or(1).max(1);
    let limit = params.limit.unwrap_or(30).min(200);
    let offset = (page - 1) * limit;

    let mut results: Vec<HighCourtDTO> = Vec::new();
    let mut total: i64 = 0;
    let conn_guard = state.legal_db.get_conn().await;
    if let Some(conn) = conn_guard.as_ref() {
        let q_pattern = format!("%{}%", q.to_lowercase());
        
        if !court_filter.is_empty() && !q.is_empty() {
            if let Ok(mut c_stmt) = conn.prepare("SELECT count(*) FROM high_court_judgments WHERE court_code = ?1 AND (LOWER(case_name) LIKE ?2 OR LOWER(summary) LIKE ?2 OR LOWER(ratio_decidendi) LIKE ?2 OR LOWER(sections_referred) LIKE ?2)") {
                total = c_stmt.query_row(rusqlite::params![court_filter, q_pattern], |r| r.get::<_, i64>(0)).unwrap_or(0);
            }
            if let Ok(mut stmt) = conn.prepare("SELECT id, high_court_name, court_code, state_code, case_name, citation, year, bench, summary, ratio_decidendi, sections_referred, disposition FROM high_court_judgments WHERE court_code = ?1 AND (LOWER(case_name) LIKE ?2 OR LOWER(summary) LIKE ?2 OR LOWER(ratio_decidendi) LIKE ?2 OR LOWER(sections_referred) LIKE ?2) ORDER BY year DESC, case_name ASC LIMIT ?3 OFFSET ?4") {
                if let Ok(rows) = stmt.query_map(rusqlite::params![court_filter, q_pattern, limit as i64, offset as i64], |row| {
                    Ok(HighCourtDTO {
                        id: row.get(0)?, high_court_name: row.get(1)?, court_code: row.get(2)?, state_code: row.get(3)?,
                        case_name: row.get(4)?, citation: row.get(5)?, year: row.get(6)?, bench: row.get(7).ok(),
                        summary: row.get(8)?, ratio_decidendi: row.get(9)?, sections_referred: row.get(10).ok(),
                        disposition: row.get(11).ok(),
                    })
                }) {
                    for item in rows.flatten() { results.push(item); }
                }
            }
        } else if !court_filter.is_empty() {
            if let Ok(mut c_stmt) = conn.prepare("SELECT count(*) FROM high_court_judgments WHERE court_code = ?1") {
                total = c_stmt.query_row(rusqlite::params![court_filter], |r| r.get::<_, i64>(0)).unwrap_or(0);
            }
            if let Ok(mut stmt) = conn.prepare("SELECT id, high_court_name, court_code, state_code, case_name, citation, year, bench, summary, ratio_decidendi, sections_referred, disposition FROM high_court_judgments WHERE court_code = ?1 ORDER BY year DESC, case_name ASC LIMIT ?2 OFFSET ?3") {
                if let Ok(rows) = stmt.query_map(rusqlite::params![court_filter, limit as i64, offset as i64], |row| {
                    Ok(HighCourtDTO {
                        id: row.get(0)?, high_court_name: row.get(1)?, court_code: row.get(2)?, state_code: row.get(3)?,
                        case_name: row.get(4)?, citation: row.get(5)?, year: row.get(6)?, bench: row.get(7).ok(),
                        summary: row.get(8)?, ratio_decidendi: row.get(9)?, sections_referred: row.get(10).ok(),
                        disposition: row.get(11).ok(),
                    })
                }) {
                    for item in rows.flatten() { results.push(item); }
                }
            }
        } else if !state_filter.is_empty() {
            if let Ok(mut c_stmt) = conn.prepare("SELECT count(*) FROM high_court_judgments WHERE state_code = ?1") {
                total = c_stmt.query_row(rusqlite::params![state_filter], |r| r.get::<_, i64>(0)).unwrap_or(0);
            }
            if let Ok(mut stmt) = conn.prepare("SELECT id, high_court_name, court_code, state_code, case_name, citation, year, bench, summary, ratio_decidendi, sections_referred, disposition FROM high_court_judgments WHERE state_code = ?1 ORDER BY year DESC, case_name ASC LIMIT ?2 OFFSET ?3") {
                if let Ok(rows) = stmt.query_map(rusqlite::params![state_filter, limit as i64, offset as i64], |row| {
                    Ok(HighCourtDTO {
                        id: row.get(0)?, high_court_name: row.get(1)?, court_code: row.get(2)?, state_code: row.get(3)?,
                        case_name: row.get(4)?, citation: row.get(5)?, year: row.get(6)?, bench: row.get(7).ok(),
                        summary: row.get(8)?, ratio_decidendi: row.get(9)?, sections_referred: row.get(10).ok(),
                        disposition: row.get(11).ok(),
                    })
                }) {
                    for item in rows.flatten() { results.push(item); }
                }
            }
        } else if !q.is_empty() {
            if let Ok(mut c_stmt) = conn.prepare("SELECT count(*) FROM high_court_judgments WHERE (LOWER(case_name) LIKE ?1 OR LOWER(summary) LIKE ?1 OR LOWER(ratio_decidendi) LIKE ?1 OR LOWER(high_court_name) LIKE ?1 OR LOWER(sections_referred) LIKE ?1)") {
                total = c_stmt.query_row(rusqlite::params![q_pattern], |r| r.get::<_, i64>(0)).unwrap_or(0);
            }
            if let Ok(mut stmt) = conn.prepare("SELECT id, high_court_name, court_code, state_code, case_name, citation, year, bench, summary, ratio_decidendi, sections_referred, disposition FROM high_court_judgments WHERE (LOWER(case_name) LIKE ?1 OR LOWER(summary) LIKE ?1 OR LOWER(ratio_decidendi) LIKE ?1 OR LOWER(high_court_name) LIKE ?1 OR LOWER(sections_referred) LIKE ?1) ORDER BY high_court_name ASC, year DESC LIMIT ?2 OFFSET ?3") {
                if let Ok(rows) = stmt.query_map(rusqlite::params![q_pattern, limit as i64, offset as i64], |row| {
                    Ok(HighCourtDTO {
                        id: row.get(0)?, high_court_name: row.get(1)?, court_code: row.get(2)?, state_code: row.get(3)?,
                        case_name: row.get(4)?, citation: row.get(5)?, year: row.get(6)?, bench: row.get(7).ok(),
                        summary: row.get(8)?, ratio_decidendi: row.get(9)?, sections_referred: row.get(10).ok(),
                        disposition: row.get(11).ok(),
                    })
                }) {
                    for item in rows.flatten() { results.push(item); }
                }
            }
        } else {
            if let Ok(mut c_stmt) = conn.prepare("SELECT count(*) FROM high_court_judgments") {
                total = c_stmt.query_row([], |r| r.get::<_, i64>(0)).unwrap_or(0);
            }
            if let Ok(mut stmt) = conn.prepare("SELECT id, high_court_name, court_code, state_code, case_name, citation, year, bench, summary, ratio_decidendi, sections_referred, disposition FROM high_court_judgments ORDER BY high_court_name ASC, year DESC LIMIT ?1 OFFSET ?2") {
                if let Ok(rows) = stmt.query_map(rusqlite::params![limit as i64, offset as i64], |row| {
                    Ok(HighCourtDTO {
                        id: row.get(0)?, high_court_name: row.get(1)?, court_code: row.get(2)?, state_code: row.get(3)?,
                        case_name: row.get(4)?, citation: row.get(5)?, year: row.get(6)?, bench: row.get(7).ok(),
                        summary: row.get(8)?, ratio_decidendi: row.get(9)?, sections_referred: row.get(10).ok(),
                        disposition: row.get(11).ok(),
                    })
                }) {
                    for item in rows.flatten() { results.push(item); }
                }
            }
        }
    }

    let total_pages = if limit > 0 { (total as usize + limit - 1) / limit } else { 1 };
    Json(json!({ "query": q, "court_code": if court_filter.is_empty() { None } else { Some(court_filter) }, "page": page, "total": total, "total_pages": total_pages, "results": results }))
}

// 5. Enterprise Stats Handler
pub async fn get_enterprise_stats_handler(
    State(state): State<Arc<AppState>>,
) -> impl IntoResponse {
    let mut central_count = 0;
    let mut state_count = 0;
    let mut sc_count = 0;
    let mut hc_count = 0;

    let conn_guard = state.legal_db.get_conn().await;
    if let Some(conn) = conn_guard.as_ref() {
        if let Ok(mut stmt) = conn.prepare("SELECT count(*) FROM central_acts") {
            if let Ok(cnt) = stmt.query_row([], |r| r.get::<_, i64>(0)) { central_count = cnt; }
        }
        if let Ok(mut stmt) = conn.prepare("SELECT count(*) FROM state_acts") {
            if let Ok(cnt) = stmt.query_row([], |r| r.get::<_, i64>(0)) { state_count = cnt; }
        }
        if let Ok(mut stmt) = conn.prepare("SELECT count(*) FROM supreme_court_judgments") {
            if let Ok(cnt) = stmt.query_row([], |r| r.get::<_, i64>(0)) { sc_count = cnt; }
        }
        if let Ok(mut stmt) = conn.prepare("SELECT count(*) FROM high_court_judgments") {
            if let Ok(cnt) = stmt.query_row([], |r| r.get::<_, i64>(0)) { hc_count = cnt; }
        }
    }

    Json(json!({
        "central_acts_count": central_count,
        "state_acts_count": state_count,
        "supreme_court_count": sc_count,
        "high_courts_count": hc_count,
        "total_database_records": central_count + state_count + sc_count + hc_count
    }))
}

// 6. Acts Handler - Ranked by Importance & Size
pub async fn get_acts_handler(
    State(state): State<Arc<AppState>>,
) -> impl IntoResponse {
    let mut acts = Vec::new();
    let conn_guard = state.legal_db.get_conn().await;
    if let Some(conn) = conn_guard.as_ref() {
        if let Ok(mut stmt) = conn.prepare("SELECT act_name, count(*) FROM central_acts GROUP BY act_name ORDER BY count(*) DESC, act_name ASC") {
            let rows = stmt.query_map([], |row| {
                let name: String = row.get(0)?;
                let count: i64 = row.get(1)?;
                Ok(json!({ "act_name": name, "section_count": count }))
            });
            if let Ok(iter) = rows {
                for item in iter.flatten() { acts.push(item); }
            }
        }
    }
    Json(acts)
}

pub async fn get_categories_handler(
    State(state): State<Arc<AppState>>,
) -> impl IntoResponse {
    let mut categories = Vec::new();
    let conn_guard = state.legal_db.get_conn().await;
    if let Some(conn) = conn_guard.as_ref() {
        if let Ok(mut stmt) = conn.prepare("SELECT DISTINCT category FROM central_acts WHERE category IS NOT NULL ORDER BY category ASC") {
            let rows = stmt.query_map([], |row| {
                let cat: String = row.get(0)?;
                Ok(json!({ "name": cat, "slug": cat.to_lowercase().replace(' ', "_") }))
            });
            if let Ok(iter) = rows {
                for item in iter.flatten() { categories.push(item); }
            }
        }
    }
    Json(categories)
}
