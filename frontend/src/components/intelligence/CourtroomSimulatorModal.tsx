'use client';

import React, { useState } from 'react';
import { SimulationData, PersonaView } from '@/lib/api';

interface CourtroomSimulatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  simulation?: SimulationData | null;
  loading?: boolean;
  situation?: string;
}

export default function CourtroomSimulatorModal({
  isOpen,
  onClose,
  simulation = null,
  loading = false,
  situation = '',
}: CourtroomSimulatorModalProps) {
  const [activeTab, setActiveTab] = useState<'counsel' | 'defense' | 'judge'>('counsel');

  if (!isOpen) return null;

  const renderPersonaCard = (view: PersonaView, type: 'counsel' | 'defense' | 'judge') => {
    const getTheme = () => {
      switch (type) {
        case 'counsel':
          return {
            border: 'border-purple-500/50',
            bg: 'from-purple-950/80 to-indigo-950/80',
            badge: 'bg-purple-500/20 text-purple-300 border-purple-500/40',
            icon: '🛡️',
            titleColor: 'text-purple-300',
            accent: 'border-purple-500',
          };
        case 'defense':
          return {
            border: 'border-rose-500/50',
            bg: 'from-rose-950/80 to-slate-950/80',
            badge: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
            icon: '🔴',
            titleColor: 'text-rose-300',
            accent: 'border-rose-500',
          };
        case 'judge':
          return {
            border: 'border-amber-500/50',
            bg: 'from-amber-950/80 to-yellow-950/80',
            badge: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
            icon: '⚖️',
            titleColor: 'text-amber-300',
            accent: 'border-amber-500',
          };
      }
    };

    const theme = getTheme();

    return (
      <div className={`p-6 rounded-2xl bg-gradient-to-br ${theme.bg} border ${theme.border} backdrop-blur-xl shadow-2xl flex flex-col justify-between space-y-6 h-full transition-all duration-300`}>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center space-x-1.5 ${theme.badge}`}>
              <span>{theme.icon}</span>
              <span>{view.role}</span>
            </span>
          </div>

          <h4 className={`text-lg font-black ${theme.titleColor}`}>{view.title}</h4>

          <div className="space-y-3">
            <h5 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Courtroom Arguments & Observations</h5>
            <div className="space-y-2">
              {view.arguments.map((arg, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start space-x-3">
                  <span className="text-xs font-bold text-slate-500 mt-0.5">{idx + 1}.</span>
                  <p className="text-sm text-slate-200 leading-relaxed">{arg}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-2 pt-4 border-t border-slate-800">
          <h5 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Citations & Precedents Relied Upon</h5>
          <div className="flex flex-wrap gap-2">
            {view.legal_citations.map((cite, idx) => (
              <span key={idx} className="px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-700 text-xs font-mono text-slate-300 flex items-center space-x-1 shadow-sm">
                <span>📖</span>
                <span>{cite}</span>
              </span>
            ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-6xl max-h-[90vh] rounded-3xl bg-slate-900/95 border border-purple-500/40 shadow-[0_0_80px_rgba(168,85,247,0.25)] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-6 bg-gradient-to-r from-purple-950 via-slate-900 to-indigo-950 border-b border-purple-500/30 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
              <span className="text-2xl">⚔️</span>
            </div>
            <div>
              <h2 className="text-xl font-black text-white tracking-wide">INTERACTIVE 360° COURTROOM SIMULATOR</h2>
              <p className="text-xs text-purple-300/80">Simulating real Indian Court proceedings under BNS 2023, BNSS 2023 & Supreme Court Precedents</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-10 h-10 rounded-xl bg-slate-800 hover:bg-rose-500/20 hover:text-rose-400 text-slate-400 flex items-center justify-center text-lg transition-all"
          >
            ✕
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="h-96 flex flex-col items-center justify-center space-y-4 text-center">
              <div className="w-16 h-16 rounded-full border-4 border-purple-500 border-t-transparent animate-spin" />
              <h3 className="text-lg font-bold text-white">Convening Virtual Court Bench & Counsel...</h3>
              <p className="text-sm text-slate-400 max-w-md">
                Advocate YAMA and Defense Counsel are presenting arguments while the Magistrate reviews statutory precedents under BNS & IT Act.
              </p>
            </div>
          ) : simulation ? (
            <>
              {/* Strategic Summary Banner */}
              <div className="p-4 rounded-2xl bg-gradient-to-r from-amber-500/20 via-purple-500/20 to-emerald-500/20 border border-amber-500/40 flex items-center space-x-4 shadow-lg">
                <span className="text-2xl">💡</span>
                <div>
                  <h4 className="text-xs font-bold text-amber-300 uppercase tracking-wider">Presiding Bench Strategic Takeaway for You</h4>
                  <p className="text-sm font-semibold text-white mt-0.5">{simulation.summary}</p>
                </div>
              </div>

              {/* Mobile Tabs Selector (Visible on Small Screens) */}
              <div className="flex lg:hidden rounded-xl bg-slate-800 p-1 border border-slate-700">
                <button
                  onClick={() => setActiveTab('counsel')}
                  className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${activeTab === 'counsel' ? 'bg-purple-600 text-white shadow-lg' : 'text-slate-400'}`}
                >
                  🛡️ Counsel View
                </button>
                <button
                  onClick={() => setActiveTab('defense')}
                  className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${activeTab === 'defense' ? 'bg-rose-600 text-white shadow-lg' : 'text-slate-400'}`}
                >
                  🔴 Defense View
                </button>
                <button
                  onClick={() => setActiveTab('judge')}
                  className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${activeTab === 'judge' ? 'bg-amber-600 text-white shadow-lg' : 'text-slate-400'}`}
                >
                  ⚖️ Judge Verdict
                </button>
              </div>

              {/* Grid for Desktop (Side-by-Side 3 columns), Single Card on Mobile */}
              <div className="hidden lg:grid grid-cols-3 gap-6 items-stretch">
                {renderPersonaCard(simulation.counsel_view, 'counsel')}
                {renderPersonaCard(simulation.defense_view, 'defense')}
                {renderPersonaCard(simulation.judge_verdict, 'judge')}
              </div>

              <div className="block lg:hidden">
                {activeTab === 'counsel' && renderPersonaCard(simulation.counsel_view, 'counsel')}
                {activeTab === 'defense' && renderPersonaCard(simulation.defense_view, 'defense')}
                {activeTab === 'judge' && renderPersonaCard(simulation.judge_verdict, 'judge')}
              </div>
            </>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-500">
              No simulation data generated yet.
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-950 border-t border-slate-800/80 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold text-sm shadow-lg hover:shadow-purple-500/30 transition-all"
          >
            Close Courtroom Arena
          </button>
        </div>
      </div>
    </div>
  );
}
