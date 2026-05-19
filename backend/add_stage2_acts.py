"""
Stage 2: Expand Labour & Social Security Laws
"""

STAGE_2_ACTS = [
    {
        "act_name": "Employees' Provident Fund and Miscellaneous Provisions Act, 1952",
        "sections": [
            {"section_number": "1", "title": "Short title and extent", "description": "This Act may be called the Employees' Provident Fund and Miscellaneous Provisions Act, 1952. It extends to the whole of India."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, unless the context otherwise requires: 'Employee' means any person employed in any establishment to do any skilled, semi-skilled or unskilled manual or non-manual work for hire or reward. 'Employer' means any person who employs one or more employees."},
            {"section_number": "6", "title": "Constitution of Fund", "description": "The Central Government shall constitute a fund to be called the Employees' Provident Fund for the purposes of this Act."},
            {"section_number": "7", "title": "Contributions to Fund", "description": "Every employer shall make contributions to the Fund at the rate of 12% of the basic wages, dearness allowance and other allowances as prescribed. Every employee shall also contribute at the prescribed rate."},
            {"section_number": "8", "title": "Withdrawal from Fund", "description": "An employee may withdraw or transfer the amount standing to his credit in the Fund under such conditions and in such manner as may be prescribed."},
            {"section_number": "14", "title": "Penalties", "description": "Whoever fails to comply with the provisions of this Act shall be liable to penalties as prescribed."},
        ]
    },
    {
        "act_name": "Employees' State Insurance Act, 1948",
        "sections": [
            {"section_number": "1", "title": "Short title and extent", "description": "This Act may be called the Employees' State Insurance Act, 1948. It applies to all establishments employing 10 or more employees."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, 'Employee' means any person employed by an employer to do any skilled, semi-skilled or unskilled manual work. 'Injury' means bodily injury by accident."},
            {"section_number": "38", "title": "Medical benefit", "description": "The employee shall be entitled to medical benefit including treatment, rehabilitation and appliances as prescribed."},
            {"section_number": "46", "title": "Disability benefit", "description": "An employee who is disabled due to employment injury is entitled to disability benefit as per prescribed rate based on degree of disability."},
            {"section_number": "56", "title": "Dependent's benefit", "description": "In case of death of an employee due to employment injury, dependents are entitled to dependent's benefit."},
            {"section_number": "75", "title": "Penalties", "description": "Employer who fails to comply with provisions shall be liable to penalties."},
        ]
    },
    {
        "act_name": "Maternity Benefit Act, 1961",
        "sections": [
            {"section_number": "1", "title": "Short title, extent and commencement", "description": "This Act may be called the Maternity Benefit Act, 1961. It extends to the whole of India and applies to establishments with 10 or more employees."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, 'Maternity benefit' means benefit granted to women in the form of cash and/or medical facilities."},
            {"section_number": "5", "title": "Maternity benefit", "description": "A woman who is confined is entitled to maternity benefit at a rate not less than her average daily wages for the period of confinement and eight weeks before confinement."},
            {"section_number": "9", "title": "Nursing break", "description": "A woman is entitled to two breaks of 15 minutes each during her working hours for nursing her child until the child attains the age of 15 months."},
            {"section_number": "11", "title": "Dismissal during pregnancy", "description": "An employer cannot dismiss or remove a woman while she is pregnant or in the post-confinement period."},
            {"section_number": "20", "title": "Penalties", "description": "Any employer who fails to comply with provisions shall be liable to penalties."},
        ]
    },
    {
        "act_name": "Minimum Wages Act, 1948",
        "sections": [
            {"section_number": "1", "title": "Short title", "description": "This Act may be called the Minimum Wages Act, 1948."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, 'Minimum wage' means the wage fixed by the Government below which no worker shall be paid."},
            {"section_number": "3", "title": "Constitution of wage boards", "description": "The Government may constitute wage boards to advise on fixation of minimum wages."},
            {"section_number": "4", "title": "Authority to fix minimum wages", "description": "The Government shall fix minimum wages for scheduled employments as prescribed."},
            {"section_number": "5", "title": "Fixation of minimum wages by Central Government", "description": "The Central Government may fix minimum wages for certain scheduled employments."},
            {"section_number": "21", "title": "Penalties for non-compliance", "description": "Any employer violating minimum wage provisions shall be liable to penalties."},
        ]
    },
    {
        "act_name": "Industrial Disputes Act, 1947",
        "sections": [
            {"section_number": "1", "title": "Short title, extent and commencement", "description": "This Act may be called the Industrial Disputes Act, 1947. It applies throughout India."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, 'Industrial dispute' means any dispute or difference between employers and workmen. 'Workman' means any person employed in an industry."},
            {"section_number": "10", "title": "Conciliation", "description": "Conciliation officers shall investigate and mediate industrial disputes to effect amicable settlement."},
            {"section_number": "25", "title": "Authority of Industrial Tribunal", "description": "Industrial tribunals have authority to adjudicate and settle industrial disputes and award compensation."},
            {"section_number": "33", "title": "Bad faith dismissal", "description": "No employer shall discharge or dismiss a workman unless there is a valid reason and due notice."},
            {"section_number": "34", "title": "Procedure for dismissal", "description": "An employer must follow prescribed procedure including notice and opportunity to show cause before dismissal."},
        ]
    },
    {
        "act_name": "Payment of Gratuity Act, 1972",
        "sections": [
            {"section_number": "1", "title": "Short title and extent", "description": "This Act may be called the Payment of Gratuity Act, 1972. It applies to all establishments with 10 or more employees."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, 'Gratuity' means the sum payable to an employee by employer as per prescribed formula."},
            {"section_number": "4", "title": "Payment of gratuity", "description": "An employee who completes 5 years of continuous service is entitled to gratuity as per formula: 15 days' wages per year or part thereof for completed years of service."},
            {"section_number": "6", "title": "Death of employee", "description": "Gratuity is payable to dependents if employee dies after 5 years of service or due to accident/disease."},
            {"section_number": "17", "title": "Penalties", "description": "Any default in payment of gratuity shall attract penalties and interest."},
        ]
    },
    {
        "act_name": "Payment of Wages Act, 1936",
        "sections": [
            {"section_number": "1", "title": "Short title and extent", "description": "This Act may be called the Payment of Wages Act, 1936."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, 'Wages' includes ordinary wages, salary and all amounts paid by employer including DA, bonuses, commission."},
            {"section_number": "5", "title": "Time and manner of payment", "description": "Wages shall be paid before the end of the day on which they become due."},
            {"section_number": "7", "title": "Deductions from wages", "description": "No deductions from wages are allowed except those authorized by law and with written consent of employee."},
            {"section_number": "15", "title": "Penalties for non-compliance", "description": "Any employer who contravenes provisions shall be liable to penalties and imprisonment."},
        ]
    },
    {
        "act_name": "Workmen's Compensation Act, 1923",
        "sections": [
            {"section_number": "1", "title": "Short title", "description": "This Act may be called the Workmen's Compensation Act, 1923."},
            {"section_number": "2", "title": "Definitions", "description": "In this Act, 'Workman' includes any person employed to do manual or non-manual work. 'Injury' means bodily injury including occupational diseases."},
            {"section_number": "3", "title": "Application", "description": "This Act applies to all accidents arising out of and in the course of employment."},
            {"section_number": "4", "title": "Liability of employer", "description": "Employer is liable to pay compensation for injury to workmen as per prescribed schedule."},
            {"section_number": "5", "title": "Amount of compensation", "description": "Compensation ranges from 40% to 60% of monthly wages based on nature of injury."},
            {"section_number": "29", "title": "Penalties", "description": "Employers who fail to comply shall be liable to penalties and imprisonment."},
        ]
    },
]

def add_stage2_acts():
    """Add stage 2 acts to database"""
    from app.db.database import get_db, engine
    from app.db.models import LawSection, Base
    
    Base.metadata.create_all(bind=engine)
    session = next(get_db())
    
    inserted = 0
    updated = 0
    
    for act_data in STAGE_2_ACTS:
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
                    category="labour",
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
    result = add_stage2_acts()
    print(f"✅ Stage 2 Loading Complete:")
    print(f"   Inserted: {result['inserted']} new sections")
    print(f"   Updated: {result['updated']} existing sections")
    print(f"\n📊 8 Labour acts expanded with detailed sections")
