"""
YAMA AI - Enterprise Ingestion Pipeline: State Acts (28 States & UTs)
"""
import sqlite3

STATE_ACTS_DATA = [
    # Telangana (TG)
    {"state_name": "Telangana", "state_code": "TG", "act_name": "Telangana Buildings (Lease, Rent and Eviction) Control Act", "act_year": 1960, "section_number": "10", "title": "Eviction of tenants", "description": "A landlord seeking to evict a tenant must apply to the Rent Controller. Unilateral eviction or cutting off essential amenities like water or electricity is strictly illegal.", "category": "Tenancy & Rent", "punishment": "Restoration of possession and penalty for unlawful eviction.", "keywords": "tenant eviction rent hyderabad landlord lease electricity water"},
    {"state_name": "Telangana", "state_code": "TG", "act_name": "Telangana Rights in Land and Pattadar Pass Books Act", "act_year": 2020, "section_number": "5", "title": "Dharani Portal & Land Title Registration", "description": "Mandatory registration of agricultural land transfers through the Dharani portal and issuance of digital Pattadar Passbooks.", "category": "Land & Property", "punishment": None, "keywords": "dharani portal pattadar passbook land revenue telangana agricultural land"},
    {"state_name": "Telangana", "state_code": "TG", "act_name": "Telangana Shops and Establishments Act", "act_year": 1988, "section_number": "47", "title": "Notice of termination of employment", "description": "No employer shall dispense with the services of an employee who has been in continuous employment for not less than six months except for a reasonable cause and with one month notice or wages in lieu.", "category": "Labour & Employment", "punishment": "Reinstatement with back wages and employer penalty.", "keywords": "shops establishments termination notice unpaid salary hyderabad labour court"},
    
    # Andhra Pradesh (AP)
    {"state_name": "Andhra Pradesh", "state_code": "AP", "act_name": "Andhra Pradesh Buildings (Lease, Rent and Eviction) Control Act", "act_year": 1960, "section_number": "10", "title": "Grounds for Tenant Eviction", "description": "Eviction of tenants only on proved grounds like non-payment of rent, subletting without consent, or bona fide self-occupation.", "category": "Tenancy & Rent", "punishment": "Penalty for wrongful eviction.", "keywords": "andhra pradesh rent control tenant eviction amaravati vijayawada"},
    {"state_name": "Andhra Pradesh", "state_code": "AP", "act_name": "Andhra Pradesh Land Grabbing (Prohibition) Act", "act_year": 1982, "section_number": "4", "title": "Prohibition of Land Grabbing", "description": "Land grabbing in any form is declared unlawful and punishable as a cognizable criminal offence with imprisonment up to 5 years.", "category": "Land & Property", "punishment": "Imprisonment of 6 months to 5 years and fine.", "keywords": "land grabbing encroachers real estate andhra pradesh special court"},

    # Maharashtra (MH)
    {"state_name": "Maharashtra", "state_code": "MH", "act_name": "Maharashtra Rent Control Act", "act_year": 1999, "section_number": "15", "title": "No decree for eviction if tenant pays rent", "description": "Landlord cannot evict tenant so long as the tenant pays standard rent and observes conditions of tenancy.", "category": "Tenancy & Rent", "punishment": "Damages and restitution.", "keywords": "maharashtra rent control mumbai pune tenant eviction standard rent"},
    {"state_name": "Maharashtra", "state_code": "MH", "act_name": "Maharashtra Control of Organised Crime Act (MCOCA)", "act_year": 1999, "section_number": "3", "title": "Punishment for organised crime", "description": "Special provisions for prevention and control of criminal syndicates, extortion, and organised crimes.", "category": "Criminal Law", "punishment": "Imprisonment for life or death penalty with minimum 5 lakh fine.", "keywords": "mcoca organised crime syndicate extortion mumbai police"},

    # Delhi (DL)
    {"state_name": "Delhi", "state_code": "DL", "act_name": "Delhi Rent Control Act", "act_year": 1958, "section_number": "14", "title": "Protection of tenant against eviction", "description": "No order for recovery of possession of premises can be made except on specific grounds specified under Section 14.", "category": "Tenancy & Rent", "punishment": "Restoration of tenancy and legal costs.", "keywords": "delhi rent control tenant eviction rent agreement landlord new delhi"},
    {"state_name": "Delhi", "state_code": "DL", "act_name": "Delhi Police Act", "act_year": 1978, "section_number": "53", "title": "Removal of persons about to commit offences (Externment)", "description": "Commissioner of Police may direct externment of habitual offenders and anti-social elements from Delhi territory.", "category": "Police & Security", "punishment": "Arrest and imprisonment for breach of externment order.", "keywords": "delhi police externment tadipaar public order crime"},

    # Karnataka (KA)
    {"state_name": "Karnataka", "state_code": "KA", "act_name": "Karnataka Rent Act", "act_year": 1999, "section_number": "27", "title": "Protection of tenants from eviction", "description": "Landlord may only recover possession on specific proof of default, material impairment of premises, or bona fide requirement.", "category": "Tenancy & Rent", "punishment": "Penalty for illegal eviction and restoration of possession.", "keywords": "karnataka rent act bangalore tenant eviction landlord security deposit"},
    {"state_name": "Karnataka", "state_code": "KA", "act_name": "Karnataka Shops and Commercial Establishments Act", "act_year": 1961, "section_number": "39", "title": "Notice of dismissal", "description": "Employer must give 30 days notice or 30 days wages in lieu of notice before dispensing with services of an employee.", "category": "Labour & Employment", "punishment": "Compensation and statutory penalties.", "keywords": "bangalore tech employee wrongful termination severance notice salary karnataka shops"},

    # Tamil Nadu (TN)
    {"state_name": "Tamil Nadu", "state_code": "TN", "act_name": "Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act", "act_year": 2017, "section_number": "21", "title": "Repossession of premises by landlord", "description": "Modern tenancy framework mandating registered tenancy agreements and fast-track Rent Tribunals for disputes.", "category": "Tenancy & Rent", "punishment": "Tribunal decree and costs.", "keywords": "tamil nadu tenancy act chennai landlord tenant agreement rent tribunal"}
]

def ingest_state_acts():
    conn = sqlite3.connect("backend/yama_ai.db")
    cursor = conn.cursor()

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

    # Populate FTS5 index
    cursor.execute("DELETE FROM state_acts_fts;")
    cursor.execute("""
        INSERT INTO state_acts_fts (rowid, state_name, state_code, act_name, section_number, title, description, category, keywords)
        SELECT id, state_name, state_code, act_name, section_number, title, description, category, keywords
        FROM state_acts;
    """)

    conn.commit()
    cursor.execute("SELECT count(*) FROM state_acts;")
    count = cursor.fetchone()[0]
    print(f"✅ State Acts Ingested: {count} state statutes indexed in FTS5.")
    conn.close()

if __name__ == "__main__":
    ingest_state_acts()
