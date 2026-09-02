"""
YAMA AI - Enterprise Ingestion Pipeline: Supreme Court Landmark Precedents
"""
import sqlite3

SC_JUDGMENTS_DATA = [
    {
        "case_name": "Lalita Kumari v. Government of U.P. & Ors.",
        "citation": "(2014) 2 SCC 1",
        "year": 2014,
        "bench": "Constitution Bench (P. Sathasivam, CJI)",
        "petitioner": "Lalita Kumari",
        "respondent": "Govt of Uttar Pradesh",
        "headnotes": "Mandatory Registration of FIR under Section 154 CrPC (Section 173 BNSS).",
        "ratio_decidendi": "Registration of FIR is mandatory under Section 154 CrPC if the information discloses the commission of a cognizable offence. Police officer cannot conduct preliminary inquiry before registering FIR in cognizable cases.",
        "sections_referred": "Section 154 CrPC, Section 173 BNSS, Article 21 Constitution",
        "verdict": "Directions Issued (Mandatory FIR)"
    },
    {
        "case_name": "Arnesh Kumar v. State of Bihar & Anr.",
        "citation": "(2014) 8 SCC 273",
        "year": 2014,
        "bench": "Chandramauli Kr. Prasad, Pinaki Chandra Ghose, JJ.",
        "petitioner": "Arnesh Kumar",
        "respondent": "State of Bihar",
        "headnotes": "Guidelines to prevent unnecessary arrests in offences punishable up to 7 years.",
        "ratio_decidendi": "No automatic arrest in cases punishable with imprisonment up to 7 years (Section 498A IPC / Section 85 BNS). Police must serve Section 41A CrPC (Section 35 BNSS) notice of appearance before making an arrest.",
        "sections_referred": "Section 41, 41A CrPC, Section 35 BNSS, Section 498A IPC",
        "verdict": "Bail Granted & National Arrest Guidelines Mandated"
    },
    {
        "case_name": "D.K. Basu v. State of West Bengal",
        "citation": "(1997) 1 SCC 416",
        "year": 1997,
        "bench": "Kuldip Singh, A.S. Anand, JJ.",
        "petitioner": "D.K. Basu",
        "respondent": "State of West Bengal",
        "headnotes": "Custodial Violence & Fundamental Rights of Arrested Persons.",
        "ratio_decidendi": "Arrested person has the right to have a friend or relative informed immediately of arrest, right to medical examination every 48 hours, and right to meet advocate during interrogation.",
        "sections_referred": "Article 21, Article 22 Constitution, Section 50, 54 CrPC",
        "verdict": "Landmark Arrest Guidelines Formulated"
    },
    {
        "case_name": "Justice K.S. Puttaswamy (Retd.) v. Union of India",
        "citation": "(2017) 10 SCC 1",
        "year": 2017,
        "bench": "9-Judge Constitution Bench",
        "petitioner": "Justice K.S. Puttaswamy",
        "respondent": "Union of India",
        "headnotes": "Right to Privacy as a Fundamental Right under Article 21.",
        "ratio_decidendi": "Right to privacy is protected as an intrinsic part of the right to life and personal liberty under Article 21 and as part of the freedoms guaranteed by Part III of the Constitution. Digital data, communications, and personal choices are legally protected.",
        "sections_referred": "Article 21, Article 14, Article 19 Constitution, IT Act 2000",
        "verdict": "Unanimously Affirmed Fundamental Right to Privacy"
    },
    {
        "case_name": "Dashrath Rupsingh Rathod v. State of Maharashtra",
        "citation": "(2014) 9 SCC 129",
        "year": 2014,
        "bench": "T.S. Thakur, Vikramajit Sen, C. Nagappan, JJ.",
        "petitioner": "Dashrath Rupsingh Rathod",
        "respondent": "State of Maharashtra",
        "headnotes": "Territorial Jurisdiction in Cheque Bounce Cases under Section 138 NI Act.",
        "ratio_decidendi": "Section 138 Negotiable Instruments Act complaint must be filed in the court within whose local jurisdiction the branch of the bank where the payee maintains the account is situated (as amended in NI Act Section 142(2)).",
        "sections_referred": "Section 138, 142 Negotiable Instruments Act 1881",
        "verdict": "Jurisdiction Standardized for Cheque Bounce"
    },
    {
        "case_name": "Satender Kumar Antil v. Central Bureau of Investigation",
        "citation": "(2022) 10 SCC 51",
        "year": 2022,
        "bench": "Sanjay Kishan Kaul, M.M. Sundresh, JJ.",
        "petitioner": "Satender Kumar Antil",
        "respondent": "CBI & Ors.",
        "headnotes": "Bail Reforms & Categorization of Offences for Grant of Bail.",
        "ratio_decidendi": "Bail is the rule and jail is the exception. Courts should not routinely remand accused to custody if they cooperated with investigation and offences are punishable under 7 years.",
        "sections_referred": "Section 436, 437, 438, 439 CrPC, Section 479, 480, 482 BNSS",
        "verdict": "Comprehensive Bail Guidelines"
    }
]

def ingest_supreme_court():
    conn = sqlite3.connect("backend/yama_ai.db")
    cursor = conn.cursor()

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

    # Populate FTS5 index
    cursor.execute("DELETE FROM sc_judgments_fts;")
    cursor.execute("""
        INSERT INTO sc_judgments_fts (rowid, case_name, citation, bench, headnotes, ratio_decidendi, sections_referred)
        SELECT id, case_name, citation, bench, headnotes, ratio_decidendi, sections_referred
        FROM supreme_court_judgments;
    """)

    conn.commit()
    cursor.execute("SELECT count(*) FROM supreme_court_judgments;")
    count = cursor.fetchone()[0]
    print(f"✅ Supreme Court Precedents Ingested: {count} cases indexed in FTS5.")
    conn.close()

if __name__ == "__main__":
    ingest_supreme_court()
