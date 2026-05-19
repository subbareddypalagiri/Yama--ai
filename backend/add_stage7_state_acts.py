"""
Stage 7: State Laws Expansion - Add laws from additional Indian states
"""

STAGE_7_STATE_ACTS = [
    {
        "state": "Uttar Pradesh",
        "acts": [
            {"act_name": "Uttar Pradesh Gangsters and Anti-Social Activities (Prevention) Act, 1986", "sections": [
                {"section_number": "1", "title": "Short title", "description": "This Act may be called the Uttar Pradesh Gangsters and Anti-Social Activities (Prevention) Act, 1986."},
                {"section_number": "4", "title": "Detention", "description": "Government may detain any person engaged in gangster activities for prevention of anti-social activities."},
            ]},
        ]
    },
    {
        "state": "Bihar",
        "acts": [
            {"act_name": "Bihar State Prohibition of Slaughter of Cattle Act, 1992", "sections": [
                {"section_number": "1", "title": "Short title", "description": "This Act may be called the Bihar State Prohibition of Slaughter of Cattle Act, 1992."},
                {"section_number": "3", "title": "Prohibition of slaughter", "description": "No person shall slaughter any bovine animal except as permitted by law."},
            ]},
        ]
    },
    {
        "state": "Odisha",
        "acts": [
            {"act_name": "Odisha Agricultural Produce Marketing Act, 1991", "sections": [
                {"section_number": "1", "title": "Short title", "description": "This Act may be called the Odisha Agricultural Produce Marketing Act, 1991."},
                {"section_number": "4", "title": "Licensing of merchants", "description": "Merchants dealing in agricultural produce must obtain license from prescribed authorities."},
            ]},
        ]
    },
    {
        "state": "Jharkhand",
        "acts": [
            {"act_name": "Jharkhand Tenancy Act, 1949", "sections": [
                {"section_number": "1", "title": "Short title", "description": "This Act may be called the Jharkhand Tenancy Act, 1949."},
                {"section_number": "5", "title": "Rights of tenant", "description": "Tenants have rights to peaceful possession and security of tenure as prescribed."},
            ]},
        ]
    },
    {
        "state": "Chhattisgarh",
        "acts": [
            {"act_name": "Chhattisgarh Land Revenue Code, 1959", "sections": [
                {"section_number": "1", "title": "Short title", "description": "This Act regulates land revenue and land records in Chhattisgarh."},
                {"section_number": "15", "title": "Land records", "description": "Accurate land records shall be maintained by Revenue Department for identification of land rights."},
            ]},
        ]
    },
    {
        "state": "Assam",
        "acts": [
            {"act_name": "Assam Shops and Establishments Act, 1965", "sections": [
                {"section_number": "1", "title": "Short title", "description": "This Act regulates working conditions and hours of work in shops and establishments in Assam."},
                {"section_number": "9", "title": "Hours of work", "description": "Worker shall not work more than 48 hours per week and 9 hours per day as prescribed."},
            ]},
        ]
    },
    {
        "state": "Meghalaya",
        "acts": [
            {"act_name": "Meghalaya Liquor Prohibition Act, 1989", "sections": [
                {"section_number": "1", "title": "Short title", "description": "This Act regulates production and consumption of liquor in Meghalaya."},
                {"section_number": "3", "title": "Prohibition", "description": "Production and sale of liquor prohibited except under license as prescribed."},
            ]},
        ]
    },
    {
        "state": "Manipur",
        "acts": [
            {"act_name": "Manipur Land (Niglected) Terraces and Hill Slopes Reclamation Act, 1980", "sections": [
                {"section_number": "1", "title": "Short title", "description": "This Act promotes reclamation of neglected terraces and hill slopes in Manipur."},
                {"section_number": "5", "title": "Reclamation scheme", "description": "Government may grant land to persons for reclamation and development purposes."},
            ]},
        ]
    },
    {
        "state": "Mizoram",
        "acts": [
            {"act_name": "Mizoram Cooperative Societies Act, 1982", "sections": [
                {"section_number": "1", "title": "Short title", "description": "This Act regulates cooperative societies in Mizoram."},
                {"section_number": "8", "title": "Registration", "description": "Cooperative societies must be registered with prescribed authorities."},
            ]},
        ]
    },
    {
        "state": "Nagaland",
        "acts": [
            {"act_name": "Nagaland Land and Land Revenue and Courts of Wards Act, 1989", "sections": [
                {"section_number": "1", "title": "Short title", "description": "This Act regulates land in Nagaland and matters related to land revenue."},
                {"section_number": "12", "title": "Protection of land", "description": "Land protected from unauthorized sale or transfer to maintain land rights."},
            ]},
        ]
    },
]

def add_stage7_state_acts():
    """Add stage 7 state acts to database"""
    from app.db.database import get_db, engine
    from app.db.models import LawSection, Base
    
    Base.metadata.create_all(bind=engine)
    session = next(get_db())
    
    inserted = 0
    
    for state_data in STAGE_7_STATE_ACTS:
        state = state_data["state"]
        for act_item in state_data["acts"]:
            act_name = act_item["act_name"]
            for sec in act_item["sections"]:
                law = LawSection(
                    act_name=act_name,
                    section_number=sec["section_number"],
                    title=sec["title"],
                    description=sec["description"],
                    keywords=f"state, {state.lower()}, {sec['title'].lower()[:15]}",
                    category="general",
                    jurisdiction="state",
                    state_name=state,
                    law_type="act",
                    is_active=True,
                )
                session.add(law)
                inserted += 1
    
    session.commit()
    session.close()
    
    return {"inserted": inserted}

if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/backend")
    result = add_stage7_state_acts()
    print(f"\n✅ Stage 7 Loading Complete:")
    print(f"   Inserted: {result['inserted']} state law sections")
    print(f"\n🏛️ State Laws from 10 Additional States:")
    print(f"   • Uttar Pradesh - Gangsters Prevention Act")
    print(f"   • Bihar - Cattle Slaughter Prohibition")
    print(f"   • Odisha - Agricultural Produce Marketing")
    print(f"   • Jharkhand - Tenancy Act")
    print(f"   • Chhattisgarh - Land Revenue Code")
    print(f"   • Assam - Shops & Establishments Act")
    print(f"   • Meghalaya - Liquor Prohibition")
    print(f"   • Manipur - Land Reclamation")
    print(f"   • Mizoram - Cooperative Societies")
    print(f"   • Nagaland - Land and Revenue Act")
    print(f"\nTotal Stage 7: 20 state law sections")
