'use client';

import React, { useState } from 'react';
import { ArrowLeftRight, Search, X, Shield, Calendar, BookOpen, Check, Copy } from 'lucide-react';

interface LawMapping {
  offense: string;
  bnsSection: string;
  ipcSection: string;
  punishment: string;
  bailable: boolean;
  cognizable: boolean;
  notes: string;
}

const DUAL_LAW_MAPPINGS: LawMapping[] = [
  {
    offense: 'Extortion / Blackmail',
    bnsSection: 'Section 308 BNS, 2023',
    ipcSection: 'Section 383 / 384 IPC, 1860',
    punishment: 'Imprisonment up to 3 to 7 years + Fine',
    bailable: false,
    cognizable: true,
    notes: 'Extortion via social media or cyber threats falls squarely under this section.',
  },
  {
    offense: 'Cheating / Fraud / Financial Swindling',
    bnsSection: 'Section 318 BNS, 2023',
    ipcSection: 'Section 415 / 420 IPC, 1860',
    punishment: 'Imprisonment up to 7 years + Fine',
    bailable: false,
    cognizable: true,
    notes: 'Replaces old Section 420 IPC. Punishes dishonest inducement and property deception.',
  },
  {
    offense: 'Murder / Culpable Homicide',
    bnsSection: 'Section 103 BNS, 2023',
    ipcSection: 'Section 302 IPC, 1860',
    punishment: 'Death penalty or Life Imprisonment + Fine',
    bailable: false,
    cognizable: true,
    notes: 'Replaces old Section 302 IPC. Includes organized crime & mob lynching sub-clauses.',
  },
  {
    offense: 'Criminal Breach of Trust (Embezzlement)',
    bnsSection: 'Section 316 BNS, 2023',
    ipcSection: 'Section 405 / 406 IPC, 1860',
    punishment: 'Imprisonment up to 5 years + Fine',
    bailable: false,
    cognizable: true,
    notes: 'Applicable when agents, partners, or employees misappropriate entrusted money.',
  },
  {
    offense: 'Forgery / Fake Documents & Wills',
    bnsSection: 'Section 336 / 338 BNS, 2023',
    ipcSection: 'Section 463 / 465 / 468 IPC, 1860',
    punishment: 'Imprisonment up to 7 years + Fine',
    bailable: false,
    cognizable: true,
    notes: 'Creation of electronic signatures or forged deeds.',
  },
  {
    offense: 'FIR Registration (Police Duty)',
    bnsSection: 'Section 173 BNSS, 2023',
    ipcSection: 'Section 154 CrPC, 1973',
    punishment: 'Mandatory Zero-FIR & e-FIR registration',
    bailable: true,
    cognizable: true,
    notes: 'Introduces mandatory e-FIR and Zero-FIR regardless of territorial jurisdiction.',
  },
  {
    offense: 'Police Power of Arrest & Notice of Appearance',
    bnsSection: 'Section 35 BNSS, 2023',
    ipcSection: 'Section 41 & 41A CrPC, 1973',
    punishment: 'Prior DSP permission needed for elderly/infirm',
    bailable: true,
    cognizable: true,
    notes: 'Arnesh Kumar guidelines codified into statutory law for offenses under 7 years.',
  },
  {
    offense: 'Electronic Evidence Admissibility (WhatsApp/CCTV)',
    bnsSection: 'Section 63 BSA, 2023',
    ipcSection: 'Section 65B Indian Evidence Act, 1872',
    punishment: 'Mandatory certificate format for all digital media',
    bailable: true,
    cognizable: true,
    notes: 'Standardizes digital record admissibility without requiring physical server seizure.',
  },
  {
    offense: 'Theft / Cyber Digital Theft',
    bnsSection: 'Section 303 BNS, 2023',
    ipcSection: 'Section 378 / 379 IPC, 1860',
    punishment: 'Imprisonment up to 3 years or Community Service',
    bailable: false,
    cognizable: true,
    notes: 'First-time petty theft allows community service instead of prison.',
  },
  {
    offense: 'Criminal Defamation',
    bnsSection: 'Section 356 BNS, 2023',
    ipcSection: 'Section 499 / 500 IPC, 1860',
    punishment: 'Simple imprisonment up to 2 years or Community Service',
    bailable: true,
    cognizable: false,
    notes: 'Community service introduced as an alternative penal remedy.',
  },
];

