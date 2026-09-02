-- ====================================================================
-- YAMA AI: Enterprise Indian Legal Database Schema
-- Multi-Tier Partitioned Architecture for Central Acts, State Acts,
-- Supreme Court Precedents & 25 State High Courts
-- ====================================================================

-- 1. CENTRAL ACTS (All 850+ Union Bare Acts & New Criminal Codes)
CREATE TABLE IF NOT EXISTS central_acts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    act_name VARCHAR(500) NOT NULL,
    act_year INTEGER,
    act_number VARCHAR(100),
    section_number VARCHAR(50) NOT NULL,
    title VARCHAR(1000) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    punishment TEXT,
    bailable_status VARCHAR(50),
    cognizable_status VARCHAR(50),
    compoundable_status VARCHAR(50),
    old_law_reference VARCHAR(500),
    keywords TEXT,
    source_url VARCHAR(2000),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_central_acts_sec ON central_acts(act_name, section_number);
CREATE INDEX IF NOT EXISTS idx_central_acts_cat ON central_acts(category);
CREATE INDEX IF NOT EXISTS idx_central_acts_old ON central_acts(old_law_reference);

-- 2. STATE ACTS (28 States & 8 Union Territories)
CREATE TABLE IF NOT EXISTS state_acts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state_name VARCHAR(200) NOT NULL,
    state_code VARCHAR(10) NOT NULL, -- e.g. TG, AP, MH, DL, KA, TN, KL, WB, UP
    act_name VARCHAR(500) NOT NULL,
    act_year INTEGER,
    section_number VARCHAR(50) NOT NULL,
    title VARCHAR(1000) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    punishment TEXT,
    keywords TEXT,
    source_url VARCHAR(2000),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_state_acts_state ON state_acts(state_code, act_name);
CREATE INDEX IF NOT EXISTS idx_state_acts_sec ON state_acts(section_number);

-- 3. SUPREME COURT JUDGMENTS (1950 - 2026 Landmark Precedents)
CREATE TABLE IF NOT EXISTS supreme_court_judgments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_name VARCHAR(500) NOT NULL,
    citation VARCHAR(250) NOT NULL,
    year INTEGER NOT NULL,
    bench VARCHAR(500),
    judgment_date VARCHAR(50),
    petitioner VARCHAR(500),
    respondent VARCHAR(500),
    headnotes TEXT,
    ratio_decidendi TEXT NOT NULL,
    sections_referred TEXT,
    verdict VARCHAR(100), -- Allowed, Dismissed, Disposed, Quashed
    is_landmark BOOLEAN DEFAULT 1,
    source_url VARCHAR(2000),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sc_year ON supreme_court_judgments(year);
CREATE INDEX IF NOT EXISTS idx_sc_citation ON supreme_court_judgments(citation);
CREATE INDEX IF NOT EXISTS idx_sc_case ON supreme_court_judgments(case_name);

-- 4. 25 HIGH COURTS JUDGMENTS (Partitioned by Court)
CREATE TABLE IF NOT EXISTS high_court_judgments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    high_court_name VARCHAR(250) NOT NULL, -- e.g. High Court of Telangana, High Court of Delhi, Bombay High Court
    court_code VARCHAR(20) NOT NULL,       -- e.g. HCTG, HCAP, HCDL, HCMH, HCMDS, HCCAL, HCALL
    state_code VARCHAR(10) NOT NULL,       -- e.g. TG, AP, DL, MH, TN, WB, UP
    case_name VARCHAR(500) NOT NULL,
    citation VARCHAR(250) NOT NULL,
    year INTEGER NOT NULL,
    bench VARCHAR(500),
    judgment_date VARCHAR(50),
    petitioner VARCHAR(500),
    respondent VARCHAR(500),
    summary TEXT NOT NULL,
    ratio_decidendi TEXT NOT NULL,
    sections_referred TEXT,
    disposition VARCHAR(100),              -- Quashed, Bail Granted, Injunction Granted, Dismissed
    source_url VARCHAR(2000),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_hc_code ON high_court_judgments(court_code, year);
CREATE INDEX IF NOT EXISTS idx_hc_state ON high_court_judgments(state_code);
CREATE INDEX IF NOT EXISTS idx_hc_citation ON high_court_judgments(citation);
CREATE INDEX IF NOT EXISTS idx_hc_case ON high_court_judgments(case_name);

-- 5. FULL-TEXT SEARCH (FTS5) VIRTUAL TABLES FOR SUB-5MS RETRIEVAL
CREATE VIRTUAL TABLE IF NOT EXISTS central_acts_fts USING fts5(
    act_name, section_number, title, description, category, punishment, old_law_reference, keywords,
    content='central_acts', content_rowid='id'
);

CREATE VIRTUAL TABLE IF NOT EXISTS state_acts_fts USING fts5(
    state_name, state_code, act_name, section_number, title, description, category, keywords,
    content='state_acts', content_rowid='id'
);

CREATE VIRTUAL TABLE IF NOT EXISTS sc_judgments_fts USING fts5(
    case_name, citation, bench, headnotes, ratio_decidendi, sections_referred,
    content='supreme_court_judgments', content_rowid='id'
);

CREATE VIRTUAL TABLE IF NOT EXISTS hc_judgments_fts USING fts5(
    high_court_name, court_code, state_code, case_name, citation, summary, ratio_decidendi, sections_referred,
    content='high_court_judgments', content_rowid='id'
);
