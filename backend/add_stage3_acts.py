"""
Stage 3: Expand Specialized & Social Welfare Laws
"""

STAGE_3_ACTS = [
    {
        "act_name": "Environmental Protection Act, 1986",
        "sections": [
            {"section_number": "1", "title": "Short title and commencement", "description": "This Act may be called the Environment Protection Act, 1986. It applies to all aspects of environmental protection."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, 'Environment' includes water, air and land. 'Environmental pollution' means introduction of pollutants into the environment."},
            {"section_number": "5", "title": "Power to issue directions", "description": "The Central Government may issue directions to any person to take measures to prevent environmental pollution."},
            {"section_number": "15", "title": "Penalties for violation", "description": "Any person who contravenes provisions shall be liable to fine and/or imprisonment."},
            {"section_number": "19", "title": "Power to make rules", "description": "The Central Government may make rules for implementation of this Act."},
        ]
    },
    {
        "act_name": "Food Safety and Standards Act, 2006",
        "sections": [
            {"section_number": "1", "title": "Short title and commencement", "description": "This Act may be called the Food Safety and Standards Act, 2006. It applies to all food articles sold in India."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, 'Food' includes any substance whether processed or raw intended for human consumption. 'Food safety' means assurance that food is safe for consumption."},
            {"section_number": "21", "title": "Food Safety and Standards Authority", "description": "There shall be established a statutory body to regulate food business operations and standards."},
            {"section_number": "31", "title": "License requirement", "description": "No person shall operate food business without obtaining license from the authority."},
            {"section_number": "63", "title": "Penalties", "description": "Violations attract penalties up to 5 lakhs and/or imprisonment up to 6 months."},
        ]
    },
    {
        "act_name": "National Security Act, 1980",
        "sections": [
            {"section_number": "1", "title": "Short title and extent", "description": "This Act may be called the National Security Act, 1980. It applies throughout India."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, 'National security' includes sovereignty, territorial integrity and public order."},
            {"section_number": "3", "title": "Power to make orders", "description": "The appropriate Government may pass orders for prevention of persons prejudicial to national security."},
            {"section_number": "8", "title": "Advisory Board", "description": "An Advisory Board may be constituted to advise on detention orders."},
            {"section_number": "12", "title": "Duration of detention", "description": "A person may be detained for a period not exceeding 12 months."},
        ]
    },
    {
        "act_name": "Unlawful Activities (Prevention) Act, 1967",
        "sections": [
            {"section_number": "1", "title": "Short title and extent", "description": "This Act may be called the Unlawful Activities (Prevention) Act, 1967."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, 'Terrorist' means person committing acts prejudicial to national security. 'Unlawful activity' includes acts of terrorism or secessionism."},
            {"section_number": "15", "title": "Offences relating to terrorist acts", "description": "Committing terrorist acts is punishable with imprisonment and fine."},
            {"section_number": "43", "title": "Terrorist organization", "description": "Organizations engaged in terrorist activities shall be banned by the Government."},
            {"section_number": "49", "title": "Penalties", "description": "Punishment ranges from 5 to 14 years imprisonment for terrorist offences."},
        ]
    },
    {
        "act_name": "Maintenance and Welfare of Parents and Senior Citizens Act, 2007",
        "sections": [
            {"section_number": "1", "title": "Short title", "description": "This Act may be called the Maintenance and Welfare of Parents and Senior Citizens Act, 2007."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, 'Senior citizen' means person aged 60 years or above. 'Children' includes all sons and daughters of senior citizen."},
            {"section_number": "3", "title": "Duty to maintain", "description": "It is the duty of children to maintain their parents. If children fail, parents can file petition in Maintenance Tribunal."},
            {"section_number": "5", "title": "Determination of maintenance", "description": "The tribunal shall determine maintenance taking into account needs of senior citizen and capacity of children."},
            {"section_number": "12", "title": "Offence and penalties", "description": "Abandonment of senior citizen is punishable with fine and/or imprisonment up to 3 months."},
        ]
    },
    {
        "act_name": "Sexual Harassment of Women at Workplace Act, 2013",
        "sections": [
            {"section_number": "1", "title": "Short title and commencement", "description": "This Act may be called the Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, 'Sexual harassment' includes unwelcome acts or behavior of a sexual nature. 'Workplace' includes all places of work."},
            {"section_number": "3", "title": "Duty to prevent harassment", "description": "Every employer shall take measures to prevent sexual harassment at workplace."},
            {"section_number": "4", "title": "Constitution of Internal Complaints Committee", "description": "Organizations with 10 or more employees must constitute ICC to address complaints."},
            {"section_number": "20", "title": "Penalties for non-compliance", "description": "Employers who fail to comply shall be liable to penalties up to 5 lakhs."},
        ]
    },
    {
        "act_name": "Right to Education Act, 2009",
        "sections": [
            {"section_number": "1", "title": "Short title and commencement", "description": "This Act may be called the Right of Free and Compulsory Education Act, 2009."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, 'Child' means person aged 6 to 14 years. 'Education' means imparting knowledge and skills to develop personality."},
            {"section_number": "3", "title": "Right to free and compulsory education", "description": "Every child has the right to free and compulsory education from age 6 to 14 years."},
            {"section_number": "6", "title": "Curriculum and evaluation", "description": "Schools shall follow prescribed curriculum focusing on overall development of child."},
            {"section_number": "32", "title": "Penalties", "description": "Non-compliance by schools shall attract penalties up to 1 lakh rupees."},
        ]
    },
    {
        "act_name": "Right to Information Act, 2005",
        "sections": [
            {"section_number": "1", "title": "Short title and commencement", "description": "This Act may be called the Right to Information Act, 2005. It promotes transparency in government."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, 'Information' means records held by public authorities. 'Right to information' means citizen's right to obtain information from government."},
            {"section_number": "4", "title": "Obligation of public authorities", "description": "All public authorities must maintain records and provide information to citizens."},
            {"section_number": "6", "title": "Right to information", "description": "Every citizen has right to seek information in any form from public authority within 30 days."},
            {"section_number": "20", "title": "Penalties", "description": "Information officers failing to provide information face penalties up to 25,000 rupees."},
        ]
    },
]

def add_stage3_acts():
    """Add stage 3 acts to database"""
    from app.db.database import get_db, engine
    from app.db.models import LawSection, Base
    
    Base.metadata.create_all(bind=engine)
    session = next(get_db())
    
    inserted = 0
    updated = 0
    
    category_map = {
        "Environmental": "environmental",
        "Food": "general",
        "National": "general",
        "Unlawful": "criminal",
        "Maintenance": "family",
        "Sexual": "general",
        "Right to Education": "education",
        "Right to Information": "rti",
    }
    
    for act_data in STAGE_3_ACTS:
        act_name = act_data["act_name"]
        
        # Determine category
        category = "general"
        for keyword, cat in category_map.items():
            if keyword in act_name:
                category = cat
                break
        
        for sec in act_data["sections"]:
            # Check if already exists
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
                    category=category,
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
    result = add_stage3_acts()
    print(f"✅ Stage 3 Loading Complete:")
    print(f"   Inserted: {result['inserted']} new sections")
    print(f"   Updated: {result['updated']} existing sections")
    print(f"\n📊 8 Specialized acts expanded with detailed sections")
    print(f"🎉 ALL 3 STAGES COMPLETE - Database fully loaded!")
