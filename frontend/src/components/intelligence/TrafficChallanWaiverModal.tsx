'use client';

import React, { useState } from 'react';
import { Car, Printer, Copy, Check, X, ShieldAlert, FileText, Calendar, IndianRupee, Scale, Award } from 'lucide-react';

interface TrafficChallanWaiverModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultState?: string;
}

export default function TrafficChallanWaiverModal({
  isOpen,
  onClose,
  defaultState = 'Andhra Pradesh',
}: TrafficChallanWaiverModalProps) {
  const [vehicleNumber, setVehicleNumber] = useState('AP 04 XX 1234');
  const [ownerName, setOwnerName] = useState('Vehicle Registered Owner');
  const [totalChallans, setTotalChallans] = useState<number>(5500);
  const [violationCount, setViolationCount] = useState<number>(4);
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const today = new Date().toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  // Calculate 50% - 75% Lok Adalat waiver bands
  const minSettlement = Math.round(totalChallans * 0.25);
  const maxSettlement = Math.round(totalChallans * 0.50);
  const savings = totalChallans - minSettlement;

  const petitionContent = `BEFORE THE HON'BLE NATIONAL LOK ADALAT / DISTRICT LEGAL SERVICES AUTHORITY (DLSA)
IN THE COURT OF MOTOR ACCIDENTS & TRAFFIC ADVISORY BENCH, ${defaultState.toUpperCase()}

APPLICATION FOR COMPOUNDING & WAIVER OF PENDING E-CHALLANS
UNDER SECTION 19 OF LEGAL SERVICES AUTHORITIES ACT, 1987
READ WITH SECTIONS 136A, 200 & 208 OF MOTOR VEHICLES (AMENDMENT) ACT, 2019

Date: ${today}

IN THE MATTER OF:
${ownerName}
Registered Owner of Motor Vehicle Reg No: [ ${vehicleNumber} ]
Residing in: ${defaultState}, India.                                  ...PETITIONER / APPLICANT

VERSUS

TRAFFIC POLICE & TRANSPORT DEPARTMENT,
GOVERNMENT OF ${defaultState.toUpperCase()}.                        ...RESPONDENTS

MOST RESPECTFULLY SHOWETH:

1. That the Applicant is the registered owner of the Motor Vehicle bearing Registration No. [ ${vehicleNumber} ], having a clean driving record and being a law-abiding citizen.

2. That upon checking the online traffic portal, the Applicant discovered ${violationCount} electronic challans amounting to a cumulative penal sum of Rs. ${totalChallans.toLocaleString('en-IN')}/- issued through automated CCTV / speed monitoring cameras.

3. CHALLENGE UNDER SECTION 136A OF MOTOR VEHICLES ACT, 2019:
   That under Section 136A of the Motor Vehicles Act, 2019 read with Rule 167A of the Central Motor Vehicles Rules, any electronic enforcement device used to capture violations must possess an unexpired Annual Calibration and Verification Certificate issued by the Legal Metrology Department. The Applicant puts the prosecution to strict proof regarding the physical calibration of the cameras generating the aforesaid challans.

4. STATUTORY LIMITATION UNDER SECTION 208 MV ACT:
   That several compoundable offenses listed are beyond the ordinary period of statutory cognizance and involve inadvertent minor civil infractions without any criminal intent or vehicular collision.

5. PRAYER FOR COMPOUNDING BEFORE LOK ADALAT BENCH:
   That the Applicant is eager to amicably resolve, compound, and settle all outstanding e-challans under the beneficial statutory scheme of the National Lok Adalat.

PRAYER:
Wherefore, it is most respectfully prayed that this Hon'ble Lok Adalat Bench may graciously be pleased to:
a) Compound and settle all ${violationCount} pending e-challans against Vehicle No. ${vehicleNumber} by granting a statutory compounding concession of 50% to 75%;
b) Permit the Applicant to deposit the settled sum of approximately Rs. ${minSettlement.toLocaleString('en-IN')}/- to Rs. ${maxSettlement.toLocaleString('en-IN')}/- in full and final settlement;
c) Direct the Respondent Transport and Police Department to clear, discharge, and update the vehicle ledger to zero penalty.

Yours respectfully,

____________________________________
(${ownerName})
Applicant / Vehicle Owner: ${vehicleNumber}`;

  const handleCopy = () => {
    navigator.clipboard.writeText(petitionContent);
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
          <title>Lok Adalat Challan Compounding Application - YAMA AI</title>
          <style>
            @page { size: A4; margin: 25mm 20mm; }
            body { font-family: 'Times New Roman', serif; padding: 20px 40px; line-height: 1.7; font-size: 12pt; color: #111; }
            .header { text-align: center; border-bottom: 2px solid #222; padding-bottom: 10px; margin-bottom: 20px; }
            pre { white-space: pre-wrap; font-family: inherit; font-size: 11.5pt; line-height: 1.7; }
          </style>
        </head>
        <body>
          <div class="header">
            <h3 style="margin:0;">NATIONAL LOK ADALAT COMPOUNDING BENCH</h3>
            <p style="margin:4px 0; font-size:9.5pt;">Under Legal Services Authorities Act, 1987 • District Legal Services Authority (DLSA)</p>
          </div>
          <pre>${petitionContent}</pre>
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
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-red-500 flex items-center justify-center shadow-lg shadow-amber-500/20">
              <Car className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>Traffic Challan &amp; Lok Adalat 50-75% Waiver Suite</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  MV ACT SEC 136A &amp; 208
                </span>
              </h3>
              <p className="text-xs text-white/40">Challenge Camera Calibration &amp; Generate Lok Adalat Compounding Petition</p>
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
              <label className="text-[10px] text-white/40 block mb-0.5 font-bold uppercase tracking-wider">Vehicle Reg Number</label>
              <input
                type="text"
                value={vehicleNumber}
                onChange={(e) => setVehicleNumber(e.target.value.toUpperCase())}
                placeholder="e.g. AP 04 XX 1234"
                className="w-full px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-amber-500/50 font-mono"
              />
            </div>

            <div>
              <label className="text-[10px] text-white/40 block mb-0.5 font-bold uppercase tracking-wider">Registered Owner Name</label>
              <input
                type="text"
                value={ownerName}
                onChange={(e) => setOwnerName(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-amber-500/50"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-[10px] text-white/40 block mb-0.5 font-bold uppercase tracking-wider">Total Fine (₹)</label>
                <input
                  type="number"
                  value={totalChallans}
                  onChange={(e) => setTotalChallans(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-amber-500/50 font-mono"
                />
              </div>
              <div>
                <label className="text-[10px] text-white/40 block mb-0.5 font-bold uppercase tracking-wider">Challan Count</label>
                <input
                  type="number"
                  value={violationCount}
                  onChange={(e) => setViolationCount(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-amber-500/50 font-mono"
                />
              </div>
            </div>

            {/* Lok Adalat Concession Estimation Box */}
            <div className="p-3.5 rounded-2xl bg-amber-500/10 border border-amber-500/20 space-y-2">
              <span className="text-[11px] font-bold text-amber-300 uppercase tracking-wider flex items-center gap-1.5">
                <Award className="w-3.5 h-3.5" /> Lok Adalat 50% - 75% Waiver Band
              </span>
              <div className="flex justify-between text-xs text-white/70">
                <span>Original Portal Fine:</span>
                <span className="font-mono text-white/50 line-through">₹{totalChallans.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between text-xs text-white/70">
                <span>Compounded Settlement Target:</span>
                <span className="font-mono font-bold text-amber-300">₹{minSettlement.toLocaleString('en-IN')} - ₹{maxSettlement.toLocaleString('en-IN')}</span>
              </div>
              <div className="pt-2 border-t border-white/[0.08] flex justify-between text-xs font-bold text-emerald-400">
                <span>Estimated Citizen Savings:</span>
                <span className="font-mono text-sm">Up to ₹{savings.toLocaleString('en-IN')}</span>
              </div>
            </div>
          </div>

          {/* Petition Document Preview */}
          <div className="md:col-span-7 flex flex-col h-full">
            <div className="flex items-center justify-between pb-2">
              <span className="text-[11px] font-bold text-amber-300 uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5" /> Court Compounding Petition
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-xs text-white/80 hover:text-white transition-all"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'Copy Petition'}</span>
                </button>
                <button
                  onClick={handlePrint}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-amber-500/20 border border-amber-500/40 text-xs font-semibold text-amber-300 hover:bg-amber-500/30 transition-all"
                >
                  <Printer className="w-3.5 h-3.5" />
                  <span>Print / PDF</span>
                </button>
              </div>
            </div>

            <div className="flex-1 bg-black/40 border border-white/[0.08] rounded-2xl p-4 overflow-y-auto font-mono text-[11px] text-white/80 leading-relaxed max-h-96 whitespace-pre-wrap select-all">
              {petitionContent}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-white/[0.08] flex items-center justify-between text-xs text-white/40">
          <span>Directly admissible before District Legal Services Authority (DLSA) Lok Adalat benches.</span>
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
