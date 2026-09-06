'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  FileText,
  Printer,
  Download,
  Copy,
  Check,
  Sparkles,
  Shield,
  Scale,
  Calendar,
  IndianRupee,
  User,
  Building,
  AlertCircle,
  FolderPlus
} from 'lucide-react';
import { PRECEDENTS_DATA } from '@/data/precedents_data';

export type NoticeTemplateType =
  | 'section_138'
  | 'tenant_refund'
  | 'consumer_demand'
  | 'police_41a_safeguard'
  | 'mv_act_136a';

interface NoticeConfig {
  id: NoticeTemplateType;
  title: string;
  badge: string;
  statute: string;
  statutory_period_days: number;
  description: string;
}

const TEMPLATES: NoticeConfig[] = [
  {
    id: 'section_138',
    title: 'Cheque Dishonour Statutory Notice',
    badge: 'Criminal & Financial',
    statute: 'Section 138 Negotiable Instruments Act, 1881',
    statutory_period_days: 15,
    description: 'Mandatory 15-day statutory demand notice before initiating criminal proceedings for bounced cheques.'
  },
  {
    id: 'tenant_refund',
    title: 'Tenant Security Deposit Recovery Notice',
    badge: 'Tenancy & Property',
    statute: 'Transfer of Property Act § 106 & State Tenancy Act § 21',
    statutory_period_days: 15,
    description: 'Formal demand for unlawful withholding of advance security deposit after vacating premises.'
  },
  {
    id: 'consumer_demand',
    title: 'Consumer Protection Demand Notice',
    badge: 'Consumer Rights',
    statute: 'Consumer Protection Act, 2019 - Section 35',
    statutory_period_days: 30,
    description: 'Statutory demand against e-commerce sellers, builders, or service providers for deficiency & fraud.'
  },
  {
    id: 'police_41a_safeguard',
    title: 'BNSS § 35 / CrPC § 41A Police Representation',
    badge: 'Criminal Defense',
    statute: 'BNSS 2023 § 35 (CrPC § 41A) & Arnesh Kumar Guidelines',
    statutory_period_days: 7,
    description: 'Formal letter to Station House Officer agreeing to co-operate and invoking arrest immunity guidelines.'
  },
  {
    id: 'mv_act_136a',
    title: 'Traffic Challan Virtual Court Contest',
    badge: 'Traffic & Motor Vehicles',
    statute: 'Motor Vehicles Act § 136A & Electronic Enforcement Rules 2021',
    statutory_period_days: 15,
    description: 'Official representation contesting automatic camera speed challan for lack of statutory calibration certificate.'
  }
];

