"""
YAMA AI - Master Enterprise Legal Ingestion Orchestrator
Populates Central Acts, State Acts, Supreme Court & 25 High Courts.
"""
import sqlite3
import os

from ingest_state_acts import STATE_ACTS_DATA
from ingest_supreme_court import SC_JUDGMENTS_DATA
from ingest_25_high_courts import HIGH_COURT_JUDGMENTS_DATA

def run_master_ingestion():
    db_path = "backend/yama_ai.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. CENTRAL ACTS - Copy from existing law_sections
    cursor.execute("""
        INSERT OR IGNORE INTO central_acts (
            id, act_name, act_year, section_number, title, description,
            category, punishment, old_law_reference, keywords, source_url
        )
        SELECT 
            id, act_name, 2023, section_number, title, description,
            category, punishment, old_law_reference, keywords, source_url
        FROM law_sections;
    """)
    conn.commit()

    # 2. STATE ACTS
    for item in STATE_ACTS_DATA:
        cursor.execute("""
            INSERT OR REPLACE INTO state_acts (
                state_name, state_code, act_name, act_year, section_number,
                title, description, category, punishment, keywords
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            item["state_name"], item["state_code"], item["act_name"], item["act_year"], item["section_number"],
            item["title"], item["description"], item["category"], item["punishment"], item["keywords"]
        ))
    conn.commit()

    # 3. SUPREME COURT PRECEDENTS
    for item in SC_JUDGMENTS_DATA:
        cursor.execute("""
            INSERT OR REPLACE INTO supreme_court_judgments (
                case_name, citation, year, bench, petitioner, respondent,
                headnotes, ratio_decidendi, sections_referred, verdict
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            item["case_name"], item["citation"], item["year"], item["bench"], item["petitioner"], item["respondent"],
            item["headnotes"], item["ratio_decidendi"], item["sections_referred"], item["verdict"]
        ))
    conn.commit()

    # 4. 25 HIGH COURTS PRECEDENTS
    for item in HIGH_COURT_JUDGMENTS_DATA:
        cursor.execute("""
            INSERT OR REPLACE INTO high_court_judgments (
                high_court_name, court_code, state_code, case_name, citation,
                year, bench, petitioner, respondent, summary, ratio_decidendi,
                sections_referred, disposition
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            item["high_court_name"], item["court_code"], item["state_code"], item["case_name"], item["citation"],
            item["year"], item["bench"], item["petitioner"], item["respondent"], item["summary"],
            item["ratio_decidendi"], item["sections_referred"], item["disposition"]
        ))
    conn.commit()

    # Rebuild FTS5 indices safely
    try:
        cursor.execute("INSERT INTO central_acts_fts(central_acts_fts) VALUES('rebuild');")
        cursor.execute("INSERT INTO state_acts_fts(state_acts_fts) VALUES('rebuild');")
        cursor.execute("INSERT INTO sc_judgments_fts(sc_judgments_fts) VALUES('rebuild');")
        cursor.execute("INSERT INTO hc_judgments_fts(hc_judgments_fts) VALUES('rebuild');")
        conn.commit()
    except Exception as e:
        print("[Note] FTS5 rebuild status:", e)

    # Summary report
    cursor.execute("SELECT count(*) FROM central_acts;")
    ca_cnt = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM state_acts;")
    sa_cnt = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM supreme_court_judgments;")
    sc_cnt = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM high_court_judgments;")
    hc_cnt = cursor.fetchone()[0]

    print("==================================================")
    print("       YAMA AI ENTERPRISE INGESTION COMPLETE      ")
    print("==================================================")
    print(f"[+] Central Acts Indexed        : {ca_cnt} sections")
    print(f"[+] State Acts Indexed          : {sa_cnt} state statutes")
    print(f"[+] Supreme Court Precedents    : {sc_cnt} landmark rulings")
    print(f"[+] 25 High Courts Precedents   : {hc_cnt} High Court judgments")
    print("==================================================")

    conn.close()

if __name__ == "__main__":
    run_master_ingestion()
