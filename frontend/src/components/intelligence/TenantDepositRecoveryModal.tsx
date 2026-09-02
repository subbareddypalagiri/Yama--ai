'use client';

import React, { useState } from 'react';
import { Home, Printer, Copy, Check, X, ShieldAlert, FileText, Calendar, IndianRupee, Scale } from 'lucide-react';

interface TenantDepositRecoveryModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultState?: string;
  defaultClientName?: string;
}

export default function TenantDepositRecoveryModal({
  isOpen,
  onClose,
  defaultState = 'Andhra Pradesh',
  defaultClientName = 'Tenant',
}: TenantDepositRecoveryModalProps) {
  const [tenantName, setTenantName] = useState(defaultClientName);
  const [landlordName, setLandlordName] = useState('Landlord / Property Owner');
  const [propertyAddress, setPropertyAddress] = useState('Flat No. 402, Royal Enclave, Hyderabad / Vijayawada');
  const [landlordContact, setLandlordContact] = useState('+91 98765 43210');
  const [depositAmount, setDepositAmount] = useState<number>(60000);
  const [deductionsClaimed, setDeductionsClaimed] = useState<number>(15000);
  const [monthsDelayed, setMonthsDelayed] = useState<number>(2);
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const today = new Date().toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  // Calculate 18% per annum statutory interest
  const annualInterestRate = 0.18;
  const interestAmount = Math.round((depositAmount * annualInterestRate * monthsDelayed) / 12);
  const totalDemandAmount = depositAmount + interestAmount;

  const noticeContent = `STATUTORY LEGAL DEMAND NOTICE
UNDER SECTION 21 OF RESIDENTIAL AND NON-RESIDENTIAL TENANCY ACT, 2017/2021
READ WITH SECTIONS 73 & 74 OF INDIAN CONTRACT ACT, 1872
FOR IMMEDIATE REFUND OF SECURITY ADVANCE DEPOSIT WITH 18% PENAL INTEREST

Date: ${today}
Ref: YAMA/TENANCY/DEP/${new Date().getFullYear()}/${Math.floor(1000 + Math.random() * 9000)}

TO:
${landlordName}
Contact / Handled by: ${landlordContact}
Owner / Landlord of: ${propertyAddress}

FROM:
CHAMBERS OF ADVOCATE YAMA
Advocates & Legal Counselors • High Court Jurisdiction: ${defaultState}
On behalf of Client: ${tenantName} (Former Lawful Tenant)

SUBJECT: URGENT 15-DAY STATUTORY DEMAND FOR IMMEDIATE REFUND OF ADVANCE SECURITY DEPOSIT OF RS. ${depositAmount.toLocaleString('en-IN')}/- ALONG WITH 18% STATUTORY PENAL INTEREST ACCRUED OF RS. ${interestAmount.toLocaleString('en-IN')}/- (TOTAL DEMAND: RS. ${totalDemandAmount.toLocaleString('en-IN')}/-).

SIR / MADAM,

Under explicit instructions from and on behalf of my client ${tenantName}, I do hereby serve upon you this formal Statutory Legal Notice:

1. That my client was the lawful and bona fide tenant occupying the premises situated at [ ${propertyAddress} ], having punctually and conscientiously paid all monthly rentals without default.

2. That at the inception of the tenancy, my client paid an amount of Rs. ${depositAmount.toLocaleString('en-IN')}/- towards refundable Advance Security Deposit, which was mutually agreed to be returned in full upon vacant peaceful delivery of possession.

3. That my client lawfully vacated and handed over peaceful, clear, and unencumbered possession of the demised premises in pristine condition, following which more than ${monthsDelayed} months have elapsed.

4. STATUTORY VIOLATION OF TENANCY LAW:
   Under Section 21 of the Residential and Non-Residential Tenancy Act, the Landlord is legally mandated to refund the full security deposit to the tenant within THIRTY (30) DAYS of handing over vacant possession. Your unilateral withholding and arbitrary claim of Rs. ${deductionsClaimed.toLocaleString('en-IN')}/- without statutory inspection reports or joint architectural invoices is illegal, mala fide, and constitutes criminal breach of trust.

5. ACCRUAL OF 18% STATUTORY PENAL INTEREST:
   By virtue of your willful withholding beyond 30 days, my client is entitled under Section 73 of the Indian Contract Act, 1872 to claim statutory penal interest @ 18% per annum, quantified as Rs. ${interestAmount.toLocaleString('en-IN')}/- for the period of delay.

PRAYER / STATUTORY ULTIMATUM:
TAKE NOTICE that you are hereby called upon to refund the entire sum of Rs. ${totalDemandAmount.toLocaleString('en-IN')}/- (Principal Rs. ${depositAmount.toLocaleString('en-IN')}/- + 18% Interest Rs. ${interestAmount.toLocaleString('en-IN')}/-) into my client's designated bank account within FIFTEEN (15) DAYS of the receipt hereof.

FAIL NOT, or my client has given me peremptory instructions to initiate formal proceedings before the Competent Rent Authority / District Rent Tribunal for recovery with penal damages, and to initiate Criminal Prosecution under Bharatiya Nyaya Sanhita, 2023 for criminal misappropriation, at your entire cost and peril.

Yours faithfully,

____________________________________
CHAMBERS OF ADVOCATE YAMA
Advocate & Legal Counsel for Client
Enrolment No: AP/BCI/2021/984`;

  const handleCopy = () => {
    navigator.clipboard.writeText(noticeContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Tenant Security Deposit Legal Notice - YAMA AI</title>
          <style>
            @page { size: A4; margin: 25mm 20mm; }
            body { font-family: 'Times New Roman', serif; padding: 20px 40px; line-height: 1.7; font-size: 12.5pt; color: #111; }
            .letterhead { text-align: center; border-bottom: 2.5px double #222; padding-bottom: 12px; margin-bottom: 25px; }
            .letterhead h1 { margin: 0; font-size: 19pt; letter-spacing: 2px; }
            .letterhead p { margin: 3px 0; font-size: 9.5pt; color: #444; }
            pre { white-space: pre-wrap; font-family: inherit; font-size: 12pt; line-height: 1.7; }
            .seal-box { margin-top: 40px; display: flex; justify-content: space-between; align-items: flex-end; }
            .seal { width: 105px; height: 105px; border: 3px solid #8B0000; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #8B0000; font-size: 7.5pt; font-weight: bold; text-align: center; transform: rotate(-10deg); }
          </style>
        </head>
        <body>
          <div class="letterhead">
            <h1>CHAMBERS OF ADVOCATE YAMA</h1>
            <p>Advocates &amp; Real Estate Legal Counselors • High Court Jurisdiction: ${defaultState}</p>
            <p>Tenancy Redressal &amp; Rent Tribunal Appellate Division • Bar Enrolment: AP/BCI/2021/984</p>
          </div>
          <pre>${noticeContent}</pre>
          <div class="seal-box">
            <div class="seal">
              <div>★ ADVOCATE ★</div>
              <div style="font-size: 6.5pt;">RENT TRIBUNAL</div>
              <div>BAR ENROLLED</div>
            </div>
            <div>
              <p>For Chambers of Advocate YAMA</p>
              <p style="margin-top: 45px; font-weight: bold;">(ADVOCATE SIGNATURE &amp; STAMP)</p>
            </div>
          </div>
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 font-sans">
      <div className="bg-[#0e0e12] border border-white/[0.12] w-full max-w-4xl rounded-3xl p-6 shadow-2xl relative max-h-[92vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/[0.08]">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Home className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>Tenant Security Deposit Recovery Suite</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  TENANCY ACT SEC 21
                </span>
              </h3>
              <p className="text-xs text-white/40">15-Day Demand Notice with 18% Statutory Interest &amp; Rent Court Draft</p>
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
          {/* Inputs Panel */}
          <div className="md:col-span-5 space-y-3">
            <div>
              <label className="text-[10px] text-white/40 block mb-0.5 font-bold uppercase tracking-wider">Tenant (Your Name)</label>
              <input
                type="text"
                value={tenantName}
                onChange={(e) => setTenantName(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-emerald-500/50"
              />
            </div>

            <div>
              <label className="text-[10px] text-white/40 block mb-0.5 font-bold uppercase tracking-wider">Landlord / Owner Name</label>
              <input
                type="text"
                value={landlordName}
                onChange={(e) => setLandlordName(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-emerald-500/50"
              />
            </div>

            <div>
              <label className="text-[10px] text-white/40 block mb-0.5 font-bold uppercase tracking-wider">Rented Property Address</label>
              <input
                type="text"
                value={propertyAddress}
                onChange={(e) => setPropertyAddress(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-emerald-500/50"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-[10px] text-white/40 block mb-0.5 font-bold uppercase tracking-wider">Deposit Paid (₹)</label>
                <input
                  type="number"
                  value={depositAmount}
                  onChange={(e) => setDepositAmount(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-emerald-500/50 font-mono"
                />
              </div>
              <div>
                <label className="text-[10px] text-white/40 block mb-0.5 font-bold uppercase tracking-wider">Delay (Months)</label>
                <input
                  type="number"
                  value={monthsDelayed}
                  onChange={(e) => setMonthsDelayed(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-emerald-500/50 font-mono"
                />
              </div>
            </div>

            {/* Statutory Interest Calculator Card */}
            <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 space-y-2">
              <span className="text-[11px] font-bold text-emerald-300 uppercase tracking-wider flex items-center gap-1.5">
                <Scale className="w-3.5 h-3.5" /> Statutory Claim Breakdown
              </span>
              <div className="flex justify-between text-xs text-white/70">
                <span>Principal Deposit:</span>
                <span className="font-mono font-bold text-white">₹{depositAmount.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between text-xs text-white/70">
                <span>18% Penal Interest ({monthsDelayed} mos):</span>
                <span className="font-mono font-bold text-emerald-300">+ ₹{interestAmount.toLocaleString('en-IN')}</span>
              </div>
              <div className="pt-2 border-t border-white/[0.08] flex justify-between text-xs font-bold text-white">
                <span>Total Legal Demand:</span>
                <span className="font-mono text-emerald-400 text-sm">₹{totalDemandAmount.toLocaleString('en-IN')}</span>
              </div>
            </div>
          </div>

          {/* Legal Notice Preview */}
          <div className="md:col-span-7 flex flex-col h-full">
            <div className="flex items-center justify-between pb-2">
              <span className="text-[11px] font-bold text-emerald-300 uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5" /> Rent Tribunal Ready Notice
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-xs text-white/80 hover:text-white transition-all"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
                <button
                  onClick={handlePrint}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-xs font-semibold text-emerald-300 hover:bg-emerald-500/30 transition-all"
                >
                  <Printer className="w-3.5 h-3.5" />
                  <span>Print / PDF</span>
                </button>
              </div>
            </div>

            <div className="flex-1 bg-black/40 border border-white/[0.08] rounded-2xl p-4 overflow-y-auto font-mono text-[11px] text-white/80 leading-relaxed max-h-96 whitespace-pre-wrap select-all">
              {noticeContent}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-white/[0.08] flex items-center justify-between text-xs text-white/40">
          <span>Enforceable before Rent Court under Section 21 of AP/TS Tenancy Act.</span>
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
