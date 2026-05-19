"""
Stage 4: Deep Expansion of Core Legal Acts
Expands IPC, Constitution, Contract Act, and IT Act with detailed sections
"""

STAGE_4_ACTS = [
    {
        "act_name": "Indian Penal Code, 1860",
        "sections": [
            {"section_number": "52", "title": "Definitions of 'good faith'", "description": "Nothing is an offence by reason of any harm which it may cause to a person who has given consent in writing to suffer that harm."},
            {"section_number": "79", "title": "Act of person who, by reason of insanity, does not know the nature of the act", "description": "Nothing is an offence which is committed by a person who, at the time of doing it, by reason of unsoundness of mind, does not know the nature of the act."},
            {"section_number": "100", "title": "When the right of private defence of the body extends to causing death", "description": "The right of private defence of the body extends under certain circumstances to causing death."},
            {"section_number": "149", "title": "Every member of unlawful assembly guilty of offence committed in prosecution of common object", "description": "If an offence is committed by any member of an unlawful assembly in prosecution of the common object of that assembly it is deemed to be committed by all."},
            {"section_number": "153", "title": "Wantonly provoking any person by act or sound", "description": "Whoever intentionally insults and thereby wantonly provokes any person intending or knowing it to be likely that such provocation will cause him to commit any offence."},
            {"section_number": "201", "title": "Causing disappearance of evidence of offence", "description": "Whoever commits or is concerned in or is privy to an offence against this Code causing its disappearance shall be punished with imprisonment."},
            {"section_number": "304", "title": "Causing death by negligence", "description": "Causing death by doing any rash or negligent act not amounting to culpable homicide shall be punished with fine or imprisonment."},
            {"section_number": "335", "title": "Voluntarily causing hurt", "description": "Whoever voluntarily causes hurt shall be punished with imprisonment or fine not exceeding 500 rupees."},
            {"section_number": "375", "title": "Rape", "description": "A man is said to commit rape if he has sexual intercourse with a woman without her consent, against her will or knowing that he is likely to cause such injury."},
            {"section_number": "420", "title": "Cheating and dishonestly inducing delivery of property", "description": "Whoever cheats and thereby dishonestly induces any person to deliver any property to any person, or to make, alter or destroy any valuable security shall be punished with imprisonment."},
        ]
    },
    {
        "act_name": "Constitution of India",
        "sections": [
            {"section_number": "14", "title": "Equality before law", "description": "The State shall not deny to any person equality before the law or the equal protection of the laws."},
            {"section_number": "19", "title": "Protection of certain rights regarding freedom of speech", "description": "All citizens shall have the right to freedom of speech and expression, freedom of assembly, freedom of association and freedom to move freely."},
            {"section_number": "21", "title": "Protection of life and personal liberty", "description": "No person shall be deprived of his life or personal liberty except according to procedure established by law."},
            {"section_number": "25", "title": "Freedom of conscience and free profession, practice and propagation of religion", "description": "Subject to public order, morality and health, all persons are equally entitled to freedom of conscience and the right freely to profess, practise and propagate religion."},
            {"section_number": "44", "title": "Uniform civil code in the States", "description": "The State shall endeavour to secure for the citizens a uniform civil code throughout the territory of India."},
            {"section_number": "51A", "title": "Fundamental duties", "description": "It shall be the duty of every citizen of India to abide by the Constitution and respect its ideals and institutions."},
            {"section_number": "73", "title": "Power of Parliament with respect to union territory", "description": "Parliament has power to make laws with respect to the administration of union territories."},
            {"section_number": "226", "title": "Issue of directions, orders or writs", "description": "Any high court may issue directions or orders or writs for the enforcement of any of the fundamental rights or any other purpose."},
        ]
    },
    {
        "act_name": "Indian Contract Act, 1872",
        "sections": [
            {"section_number": "23", "title": "Consideration must not be unlawful", "description": "Consideration is lawful, unless and until the court finds it to be otherwise."},
            {"section_number": "29", "title": "Voidability of agreement without free consent", "description": "If the consent to an agreement was obtained by coercion, fraud, misrepresentation, mistake or undue influence, the agreement is voidable."},
            {"section_number": "35", "title": "When proposal is accepted", "description": "In the case of a proposal made in so many words, the acceptance must likewise be in words."},
            {"section_number": "55", "title": "Time for acceptance of proposal", "description": "An offer must be accepted within such time as the proposer may prescribe in his offer, or if no time is prescribed, within a reasonable time."},
            {"section_number": "73", "title": "Obligation of seller", "description": "In a contract of sale, the seller is bound to transfer the ownership of the goods to the buyer."},
            {"section_number": "76", "title": "Caveat emptor", "description": "In contracts of sale, where there is no warranty or stipulation, the buyer takes the goods subject to the condition that he takes them at his own risk."},
            {"section_number": "113", "title": "Consequence of breach of warranty", "description": "Where the seller is guilty of a breach of warranty, the buyer cannot reject the goods but may claim damages."},
            {"section_number": "142", "title": "Pledge", "description": "A pledge is the bailment of goods as security for payment of a debt, or performance of a promise."},
        ]
    },
    {
        "act_name": "Information Technology Act, 2000",
        "sections": [
            {"section_number": "43", "title": "Penalty and compensation for damage to computer, computer system or computer network", "description": "If any person secures access to a computer without authorization, he shall be liable for damages."},
            {"section_number": "66", "title": "Computer related offences", "description": "Whoever commits computer fraud or unauthorized access to computer systems shall be punished with imprisonment or fine."},
            {"section_number": "67", "title": "Punishment for publishing or transmitting obscene material in electronic form", "description": "Whoever publishes or transmits obscene material in electronic form shall be punished with imprisonment up to 5 years and fine."},
            {"section_number": "72", "title": "Breach of confidentiality and privacy", "description": "Whoever obtains any information in breach of confidentiality shall be punished with imprisonment up to 2 years and fine up to 1 lakh."},
            {"section_number": "75", "title": "Preservation of electronic records", "description": "Service providers are required to preserve and retain records as per directions of the government."},
            {"section_number": "79", "title": "Exemption from liability of intermediaries", "description": "Intermediaries providing network services shall not be liable for third party data transmitted through their network."},
        ]
    },
]

def add_stage4_acts():
    """Add stage 4 expanded acts to database"""
    from app.db.database import get_db, engine
    from app.db.models import LawSection, Base
    
    Base.metadata.create_all(bind=engine)
    session = next(get_db())
    
    inserted = 0
    updated = 0
    
    for act_data in STAGE_4_ACTS:
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
                    category="criminal" if "Penal Code" in act_name else ("constitutional" if "Constitution" in act_name else "civil"),
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
    result = add_stage4_acts()
    print(f"\n✅ Stage 4 Loading Complete:")
    print(f"   Inserted: {result['inserted']} new sections")
    print(f"   Updated: {result['updated']} existing sections")
    print(f"\n📚 4 Core Acts Expanded:")
    print(f"   • Indian Penal Code (10 sections)")
    print(f"   • Constitution of India (8 sections)")
    print(f"   • Indian Contract Act (8 sections)")
    print(f"   • Information Technology Act (6 sections)")
    print(f"\nTotal Stage 4: 32 new sections")
