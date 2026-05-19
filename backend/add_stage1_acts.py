"""
Stage 1: Add Income Tax Act and expand financial laws
"""
import json
from datetime import datetime, timezone

STAGE_1_ACTS = [
    {
        "act_name": "Income Tax Act, 1961",
        "sections": [
            {"section_number": "1", "title": "Short title, extent and commencement", "description": "This Act may be called the Income-tax Act, 1961. It extends to the whole of India. It shall come into force on the 1st day of April, 1962."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, unless the context otherwise requires: (1) 'Agricultural income' means income derived from land in India, from agricultural operations. (2) 'Assessee' means a person by whom any tax is payable or who is assessed to tax or against whom proceedings are taken for assessment."},
            {"section_number": "4", "title": "Basis of charge", "description": "Income-tax shall be charged for any previous year in accordance with and subject to the provisions of this Act on the total income of every person who is a resident or a person who is not a resident but has income which accrues or arises in India."},
            {"section_number": "5", "title": "Incidence of income-tax", "description": "Subject to the provisions of this Act, the following income shall be chargeable to income-tax: (1) income which accrues or arises in India; (2) income received in India; (3) income deemed to accrue or arise in India."},
            {"section_number": "14", "title": "Previous year", "description": "Unless otherwise prescribed, the previous year shall be the financial year immediately preceding the relevant year."},
            {"section_number": "23", "title": "Tax on income of individuals", "description": "The tax shall be charged for the relevant year on the total income of an individual at the rates specified in the Finance Act, having regard to the nature of income and exemptions available."},
            {"section_number": "80C", "title": "Deductions for life insurance premium", "description": "Subject to the provisions of this section, in computing the income of an individual for any previous year, there shall be allowed a deduction of an amount paid, by way of premium, during the previous year on an insurance on the life of himself or any other person."},
            {"section_number": "80D", "title": "Deductions for health insurance premium", "description": "Subject to the provisions of this section, an individual shall be allowed a deduction of an amount paid towards health insurance premium for self and family members."},
            {"section_number": "80E", "title": "Deduction for interest on education loan", "description": "An individual shall be allowed a deduction of interest paid on a loan taken for higher education of himself or any dependent."},
            {"section_number": "139", "title": "Return of income", "description": "Every person whose total income during a previous year exceeds the maximum amount which is not chargeable to tax shall furnish a return of income within the prescribed period."},
            {"section_number": "143", "title": "Assessment", "description": "On receipt of a return of income, the Assessing Officer shall examine the return and may make an assessment within the prescribed period."},
            {"section_number": "144", "title": "Assessment in case of default", "description": "If any person who is required to furnish a return of income fails to do so, the Assessing Officer may, after making such inquiry as he thinks fit, assess the total income of such person."},
            {"section_number": "147", "title": "Assessment or reassessment for certain persons", "description": "The Assessing Officer may, after the expiry of one year from the end of the financial year in which the assessment was made, assess or reassess the income of any person for the previous year."},
            {"section_number": "271", "title": "Penalty for failure to furnish return", "description": "If any person required to furnish a return fails to do so within the prescribed period, he shall be liable to a penalty."},
            {"section_number": "275", "title": "Penalty for failure to furnish statement", "description": "If any person fails to furnish a statement in accordance with the provisions of this Act, he shall be liable to penalty."},
        ]
    },
    {
        "act_name": "Companies Act, 2013",
        "sections": [
            {"section_number": "1", "title": "Short title, extent and commencement", "description": "This Act may be called the Companies Act, 2013. It extends to the whole of India. It provides regulation for company formation, management and dissolution."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, unless the context otherwise requires: 'Company' means a company incorporated under this Act or under any previous company law. 'Director' means a director appointed to the Board of a company."},
            {"section_number": "7", "title": "Incorporation of company", "description": "Any two or more persons associated for a lawful purpose may, by subscribing their names to a memorandum of association and complying with the requirements, form an incorporated company."},
            {"section_number": "149", "title": "Number and tenure of directors", "description": "Every company shall have a Board consisting of individuals as directors. The minimum number of directors shall be one. The maximum shall be fifteen."},
            {"section_number": "178", "title": "Independent directors", "description": "A company shall have at least one independent director from the date of incorporation if it is a listed company, public company or private company as prescribed."},
            {"section_number": "373", "title": "Appointment of auditor", "description": "An auditor shall be appointed at the first Annual General Meeting of the company. The auditor shall hold office for a period of five consecutive financial years."},
            {"section_number": "457", "title": "Adjudication", "description": "If the Registrar has reason to believe that a company has contravened the provisions of this Act, the Registrar may seek adjudication by the Adjudicating Officer."},
        ]
    },
    {
        "act_name": "Goods and Services Tax Act, 2017",
        "sections": [
            {"section_number": "1", "title": "Short title and commencement", "description": "This Act may be called the Goods and Services Tax Act, 2017. It comes into force on such date as the Central Government may notify."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, unless the context otherwise requires: 'Goods' means every description of moveable property other than money and securities. 'Service' means anything other than goods, money and securities."},
            {"section_number": "9", "title": "Tax on supply of goods or services", "description": "Goods and services tax shall be levied on all supplies of goods or services in the course of trade or business at such rate and manner as prescribed."},
            {"section_number": "24", "title": "Input tax credit", "description": "The input tax credit of a person in relation to a month shall be the sum of Central Tax, State Tax and integrated GST charged on supplies made to him."},
            {"section_number": "39", "title": "Return", "description": "Every registered person shall furnish a return in such manner as may be prescribed for each month or quarter as specified."},
            {"section_number": "62", "title": "Demand and recovery of tax", "description": "If the Proper Officer is of the opinion that any person is liable to pay any tax, the Officer may serve notice to such person for payment of tax."},
        ]
    },
]

def add_stage1_acts():
    """Add stage 1 acts to database"""
    from app.db.database import get_db, engine
    from app.db.models import LawSection, Base
    from sqlalchemy.orm import Session
    
    Base.metadata.create_all(bind=engine)
    session = next(get_db())
    
    inserted = 0
    updated = 0
    
    for act_data in STAGE_1_ACTS:
        act_name = act_data["act_name"]
        
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
                    category="tax" if "Income Tax" in act_name else ("corporate" if "Companies" in act_name else "tax"),
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
    result = add_stage1_acts()
    print(f"Stage 1 Loading Complete:")
    print(f"  Inserted: {result['inserted']}")
    print(f"  Updated: {result['updated']}")
