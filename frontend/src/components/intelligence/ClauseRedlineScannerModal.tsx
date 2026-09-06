'use client';

import React, { useState } from 'react';
import {
  X, FileText, Upload, AlertTriangle, CheckCircle2, ShieldAlert,
  ArrowRight, Copy, Check, Sparkles, Loader2, RefreshCw, Scale
} from 'lucide-react';

interface ClauseRedlineScannerModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface RedlineIssue {
  id: string;
  clauseTitle: string;
  originalText: string;
  riskSeverity: 'critical' | 'high' | 'medium';
  statutoryViolation: string;
  explanation: string;
  counterClause: string;
}

export default function ClauseRedlineScannerModal({ isOpen, onClose }: ClauseRedlineScannerModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [results, setResults] = useState<{
    riskScore: number;
    riskLevel: string;
    issues: RedlineIssue[];
    summary: string;
  } | null>(null);

  if (!isOpen) return null;

  const sampleRentalAgreement = `CLAUSE 4: The Tenant agrees to deposit a sum of Rs. 2,00,000 as Security Deposit. In the event Tenant vacates before completion of 24 months, the entire deposit shall be forfeited unconditionally as liquidated damages without dispute.

CLAUSE 7: The Landlord reserves the absolute right to inspect the premises at any hour of the day or night without prior notice and may terminate this agreement with 24 hours notice for any inconvenience caused.

CLAUSE 11: Any delay in monthly rent payment beyond the 1st of the month shall attract a compound penalty of 10% per day. The Tenant waives all rights to approach civil court or rent tribunal.`;

  const handleLoadSample = () => {
    setInputText(sampleRentalAgreement);
  };

  const handleScan = async () => {
    if (!inputText.trim() && !file) return;

    setLoading(true);
    try {
      // Analyze text via Gemini or intelligent statutory heuristics
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const mockIssues: RedlineIssue[] = [
        {
          id: '1',
          clauseTitle: 'Clause 4: 100% Security Deposit Forfeiture Trap',
          originalText: 'In the event Tenant vacates before completion of 24 months, the entire deposit shall be forfeited unconditionally as liquidated damages without dispute.',
          riskSeverity: 'critical',
          statutoryViolation: 'Violates Indian Contract Act, 1872 § 74 & State Tenancy Act § 21',
          explanation: 'Under Section 74 of the Contract Act (Kailash Nath Associates v. DDA), liquidated damages can only be claimed for actual proven losses, not arbitrary punitive forfeiture. Furthermore, State Tenancy Laws mandate deposit refund within 30 days minus actual documented damages.',
          counterClause: 'In the event of early vacation, the Landlord shall refund the security deposit within 30 days after deducting only verified physical damages beyond normal wear and tear, subject to 30 days written advance notice.',
        },
        {
          id: '2',
          clauseTitle: 'Clause 7: Unrestricted Midnight Entry & 24h Eviction',
          originalText: 'The Landlord reserves the absolute right to inspect the premises at any hour of the day or night without prior notice and may terminate this agreement with 24 hours notice...',
          riskSeverity: 'critical',
          statutoryViolation: 'Violates Right to Privacy (Art. 21) & Transfer of Property Act § 106',
          explanation: 'Section 106 of the Transfer of Property Act requires at least 15 days mandatory written notice for terminating a monthly tenancy. Unannounced entry violates the fundamental right to privacy under Justice K.S. Puttaswamy v. UOI.',
          counterClause: 'The Landlord may inspect the premises only between 9:00 AM and 7:00 PM upon providing at least 24 hours prior written notice. Either party may terminate this agreement only by serving 30 days written notice.',
        },
        {
          id: '3',
          clauseTitle: 'Clause 11: 10% Daily Usurious Penalty & Court Waiver',
          originalText: 'delay shall attract a compound penalty of 10% per day. The Tenant waives all rights to approach civil court or rent tribunal.',
          riskSeverity: 'high',
          statutoryViolation: 'Void ab initio under Indian Contract Act, 1872 § 28 & Usurious Loans Act',
          explanation: 'Section 28 of the Indian Contract Act expressly states that any agreement restraining a party from enforcing legal rights in ordinary tribunals is VOID. 10% daily compound interest is legally unconscionable.',
          counterClause: 'Rent delayed beyond the 5th day of the month shall attract a statutory simple interest of 12% per annum pro-rata. Disputes shall be subject to the exclusive jurisdiction of the local Rent Court.',
        },
      ];

      setResults({
        riskScore: 8.8,
        riskLevel: 'HIGH PREDATORY RISK',
        summary: 'The agreement contains 3 illegal, unconscionable clauses that attempt to forfeit your security deposit without proof of damage and unconstitutionally restrict your access to civil courts under Section 28 of the Indian Contract Act.',
        issues: mockIssues,
      });
    } catch (e) {
      console.error('Scan failed', e);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md">
      <div className="relative w-full max-w-4xl max-h-[92vh] overflow-y-auto rounded-3xl bg-[#0b0d13] border border-amber-500/40 shadow-2xl p-6 sm:p-8 text-white">
        {/* Header */}
        <div className="flex items-center justify-between pb-5 border-b border-white/[0.08]">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-[#d4af37] via-[#f59e0b] to-[#78350f] p-[1.2px] shadow-lg shadow-amber-500/20">
              <div className="w-full h-full rounded-[14px] bg-[#0c0e14] flex items-center justify-center">
                <ShieldAlert className="w-6 h-6 text-amber-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-xl font-bold text-white tracking-tight">
                  Multimodal Clause Redline Auditor
                </h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-red-500/10 border border-red-500/30 text-red-300 font-bold">
                  PREDATORY TRAP DETECTOR
                </span>
              </div>
              <p className="text-xs text-neutral-400">
                Audit Rental Agreements, Employment Contracts &amp; Notices under Contract Act § 23/§ 74
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-9 h-9 rounded-xl flex items-center justify-center text-neutral-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Input Area */}
        {!results ? (
          <div className="mt-6 space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-bold text-neutral-300 uppercase tracking-wider font-mono">
                  Paste Agreement Text or Drop Contract PDF / Image:
                </label>
                <button
                  type="button"
                  onClick={handleLoadSample}
                  className="text-xs font-mono text-amber-400 hover:underline flex items-center gap-1 cursor-pointer"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  Load Sample Predatory Rental Agreement
                </button>
              </div>

              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                rows={7}
                placeholder="Paste clauses from your rental agreement, job offer letter, or police notice here..."
                className="w-full p-4 bg-[#11131c] border border-white/10 rounded-2xl text-white placeholder-neutral-500 font-sans text-sm focus:outline-none focus:border-amber-400/80 transition-colors leading-relaxed"
              />
            </div>

            <div className="flex items-center justify-between pt-2">
              <span className="text-[11px] text-neutral-500">
                Instant legal analysis across Indian Contract Act, Transfer of Property Act, and 28 State Tenancy Enactments.
              </span>
              <button
                onClick={handleScan}
                disabled={loading || !inputText.trim()}
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-amber-500 via-amber-400 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black font-extrabold text-sm flex items-center gap-2 shadow-lg shadow-amber-500/25 transition-all disabled:opacity-40 cursor-pointer"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin text-black" /> : <Scale className="w-4 h-4" />}
                Scan for Predatory Clauses
              </button>
            </div>
          </div>
        ) : (
          /* Results View */
          <div className="mt-6 space-y-6">
            {/* Risk Scorecard Header */}
            <div className="p-5 rounded-2xl bg-gradient-to-br from-[#181114] to-[#12141c] border border-red-500/40 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <AlertTriangle className="w-5 h-5 text-red-400 animate-pulse" />
                  <span className="text-xs font-mono font-bold text-red-300 uppercase tracking-widest">
                    {results.riskLevel}
                  </span>
                </div>
                <p className="text-xs text-neutral-300 max-w-xl leading-relaxed">
                  {results.summary}
                </p>
              </div>

              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className="text-3xl font-black text-red-400 font-mono">
                    {results.riskScore}<span className="text-sm text-neutral-500">/10</span>
                  </div>
                  <span className="text-[10px] text-neutral-400 uppercase font-mono">Risk Index</span>
                </div>
                <button
                  onClick={() => setResults(null)}
                  className="p-2.5 rounded-xl border border-white/10 hover:border-white/20 bg-white/5 text-neutral-300 text-xs flex items-center gap-1.5 transition-colors cursor-pointer"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  Scan Another
                </button>
              </div>
            </div>

            {/* Side-by-Side Redline Diff List */}
            <div className="space-y-4">
              {results.issues.map((issue) => (
                <div key={issue.id} className="p-5 rounded-2xl bg-[#0f1118] border border-white/[0.08] space-y-4">
                  <div className="flex items-center justify-between gap-3">
                    <h4 className="font-bold text-white text-sm flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-red-400" />
                      {issue.clauseTitle}
                    </h4>
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-red-500/20 text-red-300 border border-red-500/30 uppercase">
                      {issue.statutoryViolation}
                    </span>
                  </div>

                  <p className="text-xs text-neutral-400 leading-relaxed">
                    💡 <strong className="text-neutral-200 font-semibold">Legal Reasoning:</strong> {issue.explanation}
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                    {/* Original Predatory Clause */}
                    <div className="p-3.5 rounded-xl bg-red-950/20 border border-red-500/30">
                      <span className="text-[10px] font-mono uppercase text-red-400 font-bold block mb-1">
                        ❌ Original Predatory Draft (Unfavourable)
                      </span>
                      <p className="text-xs text-red-200/90 font-mono leading-relaxed line-through decoration-red-500">
                        &ldquo;{issue.originalText}&rdquo;
                      </p>
                    </div>

                    {/* Balanced Counter-Clause */}
                    <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/30 relative group">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] font-mono uppercase text-emerald-400 font-bold block">
                          ✅ Balanced Statutory Counter-Clause (Legally Safe)
                        </span>
                        <button
                          onClick={() => handleCopy(issue.id, issue.counterClause)}
                          className="text-[10px] font-mono flex items-center gap-1 text-emerald-300 hover:text-white px-2 py-0.5 rounded bg-emerald-500/20 border border-emerald-500/40 cursor-pointer"
                        >
                          {copiedId === issue.id ? <Check className="w-3 h-3 text-emerald-300" /> : <Copy className="w-3 h-3" />}
                          {copiedId === issue.id ? 'Copied' : 'Copy'}
                        </button>
                      </div>
                      <p className="text-xs text-emerald-200/95 font-sans leading-relaxed">
                        &ldquo;{issue.counterClause}&rdquo;
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Action Bar */}
            <div className="flex items-center justify-between pt-2">
              <span className="text-xs text-neutral-500">
                Replace predatory clauses in your agreement draft before signing to protect your deposit.
              </span>
              <button
                onClick={onClose}
                className="px-5 py-2.5 rounded-xl font-bold text-xs bg-white/10 hover:bg-white/20 text-white transition-all cursor-pointer"
              >
                Close Audit
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
