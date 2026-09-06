export interface Precedent {
  id: string;
  title: string;
  citation: string;
  court: 'Supreme Court of India' | 'High Court of Andhra Pradesh' | 'High Court of Telangana' | 'Delhi High Court' | 'Bombay High Court';
  year: number;
  bench: string;
  category: 'arrest_bail' | 'cheque_bounce' | 'tenancy_property' | 'consumer_fraud' | 'cyber_privacy' | 'motor_accidents';
  category_label: string;
  summary: string;
  ratio_decidendi: string;
  key_principles: string[];
  applicable_statutes: string[];
  copyable_citation: string;
}

export const PRECEDENTS_DATA: Precedent[] = [
  {
    id: 'arnesh-kumar-2014',
    title: 'Arnesh Kumar v. State of Bihar & Anr.',
    citation: '(2014) 8 SCC 273',
    court: 'Supreme Court of India',
    year: 2014,
    bench: 'Hon\'ble Chandramauli Kr. Prasad & Pinaki Chandra Ghose, JJ.',
    category: 'arrest_bail',
    category_label: 'Arrest & Police Custody',
    summary: 'Landmark ruling mandating that police officers cannot automatically arrest an accused in offences punishable with imprisonment up to 7 years without satisfying Section 41 CrPC (now Section 35 BNSS).',
    ratio_decidendi: 'No arrest should be made merely because it is lawful for the police officer to do so. The police officer must satisfy himself about the necessity for arrest based on parameters laid down under the statutory checklist.',
    key_principles: [
      'Mandatory Section 41A (Section 35 BNSS) notice of appearance before arrest',
      'Magistrate must not authorize detention mechanically without recorded reasons',
      'Police officers failing to follow guidelines liable for departmental action and contempt of court'
    ],
    applicable_statutes: [
      'Bharatiya Nagarik Suraksha Sanhita, 2023 - Section 35',
      'Code of Criminal Procedure, 1973 - Section 41 & 41A',
      'Indian Penal Code - Section 498A'
    ],
    copyable_citation: 'Arnesh Kumar v. State of Bihar, (2014) 8 SCC 273'
  },
  {
    id: 'satender-kumar-antil-2022',
    title: 'Satender Kumar Antil v. Central Bureau of Investigation',
    citation: '(2022) 10 SCC 51',
    court: 'Supreme Court of India',
    year: 2022,
    bench: 'Hon\'ble Sanjay Kishan Kaul & M.M. Sundresh, JJ.',
    category: 'arrest_bail',
    category_label: 'Bail Guidelines & Liberty',
    summary: 'Comprehensive guidelines categorizing offences into four classes (A, B, C, D) and directing that bail applications must be decided within two weeks and anticipatory bail within six weeks.',
    ratio_decidendi: 'Jails in India are flooded with undertrial prisoners. The arrest is a draconian measure which should result only when it is strictly necessary. Bail is the rule and jail is the exception.',
    key_principles: [
      'Category A offences (punishable up to 7 years): Summons/Bailable warrant without custodial arrest if co-operating',
      'Strict adherence to Section 41 and 41A CrPC / Section 35 BNSS',
      'Default bail applications under Section 167(2) CrPC / Section 187 BNSS must be prioritized'
    ],
    applicable_statutes: [
      'Bharatiya Nagarik Suraksha Sanhita, 2023 - Section 479 & 480',
      'Code of Criminal Procedure, 1973 - Section 436, 437 & 439'
    ],
    copyable_citation: 'Satender Kumar Antil v. CBI, (2022) 10 SCC 51'
  },
  {
    id: 'lalita-kumari-2014',
    title: 'Lalita Kumari v. Govt. of U.P. & Ors.',
    citation: '(2014) 2 SCC 1',
    court: 'Supreme Court of India',
    year: 2014,
    bench: 'Constitution Bench (5 Judges) - P. Sathasivam, CJI, et al.',
    category: 'arrest_bail',
    category_label: 'Mandatory FIR Registration',
    summary: 'Held that registration of First Information Report (FIR) is mandatory under Section 154 CrPC (now Section 173 BNSS) if the information discloses commission of a cognizable offence.',
    ratio_decidendi: 'Registration of FIR is mandatory under Section 154 of the Code, if the information discloses commission of a cognizable offence and no preliminary inquiry is permissible in such a situation.',
    key_principles: [
      'Police cannot refuse FIR on grounds of preliminary inquiry if cognizable offence is disclosed',
      'Preliminary inquiry permitted only in matrimonial disputes, commercial offences, medical negligence, corruption, or 3-month delayed matters',
      'Preliminary inquiry must be completed within 7 to 14 days'
    ],
    applicable_statutes: [
      'Bharatiya Nagarik Suraksha Sanhita, 2023 - Section 173',
      'Code of Criminal Procedure, 1973 - Section 154'
    ],
    copyable_citation: 'Lalita Kumari v. Govt. of U.P., (2014) 2 SCC 1'
  },
  {
    id: 'dk-basu-1997',
    title: 'D.K. Basu v. State of West Bengal',
    citation: '(1997) 1 SCC 416',
    court: 'Supreme Court of India',
    year: 1997,
    bench: 'Hon\'ble Kuldip Singh & A.S. Anand, JJ.',
    category: 'arrest_bail',
    category_label: 'Custodial Violence & Arrestee Rights',
    summary: 'Formulated 11 mandatory guidelines for police personnel carrying out arrest and interrogation to eliminate custodial violence, torture, and lock-up deaths.',
    ratio_decidendi: 'Custodial violence, including torture and death in the lock ups, strikes a blow at the rule of law. Citizens retain their fundamental right to life under Article 21 even under detention.',
    key_principles: [
      'Arresting officer must wear accurate, visible name tags with designations',
      'Preparation of Arrest Memo signed by at least one witness and countersigned by arrestee',
      'Right of arrestee to have a friend or relative informed within 8-12 hours of arrest',
      'Mandatory medical examination of arrestee every 48 hours by approved doctor'
    ],
    applicable_statutes: [
      'Constitution of India - Article 21 & 22',
      'Bharatiya Nagarik Suraksha Sanhita, 2023 - Section 36 & 53'
    ],
    copyable_citation: 'D.K. Basu v. State of West Bengal, (1997) 1 SCC 416'
  },
  {
    id: 'bir-singh-2019',
    title: 'Bir Singh v. Mukesh Kumar',
    citation: '(2019) 4 SCC 197',
    court: 'Supreme Court of India',
    year: 2019,
    bench: 'Hon\'ble R. Banumathi & Indira Banerjee, JJ.',
    category: 'cheque_bounce',
    category_label: 'Cheque Dishonour & Section 138',
    summary: 'Ruled that once the signature on a cheque is admitted, the statutory presumption under Section 139 of the Negotiable Instruments Act operates that the cheque was issued in discharge of a debt or liability.',
    ratio_decidendi: 'Even if a blank signed cheque leaf is voluntarily provided towards some payment, the payee filling up the particulars does not invalidate the statutory presumption under Section 139 NI Act.',
    key_principles: [
      'Signature on the cheque creates mandatory presumption of existing debt under § 139 NI Act',
      'Onus is strictly on the drawer/accused to lead probable defence evidence to rebut presumption',
      '15-day statutory notice is a jurisdictional condition precedent before filing criminal complaint'
    ],
    applicable_statutes: [
      'Negotiable Instruments Act, 1881 - Section 138, 139 & 142'
    ],
    copyable_citation: 'Bir Singh v. Mukesh Kumar, (2019) 4 SCC 197'
  },
  {
    id: 'dashrath-rupsingh-2014',
    title: 'Dashrath Rupsingh Rathod v. State of Maharashtra',
    citation: '(2014) 9 SCC 129',
    court: 'Supreme Court of India',
    year: 2014,
    bench: 'Hon\'ble R.M. Lodha, CJI, et al.',
    category: 'cheque_bounce',
    category_label: 'Cheque Jurisdiction & Forum',
    summary: 'Led to the 2015 amendment in Section 142(2) NI Act establishing territorial jurisdiction of cheque bounce complaints where the payee bank branch is situated.',
    ratio_decidendi: 'A complaint under Section 138 NI Act can only be instituted where the payee bank maintains its account, preventing harassment across arbitrary jurisdictions.',
    key_principles: [
      'Jurisdiction lies at the place where the branch of the bank where the payee maintains account is situated',
      'Electronic presentation covered under Section 142(2)(a)',
      'Multiple cheques against same transaction can be clubbed'
    ],
    applicable_statutes: [
      'Negotiable Instruments Act, 1881 - Section 142(2)'
    ],
    copyable_citation: 'Dashrath Rupsingh Rathod v. State of Maharashtra, (2014) 9 SCC 129'
  },
  {
    id: 'vidya-drolia-2021',
    title: 'Vidya Drolia and Others v. Durga Trading Corporation',
    citation: '(2021) 2 SCC 1',
    court: 'Supreme Court of India',
    year: 2021,
    bench: 'Hon\'ble N.V. Ramana, Sanjiv Khanna & Krishna Murari, JJ.',
    category: 'tenancy_property',
    category_label: 'Tenancy Disputes & Arbitration',
    summary: 'Clarified arbitrability of tenancy disputes, ruling that tenancy disputes governed by the Transfer of Property Act are arbitrable, whereas those covered by special State Rent Control Acts are not.',
    ratio_decidendi: 'Landlord-tenant disputes under the Transfer of Property Act are arbitrable as they do not affect third-party rights and are actions in personam.',
    key_principles: [
      'Leases covered under general contract/Transfer of Property Act can use arbitration clauses',
      'Special State Rent Control Act tenancies are strictly subject to Rent Controller jurisdiction',
      'Security deposit disputes are civil money claims enforceable through summary procedure'
    ],
    applicable_statutes: [
      'Transfer of Property Act, 1882 - Section 106 & 111',
      'Arbitration and Conciliation Act, 1996 - Section 8 & 11'
    ],
    copyable_citation: 'Vidya Drolia v. Durga Trading Corporation, (2021) 2 SCC 1'
  },
  {
    id: 'lucknow-dev-1994',
    title: 'Lucknow Development Authority v. M.K. Gupta',
    citation: '(1994) 1 SCC 243',
    court: 'Supreme Court of India',
    year: 1994,
    bench: 'Hon\'ble R.M. Sahai & B.L. Hansaria, JJ.',
    category: 'consumer_fraud',
    category_label: 'Consumer Rights & Public Authority Liability',
    summary: 'Held that statutory housing boards and developers providing housing services are covered under the Consumer Protection Act, and public officers causing harassment are personally liable for damages.',
    ratio_decidendi: 'When a public authority acts oppressively causing harassment and mental agony to a citizen, the Consumer Forum has jurisdiction to award compensation and recover it from delinquent officers.',
    key_principles: [
      'Housing construction and plot allotment are "services" under Consumer Protection Act',
      'Right to compensation for delay, deficiency, and harassment',
      'Principle applied to modern e-commerce platforms and private builders alike'
    ],
    applicable_statutes: [
      'Consumer Protection Act, 2019 - Section 2(42), 35 & 39'
    ],
    copyable_citation: 'Lucknow Development Authority v. M.K. Gupta, (1994) 1 SCC 243'
  },
  {
    id: 'puttaswamy-2017',
    title: 'Justice K.S. Puttaswamy (Retd.) v. Union of India',
    citation: '(2017) 10 SCC 1',
    court: 'Supreme Court of India',
    year: 2017,
    bench: 'Constitution Bench (9 Judges) - J.S. Khehar, CJI, et al.',
    category: 'cyber_privacy',
    category_label: 'Right to Privacy & Digital Surveillance',
    summary: 'Unanimously declared that the Right to Privacy is a Fundamental Right guaranteed under Article 21 of the Indian Constitution, setting strict tests of Legality, Need, and Proportionality.',
    ratio_decidendi: 'Privacy is the constitutional core of human dignity. Any state encroachment on digital data or communication must satisfy the threefold test of legality, legitimate state aim, and proportionality.',
    key_principles: [
      'Phone tapping and unauthorized digital data surveillance violate Article 21',
      'Electronic evidence must comply with strict statutory custody chains',
      'Citizens have fundamental rights over their personal biometric and digital footprints'
    ],
    applicable_statutes: [
      'Constitution of India - Article 21',
      'Information Technology Act, 2000 - Section 43A & 69',
      'Digital Personal Data Protection Act, 2023'
    ],
    copyable_citation: 'Justice K.S. Puttaswamy v. Union of India, (2017) 10 SCC 1'
  },
  {
    id: 'shreya-singhal-2015',
    title: 'Shreya Singhal v. Union of India',
    citation: '(2015) 5 SCC 1',
    court: 'Supreme Court of India',
    year: 2015,
    bench: 'Hon\'ble J. Chelameswar & Rohinton F. Nariman, JJ.',
    category: 'cyber_privacy',
    category_label: 'Online Free Speech & Cyber Law',
    summary: 'Struck down Section 66A of the Information Technology Act, 2000 as unconstitutional, preventing arbitrary police arrest for online posts, social media comments, and speech.',
    ratio_decidendi: 'Section 66A arbitrarily, excessively, and disproportionately invades the right of free speech and upsets the balance between such right and reasonable restrictions under Article 19(2).',
    key_principles: [
      'Police cannot register FIRs under Section 66A IT Act',
      'Intermediary liability safe-harbor under Section 79 protected',
      'Government takedown orders must follow judicial or statutory review'
    ],
    applicable_statutes: [
      'Constitution of India - Article 19(1)(a) & 19(2)',
      'Information Technology Act, 2000 - Section 66A (Struck down) & Section 79'
    ],
    copyable_citation: 'Shreya Singhal v. Union of India, (2015) 5 SCC 1'
  },
  {
    id: 'pranay-sethi-2017',
    title: 'National Insurance Co. Ltd. v. Pranay Sethi',
    citation: '(2017) 16 SCC 680',
    court: 'Supreme Court of India',
    year: 2017,
    bench: 'Constitution Bench (5 Judges) - Dipak Misra, CJI, et al.',
    category: 'motor_accidents',
    category_label: 'Motor Accidents Claims & Compensation',
    summary: 'Standardized compensation calculations under the Motor Vehicles Act, fixing conventional heads (loss of estate, consortium, funeral expenses) and future prospects additions.',
    ratio_decidendi: 'To ensure uniformity and avoid speculative awards by Motor Accident Claims Tribunals, standardized mathematical multipliers and conventional heads must be uniformly applied.',
    key_principles: [
      'Standardized future prospect additions (10% to 50% depending on age and employment)',
      'Mandatory compensation for loss of consortium and estate',
      'Insurance companies strictly liable if policy was subsisting on date of accident'
    ],
    applicable_statutes: [
      'Motor Vehicles Act, 1988 - Section 166, 168 & 173',
      'Motor Vehicles Amendment Act, 2019'
    ],
    copyable_citation: 'National Insurance Co. Ltd. v. Pranay Sethi, (2017) 16 SCC 680'
  }
];
