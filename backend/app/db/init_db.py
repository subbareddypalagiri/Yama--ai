"""
YAMA AI — Database Initialization & Seeding
Run: python -m app.db.init_db
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.db.database import engine, SessionLocal
from app.db.models import Base, LawSection, LegalCategory
from app.core.constants import LEGAL_CATEGORIES


def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully.")


def seed_categories(db):
    """Seed legal categories."""
    print("Seeding legal categories...")
    for slug, name in LEGAL_CATEGORIES.items():
        existing = db.query(LegalCategory).filter_by(slug=slug).first()
        if not existing:
            db.add(LegalCategory(name=name, slug=slug, description=f"Laws related to {name}"))
    db.commit()
    print("✅ Categories seeded.")


def seed_laws(db):
    """Seed sample legal provisions."""
    print("Seeding sample legal provisions...")

    laws = [
        # ── Bharatiya Nyaya Sanhita (BNS) 2023 ──
        {
            "act_name": "Bharatiya Nyaya Sanhita, 2023",
            "section_number": "100",
            "title": "Murder",
            "description": "Whoever causes death by doing an act with the intention of causing death, or with the intention of causing such bodily injury as is likely to cause death, or with the knowledge that he is likely by such act to cause death, commits the offence of murder.",
            "keywords": "murder, homicide, death, killing, intention to kill",
            "category": "criminal",
            "punishment": "Death or imprisonment for life, and shall also be liable to fine.",
            "old_law_reference": "Indian Penal Code, Section 302",
        },
        {
            "act_name": "Bharatiya Nyaya Sanhita, 2023",
            "section_number": "101",
            "title": "Culpable Homicide not amounting to murder",
            "description": "Whoever causes death by doing an act with the intention of causing death, or with the intention of causing such bodily injury as is likely to cause death, or with the knowledge that he is likely by such act to cause death, but where the act by which the death is caused is done without premeditation in a sudden fight in the heat of passion upon a sudden quarrel, and without the offender having taken undue advantage or acted in a cruel or unusual manner.",
            "keywords": "culpable homicide, manslaughter, death, sudden fight, heat of passion",
            "category": "criminal",
            "punishment": "Imprisonment for life, or imprisonment up to 10 years, and fine.",
            "old_law_reference": "Indian Penal Code, Section 304",
        },
        {
            "act_name": "Bharatiya Nyaya Sanhita, 2023",
            "section_number": "115",
            "title": "Voluntarily causing hurt",
            "description": "Whoever does any act with the intention of thereby causing hurt to any person, or with the knowledge that he is likely thereby to cause hurt to any person, and does thereby cause hurt to any person, is said to voluntarily cause hurt.",
            "keywords": "hurt, assault, bodily harm, injury, violence",
            "category": "criminal",
            "punishment": "Imprisonment up to one year, or fine up to ten thousand rupees, or both.",
            "old_law_reference": "Indian Penal Code, Section 323",
        },
        {
            "act_name": "Bharatiya Nyaya Sanhita, 2023",
            "section_number": "303",
            "title": "Theft",
            "description": "Whoever, intending to take dishonestly any moveable property out of the possession of any person without that person's consent, moves that property in order to such taking, is said to commit theft.",
            "keywords": "theft, stealing, dishonest taking, moveable property, stolen",
            "category": "criminal",
            "punishment": "Imprisonment up to three years, or fine, or both.",
            "old_law_reference": "Indian Penal Code, Section 378",
        },
        {
            "act_name": "Bharatiya Nyaya Sanhita, 2023",
            "section_number": "308",
            "title": "Extortion",
            "description": "Whoever intentionally puts any person in fear of any injury to that person or to any other person, and thereby dishonestly induces the person so put in fear to deliver to any person any property or valuable security, or anything signed or sealed which may be converted into a valuable security, commits extortion.",
            "keywords": "extortion, threat, fear, coercion, blackmail, demand",
            "category": "criminal",
            "punishment": "Imprisonment up to three years, or fine, or both.",
            "old_law_reference": "Indian Penal Code, Section 383",
        },
        {
            "act_name": "Bharatiya Nyaya Sanhita, 2023",
            "section_number": "316",
            "title": "Criminal Breach of Trust",
            "description": "Whoever, being in any manner entrusted with property, or with any dominion over property, dishonestly misappropriates or converts to his own use that property, or dishonestly uses or disposes of that property in violation of any direction of law prescribing the mode in which such trust is to be discharged, commits criminal breach of trust.",
            "keywords": "breach of trust, misappropriation, embezzlement, trust, dishonest",
            "category": "criminal",
            "punishment": "Imprisonment up to three years, or fine, or both.",
            "old_law_reference": "Indian Penal Code, Section 405",
        },
        {
            "act_name": "Bharatiya Nyaya Sanhita, 2023",
            "section_number": "318",
            "title": "Cheating",
            "description": "Whoever, by deceiving any person, fraudulently or dishonestly induces the person so deceived to deliver any property to any person, or to consent that any person shall retain any property, or intentionally induces the person so deceived to do or omit to do anything which he would not do or omit if he were not so deceived, and which act or omission causes or is likely to cause damage or harm to that person in body, mind, reputation or property, is said to cheat.",
            "keywords": "cheating, fraud, deception, dishonest, inducement, scam",
            "category": "criminal",
            "punishment": "Imprisonment up to three years, or fine, or both.",
            "old_law_reference": "Indian Penal Code, Section 415/420",
        },
        {
            "act_name": "Bharatiya Nyaya Sanhita, 2023",
            "section_number": "351",
            "title": "Criminal Intimidation",
            "description": "Whoever threatens another with any injury to his person, reputation or property, or to the person or reputation of any one in whom that person is interested, with intent to cause alarm to that person, or to cause that person to do any act which he is not legally bound to do, or to omit to do any act which that person is legally entitled to do, as the means of avoiding the execution of such threat, commits criminal intimidation.",
            "keywords": "intimidation, threat, alarm, criminal threat, menace",
            "category": "criminal",
            "punishment": "Imprisonment up to two years, or fine, or both.",
            "old_law_reference": "Indian Penal Code, Section 503/506",
        },
        {
            "act_name": "Bharatiya Nyaya Sanhita, 2023",
            "section_number": "63",
            "title": "Sexual harassment",
            "description": "A man committing any of the following acts: (i) physical contact and advances involving unwelcome and explicit sexual overtures; (ii) a demand or request for sexual favours; (iii) showing pornography against the will of a woman; (iv) making sexually coloured remarks, shall be guilty of the offence of sexual harassment.",
            "keywords": "sexual harassment, unwelcome advances, sexual favours, workplace harassment",
            "category": "criminal",
            "punishment": "Imprisonment up to three years, or fine, or both.",
            "old_law_reference": "Indian Penal Code, Section 354A",
        },
        {
            "act_name": "Bharatiya Nyaya Sanhita, 2023",
            "section_number": "85",
            "title": "Cruelty by husband or relatives of husband",
            "description": "Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty shall be punished. Cruelty means (a) any wilful conduct which is of such a nature as is likely to drive the woman to commit suicide or to cause grave injury or danger to life, limb or health; (b) harassment of the woman where such harassment is with a view to coercing her or any person related to her to meet any unlawful demand for any property or valuable security.",
            "keywords": "domestic violence, cruelty, dowry harassment, husband, marital cruelty",
            "category": "criminal",
            "punishment": "Imprisonment up to three years and fine.",
            "old_law_reference": "Indian Penal Code, Section 498A",
        },

        # ── Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023 ──
        {
            "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
            "section_number": "173",
            "title": "FIR - Information in cognizable cases",
            "description": "Every information relating to the commission of a cognizable offence, if given orally to an officer in charge of a police station, shall be reduced to writing by him or under his direction, and be read over to the informant; and every such information, whether given in writing or reduced to writing as aforesaid, shall be signed by the person giving it.",
            "keywords": "FIR, first information report, police complaint, cognizable offence",
            "category": "criminal",
            "punishment": None,
            "old_law_reference": "Code of Criminal Procedure, Section 154",
        },
        {
            "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
            "section_number": "175",
            "title": "Police officer's power to investigate cognizable case",
            "description": "Any officer in charge of a police station may, without the order of a Magistrate, investigate any cognizable case which a court having jurisdiction over the local area within the limits of such station would have power to inquire into or try.",
            "keywords": "investigation, police power, cognizable offence, inquiry",
            "category": "criminal",
            "punishment": None,
            "old_law_reference": "Code of Criminal Procedure, Section 156",
        },
        {
            "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
            "section_number": "480",
            "title": "Bail in non-bailable offence",
            "description": "When any person accused of or suspected of the commission of any non-bailable offence is arrested or detained without warrant by an officer in charge of a police station or appears or is brought before a Court, he may be released on bail. The court shall consider the nature of the accusation, the severity of the punishment, and the character of the evidence.",
            "keywords": "bail, non-bailable offence, arrest, detention, release",
            "category": "criminal",
            "punishment": None,
            "old_law_reference": "Code of Criminal Procedure, Section 437",
        },
        {
            "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
            "section_number": "482",
            "title": "Anticipatory Bail",
            "description": "When any person has reason to believe that he may be arrested on an accusation of having committed a non-bailable offence, he may apply to the High Court or the Court of Session for a direction that in the event of such arrest, he shall be released on bail.",
            "keywords": "anticipatory bail, pre-arrest bail, apprehension of arrest",
            "category": "criminal",
            "punishment": None,
            "old_law_reference": "Code of Criminal Procedure, Section 438",
        },

        # ── Bharatiya Sakshya Adhiniyam (BSA) 2023 ──
        {
            "act_name": "Bharatiya Sakshya Adhiniyam, 2023",
            "section_number": "57",
            "title": "Electronic Records as Evidence",
            "description": "Information contained in an electronic record which is printed on paper, stored, recorded or copied in optical or magnetic media produced by a computer shall be deemed to be a document and shall be admissible in evidence without further proof or production of the original, if the conditions mentioned in this section are satisfied.",
            "keywords": "electronic evidence, digital record, computer evidence, e-evidence, digital proof",
            "category": "criminal",
            "punishment": None,
            "old_law_reference": "Indian Evidence Act, Section 65B",
        },
        {
            "act_name": "Bharatiya Sakshya Adhiniyam, 2023",
            "section_number": "23",
            "title": "Confession to police not to be proved",
            "description": "No confession made to a police officer shall be proved as against a person accused of any offence.",
            "keywords": "confession, police, inadmissible, statement, accused",
            "category": "criminal",
            "punishment": None,
            "old_law_reference": "Indian Evidence Act, Section 25",
        },

        # ── Constitution of India ──
        {
            "act_name": "Constitution of India",
            "section_number": "Article 14",
            "title": "Equality before law",
            "description": "The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.",
            "keywords": "equality, equal protection, fundamental rights, discrimination",
            "category": "constitutional",
            "punishment": None,
            "old_law_reference": None,
        },
        {
            "act_name": "Constitution of India",
            "section_number": "Article 19",
            "title": "Protection of certain rights regarding freedom of speech",
            "description": "All citizens shall have the right to freedom of speech and expression; to assemble peaceably and without arms; to form associations or unions; to move freely throughout the territory of India; to reside and settle in any part of the territory of India; and to practise any profession, or to carry on any occupation, trade or business.",
            "keywords": "freedom of speech, expression, assembly, movement, profession, fundamental rights",
            "category": "constitutional",
            "punishment": None,
            "old_law_reference": None,
        },
        {
            "act_name": "Constitution of India",
            "section_number": "Article 21",
            "title": "Protection of life and personal liberty",
            "description": "No person shall be deprived of his life or personal liberty except according to procedure established by law.",
            "keywords": "right to life, personal liberty, fundamental rights, due process",
            "category": "constitutional",
            "punishment": None,
            "old_law_reference": None,
        },
        {
            "act_name": "Constitution of India",
            "section_number": "Article 32",
            "title": "Remedies for enforcement of fundamental rights",
            "description": "The right to move the Supreme Court by appropriate proceedings for the enforcement of the rights conferred by this Part is guaranteed. The Supreme Court shall have power to issue directions or orders or writs for the enforcement of any of the rights conferred by this Part.",
            "keywords": "writ petition, Supreme Court, fundamental rights enforcement, habeas corpus, mandamus",
            "category": "constitutional",
            "punishment": None,
            "old_law_reference": None,
        },

        # ── Information Technology Act, 2000 ──
        {
            "act_name": "Information Technology Act, 2000",
            "section_number": "43",
            "title": "Penalty for damage to computer system",
            "description": "If any person without permission of the owner or any other person who is in charge of a computer, computer system or computer network accesses or secures access, downloads, copies or extracts any data, introduces any computer contaminant or computer virus, damages or causes to be damaged any computer, computer system or computer network, disrupts or causes disruption, denies or causes the denial of access, or charges the services availed of by a person to the account of another person, he shall be liable to pay damages by way of compensation to the person so affected.",
            "keywords": "hacking, unauthorized access, computer damage, cyber attack, data theft",
            "category": "cyber",
            "punishment": "Compensation up to Rs. 5 crore as determined by Adjudicating Officer.",
            "old_law_reference": None,
        },
        {
            "act_name": "Information Technology Act, 2000",
            "section_number": "66",
            "title": "Computer related offences",
            "description": "If any person, dishonestly or fraudulently, does any act referred to in section 43, he shall be punishable with imprisonment for a term which may extend to three years or with fine which may extend to five lakh rupees or with both.",
            "keywords": "hacking, cyber crime, fraud, computer offence, dishonest",
            "category": "cyber",
            "punishment": "Imprisonment up to 3 years, or fine up to Rs. 5 lakh, or both.",
            "old_law_reference": None,
        },
        {
            "act_name": "Information Technology Act, 2000",
            "section_number": "66A",
            "title": "Punishment for sending offensive messages (STRUCK DOWN)",
            "description": "This section was struck down by the Supreme Court of India in Shreya Singhal v. Union of India (2015) as unconstitutional, being violative of Article 19(1)(a) of the Constitution. It previously dealt with punishment for sending offensive messages through communication service.",
            "keywords": "offensive messages, online speech, struck down, unconstitutional, Shreya Singhal",
            "category": "cyber",
            "punishment": "SECTION STRUCK DOWN - No longer applicable.",
            "old_law_reference": None,
        },
        {
            "act_name": "Information Technology Act, 2000",
            "section_number": "67",
            "title": "Punishment for publishing obscene material in electronic form",
            "description": "Whoever publishes or transmits or causes to be published or transmitted in the electronic form, any material which is lascivious or appeals to the prurient interest or if its effect is such as to tend to deprave and corrupt persons, shall be punished on first conviction with imprisonment for a term which may extend to three years and with fine.",
            "keywords": "obscene content, pornography, electronic publishing, online obscenity",
            "category": "cyber",
            "punishment": "First conviction: imprisonment up to 3 years + fine up to Rs. 5 lakh. Subsequent: imprisonment up to 5 years + fine up to Rs. 10 lakh.",
            "old_law_reference": None,
        },

        # ── Consumer Protection Act, 2019 ──
        {
            "act_name": "Consumer Protection Act, 2019",
            "section_number": "2(7)",
            "title": "Definition of Consumer",
            "description": "Consumer means any person who buys any goods or hires or avails of any service for a consideration which has been paid or promised or partly paid and partly promised, or under any system of deferred payment and includes any user of such goods or beneficiary of such service, but does not include a person who obtains such goods for resale or for any commercial purpose.",
            "keywords": "consumer, buyer, service user, goods, purchase",
            "category": "consumer",
            "punishment": None,
            "old_law_reference": "Consumer Protection Act 1986, Section 2(1)(d)",
        },
        {
            "act_name": "Consumer Protection Act, 2019",
            "section_number": "34",
            "title": "District Consumer Disputes Redressal Commission",
            "description": "A complaint relating to goods or services where the value does not exceed one crore rupees shall be filed before the District Commission. The District Commission shall have the power to adjudicate complaints and provide remedies including replacement of goods, refund, compensation for losses, and punitive damages.",
            "keywords": "consumer complaint, district commission, consumer forum, redressal, compensation",
            "category": "consumer",
            "punishment": None,
            "old_law_reference": "Consumer Protection Act 1986, Section 11",
        },
        {
            "act_name": "Consumer Protection Act, 2019",
            "section_number": "2(28)",
            "title": "Misleading Advertisement",
            "description": "Misleading advertisement in relation to any product or service, means an advertisement which falsely describes such product or service; or gives a false guarantee to, or is likely to mislead the consumers as to the nature, substance, quantity or quality of such product or service; or conveys an express or implied representation which, if made by the manufacturer or seller, would constitute an unfair trade practice.",
            "keywords": "misleading advertisement, false advertising, unfair trade, consumer deception",
            "category": "consumer",
            "punishment": None,
            "old_law_reference": None,
        },

        # ── Motor Vehicles Act, 1988 ──
        {
            "act_name": "Motor Vehicles Act, 1988",
            "section_number": "185",
            "title": "Driving by a drunken person or by a person under the influence of drugs",
            "description": "Whoever, while driving, or attempting to drive, a motor vehicle has, in his blood, alcohol exceeding 30 mg per 100 ml of blood detected in a test by a breath analyser, shall be punishable for the first offence with imprisonment for a term which may extend to six months, or with fine which may extend to ten thousand rupees, or with both.",
            "keywords": "drunk driving, DUI, alcohol, intoxication, breath test, driving under influence",
            "category": "motor_vehicle",
            "punishment": "First offence: imprisonment up to 6 months, or fine up to Rs. 10,000, or both. Subsequent: imprisonment up to 2 years, or fine up to Rs. 15,000, or both.",
            "old_law_reference": None,
        },
        {
            "act_name": "Motor Vehicles Act, 1988",
            "section_number": "184",
            "title": "Driving dangerously",
            "description": "Whoever drives a motor vehicle at a speed or in a manner which is dangerous to the public, having regard to all the circumstances of the case, including the nature, condition and use of the place where the vehicle is driven and the amount of traffic which actually is or might reasonably be expected to be in the place, shall be punishable.",
            "keywords": "rash driving, dangerous driving, over speeding, reckless driving, road accident",
            "category": "motor_vehicle",
            "punishment": "First offence: imprisonment up to 1 year, or fine up to Rs. 5,000, or both. If causing injury: imprisonment up to 6 months, or fine up to Rs. 10,000, or both.",
            "old_law_reference": None,
        },
        {
            "act_name": "Motor Vehicles Act, 1988",
            "section_number": "166",
            "title": "Application for compensation",
            "description": "An application for compensation arising out of an accident of the nature specified in sub-section (1) of section 165 may be made by the person who has sustained the injury, or by the owner of the property, or where death has resulted from the accident, by all or any of the legal representatives of the deceased, or by any agent duly authorised by the person injured or all or any of the legal representatives of the deceased.",
            "keywords": "motor accident, compensation, claim, injury, death, road accident, MACT",
            "category": "motor_vehicle",
            "punishment": None,
            "old_law_reference": None,
        },

        # ── Protection of Women from Domestic Violence Act, 2005 ──
        {
            "act_name": "Protection of Women from Domestic Violence Act, 2005",
            "section_number": "3",
            "title": "Definition of domestic violence",
            "description": "Any act, omission or commission or conduct of the respondent shall constitute domestic violence in case it harms or injures or endangers the health, safety, life, limb or well-being, whether mental or physical, of the aggrieved person or tends to do so and includes causing physical abuse, sexual abuse, verbal and emotional abuse and economic abuse.",
            "keywords": "domestic violence, abuse, physical abuse, emotional abuse, economic abuse, women protection",
            "category": "criminal",
            "punishment": None,
            "old_law_reference": None,
        },

        # ── Right to Information Act, 2005 ──
        {
            "act_name": "Right to Information Act, 2005",
            "section_number": "6",
            "title": "Request for obtaining information",
            "description": "A person who desires to obtain any information under this Act shall make a request in writing or through electronic means in English or Hindi or in the official language of the area in which the application is being made, accompanied by the prescribed fee, to the Public Information Officer of the concerned public authority.",
            "keywords": "RTI, right to information, public information, government transparency, PIO",
            "category": "constitutional",
            "punishment": None,
            "old_law_reference": None,
        },
    ]

    for law_data in laws:
        existing = db.query(LawSection).filter_by(
            act_name=law_data["act_name"],
            section_number=law_data["section_number"]
        ).first()
        if not existing:
            db.add(LawSection(**law_data))

    db.commit()
    count = db.query(LawSection).count()
    print(f"✅ Laws seeded. Total sections in database: {count}")


def init_database():
    """Initialize database: create tables and seed data."""
    create_tables()
    db = SessionLocal()
    try:
        seed_categories(db)
        seed_laws(db)
    finally:
        db.close()
    print("\n🎉 Database initialization complete!")


if __name__ == "__main__":
    init_database()