interface DualLawConverterModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function DualLawConverterModal({ isOpen, onClose }: DualLawConverterModalProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [copiedSection, setCopiedSection] = useState<string | null>(null);

  if (!isOpen) return null;

  const filtered = DUAL_LAW_MAPPINGS.filter(
    (m) =>
      m.offense.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.bnsSection.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.ipcSection.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.notes.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(text);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-[#0e0e12] border border-white/[0.12] w-full max-w-4xl rounded-3xl p-6 shadow-2xl relative max-h-[90vh] flex flex-col font-sans">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/[0.08]">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <ArrowLeftRight className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>Dual-Law Transition Engine</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  BNS 2023 ↔ IPC 1860
                </span>
              </h3>
              <p className="text-xs text-white/40">Instant Cross-Reference between New Criminal Sanhitas &amp; Old Codes</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-white/40 hover:text-white hover:bg-white/[0.06] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Transition Date Rule Alert */}
        <div className="my-3 p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/25 flex items-start gap-3">
          <Calendar className="w-5 h-5 text-indigo-400 flex-shrink-0 mt-0.5" />
          <div className="text-xs leading-relaxed text-indigo-200">
            <strong>Mandatory Judicial Transition Rule:</strong>
            <ul className="list-disc list-inside mt-0.5 text-white/80 space-y-0.5">
              <li>Offenses committed <strong>BEFORE July 1, 2024:</strong> Must be registered and tried under <strong>IPC / CrPC / IEA</strong>.</li>
              <li>Offenses committed <strong>ON OR AFTER July 1, 2024:</strong> Must be registered under <strong>BNS / BNSS / BSA</strong>.</li>
            </ul>
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative mb-3">
          <Search className="w-4 h-4 text-white/40 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by offense, section (e.g. 420, 302, 308, Extortion, Cheating)..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-xs text-white placeholder-white/30 focus:outline-none focus:border-indigo-500/50"
            autoFocus
          />
        </div>

        {/* Mappings List */}
        <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
          {filtered.map((m, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-2xl bg-white/[0.02] border border-white/[0.06] hover:border-indigo-500/30 hover:bg-white/[0.04] transition-all"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-sm text-white">{m.offense}</span>
                <div className="flex items-center gap-1.5">
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${m.cognizable ? 'bg-red-500/15 text-red-300 border border-red-500/30' : 'bg-green-500/15 text-green-300 border border-green-500/30'}`}>
                    {m.cognizable ? 'Cognizable' : 'Non-Cognizable'}
                  </span>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${m.bailable ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30' : 'bg-orange-500/15 text-orange-300 border border-orange-500/30'}`}>
                    {m.bailable ? 'Bailable' : 'Non-Bailable'}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-2">
                {/* New Law */}
                <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] uppercase tracking-wider text-indigo-300 block font-bold">New Law (Post July 1, 2024)</span>
                    <span className="text-xs font-bold text-white">{m.bnsSection}</span>
                  </div>
                  <button
                    onClick={() => handleCopy(m.bnsSection)}
                    className="p-1 rounded text-white/40 hover:text-white"
                  >
                    {copiedSection === m.bnsSection ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                </div>

                {/* Old Law */}
                <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-between">
                  <div>
                    <span className="text-[10px] uppercase tracking-wider text-white/40 block font-bold">Old Law (Pre July 1, 2024)</span>
                    <span className="text-xs font-bold text-white/80">{m.ipcSection}</span>
                  </div>
                  <button
                    onClick={() => handleCopy(m.ipcSection)}
                    className="p-1 rounded text-white/40 hover:text-white"
                  >
                    {copiedSection === m.ipcSection ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              <div className="text-[11px] text-white/50 flex items-center justify-between pt-1 border-t border-white/[0.04]">
                <span>⚖️ <strong>Penal Punishment:</strong> {m.punishment}</span>
                <span className="italic text-white/40 hidden sm:inline">{m.notes}</span>
              </div>
            </div>
          ))}

          {filtered.length === 0 && (
            <div className="text-center py-10 text-white/40 text-xs">
              No matching sections found. Try searching &quot;Extortion&quot;, &quot;420&quot;, or &quot;302&quot;.
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-white/[0.08] flex items-center justify-between text-xs text-white/40">
          <span>Official Law Commission of India &amp; Ministry of Home Affairs Concordance Table.</span>
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
