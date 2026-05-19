'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Scale, BookOpen, ChevronRight, ChevronDown, Loader2, ChevronLeft } from 'lucide-react';
import { getActs, getSectionsByAct } from '@/lib/api';
import type { LawSection } from '@/types';

export default function ExplorePage() {
  const [acts, setActs] = useState<{ act_name: string }[]>([]);
  const [selectedAct, setSelectedAct] = useState<string | null>(null);
  const [sections, setSections] = useState<LawSection[]>([]);
  const [isLoadingActs, setIsLoadingActs] = useState(true);
  const [isLoadingSections, setIsLoadingSections] = useState(false);

  useEffect(() => {
    getActs().then(setActs).catch(() => setActs([])).finally(() => setIsLoadingActs(false));
  }, []);

  const handleSelectAct = async (actName: string) => {
    setSelectedAct(actName);
    setIsLoadingSections(true);
    try { setSections(await getSectionsByAct(actName)); }
    catch { setSections([]); }
    finally { setIsLoadingSections(false); }
  };

  return (
    <div className="min-h-screen bg-justice-dark text-white">
      <header className="border-b border-white/[0.07] glass-dark sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/" className="text-white/40 hover:text-white transition-colors p-1.5 rounded-lg hover:bg-white/5">
              <ChevronLeft className="w-5 h-5" />
            </Link>
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gold-gradient flex items-center justify-center shadow-gold">
                <Scale className="w-4 h-4 text-justice-dark" />
              </div>
              <div>
                <h1 className="text-sm font-bold leading-none">YAMA AI</h1>
                <p className="text-[10px] text-white/35 mt-0.5">Section Explorer</p>
              </div>
            </div>
          </div>
          <nav className="flex gap-1">
            <Link href="/chat"   className="px-3 py-1.5 text-white/45 hover:text-white hover:bg-white/5 rounded-lg text-xs transition-colors">Chat</Link>
            <Link href="/search" className="px-3 py-1.5 text-white/45 hover:text-white hover:bg-white/5 rounded-lg text-xs transition-colors">Search Laws</Link>
          </nav>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-10">
        <h2 className="text-2xl font-bold text-white mb-1">Explore Indian Acts</h2>
        <p className="text-white/40 text-sm mb-8">Browse sections of any Indian act — select an act from the list to view its contents.</p>

        <div className="grid md:grid-cols-3 gap-6">
          <div className="md:col-span-1">
            <p className="text-[11px] font-semibold text-white/30 uppercase tracking-widest mb-3">
              {isLoadingActs ? 'Loading...' : `${acts.length} Acts Available`}
            </p>
            {isLoadingActs ? (
              <div className="flex items-center gap-2 text-white/30 py-4">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Loading acts...</span>
              </div>
            ) : (
              <div className="space-y-1.5 max-h-[70vh] overflow-y-auto pr-1">
                {acts.map((act) => (
                  <button
                    key={act.act_name}
                    onClick={() => handleSelectAct(act.act_name)}
                    className={`w-full text-left px-3.5 py-2.5 rounded-xl text-sm transition-all flex items-center justify-between group ${
                      selectedAct === act.act_name
                        ? 'text-justice-dark font-semibold shadow-gold'
                        : 'glass text-white/55 hover:text-white hover:border-gold-500/20'
                    }`}
                    style={selectedAct === act.act_name ? { background: 'linear-gradient(135deg, #fbbf24, #e2b659)' } : undefined}
                  >
                    <span className="truncate pr-2">{act.act_name}</span>
                    <ChevronRight className="w-3.5 h-3.5 flex-shrink-0 opacity-50" />
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="md:col-span-2">
            {selectedAct ? (
              <>
                <div className="flex items-center gap-2.5 mb-5">
                  <BookOpen className="w-5 h-5 text-gold-400" />
                  <h3 className="text-base font-bold text-white">{selectedAct}</h3>
                </div>
                {isLoadingSections ? (
                  <div className="flex items-center gap-3 text-white/30 py-10">
                    <Loader2 className="w-5 h-5 animate-spin text-gold-400" />
                    <span className="text-sm">Loading sections...</span>
                  </div>
                ) : sections.length === 0 ? (
                  <p className="text-white/30 py-10 text-sm">No sections found for this act.</p>
                ) : (
                  <div className="space-y-2.5">
                    {sections.map((section) => <SectionCard key={section.id} section={section} />)}
                  </div>
                )}
              </>
            ) : (
              <div className="flex flex-col items-center justify-center py-24 text-center glass rounded-2xl">
                <div className="w-14 h-14 rounded-2xl bg-gold-500/10 flex items-center justify-center mb-4">
                  <BookOpen className="w-7 h-7 text-gold-400/50" />
                </div>
                <p className="text-white/30 text-sm">Select an act from the left to view its sections</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function SectionCard({ section }: { section: LawSection }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="glass rounded-xl p-4 cursor-pointer hover:border-gold-500/20 transition-all" onClick={() => setExpanded(!expanded)}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <span className="text-[11px] font-semibold text-gold-400 bg-gold-500/10 px-2 py-0.5 rounded-lg border border-gold-500/15">§ {section.section_number}</span>
          <h4 className="font-medium text-white mt-2">{section.title}</h4>
        </div>
        <ChevronDown className={`w-4 h-4 text-white/25 flex-shrink-0 mt-1 transition-transform ${expanded ? 'rotate-180' : ''}`} />
      </div>
      {expanded && (
        <div className="mt-3 pt-3 border-t border-white/[0.07] space-y-2.5">
          <p className="text-sm text-white/60 leading-relaxed">{section.description}</p>
          {section.punishment && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-3.5 py-2.5">
              <span className="text-[11px] font-semibold text-red-400/70 uppercase tracking-wider">Punishment: </span>
              <span className="text-xs text-red-300">{section.punishment}</span>
            </div>
          )}
          {section.old_law_reference && (
            <p className="text-xs text-white/30"><span className="font-medium text-white/40">Old Law: </span>{section.old_law_reference}</p>
          )}
        </div>
      )}
    </div>
  );
}
