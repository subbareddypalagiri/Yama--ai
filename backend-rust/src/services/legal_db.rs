use rusqlite::{Connection, OpenFlags, params};
use serde::{Deserialize, Serialize};
use std::path::Path;
use tokio::sync::Mutex;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LawSectionResult {
    pub id: i64,
    pub act_name: String,
    pub section_number: String,
    pub title: String,
    pub description: String,
    pub category: String,
    pub punishment: Option<String>,
    pub old_law_reference: Option<String>,
}

pub struct LegalDatabase {
    pub db_path: String,
    conn: Mutex<Option<Connection>>,
}

impl LegalDatabase {
    pub fn new() -> Self {
        let candidate_paths = [
            "../backend/yama_ai.db",
            "backend/yama_ai.db",
            "yama_ai.db",
        ];

        let mut db_path = "../backend/yama_ai.db".to_string();
        for p in candidate_paths {
            if Path::new(p).exists() {
                db_path = p.to_string();
                break;
            }
        }

        let conn = match Connection::open_with_flags(
            &db_path,
            OpenFlags::SQLITE_OPEN_READ_ONLY | OpenFlags::SQLITE_OPEN_NO_MUTEX,
        ) {
            Ok(c) => {
                println!("📚 Legal Database connected successfully: {}", db_path);
                Some(c)
            }
            Err(e) => {
                eprintln!("⚠️ Warning: Could not open legal database at {}: {}", db_path, e);
                None
            }
        };

        Self {
            db_path,
            conn: Mutex::new(conn),
        }
    }

    pub async fn search_laws(&self, query: &str, limit: usize) -> Vec<LawSectionResult> {
        let conn_guard = self.conn.lock().await;
        let conn = match &*conn_guard {
            Some(c) => c,
            None => return Vec::new(),
        };

        let clean_query = query.trim().to_lowercase();
        if clean_query.is_empty() {
            return Vec::new();
        }

        let words: Vec<&str> = clean_query
            .split_whitespace()
            .filter(|w| w.len() > 1 && !["the", "and", "for", "what", "how", "why", "with", "this", "that", "tell", "give", "please"].contains(w))
            .collect();

        let mut results = Vec::new();
        let mut seen_ids = std::collections::HashSet::new();

        for word in &words {
            if word.chars().any(|c| c.is_ascii_digit()) {
                let sec_query = format!("%{}%", word);
                let mut stmt = match conn.prepare(
                    "SELECT id, act_name, section_number, title, description, category, punishment, old_law_reference 
                     FROM law_sections 
                     WHERE LOWER(section_number) = ?1 OR LOWER(section_number) LIKE ?2 OR LOWER(old_law_reference) LIKE ?2
                     LIMIT 5"
                ) {
                    Ok(s) => s,
                    Err(_) => continue,
                };

                let rows = stmt.query_map(params![word, sec_query], |row| {
                    Ok(LawSectionResult {
                        id: row.get(0)?,
                        act_name: row.get(1)?,
                        section_number: row.get(2)?,
                        title: row.get(3)?,
                        description: row.get(4)?,
                        category: row.get(5)?,
                        punishment: row.get(6).ok(),
                        old_law_reference: row.get(7).ok(),
                    })
                });

                if let Ok(iter) = rows {
                    for item in iter.flatten() {
                        if seen_ids.insert(item.id) {
                            results.push(item);
                        }
                    }
                }
            }
        }

        if results.len() < limit && !words.is_empty() {
            for word in &words {
                if results.len() >= limit {
                    break;
                }
                let pattern = format!("%{}%", word);
                let mut stmt = match conn.prepare(
                    "SELECT id, act_name, section_number, title, description, category, punishment, old_law_reference 
                     FROM law_sections 
                     WHERE (LOWER(title) LIKE ?1 OR LOWER(keywords) LIKE ?1 OR LOWER(description) LIKE ?1 OR LOWER(act_name) LIKE ?1)
                     LIMIT ?2"
                ) {
                    Ok(s) => s,
                    Err(_) => continue,
                };

                let remaining = limit.saturating_sub(results.len());
                let rows = stmt.query_map(params![pattern, remaining as i64], |row| {
                    Ok(LawSectionResult {
                        id: row.get(0)?,
                        act_name: row.get(1)?,
                        section_number: row.get(2)?,
                        title: row.get(3)?,
                        description: row.get(4)?,
                        category: row.get(5)?,
                        punishment: row.get(6).ok(),
                        old_law_reference: row.get(7).ok(),
                    })
                });

                if let Ok(iter) = rows {
                    for item in iter.flatten() {
                        if seen_ids.insert(item.id) {
                            results.push(item);
                        }
                    }
                }
            }
        }

        results
    }
}
