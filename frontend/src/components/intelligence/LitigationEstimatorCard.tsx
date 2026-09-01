'use client';

import React from 'react';
import { EstimatorData } from '@/lib/api';

interface LitigationEstimatorCardProps {
  isOpen: boolean;
  onClose: () => void;
  estimator: EstimatorData | null;
  loading: boolean;
}

export default function LitigationEstimatorCard({
  isOpen,
  onClose,
  estimator,
  loading,
}: LitigationEstimatorCardProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-4xl rounded-3xl bg-slate-900 border border-emerald-500/40 shadow-[0_0_80px_rgba(16,185,129,0.2)] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-6 bg-gradient-to-r from-emerald-950 via-slate-900 to-teal-950 border-b border-emerald-500/30 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/30">
              <span className="text-2xl">⏳</span>
            </div>
            <div>
              <h2 className="text-xl font-black text-white tracking-wide">LITIGATION TIMELINE & COST ESTIMATOR</h2>
              <p className="text-xs text-emerald-300/80">Transparent judicial cost & timeline audit under Indian Court Fee & Procedural rules</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-10 h-10 rounded-xl bg-slate-800 hover:bg-emerald-500/20 text-slate-400 hover:text-emerald-300 flex items-center justify-center text-lg transition-all"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[80vh] space-y-6">
          {loading ? (
            <div className="h-64 flex flex-col items-center justify-center space-y-4 text-center">
              <div className="w-14 h-14 rounded-full border-4 border-emerald-500 border-t-transparent animate-spin" />
              <h3 className="text-lg font-bold text-white">Auditing Court Stamp Duties & Jurisdiction Timelines...</h3>
              <p className="text-sm text-slate-400">Calculating statutory fees and fast-track dispute resolution pathways.</p>
            </div>
          ) : estimator ? (
            <div className="space-y-6">
              {/* Category tag */}
              <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-800/80 border border-slate-700">
                <div>
                  <span className="text-[11px] font-mono font-bold text-emerald-400 uppercase tracking-wider">Case Classification</span>
                  <h3 className="text-lg font-black text-white mt-0.5">{estimator.case_type}</h3>
                </div>
                <span className="px-3 py-1.5 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 font-bold text-xs">
                  {estimator.key_steps_count} Procedural Stages
                </span>
              </div>

              {/* Grid 3 big cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Duration */}
                <div className="p-5 rounded-2xl bg-gradient-to-br from-slate-900 to-emerald-950/40 border border-emerald-500/30 flex flex-col justify-between space-y-3">
                  <div>
                    <span className="text-2xl">⏳</span>
                    <h4 className="text-xs font-bold text-emerald-300 uppercase tracking-wider mt-2">Estimated Timeline</h4>
                  </div>
                  <p className="text-base font-black text-white leading-snug">{estimator.estimated_duration}</p>
                  <span className="text-[11px] text-slate-400 font-medium">Includes notice period, pleading & argument stages</span>
                </div>

                {/* Court Fee */}
                <div className="p-5 rounded-2xl bg-gradient-to-br from-slate-900 to-indigo-950/40 border border-indigo-500/30 flex flex-col justify-between space-y-3">
                  <div>
                    <span className="text-2xl">🏛️</span>
                    <h4 className="text-xs font-bold text-indigo-300 uppercase tracking-wider mt-2">Court Stamp Duty</h4>
                  </div>
                  <p className="text-base font-black text-white leading-snug">{estimator.court_fee_stamp_duty}</p>
                  <span className="text-[11px] text-slate-400 font-medium">Statutory court stamps payable under Court Fees Act</span>
                </div>

                {/* Lawyer Fee Range */}
                <div className="p-5 rounded-2xl bg-gradient-to-br from-slate-900 to-purple-950/40 border border-purple-500/30 flex flex-col justify-between space-y-3">
                  <div>
                    <span className="text-2xl">💼</span>
                    <h4 className="text-xs font-bold text-purple-300 uppercase tracking-wider mt-2">Litigation Fee Range</h4>
                  </div>
                  <p className="text-base font-black text-white leading-snug">{estimator.lawyer_fee_range}</p>
                  <span className="text-[11px] text-slate-400 font-medium">Typical bar advocate retainership & drafting cost</span>
                </div>
              </div>

              {/* Fast track remedy */}
              <div className="p-5 rounded-2xl bg-gradient-to-r from-emerald-500/20 via-teal-500/20 to-slate-900 border border-emerald-500/50 space-y-2 shadow-xl">
                <div className="flex items-center space-x-2">
                  <span className="text-xl">🚀</span>
                  <h4 className="text-sm font-black text-emerald-300 uppercase tracking-wider">Fast-Track ₹0 Cost Alternative Remedy</h4>
                </div>
                <p className="text-sm font-semibold text-white leading-relaxed">{estimator.fast_track_remedy}</p>
                <p className="text-xs text-emerald-200/80">
                  Instead of lengthy court proceedings, utilizing statutory online portals or District Legal Services Authority (DLSA) can resolve this swiftly at zero court fee.
                </p>
              </div>
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center text-slate-500">
              No estimation data generated yet.
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-950 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-bold text-sm shadow-lg hover:shadow-emerald-500/30 transition-all"
          >
            Close Cost Estimator
          </button>
        </div>
      </div>
    </div>
  );
}