export default function LegalNoticeStudio({ initialTemplate }: { initialTemplate?: string }) {
  const [selectedTemplate, setSelectedTemplate] = useState<NoticeTemplateType>('section_138');
  
  // Form State
  const [advocateName, setAdvocateName] = useState('Advocate K. Subba Reddy');
  const [barEnrollment, setBarEnrollment] = useState('AP/2451/2021');
  const [clientName, setClientName] = useState('M. Rajesh Kumar');
  const [clientAddress, setClientAddress] = useState('Flat 402, Sri Sai Nilayam, Gachibowli, Hyderabad - 500032');
  
  const [oppositePartyName, setOppositePartyName] = useState('V. Suresh Babu');
  const [oppositePartyAddress, setOppositePartyAddress] = useState('House No. 12-4-89, Main Road, Vijayawada - 520001');
  
  const [instrumentNumber, setInstrumentNumber] = useState('CHQ-849201');
  const [bankOrAuthority, setBankOrAuthority] = useState('State Bank of India, Somajiguda Branch');
  const [incidentDate, setIncidentDate] = useState('2026-08-15');
  const [demandAmount, setDemandAmount] = useState('1,50,000');
  const [specificFacts, setSpecificFacts] = useState(
    'The cheque was presented for clearance on 15-08-2026 and was dishonoured with the bank return memo endorsed "FUNDS INSUFFICIENT" on 18-08-2026.'
  );

  const [isCopied, setIsCopied] = useState(false);
  const [isSavingCase, setIsSavingCase] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (initialTemplate && TEMPLATES.some((t) => t.id === initialTemplate)) {
      setSelectedTemplate(initialTemplate as NoticeTemplateType);
    }
  }, [initialTemplate]);

  // Update default placeholders when template changes
  const handleTemplateChange = (type: NoticeTemplateType) => {
    setSelectedTemplate(type);
    if (type === 'section_138') {
      setInstrumentNumber('CHQ-849201');
      setBankOrAuthority('State Bank of India, Somajiguda Branch');
      setDemandAmount('1,50,000');
      setSpecificFacts('The cheque was issued towards legally enforceable debt and returned unpaid with endorsement "FUNDS INSUFFICIENT".');
    } else if (type === 'tenant_refund') {
      setInstrumentNumber('LEASE-AGR-2023');
      setBankOrAuthority('Landlord / Property Owner');
      setDemandAmount('75,000');
      setSpecificFacts('Premises vacated in pristine condition on 31-07-2026 with all utility bills cleared. Landlord unlawfully withheld security deposit without inspection report.');
    } else if (type === 'consumer_demand') {
      setInstrumentNumber('INV-ECOM-99124');
      setBankOrAuthority('XYZ Electronics & Retail Pvt Ltd');
      setDemandAmount('45,000');
      setSpecificFacts('Product delivered with severe manufacturing defect. Despite multiple service requests and warranty coverage, replacement and refund were wrongfully refused.');
    } else if (type === 'police_41a_safeguard') {
      setInstrumentNumber('Cr. No. 142/2026');
      setBankOrAuthority('Station House Officer, Madhapur Police Station');
      setDemandAmount('0');
      setSpecificFacts('Client is ready and willing to join investigation. Notice under Section 35 BNSS is acknowledged and no custodial arrest is warrantable as offence carries under 7 years.');
    } else if (type === 'mv_act_136a') {
      setInstrumentNumber('CHLN-AP-2026-9021');
      setBankOrAuthority('Virtual Traffic Court / Commissioner of Police');
      setDemandAmount('2,000');
      setSpecificFacts('Challan issued via automated speed trap without displaying calibration certificate of speed sensor or signboards 100 meters prior as mandated by Central MV Rules.');
    }
  };

  const currentConfig = TEMPLATES.find((t) => t.id === selectedTemplate)!;
  const todayFormatted = new Date().toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
  const refCode = `YAMA/STAT/${selectedTemplate.toUpperCase()}/${Math.floor(100000 + Math.random() * 900000)}`;

  // Generate Notice Body
  const generateNoticeText = () => {
    return `
REGISTERED POST WITH ACKNOWLEDGEMENT DUE (RPAD) / SPEED POST

LEGAL NOTICE UNDER ${currentConfig.statute.toUpperCase()}

Ref No: ${refCode}
Date: ${todayFormatted}

TO:
${oppositePartyName}
${oppositePartyAddress}

FROM:
${advocateName}
Advocate & Legal Counsel (Enrollment No: ${barEnrollment})
Office at Chamber 14, High Court Complex
Email: counsel@yama-ai.legal | Helpline: +91-40-2345-6789

UNDER INSTRUCTIONS FROM AND ON BEHALF OF MY CLIENT:
${clientName}, residing at ${clientAddress}, I hereby serve upon you this formal statutory legal notice as follows:

1. That my client is a law-abiding citizen and engaged in lawful transactions with you.

2. That concerning Reference / Instrument No. ${instrumentNumber} dated ${incidentDate} involving ${bankOrAuthority}, the following material facts occurred:
${specificFacts}

3. That under the provisions of ${currentConfig.statute}, your actions constitute a direct breach of statutory duties and cause severe financial loss, mental harassment, and legal injury to my client.

4. That as held by the Hon'ble Supreme Court of India, statutory compliance is mandatory and deliberate default invites immediate penal and civil liabilities.

5. THEREFORE, I HEREBY CALL UPON YOU TO:
a) Make payment of the outstanding / refund sum of Rs. ${demandAmount}/- (Rupees ${demandAmount} only) directly to my client;
b) Remit legal expenses of Rs. 5,000/- incurred towards the issuance of this legal notice;
WITHIN A PERIOD OF ${currentConfig.statutory_period_days} DAYS from the date of receipt of this notice.

PLEASE TAKE NOTE that if you fail to comply with the requisitions of this notice within the aforesaid ${currentConfig.statutory_period_days} days, my client has given me strict instructions to initiate appropriate criminal and civil proceedings against you before the Competent Court of Jurisdiction, holding you entirely responsible for all costs, damages, and consequences arising therefrom.

A copy of this notice is retained in my office for future legal reference and filing.

Yours sincerely,

(${advocateName})
Advocate for the Complainant
Bar Council Enrollment: ${barEnrollment}
    `.trim();
  };

  const handleCopyText = () => {
    navigator.clipboard.writeText(generateNoticeText());
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handlePrintPDF = () => {
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      alert('Please allow popups to generate Court PDF');
      return;
    }

    const htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Legal Notice - ${refCode}</title>
        <style>
          @page { size: A4; margin: 25mm 20mm 20mm 20mm; }
          body {
            font-family: 'Times New Roman', Times, serif;
            font-size: 13pt;
            line-height: 1.6;
            color: #000;
            background: #fff;
            padding: 20px;
          }
          .header {
            text-align: center;
            border-bottom: 2px solid #000;
            padding-bottom: 12px;
            margin-bottom: 20px;
          }
          .advocate-title {
            font-size: 18pt;
            font-weight: bold;
            letter-spacing: 1px;
            text-transform: uppercase;
          }
          .advocate-sub {
            font-size: 11pt;
            font-style: italic;
          }
          .rpad-badge {
            display: inline-block;
            border: 1px solid #000;
            padding: 4px 10px;
            font-weight: bold;
            font-size: 10pt;
            margin-bottom: 15px;
          }
          .ref-row {
            display: flex;
            justify-content: space-between;
            font-weight: bold;
            font-size: 11pt;
            margin-bottom: 15px;
          }
          .party-box {
            margin-bottom: 15px;
            font-size: 12pt;
          }
          .notice-title {
            text-align: center;
            font-weight: bold;
            font-size: 14pt;
            text-decoration: underline;
            margin: 20px 0;
            text-transform: uppercase;
          }
          .para {
            text-align: justify;
            margin-bottom: 14px;
            text-indent: 30px;
          }
          .demands {
            margin-left: 30px;
            margin-bottom: 15px;
          }
          .signature-box {
            margin-top: 40px;
            float: right;
            text-align: center;
            width: 250px;
          }
        </style>
      </head>
      <body>
        <div class="header">
          <div class="advocate-title">${advocateName}</div>
          <div class="advocate-sub">ADVOCATE & LEGAL CONSULTANT • HIGH COURT OF JUDICATURE</div>
          <div style="font-size: 10pt; margin-top: 4px;">Enrollment No: ${barEnrollment} • Chamber 14, High Court Complex</div>
        </div>

        <div class="rpad-badge">REGISTERED POST WITH ACKNOWLEDGEMENT DUE (RPAD)</div>

        <div class="ref-row">
          <div>Ref: ${refCode}</div>
          <div>Date: ${todayFormatted}</div>
        </div>

        <div class="party-box">
          <strong>TO:</strong><br/>
          <strong>${oppositePartyName}</strong><br/>
          ${oppositePartyAddress}
        </div>

        <div class="party-box">
          <strong>UNDER INSTRUCTIONS FROM MY CLIENT:</strong><br/>
          <strong>${clientName}</strong><br/>
          ${clientAddress}
        </div>

        <div class="notice-title">
          STATUTORY LEGAL NOTICE UNDER ${currentConfig.statute.toUpperCase()}
        </div>

        <p class="para">
          Under instructions from and on behalf of my client named above, I hereby serve upon you this formal statutory legal notice as follows:
        </p>

        <p class="para">
          <strong>1.</strong> That my client is an esteemed, law-abiding citizen and had entered into transactions with you in good faith regarding Reference / Instrument No. <strong>${instrumentNumber}</strong> dated <strong>${incidentDate}</strong> relating to <strong>${bankOrAuthority}</strong>.
        </p>

        <p class="para">
          <strong>2.</strong> That the material facts giving rise to this notice are as follows: ${specificFacts}
        </p>

        <p class="para">
          <strong>3.</strong> That under the mandatory provisions of <strong>${currentConfig.statute}</strong>, your deliberate default and failure to honor your commitments constitutes a direct statutory violation, rendering you liable for criminal prosecution and civil damages.
        </p>

        <p class="para">
          <strong>4.</strong> That as affirmed by landmark judicial precedents of the Hon'ble Supreme Court of India, statutory timelines are inviolable and cannot be prolonged to prejudice the aggrieved party.
        </p>

        <p class="para">
          <strong>5. THEREFORE, I HEREBY CALL UPON YOU TO:</strong>
          <div class="demands">
            a) Remit the principal / restitution amount of <strong>Rs. ${demandAmount}/-</strong> to my client within <strong>${currentConfig.statutory_period_days} days</strong> of receipt of this notice;<br/>
            b) Compensate my client with Rs. 5,000/- towards expenses incurred for this notice.
          </div>
        </p>

        <p class="para">
          PLEASE TAKE NOTICE that upon your failure to comply within the statutory period of <strong>${currentConfig.statutory_period_days} days</strong>, my client shall initiate appropriate legal proceedings before the competent Court of Law entirely at your risk, cost, and legal consequences.
        </p>

        <div class="signature-box">
          <br/><br/>
          __________________________<br/>
          <strong>(${advocateName})</strong><br/>
          Advocate for Complainant
        </div>
      </body>
      </html>
    `;

    printWindow.document.write(htmlContent);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
      printWindow.print();
    }, 500);
  };

  const handleSaveToCaseDiary = async () => {
    setIsSavingCase(true);
    try {
      const payload = {
        case_uid: refCode,
        title: `${currentConfig.title} - ${clientName} vs ${oppositePartyName}`,
        description: specificFacts,
        category: selectedTemplate === 'section_138' ? 'criminal' : 'civil',
        status: 'active',
        priority: 'high',
        client_name: clientName,
        opponent_name: oppositePartyName,
        court_name: 'Statutory Notice Stage (Pre-Litigation)',
        case_number: refCode,
        next_hearing_date: new Date(Date.now() + currentConfig.statutory_period_days * 86400000)
          .toISOString()
          .split('T')[0],
        ai_summary: `Notice issued under ${currentConfig.statute}. Statutory cure period ends in ${currentConfig.statutory_period_days} days.`
      };

      const res = await fetch('/api/v1/cases', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 3000);
      }
    } catch (e) {
      console.error('Failed to save to cases', e);
    } finally {
      setIsSavingCase(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Template Selector Carousel */}
      <div className="space-y-3">
        <label className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center gap-1.5">
          <Scale className="w-4 h-4 text-amber-400" />
          Select Court-Ready Notice Template
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {TEMPLATES.map((tmpl) => {
            const isSelected = selectedTemplate === tmpl.id;
            return (
              <button
                key={tmpl.id}
                type="button"
                onClick={() => handleTemplateChange(tmpl.id)}
                className={`text-left p-4 rounded-xl border transition-all flex flex-col justify-between ${
                  isSelected
                    ? 'bg-[#151924] border-amber-500 shadow-lg shadow-amber-500/10'
                    : 'bg-[#0f121a] border-[#222838] hover:border-gray-600'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      {tmpl.badge}
                    </span>
                    <span className="text-[11px] font-mono text-gray-400">
                      {tmpl.statutory_period_days} Days
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-white mb-1">{tmpl.title}</h3>
                  <p className="text-xs text-gray-400 line-clamp-2">{tmpl.description}</p>
                </div>
                <div className="mt-3 text-[11px] font-mono text-amber-400/80 truncate">
                  § {tmpl.statute}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Two Column Grid: Form on Left, Document Preview on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Form: Inputs */}
        <div className="lg:col-span-6 bg-[#0f121a] border border-[#222838] rounded-2xl p-6 space-y-6">
          <div className="border-b border-[#1f2535] pb-3 flex items-center justify-between">
            <h2 className="text-sm font-bold uppercase tracking-wider text-amber-400 flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Notice & Party Specifics
            </h2>
            <span className="text-xs text-gray-500">Live Synchronized</span>
          </div>

          {/* Advocate Credentials */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Advocate / Legal Counsel</label>
              <input
                type="text"
                value={advocateName}
                onChange={(e) => setAdvocateName(e.target.value)}
                className="w-full px-3 py-2 bg-[#08090d] border border-[#232a3d] focus:border-amber-500 rounded-lg text-xs text-gray-100"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Bar Council Enrollment</label>
              <input
                type="text"
                value={barEnrollment}
                onChange={(e) => setBarEnrollment(e.target.value)}
                className="w-full px-3 py-2 bg-[#08090d] border border-[#232a3d] focus:border-amber-500 rounded-lg text-xs text-gray-100"
              />
            </div>
          </div>

          {/* Complainant (Client) Details */}
          <div className="space-y-3 pt-2 border-t border-[#1a1f2e]">
            <label className="text-xs font-bold text-gray-300 uppercase tracking-wide flex items-center gap-1.5">
              <User className="w-3.5 h-3.5 text-amber-400" />
              Aggrieved Client / Complainant
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <input
                type="text"
                value={clientName}
                onChange={(e) => setClientName(e.target.value)}
                placeholder="Client Full Name"
                className="w-full px-3 py-2 bg-[#08090d] border border-[#232a3d] focus:border-amber-500 rounded-lg text-xs text-gray-100"
              />
              <input
                type="text"
                value={clientAddress}
                onChange={(e) => setClientAddress(e.target.value)}
                placeholder="Full Residential Address"
                className="w-full px-3 py-2 bg-[#08090d] border border-[#232a3d] focus:border-amber-500 rounded-lg text-xs text-gray-100"
              />
            </div>
          </div>

          {/* Opposite Party Details */}
          <div className="space-y-3 pt-2 border-t border-[#1a1f2e]">
            <label className="text-xs font-bold text-gray-300 uppercase tracking-wide flex items-center gap-1.5">
              <Building className="w-3.5 h-3.5 text-red-400" />
              Opposite Party / Defaulting Respondent
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <input
                type="text"
                value={oppositePartyName}
                onChange={(e) => setOppositePartyName(e.target.value)}
                placeholder="Respondent / Entity Name"
                className="w-full px-3 py-2 bg-[#08090d] border border-[#232a3d] focus:border-amber-500 rounded-lg text-xs text-gray-100"
              />
              <input
                type="text"
                value={oppositePartyAddress}
                onChange={(e) => setOppositePartyAddress(e.target.value)}
                placeholder="Office or Resident Address"
                className="w-full px-3 py-2 bg-[#08090d] border border-[#232a3d] focus:border-amber-500 rounded-lg text-xs text-gray-100"
              />
            </div>
          </div>

          {/* Instrument & Claim Details */}
          <div className="space-y-3 pt-2 border-t border-[#1a1f2e]">
            <label className="text-xs font-bold text-gray-300 uppercase tracking-wide flex items-center gap-1.5">
              <IndianRupee className="w-3.5 h-3.5 text-emerald-400" />
              Statutory Claim & Monetary Amount
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-[11px] text-gray-400 mb-1">Cheque / Ref No.</label>
                <input
                  type="text"
                  value={instrumentNumber}
                  onChange={(e) => setInstrumentNumber(e.target.value)}
                  className="w-full px-3 py-2 bg-[#08090d] border border-[#232a3d] rounded-lg text-xs text-gray-100"
                />
              </div>
              <div>
                <label className="block text-[11px] text-gray-400 mb-1">Incident Date</label>
                <input
                  type="date"
                  value={incidentDate}
                  onChange={(e) => setIncidentDate(e.target.value)}
                  className="w-full px-3 py-2 bg-[#08090d] border border-[#232a3d] rounded-lg text-xs text-gray-100"
                />
              </div>
              <div>
                <label className="block text-[11px] text-gray-400 mb-1">Demand Amount (₹)</label>
                <input
                  type="text"
                  value={demandAmount}
                  onChange={(e) => setDemandAmount(e.target.value)}
                  className="w-full px-3 py-2 bg-[#08090d] border border-[#232a3d] rounded-lg text-xs text-amber-400 font-bold"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] text-gray-400 mb-1">Bank / Institution Involved</label>
              <input
                type="text"
                value={bankOrAuthority}
                onChange={(e) => setBankOrAuthority(e.target.value)}
                className="w-full px-3 py-2 bg-[#08090d] border border-[#232a3d] rounded-lg text-xs text-gray-100"
              />
            </div>

            <div>
              <label className="block text-[11px] text-gray-400 mb-1">Factual Grounds & Particulars</label>
              <textarea
                rows={3}
                value={specificFacts}
                onChange={(e) => setSpecificFacts(e.target.value)}
                className="w-full px-3 py-2 bg-[#08090d] border border-[#232a3d] focus:border-amber-500 rounded-lg text-xs text-gray-100 leading-relaxed"
              />
            </div>
          </div>
        </div>

        {/* Right Column: Court Document Live View & Actions */}
        <div className="lg:col-span-6 space-y-4">
          {/* Action Toolbar */}
          <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-[#11141d] border border-[#222838] rounded-xl">
            <div className="flex items-center gap-2">
              <button
                onClick={handlePrintPDF}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black font-bold text-xs rounded-lg shadow-lg shadow-amber-500/20 transition-all"
              >
                <Printer className="w-4 h-4" />
                Print / Court PDF
              </button>
              <button
                onClick={handleCopyText}
                className="inline-flex items-center gap-1.5 px-3 py-2 bg-[#1b212f] hover:bg-[#252e42] text-gray-200 text-xs font-semibold rounded-lg border border-[#2f3952] transition-all"
              >
                {isCopied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                {isCopied ? 'Copied!' : 'Copy Text'}
              </button>
            </div>

            <button
              onClick={handleSaveToCaseDiary}
              disabled={isSavingCase}
              className="inline-flex items-center gap-1.5 px-3 py-2 bg-[#162235] hover:bg-[#1e304b] text-blue-300 text-xs font-semibold rounded-lg border border-blue-500/30 transition-all"
            >
              {saveSuccess ? (
                <Check className="w-4 h-4 text-emerald-400" />
              ) : (
                <FolderPlus className="w-4 h-4" />
              )}
              {saveSuccess ? 'Saved to Diary!' : 'Save to Case Diary'}
            </button>
          </div>

          {/* Realistic A4 Parchment Preview */}
          <div className="bg-white text-gray-950 rounded-2xl shadow-2xl p-6 sm:p-10 font-serif border border-gray-300 text-xs sm:text-sm leading-relaxed max-h-[700px] overflow-y-auto selection:bg-amber-200">
            {/* Letterhead */}
            <div className="text-center border-b-2 border-black pb-3 mb-4">
              <div className="text-base sm:text-lg font-bold tracking-wider uppercase">
                {advocateName}
              </div>
              <div className="text-[11px] font-sans text-gray-700 italic">
                ADVOCATE & LEGAL COUNSEL • HIGH COURT OF JUDICATURE
              </div>
              <div className="text-[10px] font-sans text-gray-600 mt-0.5">
                Bar Council Enrollment No: {barEnrollment} • Chamber 14, High Court Complex
              </div>
            </div>

            {/* RPAD & Date Header */}
            <div className="flex justify-between items-center text-[10px] font-sans font-bold mb-4">
              <span className="border border-black px-2 py-0.5 uppercase tracking-wide">
                BY RPAD / SPEED POST
              </span>
              <span>DATE: {todayFormatted}</span>
            </div>

            <div className="text-[11px] font-sans font-bold text-gray-800 mb-3">
              REF NO: {refCode}
            </div>

            {/* Addresses */}
            <div className="space-y-2 mb-4 font-sans text-xs">
              <div>
                <strong>TO:</strong><br />
                <span className="font-semibold">{oppositePartyName}</span><br />
                {oppositePartyAddress}
              </div>
              <div>
                <strong>UNDER INSTRUCTIONS FROM MY CLIENT:</strong><br />
                <span className="font-semibold">{clientName}</span><br />
                {clientAddress}
              </div>
            </div>

            {/* Subject / Notice Title */}
            <div className="text-center font-bold text-xs sm:text-sm my-4 underline uppercase tracking-wide">
              STATUTORY LEGAL NOTICE UNDER {currentConfig.statute.toUpperCase()}
            </div>

            {/* Body */}
            <div className="space-y-3 text-justify">
              <p>
                Sir / Madam,
              </p>
              <p>
                Under instructions from and on behalf of my client named above, I hereby issue this statutory legal notice and communicate as follows:
              </p>
              <p>
                <strong>1.</strong> That my client is a law-abiding citizen and entered into bona fide transactions with you concerning Reference / Instrument No. <strong>{instrumentNumber}</strong> dated <strong>{incidentDate}</strong> relating to <strong>{bankOrAuthority}</strong>.
              </p>
              <p>
                <strong>2.</strong> That the material circumstances and factual grounds are as follows: {specificFacts}
              </p>
              <p>
                <strong>3.</strong> That your willful neglect and failure to settle the aforesaid liabilities violates <strong>{currentConfig.statute}</strong>, exposing you to immediate statutory remedies, penal sanctions, and civil litigation.
              </p>
              <p>
                <strong>4. THEREFORE, I HEREBY CALL UPON YOU TO:</strong>
                <div className="pl-6 mt-1 space-y-1 font-sans text-xs">
                  <div>• Remit the full demanded sum of <strong>Rs. {demandAmount}/-</strong> (Rupees {demandAmount} only) directly to my client;</div>
                  <div>• Compensate my client with Rs. 5,000/- towards legal drafting and notice charges;</div>
                </div>
              </p>
              <p>
                WITHIN A STRICT STATUTORY PERIOD OF <strong>{currentConfig.statutory_period_days} DAYS</strong> from the date of receipt of this notice.
              </p>
              <p>
                PLEASE TAKE NOTICE that upon your default, my client shall institute civil and criminal proceedings against you before the Competent Court, holding you entirely liable for all consequential damages, interest, and costs.
              </p>
            </div>

            {/* Signature */}
            <div className="mt-8 pt-4 flex justify-end">
              <div className="text-center font-sans">
                <div className="h-10"></div>
                <div className="border-t border-black pt-1 font-bold text-xs">
                  ({advocateName})
                </div>
                <div className="text-[10px] text-gray-600">
                  Advocate for the Complainant
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
