'use client';

import React, { useState } from 'react';
import { FileCheck, Printer, Copy, Check, X, Shield, Download, Scale } from 'lucide-react';

interface BsaEvidenceCertificateModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultClientName?: string;
  defaultState?: string;
}

export default function BsaEvidenceCertificateModal({
  isOpen,
  onClose,
  defaultClientName = 'Subbu',
  defaultState = 'Andhra Pradesh',
}: BsaEvidenceCertificateModalProps) {
  const [personName, setPersonName] = useState(defaultClientName);
  const [deviceModel, setDeviceModel] = useState('Android / iPhone Smartphone & Personal Laptop');
  const [evidenceType, setEvidenceType] = useState('Instagram DMs, Extortion Messages & UPI Transaction Receipts');
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const today = new Date().toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  const certificateText = `AFFIDAVIT & STATUTORY CERTIFICATE OF ELECTRONIC EVIDENCE
UNDER SECTION 63 OF BHARATIYA SAKSHYA ADHINIYAM, 2023 (BSA)
(FORMERLY SECTION 65B OF INDIAN EVIDENCE ACT, 1872)

BEFORE THE HON'BLE COURT / INVESTIGATING OFFICER

I, ${personName}, aged about major years, residing in ${defaultState}, India, do hereby solemnly affirm and declare on oath as under:

1. That I am the lawful owner and custodian of the electronic device(s), namely:
   [ ${deviceModel} ]
   which has been under my lawful custody, control, and management.

2. That the electronic output / printouts annexed hereto comprise:
   [ ${evidenceType} ]
   which were produced by the computer resource / mobile device during the period over which the device was used regularly to store or process information.

3. That throughout the material period, the aforesaid device was operating properly, and there have been no operational defects, hacking, or tampering affecting the accuracy of the contents.

4. That the printout / digital media produced reproduces faithfully and accurately the electronic records without any alteration, editing, or distortion whatsoever, in strict compliance with Section 63(4) of Bharatiya Sakshya Adhiniyam, 2023.

5. That the contents of this Certificate are true and correct to the best of my personal knowledge and belief, and no material fact has been concealed.

DEPONENT:

___________________________
(${personName})
Identified by me:

___________________________
ADVOCATE`;

  const handleCopy = () => {
    navigator.clipboard.writeText(certificateText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;
    printWindow.document.write(`
      <html>
        <head>
          <title>Section 63 BSA Electronic Certificate</title>
          <style>
            body { font-family: 'Times New Roman', serif; padding: 40px; line-height: 1.6; font-size: 13pt; color: #000; }
            pre { white-space: pre-wrap; font-family: inherit; }
            .header { text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 25px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h3 style="margin:0;">STATUTORY ELECTRONIC EVIDENCE CERTIFICATE</h3>
            <p style="margin:4px 0; font-size:10pt;">Mandatory under Section 63 Bharatiya Sakshya Adhiniyam, 2023 (Arjun Panditrao Precedent)</p>
          </div>
          <pre>${certificateText}</pre>
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-[#0e0e12] border border-white/[0.12] w-full max-w-3xl rounded-3xl p-6 shadow-2xl relative max-h-[90vh] flex flex-col font-sans">
        <div className="flex items-center justify-between pb-4 border-b border-white/[0.08]">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <FileCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>Section 63 BSA Electronic Evidence Certificate</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  STATUTORY MANDATE
                </span>
              </h3>
              <p className="text-xs text-white/40">Required in all Indian Courts for WhatsApp, Instagram, SMS &amp; UPI Admissibility</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-white/40 hover:text-white hover:bg-white/[0.06] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-5 py-4 overflow-y-auto flex-1">
          <div className="md:col-span-5 space-y-3">
            <div>
              <label className="text-[10px] text-white/40 block mb-1">Deponent Name</label>
              <input
                type="text"
                value={personName}
                onChange={(e) => setPersonName(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-emerald-500/50"
              />
            </div>

            <div>
              <label className="text-[10px] text-white/40 block mb-1">Hardware / Device Model</label>
              <input
                type="text"
                value={deviceModel}
                onChange={(e) => setDeviceModel(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-emerald-500/50"
              />
            </div>

            <div>
              <label className="text-[10px] text-white/40 block mb-1">Evidence Records Included</label>
              <textarea
                value={evidenceType}
                onChange={(e) => setEvidenceType(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-emerald-500/50 resize-none"
              />
            </div>

            <div className="bg-emerald-500/10 border border-emerald-500/20 p-3 rounded-xl text-[11px] text-emerald-300 leading-relaxed">
              <strong>Supreme Court Precedent:</strong> Under <em>Arjun Panditrao (2020)</em>, secondary electronic evidence is legally void without this Section 63 certificate.
            </div>
          </div>

          <div className="md:col-span-7 flex flex-col h-full">
            <div className="flex items-center justify-between pb-2">
              <span className="text-[11px] font-bold text-emerald-300 uppercase tracking-wider flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5" /> Admissible Court Affidavit
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
                  <span>Print Certificate</span>
                </button>
              </div>
            </div>

            <div className="flex-1 bg-black/40 border border-white/[0.08] rounded-2xl p-4 overflow-y-auto font-mono text-[11px] text-white/80 leading-relaxed max-h-80 whitespace-pre-wrap select-all">
              {certificateText}
            </div>
          </div>
        </div>

        <div className="pt-3 border-t border-white/[0.08] flex items-center justify-between text-xs text-white/40">
          <span>Ready for notary attestation or submission to Police &amp; Magistrates.</span>
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
