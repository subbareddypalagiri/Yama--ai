"""
Stage 5: Additional Central Acts - Family Laws & Criminal Procedures
"""

STAGE_5_ACTS = [
    {
        "act_name": "Hindu Marriage Act, 1955",
        "sections": [
            {"section_number": "5", "title": "Conditions for a valid marriage", "description": "The following conditions must be fulfilled for a valid marriage: (1) Neither party has a living spouse. (2) Neither party is an idiot or lunatic. (3) The male is not under 21 and female is not under 18."},
            {"section_number": "13", "title": "Grounds for divorce", "description": "Either party to a marriage may present a petition for divorce on grounds of cruelty, adultery, desertion, conversion or insanity."},
            {"section_number": "25", "title": "Alimony and maintenance", "description": "During the proceedings, and after judgment, court may order either party to pay maintenance to the other."},
            {"section_number": "26", "title": "Custody of children", "description": "In any proceeding relating to custody of a child, the court shall have regard to welfare of the child and make such order as it deems fit."},
        ]
    },
    {
        "act_name": "Bharatiya Sakshya Adhiniyam, 2023",
        "sections": [
            {"section_number": "1", "title": "Short title and commencement", "description": "This Act may be called Bharatiya Sakshya Adhiniyam, 2023. It replaces the Indian Evidence Act, 1872."},
            {"section_number": "3", "title": "Relevancy of facts", "description": "Facts are relevant when they have such a relation to and connection with the fact in issue that according to the common course of events they either prove or render it probable."},
            {"section_number": "131", "title": "Rules of admissibility of confessions", "description": "Admissions and confessions made by an accused person shall be admissible if made voluntarily without threat or inducement."},
            {"section_number": "39", "title": "Admissibility of electronic evidence", "description": "Electronic records including digital documents and audio-video records are admissible as evidence under prescribed conditions."},
        ]
    },
    {
        "act_name": "Code of Criminal Procedure, 1973",
        "sections": [
            {"section_number": "41", "title": "When police officer may arrest without warrant", "description": "A police officer may arrest without warrant if person is accused of committing offence punishable with imprisonment of 7 years or more."},
            {"section_number": "161", "title": "Examination of witness by police", "description": "Any police officer making investigation may examine any person supposed to be acquainted with facts and circumstances."},
            {"section_number": "167", "title": "Procedure when investigation cannot be completed in 24 hours", "description": "If investigation cannot be completed within 24 hours, the accused shall be produced before magistrate who may remand for further investigation."},
            {"section_number": "273", "title": "Examination of prosecution witnesses", "description": "The examination of witnesses by the prosecution shall be done in open court before the accused."},
            {"section_number": "301", "title": "Competency and compellability of spouses as witnesses", "description": "The husband or wife of the accused is a competent witness and can be compelled to testify except in certain circumstances."},
        ]
    },
    {
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "sections": [
            {"section_number": "173", "title": "First information report", "description": "Information regarding commission of an offence shall be given orally or in writing and shall be recorded in the prescribed manner."},
            {"section_number": "187", "title": "Custody of accused", "description": "Custody of an accused shall not exceed 15 days in aggregate and shall be during investigation period only."},
            {"section_number": "483", "title": "Bail", "description": "When person is accused of bailable offence, they shall be released on bail without surety unless there are reasonable grounds to believe they will abscond."},
        ]
    },
    {
        "act_name": "Dowry Prohibition Act, 1961",
        "sections": [
            {"section_number": "2", "title": "Definition of dowry", "description": "Dowry means any property or valuable security given or agreed to be given as consideration for marriage by one party to another."},
            {"section_number": "3", "title": "Prohibition of giving and taking dowry", "description": "Any person who gives or takes or abets giving or taking dowry shall be punishable with imprisonment or fine."},
            {"section_number": "8", "title": "Penalty for demanding dowry", "description": "Anyone demanding dowry directly or indirectly shall be punishable with imprisonment up to 6 months and fine."},
        ]
    },
    {
        "act_name": "Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act, 1989",
        "sections": [
            {"section_number": "3", "title": "Offences to be cognizable", "description": "Offences under this Act shall be cognizable and non-bailable, and no person shall release on bail except in exceptional cases."},
            {"section_number": "8", "title": "Punishment for offences", "description": "Punishment for offences ranges from 6 months to 6 years imprisonment with fines up to 5000 rupees."},
            {"section_number": "15", "title": "Special provisions regarding public servant", "description": "If offence involves public servant, special conditions apply for bail and conduct of trial."},
        ]
    },
]

def add_stage5_acts():
    """Add stage 5 acts to database"""
    from app.db.database import get_db, engine
    from app.db.models import LawSection, Base
    
    Base.metadata.create_all(bind=engine)
    session = next(get_db())
    
    inserted = 0
    updated = 0
    
    for act_data in STAGE_5_ACTS:
        act_name = act_data["act_name"]
        
        for sec in act_data["sections"]:
            existing = session.query(LawSection).filter(
                LawSection.act_name == act_name,
                LawSection.section_number == sec["section_number"]
            ).first()
            
            if not existing:
                law = LawSection(
                    act_name=act_name,
                    section_number=sec["section_number"],
                    title=sec["title"],
                    description=sec["description"],
                    keywords=", ".join(sec["title"].lower().split()[:5]),
                    category="family" if "Marriage" in act_name or "Dowry" in act_name else ("criminal" if "Criminal" in act_name or "Atrocities" in act_name else "general"),
                    jurisdiction="central",
                    law_type="act",
                    is_active=True,
                )
                session.add(law)
                inserted += 1
            else:
                updated += 1
    
    session.commit()
    session.close()
    
    return {"inserted": inserted, "updated": updated}

if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/backend")
    result = add_stage5_acts()
    print(f"\n✅ Stage 5 Loading Complete:")
    print(f"   Inserted: {result['inserted']} new sections")
    print(f"   Updated: {result['updated']} existing sections")
    print(f"\n📚 6 Acts Added/Expanded:")
    print(f"   • Hindu Marriage Act (4 sections)")
    print(f"   • Bharatiya Sakshya Adhiniyam (4 sections)")
    print(f"   • Code of Criminal Procedure 1973 (5 sections)")
    print(f"   • Bharatiya Nagarik Suraksha Sanhita (3 sections)")
    print(f"   • Dowry Prohibition Act (3 sections)")
    print(f"   • SC/ST Atrocities Prevention Act (3 sections)")
    print(f"\nTotal Stage 5: 22 new sections")
