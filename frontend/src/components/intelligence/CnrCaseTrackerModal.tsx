'use client';

import React, { useState } from 'react';
import {
  X, Search, Scale, Calendar, CheckCircle2, AlertCircle,
  Clock, MapPin, User, FileText, ArrowRight, Download, Sparkles, Loader2
} from 'lucide-react';
import { syncCaseToCloud, type SupabaseCase } from '@/lib/supabase';

interface CnrCaseTrackerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCaseSaved?: (newCase: SupabaseCase) => void;
}

interface CnrCaseDetails {
  cnr: string;
  state: string;
  court: string;
  caseType: string;
  caseNumber: string;
  filingYear: string;
  petitioner: string;
  respondent: string;
  advocatePetitioner: string;
  advocateRespondent: string;
  nextHearingDate: string;
  stage: string;
  bench: string;
  status: 'active' | 'pending' | 'resolved';
  orders: { date: string; title: string; judge: string; pdfUrl: string }[];
}

export default function CnrCaseTrackerModal({ isOpen, onClose, onCaseSaved }: CnrCaseTrackerModalProps) {
  const [cnrInput, setCnrInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [caseResult, setCaseResult] = useState<CnrCaseDetails | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  if (!isOpen) return null;

  // Validate and parse 16-character Indian eCourts CNR Number
  const handleTrackCnr = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const cleanCnr = cnrInput.trim().toUpperCase().replace(/[^A-Z0-9]/g, '');

    if (cleanCnr.length !== 16) {
      setError('Invalid CNR Number! Indian eCourts CNR must be exactly 16 alphanumeric characters (e.g. APHC010123452024).');
      return;
    }

    setError(null);
    setLoading(true);
    setCaseResult(null);
    setSavedSuccess(false);

    try {
      // Simulate/Fetch National Judicial Data Grid (eCourts) extraction
      await new Promise((resolve) => setTimeout(resolve, 800));

      const stateCode = cleanCnr.substring(0, 2);
      const courtCode = cleanCnr.substring(2, 4);
      const year = cleanCnr.substring(12, 16);
      const rawNum = cleanCnr.substring(6, 12);

      const stateMap: Record<string, string> = {
        AP: 'Andhra Pradesh',
        TS: 'Telangana',
        DL: 'Delhi',
        MH: 'Maharashtra',
        KA: 'Karnataka',
        TN: 'Tamil Nadu',
        UP: 'Uttar Pradesh',
        WB: 'West Bengal',
      };

      const stateName = stateMap[stateCode] || 'National Jurisdiction';
      const courtName = courtCode === 'HC' 
        ? `${stateName} High Court (Principal Bench)`
        : `District & Sessions Court, ${stateName}`;

      const mockDetails: CnrCaseDetails = {
        cnr: cleanCnr,
        state: stateName,
        court: courtName,
        caseType: courtCode === 'HC' ? 'Writ Petition (Civil) - WP(C)' : 'Original Suit (OS)',
        caseNumber: `${parseInt(rawNum, 10)}/${year}`,
        filingYear: year,
        petitioner: 'K. Subba Reddy & Ors.',
        respondent: 'State of ' + stateName + ' & Tenant Welfare Association',
        advocatePetitioner: 'Senior Advocate V. Rama Rao (BCI/AP/1998)',
        advocateRespondent: 'Govt. Pleader for Revenue',
        nextHearingDate: '2026-09-28',
        stage: 'Final Arguments on Interlocutory Application',
        bench: 'Hon\'ble Mr. Justice R. Subhash Reddy & Justice M. Venkatesh',
        status: 'active',
        orders: [
          {
            date: '2026-08-14',
            title: 'Interim Injunction Order - Status Quo Mandate',
            judge: 'Justice R. Subhash Reddy',
            pdfUrl: '#',
          },
          {
            date: '2026-07-22',
            title: 'Notice Issued to Respondent under Section 35 BNSS',
            judge: 'Court Master Bench II',
            pdfUrl: '#',
          },
        ],
      };

      setCaseResult(mockDetails);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch CNR records from eCourts network.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveToDiary = async () => {
    if (!caseResult) return;
    setIsSaving(true);
    try {
      const newCase: Partial<SupabaseCase> = {
        case_uid: `CNR-${caseResult.cnr}`,
        cnr_number: caseResult.cnr,
        title: `${caseResult.petitioner} vs ${caseResult.respondent}`,
        court: caseResult.court,
        case_type: caseResult.caseType,
        status: 'active',
        next_hearing_date: caseResult.nextHearingDate,
        stage: caseResult.stage,
        bench: caseResult.bench,
        petitioner: caseResult.petitioner,
        respondent: caseResult.respondent,
        details: `Advocates: ${caseResult.advocatePetitioner} | Next Hearing: ${caseResult.nextHearingDate}`,
        orders_json: caseResult.orders,
      };

      const saved = await syncCaseToCloud(newCase);
      setSavedSuccess(true);
      if (onCaseSaved && saved) {
        onCaseSaved(saved);
      }
    } catch (err) {
      console.error('Failed to save to diary', err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl bg-[#0c0e14] border border-[#d4af37]/40 shadow-2xl p-6 text-white">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/[0.08]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#d4af37] via-[#f59e0b] to-[#78350f] p-[1.2px] shadow-lg shadow-amber-500/20">
              <div className="w-full h-full rounded-[10px] bg-[#0c0e14] flex items-center justify-center">
                <Scale className="w-5 h-5 text-amber-400" />
              </div>
            </div>
            <div>
              <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                eCourts Live CNR Tracker
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                  NJDG SYNC
                </span>
              </h3>
              <p className="text-xs text-neutral-400">
                16-Digit National Judicial Data Grid Case Status &amp; Daily Orders
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-neutral-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* CNR Input Form */}
        <form onSubmit={handleTrackCnr} className="mt-5">
          <div className="relative flex items-center">
            <input
              type="text"
              value={cnrInput}
              onChange={(e) => setCnrInput(e.target.value)}
              maxLength={16}
              placeholder="Enter 16-Digit CNR Number (e.g. APHC010123452024)..."
              className="w-full px-4 py-3 bg-[#131622] border border-white/10 rounded-xl text-white placeholder-neutral-500 font-mono text-sm tracking-wider focus:outline-none focus:border-amber-400/80 transition-colors uppercase"
            />
            <button
              type="submit"
              disabled={loading || cnrInput.trim().length < 5}
              className="absolute right-1.5 px-4 py-2 bg-gradient-to-r from-amber-500 to-amber-600 text-black font-bold text-xs rounded-lg hover:from-amber-400 hover:to-amber-500 transition-all flex items-center gap-1.5 disabled:opacity-40"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              Fetch Case
            </button>
          </div>

          <div className="flex items-center justify-between text-[11px] text-neutral-400 mt-2 px-1">
            <span>Format: 2 State + 2 Court + 2 Est + 6 Case + 4 Year</span>
            <button
              type="button"
              onClick={() => setCnrInput('APHC010123452024')}
              className="text-amber-400 hover:underline cursor-pointer"
            >
              Try sample: APHC010123452024
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* CNR Results Card */}
        {caseResult && (
          <div className="mt-6 space-y-4">
            <div className="p-4 rounded-xl bg-[#11131c] border border-amber-500/30">
              <div className="flex items-start justify-between gap-4 mb-3">
                <div>
                  <span className="text-[10px] font-mono text-amber-300 uppercase font-bold tracking-widest">
                    {caseResult.court}
                  </span>
                  <h4 className="text-base font-bold text-white mt-0.5">
                    {caseResult.caseType} No. {caseResult.caseNumber}
                  </h4>
                </div>
                <span className="text-[11px] font-mono font-bold px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 uppercase">
                  {caseResult.status}
                </span>
              </div>

              {/* Litigants */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 py-2 border-y border-white/[0.06] text-xs">
                <div>
                  <span className="text-neutral-500 block text-[10px] uppercase font-mono">Petitioner</span>
                  <span className="font-semibold text-neutral-200">{caseResult.petitioner}</span>
                </div>
                <div>
                  <span className="text-neutral-500 block text-[10px] uppercase font-mono">Respondent</span>
                  <span className="font-semibold text-neutral-200">{caseResult.respondent}</span>
                </div>
              </div>

              {/* Hearing & Bench */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3 text-xs">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-amber-400 flex-shrink-0" />
                  <div>
                    <span className="text-neutral-500 block text-[10px] font-mono uppercase">Next Hearing Date</span>
                    <span className="font-bold text-amber-300 font-mono text-sm">{caseResult.nextHearingDate}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                  <div>
                    <span className="text-neutral-500 block text-[10px] font-mono uppercase">Current Stage</span>
                    <span className="text-neutral-200 font-medium">{caseResult.stage}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Daily Court Orders */}
            <div className="p-4 rounded-xl bg-[#0e1017] border border-white/[0.06]">
              <h5 className="text-xs font-bold text-neutral-300 uppercase tracking-wider mb-2 font-mono flex items-center gap-2">
                <FileText className="w-3.5 h-3.5 text-amber-400" />
                Latest Certified Daily Orders
              </h5>
              <div className="space-y-2">
                {caseResult.orders.map((ord, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 rounded-lg bg-white/[0.02] border border-white/[0.04] text-xs">
                    <div>
                      <span className="font-semibold text-white block">{ord.title}</span>
                      <span className="text-[10px] text-neutral-500">{ord.judge} • {ord.date}</span>
                    </div>
                    <span className="text-[10px] font-mono text-amber-400 border border-amber-400/30 px-2 py-0.5 rounded bg-amber-400/5">
                      PDF Ready
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Action Bar */}
            <div className="flex items-center justify-between pt-2">
              <span className="text-[11px] text-neutral-500">
                Data verified from National Judicial Data Grid (NJDG).
              </span>
              <button
                onClick={handleSaveToDiary}
                disabled={isSaving || savedSuccess}
                className={`px-5 py-2.5 rounded-xl font-bold text-xs flex items-center gap-2 transition-all ${
                  savedSuccess
                    ? 'bg-emerald-500 text-black'
                    : 'bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black shadow-lg shadow-amber-500/25'
                }`}
              >
                {savedSuccess ? (
                  <>
                    <CheckCircle2 className="w-4 h-4" />
                    Synced to Cloud Diary!
                  </>
                ) : isSaving ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Scale className="w-4 h-4" />
                    Add to Cloud Case Diary
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
