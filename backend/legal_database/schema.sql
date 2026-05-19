-- ═══════════════════════════════════════════════════════════════════════════
--  YAMA AI — Legal Database Schema (PostgreSQL)
-- ═══════════════════════════════════════════════════════════════════════════
--
--  This schema supports both PostgreSQL (production) and SQLite (dev).
--  Run against PostgreSQL:
--      psql -U postgres -d yama_ai -f schema.sql
--
--  Or let the Python store.py auto-create via SQLAlchemy.
-- ═══════════════════════════════════════════════════════════════════════════

-- ── Extensions (PostgreSQL only) ──
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";       -- trigram index for fuzzy search


-- ═══════════════════════════════════════════════════════════════════════════
--  1. PRIMARY TABLE: laws
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS laws (
    id                  SERIAL PRIMARY KEY,

    -- Core legal fields
    act_name            VARCHAR(500)  NOT NULL,
    section_number      VARCHAR(50)   NOT NULL,
    title               VARCHAR(1000) NOT NULL,
    description         TEXT          NOT NULL,
    keywords            TEXT,                           -- comma-separated

    -- Classification
    category            VARCHAR(100)  NOT NULL DEFAULT 'general',
    jurisdiction        VARCHAR(50)   NOT NULL DEFAULT 'central',  -- central / state
    state_name          VARCHAR(200),
    law_type            VARCHAR(100)  DEFAULT 'act',               -- act / article / rule / amendment / notification / judgment

    -- Source tracking
    source_url          VARCHAR(2000),
    content_hash        VARCHAR(64),                    -- SHA-256 for deduplication

    -- Supplementary
    punishment          TEXT,
    old_law_reference   VARCHAR(500),                   -- IPC ↔ BNS cross-reference

    -- Amendment tracking
    is_amended          BOOLEAN       DEFAULT FALSE,
    amendment_notes     TEXT,                            -- JSON array of amendment notes
    amendment_year      INTEGER,                         -- latest amendment year

    -- Status
    is_active           BOOLEAN       DEFAULT TRUE,

    -- Timestamps
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Unique constraint: one section per act
    CONSTRAINT uq_act_section UNIQUE (act_name, section_number)
);

-- ── Indexes for fast queries ──

CREATE INDEX IF NOT EXISTS idx_laws_act_name
    ON laws (act_name);

CREATE INDEX IF NOT EXISTS idx_laws_category
    ON laws (category);

CREATE INDEX IF NOT EXISTS idx_laws_jurisdiction
    ON laws (jurisdiction);

CREATE INDEX IF NOT EXISTS idx_laws_state_name
    ON laws (state_name)
    WHERE state_name IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_laws_law_type
    ON laws (law_type);

CREATE INDEX IF NOT EXISTS idx_laws_content_hash
    ON laws (content_hash);

CREATE INDEX IF NOT EXISTS idx_laws_is_active
    ON laws (is_active)
    WHERE is_active = TRUE;

-- Trigram index for full-text fuzzy search (PostgreSQL only)
CREATE INDEX IF NOT EXISTS idx_laws_title_trgm
    ON laws USING gin (title gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_laws_description_trgm
    ON laws USING gin (description gin_trgm_ops);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_laws_fts
    ON laws USING gin (
        to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
    );


-- ═══════════════════════════════════════════════════════════════════════════
--  2. LEGAL CATEGORIES (lookup table)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS legal_categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) UNIQUE NOT NULL,
    slug        VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

INSERT INTO legal_categories (name, slug, description) VALUES
    ('Criminal Law',      'criminal',      'Offences, punishment, bail, FIR, arrest'),
    ('Civil Law',         'civil',         'Contracts, torts, suits, decrees'),
    ('Constitutional',    'constitutional', 'Fundamental rights, directive principles, writs'),
    ('Consumer',          'consumer',      'Consumer rights, redressal, product liability'),
    ('Cyber Law',         'cyber',         'IT Act, electronic records, data protection'),
    ('Family Law',        'family',        'Marriage, divorce, maintenance, custody'),
    ('Motor Vehicle',     'motor_vehicle', 'Traffic, accidents, licensing, insurance'),
    ('Labour Law',        'labour',        'Employment, wages, trade unions, factories'),
    ('Property Law',      'property',      'Land, registration, transfer, tenancy'),
    ('Tax Law',           'tax',           'Income tax, GST, customs, excise'),
    ('Environmental',     'environmental', 'Pollution, forest, wildlife, green tribunal'),
    ('Corporate',         'corporate',     'Companies, SEBI, insolvency, securities')
ON CONFLICT (slug) DO NOTHING;


-- ═══════════════════════════════════════════════════════════════════════════
--  3. INGESTION LOG (audit trail for crawl runs)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS ingestion_logs (
    id                SERIAL PRIMARY KEY,
    source_name       VARCHAR(200) NOT NULL,
    run_type          VARCHAR(50)  NOT NULL,        -- full / incremental
    status            VARCHAR(50)  NOT NULL DEFAULT 'running',
    records_found     INTEGER      DEFAULT 0,
    records_inserted  INTEGER      DEFAULT 0,
    records_updated   INTEGER      DEFAULT 0,
    records_skipped   INTEGER      DEFAULT 0,
    error_message     TEXT,
    started_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at      TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_ingestion_source
    ON ingestion_logs (source_name);

CREATE INDEX IF NOT EXISTS idx_ingestion_status
    ON ingestion_logs (status);


-- ═══════════════════════════════════════════════════════════════════════════
--  4. CHAT SESSIONS & MESSAGES (user interaction history)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS chat_sessions (
    id          SERIAL PRIMARY KEY,
    session_id  VARCHAR(100) UNIQUE NOT NULL,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_session_id
    ON chat_sessions (session_id);

CREATE TABLE IF NOT EXISTS chat_messages (
    id          SERIAL PRIMARY KEY,
    session_id  INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role        VARCHAR(20) NOT NULL,               -- user / assistant
    content     TEXT NOT NULL,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ═══════════════════════════════════════════════════════════════════════════
--  5. HELPER FUNCTION: auto-update last_updated
-- ═══════════════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION update_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_laws_updated
    BEFORE UPDATE ON laws
    FOR EACH ROW
    EXECUTE FUNCTION update_last_updated();


-- ═══════════════════════════════════════════════════════════════════════════
--  6. VIEWS
-- ═══════════════════════════════════════════════════════════════════════════

-- Active laws summary by act
CREATE OR REPLACE VIEW v_laws_by_act AS
SELECT
    act_name,
    category,
    jurisdiction,
    state_name,
    COUNT(*)                         AS section_count,
    MIN(created_at)                  AS first_added,
    MAX(last_updated)                AS last_modified
FROM laws
WHERE is_active = TRUE
GROUP BY act_name, category, jurisdiction, state_name
ORDER BY act_name;

-- Laws statistics dashboard
CREATE OR REPLACE VIEW v_laws_stats AS
SELECT
    COUNT(*)                                        AS total_laws,
    COUNT(*) FILTER (WHERE jurisdiction = 'central') AS central_laws,
    COUNT(*) FILTER (WHERE jurisdiction = 'state')   AS state_laws,
    COUNT(*) FILTER (WHERE is_amended = TRUE)        AS amended_laws,
    COUNT(DISTINCT act_name)                         AS unique_acts,
    COUNT(DISTINCT category)                         AS categories_used
FROM laws
WHERE is_active = TRUE;
