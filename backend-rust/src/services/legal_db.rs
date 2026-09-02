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

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StateLawResult {
    pub id: i64,
    pub state_name: String,
    pub state_code: String,
    pub act_name: String,
    pub section_number: String,
    pub title: String,
    pub description: String,
    pub category: String,
    pub punishment: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CourtPrecedentResult {
    pub id: i64,
    pub court_name: String,
    pub court_type: String, // "Supreme Court" or "High Court"
    pub case_name: String,
    pub citation: String,
    pub year: i64,
    pub summary: String,
    pub ratio_decidendi: String,
    pub sections_referred: Option<String>,
    pub disposition: Option<String>,
}

#[derive(Debug, Clone, Default)]
pub struct UnifiedLegalSearchResult {
    pub central_laws: Vec<LawSectionResult>,
    pub state_laws: Vec<StateLawResult>,
    pub precedents: Vec<CourtPrecedentResult>,
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
                println!("📚 Enterprise Legal Database connected successfully: {}", db_path);
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

    pub async fn unified_search(
        &self,
        query: &str,
        state_hint: Option<&str>,
        limit: usize,
    ) -> UnifiedLegalSearchResult {
        let mut out = UnifiedLegalSearchResult::default();
        let conn_guard = self.conn.lock().await;
        let conn = match &*conn_guard {
            Some(c) => c,
            None => return out,
        };

        let clean_query = query.trim().to_lowercase();
        if clean_query.is_empty() {
            return out;
        }

        let words: Vec<&str> = clean_query
            .split_whitespace()
            .filter(|w| w.len() > 1 && !["the", "and", "for", "what", "how", "why", "with", "this", "that", "tell", "give", "please"].contains(w))
            .collect();

        // 1. Central Acts Search (Section numbers + Keywords)
        for word in &words {
            if word.chars().any(|c| c.is_ascii_digit()) {
                let sec_query = format!("%{}%", word);
                let mut stmt = match conn.prepare(
                    "SELECT id, act_name, section_number, title, description, category, punishment, old_law_reference 
                     FROM central_acts 
                     WHERE LOWER(section_number) = ?1 OR LOWER(section_number) LIKE ?2 OR LOWER(old_law_reference) LIKE ?2
                     LIMIT 4"
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
                        if !out.central_laws.iter().any(|x| x.id == item.id) {
                            out.central_laws.push(item);
                        }
                    }
                }
            }
        }

        if out.central_laws.len() < limit && !words.is_empty() {
            for word in &words {
                if out.central_laws.len() >= limit {
                    break;
                }
                let pattern = format!("%{}%", word);
                let mut stmt = match conn.prepare(
                    "SELECT id, act_name, section_number, title, description, category, punishment, old_law_reference 
                     FROM central_acts 
                     WHERE (LOWER(title) LIKE ?1 OR LOWER(keywords) LIKE ?1 OR LOWER(description) LIKE ?1 OR LOWER(act_name) LIKE ?1)
                     LIMIT ?2"
                ) {
                    Ok(s) => s,
                    Err(_) => continue,
                };

                let remaining = limit.saturating_sub(out.central_laws.len());
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
                        if !out.central_laws.iter().any(|x| x.id == item.id) {
                            out.central_laws.push(item);
                        }
                    }
                }
            }
        }

        // 2. State Acts Search (Telangana, AP, Delhi, Maharashtra, Karnataka, etc.)
        for word in &words {
            if out.state_laws.len() >= 3 {
                break;
            }
            let pattern = format!("%{}%", word);
            let mut stmt = match conn.prepare(
                "SELECT id, state_name, state_code, act_name, section_number, title, description, category, punishment 
                 FROM state_acts 
                 WHERE (LOWER(title) LIKE ?1 OR LOWER(keywords) LIKE ?1 OR LOWER(description) LIKE ?1 OR LOWER(act_name) LIKE ?1)
                 LIMIT 3"
            ) {
                Ok(s) => s,
                Err(_) => continue,
            };

            let rows = stmt.query_map(params![pattern], |row| {
                Ok(StateLawResult {
                    id: row.get(0)?,
                    state_name: row.get(1)?,
                    state_code: row.get(2)?,
                    act_name: row.get(3)?,
                    section_number: row.get(4)?,
                    title: row.get(5)?,
                    description: row.get(6)?,
                    category: row.get(7)?,
                    punishment: row.get(8).ok(),
                })
            });

            if let Ok(iter) = rows {
                for item in iter.flatten() {
                    if !out.state_laws.iter().any(|x| x.id == item.id) {
                        out.state_laws.push(item);
                    }
                }
            }
        }

        // 3. Supreme Court Precedents Search
        for word in &words {
            if out.precedents.len() >= 2 {
                break;
            }
            let pattern = format!("%{}%", word);
            let mut stmt = match conn.prepare(
                "SELECT id, case_name, citation, year, headnotes, ratio_decidendi, sections_referred, verdict 
                 FROM supreme_court_judgments 
                 WHERE (LOWER(case_name) LIKE ?1 OR LOWER(headnotes) LIKE ?1 OR LOWER(ratio_decidendi) LIKE ?1 OR LOWER(sections_referred) LIKE ?1)
                 LIMIT 2"
            ) {
                Ok(s) => s,
                Err(_) => continue,
            };

            let rows = stmt.query_map(params![pattern], |row| {
                Ok(CourtPrecedentResult {
                    id: row.get(0)?,
                    court_name: "Supreme Court of India".to_string(),
                    court_type: "Supreme Court".to_string(),
                    case_name: row.get(1)?,
                    citation: row.get(2)?,
                    year: row.get(3)?,
                    summary: row.get(4)?,
                    ratio_decidendi: row.get(5)?,
                    sections_referred: row.get(6).ok(),
                    disposition: row.get(7).ok(),
                })
            });

            if let Ok(iter) = rows {
                for item in iter.flatten() {
                    if !out.precedents.iter().any(|x| x.citation == item.citation) {
                        out.precedents.push(item);
                    }
                }
            }
        }

        // 4. 25 State High Courts Precedents Search
        for word in &words {
            if out.precedents.len() >= 4 {
                break;
            }
            let pattern = format!("%{}%", word);
            let mut stmt = match conn.prepare(
                "SELECT id, high_court_name, court_code, case_name, citation, year, summary, ratio_decidendi, sections_referred, disposition 
                 FROM high_court_judgments 
                 WHERE (LOWER(case_name) LIKE ?1 OR LOWER(summary) LIKE ?1 OR LOWER(ratio_decidendi) LIKE ?1 OR LOWER(sections_referred) LIKE ?1 OR LOWER(high_court_name) LIKE ?1)
                 LIMIT 2"
            ) {
                Ok(s) => s,
                Err(_) => continue,
            };

            let rows = stmt.query_map(params![pattern], |row| {
                Ok(CourtPrecedentResult {
                    id: row.get(0)?,
                    court_name: row.get(1)?,
                    court_type: "High Court".to_string(),
                    case_name: row.get(3)?,
                    citation: row.get(4)?,
                    year: row.get(5)?,
                    summary: row.get(6)?,
                    ratio_decidendi: row.get(7)?,
                    sections_referred: row.get(8).ok(),
                    disposition: row.get(9).ok(),
                })
            });

            if let Ok(iter) = rows {
                for item in iter.flatten() {
                    if !out.precedents.iter().any(|x| x.citation == item.citation) {
                        out.precedents.push(item);
                    }
                }
            }
        }

        out
    }

    // Retain search_laws backward compatibility
    pub async fn search_laws(&self, query: &str, limit: usize) -> Vec<LawSectionResult> {
        let result = self.unified_search(query, None, limit).await;
        result.central_laws
    }
}
