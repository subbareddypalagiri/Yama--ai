"""
YAMA AI - Enterprise Ingestion Pipeline: Central Acts (Union Bare Acts)
"""
import sqlite3
import json
from datetime import datetime

def ingest_central_acts():
    conn = sqlite3.connect("backend/yama_ai.db")
    cursor = conn.cursor()

    # Migrate legacy law_sections into central_acts if not already populated
    cursor.execute("""
        INSERT OR IGNORE INTO central_acts (
            id, act_name, act_year, section_number, title, description,
            category, punishment, old_law_reference, keywords, source_url
        )
        SELECT 
            id, act_name, 2023, section_number, title, description,
            category, punishment, old_law_reference, keywords, source_url
        FROM law_sections
        WHERE jurisdiction = 'Central' OR jurisdiction IS NULL OR jurisdiction = 'Union';
    """)

    # Populate FTS5 index
    cursor.execute("DELETE FROM central_acts_fts;")
    cursor.execute("""
        INSERT INTO central_acts_fts (rowid, act_name, section_number, title, description, category, punishment, old_law_reference, keywords)
        SELECT id, act_name, section_number, title, description, category, punishment, old_law_reference, keywords
        FROM central_acts;
    """)

    conn.commit()
    cursor.execute("SELECT count(*) FROM central_acts;")
    count = cursor.fetchone()[0]
    print(f"✅ Central Acts Ingested: {count} sections indexed in FTS5.")
    conn.close()

if __name__ == "__main__":
    ingest_central_acts()
