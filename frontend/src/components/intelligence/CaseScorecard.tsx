'use client';

import React, { useState } from 'react';
import { ScorecardData } from '@/lib/api';

interface CaseScorecardProps {
  scorecard: ScorecardData | null;
  loading: boolean;
  onRefresh?: () => void;
}

export default function CaseScorecard({ scorecard, loading, onRefresh }: CaseScorecardProps) {
  const [expanded, setExpanded] = useState(true);

  if (loading) {
    return (
      <div className="my-6 p-6 rounded-2xl bg-gradient-to-r from-purple-900/40 via-indigo-900/30 to-purple-900/40 border border-purple-500/30 backdrop-blur-xl shadow-2xl animate-pulse">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 rounded-full bg-purple-500/20 flex items-center justify-center">
            <span className="text-2xl animate-spin">⚖️</span>
          </div>
          <div>
            <h4 className="text-lg font-bold text-purple-200">Generating Live AI Winning Probability Scorecard...</h4>
            <p className="text-xs text-purple-400">Analyzing Bharatiya Sakshya Adhiniyam (BSA 2023) evidence requirements</p>
          </div>
        </div>
      </div>
    );
  }

  if (!scorecard) return null;

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'Low':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
      case 'Medium':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'High':
      case 'Critical':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      default:
        return 'bg-purple-500/20 text-purple-300 border-purple-500/40';
    }
  };

  const getBarColor = (prob: number) => {
    if (prob >= 80) return 'from-emerald-500 to-teal-400';
    if (prob >= 60) return 'from-amber-500 to-yellow-400';
    return 'from-rose-500 to-orange-400';
  };

  return (
    <div className="my-6 rounded-2xl bg-gradient-to-br from-slate-900/90 via-purple-950/60 to-slate-900/90 border border-purple-500/40 backdrop-blur-xl shadow-[0_0_40px_rgba(168,85,247,0.15)] overflow-hidden transition-all duration-300">
      {/* Header bar */}
      <div className="p-5 bg-gradient-to-r from-purple-900/50 to-indigo-900/30 flex items-center justify-between border-b border-purple-500/20">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-purple-500/20 border border-purple-400/30 flex items-center justify-center shadow-lg">
            <span className="text-xl">📊</span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-base font-extrabold text-white tracking-wide">AI CASE WINNING PROBABILITY METER</h3>
              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border uppercase tracking-wider ${getRiskBadge(scorecard.risk_level)}`}>
                Risk: {scorecard.risk_level}
              </span>
            </div>
            <p className="text-xs text-purple-300/80 font-medium">Under {scorecard.applicable_bns_section}</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="p-1.5 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 transition-colors text-xs flex items-center space-x-1"
              title="Recalculate Scorecard"
            >
              <span>🔄 Recalculate</span>
            </button>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1.5 rounded-lg text-purple-300 hover:text-white transition-colors"
          >
            {expanded ? '▲' : '▼'}
          </button>
        </div>
      </div>

      {expanded && (
        <div className="p-6 space-y-6">
          {/* Probability Gauge & Progress */}
          <div className="space-y-2">
            <div className="flex justify-between items-baseline">
              <span className="text-sm font-semibold text-slate-300">Estimated Case Success Rate</span>
              <span className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-indigo-300">
                {scorecard.win_probability}%
              </span>
            </div>
            <div className="w-full h-3.5 bg-slate-800/80 rounded-full overflow-hidden p-0.5 border border-slate-700">
              <div
                className={`h-full rounded-full bg-gradient-to-r ${getBarColor(scorecard.win_probability)} transition-all duration-1000 shadow-[0_0_15px_rgba(168,85,247,0.5)]`}
                style={{ width: `${scorecard.win_probability}%` }}
              />
            </div>
          </div>

          {/* Risk Factor Banner */}
          <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start space-x-3">
            <span className="text-lg mt-0.5">⚠️</span>
            <div>
              <h5 className="text-xs font-bold text-rose-300 uppercase tracking-wider">Primary Risk Factor / Loophole</h5>
              <p className="text-sm text-rose-100 mt-0.5 leading-relaxed">{scorecard.primary_risk_factor}</p>
            </div>
          </div>

          {/* Evidence Booster Tips */}
          <div className="space-y-3">
            <h5 className="text-xs font-extrabold text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
              <span>🚀 Evidence Booster Tips (+15% to +20% Boost under BSA 2023)</span>
            </h5>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {scorecard.evidence_booster_tips.map((tip, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-800/60 border border-slate-700/80 flex items-start space-x-2.5 hover:border-purple-500/40 transition-colors">
                  <span className="text-emerald-400 font-bold text-sm">✓</span>
                  <p className="text-xs text-slate-200 leading-relaxed font-medium">{tip}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
