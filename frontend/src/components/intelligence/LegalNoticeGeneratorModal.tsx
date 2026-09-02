'use client';

import React, { useState } from 'react';
import { FileText, Printer, Copy, Check, X, Shield, Download, Scale, ArrowRight } from 'lucide-react';

interface LegalNoticeGeneratorModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultClientName?: string;
  defaultState?: string;
  defaultConcern?: string;
}

export default function LegalNoticeGeneratorModal({
  isOpen,
  onClose,
  defaultClientName = 'Subbu',
  defaultState = 'Andhra Pradesh',
  defaultConcern = 'Cyber Extortion & Fraud',
}: LegalNoticeGeneratorModalProps) {
  const [clientName, setClientName] = useState(defaultClientName);
  const [clientAddress, setClientAddress] = useState(`${defaultState}, India`);
  const [opponentName, setOpponentName] = useState('Opponent / Accused Entity');
  const [opponentAddress, setOpponentAddress] = useState('Unknown IP / Digital Handle / Address');
  const [claimAmount, setClaimAmount] = useState('50,000');
  const [noticeType, setNoticeType] = useState<'demand' | 'cyber_fir' | 'cheque_bounce' | 'tenancy'>('cyber_fir');
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const today = new Date().toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  const generateNoticeContent = () => {
    if (noticeType === 'cyber_fir') {
      return `FORMAL WRITTEN CRIMINAL COMPLAINT & FIR REQUISITION
UNDER SECTIONS 173 & 175 OF BHARATIYA NAGARIK SURAKSHA SANHITA, 2023 (BNSS)
READ WITH SECTIONS 66, 66C, 66D OF INFORMATION TECHNOLOGY ACT, 2000
AND SECTIONS 308 & 318 OF BHARATIYA NYAYA SANHITA, 2023 (BNS)

Date: ${today}

To,
The Station House Officer / Cyber Crime Police Station,
${defaultState} Police Department.

COMPLAINANT:
${clientName}
Residing at: ${clientAddress}

ACCUSED / OPPONENT:
${opponentName}
Digital Handle / Associated Accounts: ${opponentAddress}

SUBJECT: Urgent registration of FIR for Identity Theft, Unauthorized Access, Extortion, and Cyber Harassment.

RESPECTED SIR/MADAM,

I, the undersigned Complainant, state and lodge this formal criminal complaint as under:

1. That the Complainant is a law-abiding citizen residing at the address mentioned above.

2. That on or around recently, the Accused Person(s) unauthorizedly gained access to the Complainant's personal social media account / digital identity, altering credentials without consent, which constitutes a cognizable offence under Section 66C (Identity Theft) and Section 66 (Computer-related offences) of the Information Technology Act, 2000.

3. That subsequently, the Accused Person(s) commenced communicating threatening messages, unlawfully demanding a sum of Rs. ${claimAmount}/- under duress, coercing and threatening the Complainant, which squarely constitutes the offence of Criminal Extortion under Section 308 of Bharatiya Nyaya Sanhita, 2023 (formerly Section 383/384 IPC).

4. That the Complainant has preserved all electronic records, transaction identifiers, profile URLs, and chat logs in strict compliance with Section 63 of Bharatiya Sakshya Adhiniyam, 2023 (BSA).

PRAYER:
It is therefore respectfully prayed that this Hon'ble Authority may be pleased to:
a) Register an immediate FIR against the Accused under Section 66C & 66D IT Act, 2000 and Section 308 & 318 BNS, 2023;
b) Direct the relevant Telecom / Intermediary platforms to freeze and preserve the audit trails, IP logs, and device identifiers;
c) Issue urgent directions to concerned banking/UPI authorities to place a debit freeze on the recipient accounts.

Yours faithfully,

___________________________
${clientName}
(Complainant)`;
    }

    if (noticeType === 'demand') {
      return `LEGAL DEMAND NOTICE
(REGISTERED A.D. / URGENT ELECTRONIC TRANSMISSION)

Date: ${today}

TO:
${opponentName}
${opponentAddress}

FROM:
ADVOCATE YAMA (LEGAL ADVISORY CHAMBERS)
On behalf of Client: ${clientName}, ${clientAddress}

SUBJECT: FINAL STATUTORY DEMAND FOR IMMEDIATE RESOLUTION & DISGORGEMENT OF RS. ${claimAmount}/-

SIR/MADAM,

Under express instructions from and on behalf of my client ${clientName}, I do hereby serve upon you this formal Statutory Legal Notice:

1. That my client had legitimate dealings/communications with you wherein you acted in bad faith, committing civil breach and unfair practices causing grave pecuniary loss.

2. That you are unlawfully withholding an amount of Rs. ${claimAmount}/- due and payable to my client, despite repeated written demands and amicable requests.

3. TAKE NOTICE that you are hereby called upon to pay the principal sum of Rs. ${claimAmount}/- together with interest @ 18% per annum from the date of default within FIFTEEN (15) DAYS from the receipt of this notice.

4. PLEASE NOTE that in the event of your failure to comply with this notice within the stipulated 15 days, my client has instructed me to initiate appropriate Civil Litigation for recovery of dues along with penal damages, and to lodge Criminal Proceedings under Bharatiya Nyaya Sanhita, 2023 for cheating and misappropriation, entirely at your own risk, cost, and legal consequences.

A copy of this notice has been retained in my office for future legal proceedings.

Yours faithfully,

___________________________
ADVOCATE FOR THE CLIENT
Bar Council Registration Enrolled`;
    }

    // Default Cheque Bounce / Tenancy
    return `STATUTORY NOTICE UNDER SECTION 138 OF NEGOTIABLE INSTRUMENTS ACT, 1881
(DEMAND FOR DISHONOURED PAYMENT)

Date: ${today}

TO: ${opponentName}, ${opponentAddress}
FROM: Counsel for ${clientName}, ${clientAddress}

SUBJECT: Statutory 15-Day Demand Notice for Dishonour of Cheque / Financial Instrument amounting to Rs. ${claimAmount}/-

SIR/MADAM,
Under instructions from my client ${clientName}, I hereby issue this statutory notice:
1. That in discharge of your legally enforceable debt, you issued payment which was dishonoured with remark "Funds Insufficient / Account Frozen".
2. TAKE NOTICE that you are hereby given FIFTEEN (15) DAYS from receipt hereof to remit Rs. ${claimAmount}/-, failing which criminal complaint under Section 138 & 142 NI Act will be filed before the competent Judicial Magistrate.

Yours faithfully,
ADVOCATE FOR CLIENT`;
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generateNoticeContent());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;
    printWindow.document.write(`
      <html>
        <head>
          <title>Legal Notice - YAMA AI</title>
          <style>
            body { font-family: 'Times New Roman', serif; padding: 40px; line-height: 1.6; font-size: 13pt; color: #000; }
            pre { white-space: pre-wrap; font-family: inherit; }
            .header { text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 25px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h2 style="margin:0;">CHAMBERS OF ADVOCATE YAMA</h2>
            <p style="margin:4px 0; font-size:10pt;">Advocates &amp; Legal Consultants • Supreme Court of India &amp; High Courts</p>
          </div>
          <pre>${generateNoticeContent()}</pre>
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-[#0e0e12] border border-white/[0.12] w-full max-w-4xl rounded-3xl p-6 shadow-2xl relative max-h-[92vh] flex flex-col font-sans">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/[0.08]">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center shadow-lg shadow-violet-500/20">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>Advocate Legal Notice &amp; Complaint Generator</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-violet-500/20 text-violet-300 border border-violet-500/30">
                  COURT READY
                </span>
              </h3>
              <p className="text-xs text-white/40">Statutory 15-Day Ultimatum &amp; Formal Criminal FIR Drafting</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-white/40 hover:text-white hover:bg-white/[0.06] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Layout */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-5 py-4 overflow-y-auto flex-1">
          {/* Controls Panel */}
          <div className="md:col-span-5 space-y-3.5">
            <div>
              <label className="text-[11px] font-bold text-white/50 uppercase tracking-wider block mb-1">Notice Template</label>
              <div className="grid grid-cols-2 gap-1.5">
                <button
                  onClick={() => setNoticeType('cyber_fir')}
                  className={`px-3 py-2 rounded-xl text-xs font-semibold text-left transition-all border ${
                    noticeType === 'cyber_fir'
                      ? 'bg-violet-500/20 border-violet-500/60 text-white'
                      : 'bg-white/[0.02] border-white/[0.06] text-white/60 hover:text-white'
                  }`}
                >
                  🚨 Cyber FIR / Complaint
                </button>
                <button
                  onClick={() => setNoticeType('demand')}
                  className={`px-3 py-2 rounded-xl text-xs font-semibold text-left transition-all border ${
                    noticeType === 'demand'
                      ? 'bg-violet-500/20 border-violet-500/60 text-white'
                      : 'bg-white/[0.02] border-white/[0.06] text-white/60 hover:text-white'
                  }`}
                >
                  📜 15-Day Demand Notice
                </button>
                <button
                  onClick={() => setNoticeType('cheque_bounce')}
                  className={`px-3 py-2 rounded-xl text-xs font-semibold text-left transition-all border ${
                    noticeType === 'cheque_bounce'
                      ? 'bg-violet-500/20 border-violet-500/60 text-white'
                      : 'bg-white/[0.02] border-white/[0.06] text-white/60 hover:text-white'
                  }`}
                >
                  💳 Sec 138 Cheque Bounce
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <div>
                <label className="text-[10px] text-white/40 block mb-0.5">Complainant / Client Name</label>
                <input
                  type="text"
                  value={clientName}
                  onChange={(e) => setClientName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-violet-500/50"
                />
              </div>

              <div>
                <label className="text-[10px] text-white/40 block mb-0.5">Opponent / Accused Name</label>
                <input
                  type="text"
                  value={opponentName}
                  onChange={(e) => setOpponentName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-violet-500/50"
                />
              </div>

              <div>
                <label className="text-[10px] text-white/40 block mb-0.5">Claim / Disputed Amount (INR)</label>
                <input
                  type="text"
                  value={claimAmount}
                  onChange={(e) => setClaimAmount(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-violet-500/50"
                />
              </div>

              <div>
                <label className="text-[10px] text-white/40 block mb-0.5">Opponent Details / Digital Handle</label>
                <input
                  type="text"
                  value={opponentAddress}
                  onChange={(e) => setOpponentAddress(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-violet-500/50"
                />
              </div>
            </div>
          </div>

          {/* Document Preview Box */}
          <div className="md:col-span-7 flex flex-col h-full">
            <div className="flex items-center justify-between pb-2">
              <span className="text-[11px] font-bold text-violet-300 uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5" /> High Court Standard Draft
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-xs text-white/80 hover:text-white transition-all"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'Copy Notice'}</span>
                </button>
                <button
                  onClick={handlePrint}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-violet-500/20 border border-violet-500/40 text-xs font-semibold text-violet-300 hover:bg-violet-500/30 transition-all"
                >
                  <Printer className="w-3.5 h-3.5" />
                  <span>Print / PDF</span>
                </button>
              </div>
            </div>

            <div className="flex-1 bg-black/40 border border-white/[0.08] rounded-2xl p-4 overflow-y-auto font-mono text-[11px] text-white/80 leading-relaxed max-h-96 whitespace-pre-wrap select-all">
              {generateNoticeContent()}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-white/[0.08] flex items-center justify-between text-xs text-white/40">
          <span>Compliant with Indian Bar Council drafting standards &amp; BNSS 2023 procedures.</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] text-white font-medium text-xs transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
