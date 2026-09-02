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

pub async fn search_laws_handler(
    State(state): State<Arc<AppState>>,
    Query(params): Query<SearchParams>,
) -> impl IntoResponse {
    let q = params.q.unwrap_or_default().trim().to_string();
    let cat = params.category.unwrap_or_default().trim().to_string();
    let limit = params.limit.unwrap_or(20).min(100);

    let unified = state.legal_db.unified_search(&q, None, limit).await;
    
    let mut results: Vec<LawSectionDTO> = unified.central_laws.into_iter().map(|l| LawSectionDTO {
        id: l.id,
        act_name: l.act_name,
        section_number: l.section_number,
        title: l.title,
        description: l.description,
        category: l.category,
        punishment: l.punishment,
        old_law_reference: l.old_law_reference,
        keywords: None,
    }).collect();

    // If query is empty or gave few results, load default sections
    if results.is_empty() && q.is_empty() {
        let conn_guard = state.legal_db.get_conn().await;
        if let Some(conn) = conn_guard.as_ref() {
            if !cat.is_empty() {
                let cat_pattern = format!("%{}%", cat.to_lowercase());
                if let Ok(mut stmt) = conn.prepare(
                    "SELECT id, act_name, section_number, title, description, category, punishment, old_law_reference, keywords 
                     FROM central_acts 
                     WHERE LOWER(category) LIKE ?1 
                     LIMIT ?2"
                ) {
                    if let Ok(rows) = stmt.query_map(rusqlite::params![cat_pattern, limit as i64], |row| {
                        Ok(LawSectionDTO {
                            id: row.get(0)?,
                            act_name: row.get(1)?,
                            section_number: row.get(2)?,
                            title: row.get(3)?,
                            description: row.get(4)?,
                            category: row.get(5)?,
                            punishment: row.get(6).ok(),
                            old_law_reference: row.get(7).ok(),
                            keywords: row.get(8).ok(),
                        })
                    }) {
                        for item in rows.flatten() {
                            results.push(item);
                        }
                    }
                }
            } else {
                if let Ok(mut stmt) = conn.prepare(
                    "SELECT id, act_name, section_number, title, description, category, punishment, old_law_reference, keywords 
                     FROM central_acts 
                     LIMIT ?1"
                ) {
                    if let Ok(rows) = stmt.query_map(rusqlite::params![limit as i64], |row| {
                        Ok(LawSectionDTO {
                            id: row.get(0)?,
                            act_name: row.get(1)?,
                            section_number: row.get(2)?,
                            title: row.get(3)?,
                            description: row.get(4)?,
                            category: row.get(5)?,
                            punishment: row.get(6).ok(),
                            old_law_reference: row.get(7).ok(),
                            keywords: row.get(8).ok(),
                        })
                    }) {
                        for item in rows.flatten() {
                            results.push(item);
                        }
                    }
                }
            }
        }
    }

    let total = results.len();
    Json(json!({
        "query": q,
        "category": if cat.is_empty() { None } else { Some(cat) },
        "total": total,
        "results": results,
    }))
}

pub async fn get_acts_handler(
    State(state): State<Arc<AppState>>,
) -> impl IntoResponse {
    let mut acts = Vec::new();
    let conn_guard = state.legal_db.get_conn().await;
    if let Some(conn) = conn_guard.as_ref() {
        if let Ok(mut stmt) = conn.prepare("SELECT act_name, count(*) FROM central_acts GROUP BY act_name ORDER BY count(*) DESC") {
            let rows = stmt.query_map([], |row| {
                let name: String = row.get(0)?;
                let count: i64 = row.get(1)?;
                Ok(json!({
                    "act_name": name,
                    "section_count": count
                }))
            });
            if let Ok(iter) = rows {
                for item in iter.flatten() {
                    acts.push(item);
                }
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
        if let Ok(mut stmt) = conn.prepare("SELECT DISTINCT category FROM central_acts WHERE category IS NOT NULL ORDER BY category") {
            let rows = stmt.query_map([], |row| {
                let cat: String = row.get(0)?;
                Ok(json!({ "name": cat, "slug": cat.to_lowercase().replace(' ', "_") }))
            });
            if let Ok(iter) = rows {
                for item in iter.flatten() {
                    categories.push(item);
                }
            }
        }
    }
    Json(categories)
}
