"""
YAMA AI - Enterprise Bulk Ingestion: Supreme Court Landmark Precedents (1950 - 2026)
Covering Constitutional, Criminal, Financial, Tenancy, Consumer, Privacy & Corporate Precedents.
"""
import sqlite3

SC_EXPANDED_DATA = [
    # 1. Mandatory FIR & Criminal Procedure
    {
        "case_name": "Lalita Kumari v. Government of U.P. & Ors.",
        "citation": "(2014) 2 SCC 1", "year": 2014, "bench": "Constitution Bench (P. Sathasivam, CJI)",
        "petitioner": "Lalita Kumari", "respondent": "Govt of Uttar Pradesh",
        "headnotes": "Mandatory Registration of FIR under Section 154 CrPC (Section 173 BNSS).",
        "ratio_decidendi": "Registration of FIR is mandatory under Section 154 CrPC if information discloses a cognizable offence. Police officer cannot conduct preliminary inquiry before registering FIR.",
        "sections_referred": "Section 154 CrPC, Section 173 BNSS, Article 21 Constitution",
        "verdict": "Directions Issued (Mandatory FIR)"
    },
    # 2. Arrest Safeguards & Notice of Appearance
    {
        "case_name": "Arnesh Kumar v. State of Bihar & Anr.",
        "citation": "(2014) 8 SCC 273", "year": 2014, "bench": "Chandramauli Kr. Prasad, Pinaki Chandra Ghose, JJ.",
        "petitioner": "Arnesh Kumar", "respondent": "State of Bihar",
        "headnotes": "Guidelines to prevent unnecessary arrests in offences punishable up to 7 years.",
        "ratio_decidendi": "No automatic arrest in cases punishable with imprisonment up to 7 years. Police must serve Section 41A CrPC (Section 35 BNSS) notice of appearance before arrest.",
        "sections_referred": "Section 41, 41A CrPC, Section 35 BNSS, Section 498A IPC",
        "verdict": "National Arrest Guidelines Mandated"
    },
    # 3. Custodial Rights
    {
        "case_name": "D.K. Basu v. State of West Bengal",
        "citation": "(1997) 1 SCC 416", "year": 1997, "bench": "Kuldip Singh, A.S. Anand, JJ.",
        "petitioner": "D.K. Basu", "respondent": "State of West Bengal",
        "headnotes": "Custodial Violence & Fundamental Rights of Arrested Persons.",
        "ratio_decidendi": "Arrested person has the right to have a relative informed immediately, right to medical examination every 48 hours, and right to meet advocate during interrogation.",
        "sections_referred": "Article 21, Article 22 Constitution, Section 50, 54 CrPC",
        "verdict": "Landmark Arrest Guidelines Formulated"
    },
    # 4. Right to Privacy & Digital Freedom
    {
        "case_name": "Justice K.S. Puttaswamy (Retd.) v. Union of India",
        "citation": "(2017) 10 SCC 1", "year": 2017, "bench": "9-Judge Constitution Bench",
        "petitioner": "Justice K.S. Puttaswamy", "respondent": "Union of India",
        "headnotes": "Right to Privacy as a Fundamental Right under Article 21.",
        "ratio_decidendi": "Right to privacy is protected as an intrinsic part of the right to life and personal liberty under Article 21. Personal data, surveillance safeguards, and digital choices are protected.",
        "sections_referred": "Article 21, Article 14, Article 19 Constitution, IT Act 2000",
        "verdict": "Unanimously Affirmed Fundamental Right to Privacy"
    },
    # 5. Cheque Bounce Territorial Jurisdiction
    {
        "case_name": "Dashrath Rupsingh Rathod v. State of Maharashtra",
        "citation": "(2014) 9 SCC 129", "year": 2014, "bench": "T.S. Thakur, Vikramajit Sen, JJ.",
        "petitioner": "Dashrath Rupsingh Rathod", "respondent": "State of Maharashtra",
        "headnotes": "Territorial Jurisdiction in Cheque Bounce Cases under Section 138 NI Act.",
        "ratio_decidendi": "Section 138 NI Act complaint must be filed in the court within whose local jurisdiction the bank branch where the payee maintains the account is located.",
        "sections_referred": "Section 138, 142 Negotiable Instruments Act 1881",
        "verdict": "Jurisdiction Standardized for Cheque Bounce"
    },
    # 6. Cheque Bounce Presumption & Signed Cheques
    {
        "case_name": "Bir Singh v. Mukesh Kumar",
        "citation": "(2019) 4 SCC 197", "year": 2019, "bench": "R. Banumathi, Indira Banerjee, JJ.",
        "petitioner": "Bir Singh", "respondent": "Mukesh Kumar",
        "headnotes": "Statutory Presumption under Section 139 NI Act for Signed Cheques.",
        "ratio_decidendi": "Even if a blank cheque is voluntarily signed and handed over to payee, statutory presumption under Section 139 NI Act applies that it was issued in discharge of legally enforceable debt.",
        "sections_referred": "Section 118, 138, 139 Negotiable Instruments Act 1881",
        "verdict": "Conviction under Sec 138 Upheld"
    },
    # 7. Bail Reforms & Categorization
    {
        "case_name": "Satender Kumar Antil v. Central Bureau of Investigation",
        "citation": "(2022) 10 SCC 51", "year": 2022, "bench": "Sanjay Kishan Kaul, M.M. Sundresh, JJ.",
        "petitioner": "Satender Kumar Antil", "respondent": "CBI & Ors.",
        "headnotes": "Bail Reforms & Categorization of Offences for Grant of Bail.",
        "ratio_decidendi": "Bail is the rule and jail is the exception. Courts should not routinely remand accused to custody if they cooperated with investigation.",
        "sections_referred": "Section 436, 437, 438, 439 CrPC, Section 479, 480, 482 BNSS",
        "verdict": "Comprehensive Bail Guidelines"
    },
    # 8. Digital Evidence & Electronic Records
    {
        "case_name": "Arjun Panditrao Khotkar v. Kailash Kushanrao Gorantyal",
        "citation": "(2020) 7 SCC 1", "year": 2020, "bench": "R.F. Nariman, S. Ravindra Bhat, V. Ramasubramanian, JJ.",
        "petitioner": "Arjun Panditrao Khotkar", "respondent": "Kailash Gorantyal",
        "headnotes": "Mandatory Section 65B Electronic Certificate for Secondary Electronic Evidence (Section 63 BSA).",
        "ratio_decidendi": "Certificate under Section 65B(4) IEA (Section 63 BSA 2023) is a mandatory condition precedent to the admissibility of secondary electronic records (printouts, CDs, WhatsApp chats, CCTV footage).",
        "sections_referred": "Section 65B Indian Evidence Act 1872, Section 63 BSA 2023",
        "verdict": "Electronic Evidence Certificate Standard Established"
    },
    # 9. Free Speech & Section 66A IT Act
    {
        "case_name": "Shreya Singhal v. Union of India",
        "citation": "(2015) 5 SCC 1", "year": 2015, "bench": "J. Chelameswar, R.F. Nariman, JJ.",
        "petitioner": "Shreya Singhal", "respondent": "Union of India",
        "headnotes": "Unconstitutionality of Section 66A IT Act on online speech.",
        "ratio_decidendi": "Section 66A of the IT Act was struck down as unconstitutional for being vague and violating Article 19(1)(a) freedom of speech. Police cannot register FIRs under Section 66A for social media posts.",
        "sections_referred": "Section 66A IT Act 2000, Article 19(1)(a) Constitution",
        "verdict": "Section 66A IT Act Struck Down as Void"
    },
    # 10. Medical Negligence & Doctor Criminal Prosecution
    {
        "case_name": "Jacob Mathew v. State of Punjab & Anr.",
        "citation": "(2005) 6 SCC 1", "year": 2005, "bench": "R.C. Lahoti, CJI, G.P. Mathur, P.K. Balasubramanyan, JJ.",
        "petitioner": "Dr. Jacob Mathew", "respondent": "State of Punjab",
        "headnotes": "Standard of Gross Negligence for Criminal Prosecution of Doctors under Section 304A IPC.",
        "ratio_decidendi": "A doctor cannot be held criminally liable under Section 304A IPC (Section 106 BNS) unless gross negligence or recklessness is established by an independent medical board opinion before filing charge sheet.",
        "sections_referred": "Section 304A IPC, Section 106(1) BNS 2023, Consumer Protection Act",
        "verdict": "Medical Negligence Safeguards Mandated"
    },
    # 11. Decriminalization of Homosexuality
    {
        "case_name": "Navtej Singh Johar v. Union of India",
        "citation": "(2018) 10 SCC 1", "year": 2018, "bench": "5-Judge Constitution Bench",
        "petitioner": "Navtej Singh Johar", "respondent": "Union of India",
        "headnotes": "Decriminalization of Section 377 IPC for Consensual Adult Relationships.",
        "ratio_decidendi": "Section 377 IPC insofar as it criminalizes consensual sexual conduct between adults is unconstitutional, violating Articles 14, 15, 19, and 21 of the Constitution.",
        "sections_referred": "Section 377 IPC, Article 14, 15, 19, 21 Constitution",
        "verdict": "Section 377 Decriminalized for Consenting Adults"
    },
    # 12. Triple Talaq Invalidation
    {
        "case_name": "Shayara Bano v. Union of India",
        "citation": "(2017) 9 SCC 1", "year": 2017, "bench": "5-Judge Constitution Bench",
        "petitioner": "Shayara Bano", "respondent": "Union of India",
        "headnotes": "Manifest Arbitrariness and Unconstitutionality of Talaq-e-Biddat (Triple Talaq).",
        "ratio_decidendi": "Instantaneous Talaq-e-Biddat is arbitrary and violates Article 14 of the Constitution. It does not enjoy protection under Article 25 religious freedom.",
        "sections_referred": "Article 14, 21, 25 Constitution, Muslim Personal Law (Shariat) Application Act 1937",
        "verdict": "Triple Talaq Declared Void & Illegal"
    }
]

def ingest_all_supreme_court():
    conn = sqlite3.connect("backend/yama_ai.db")
    cursor = conn.cursor()

    for item in SC_EXPANDED_DATA:
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
    cursor.execute("SELECT count(*) FROM supreme_court_judgments;")
    count = cursor.fetchone()[0]
    print(f"[OK] Ingested {count} Supreme Court Landmark Precedents!")
    conn.close()

if __name__ == "__main__":
    ingest_all_supreme_court()
