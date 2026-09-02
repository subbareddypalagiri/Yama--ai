'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { Scale, BookOpen, ChevronRight, ChevronDown, Loader2, Globe, Sparkles, X } from 'lucide-react';
import { getActs, getSectionsByAct } from '@/lib/api';
import UnifiedNavbar from '@/components/layout/UnifiedNavbar';
import type { LawSection } from '@/types';

const GlobeStudy = dynamic(() => import('@/components/ui/GlobeStudy'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[400px] flex items-center justify-center bg-[#08090a] text-gray-500 text-xs font-mono">
      Initializing 3D Jurisprudence Globe...
    </div>
  ),
});

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
    <div className="min-h-screen bg-[#08090d] text-white font-sans">
      <UnifiedNavbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {/* Top Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 pb-6 border-b border-[#1b1f2b]">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[#2c3244] bg-[#12141c] text-amber-300 text-[11px] font-bold uppercase tracking-widest mb-3">
              <Scale className="w-3.5 h-3.5 text-[#f59e0b]" />
              <span>Statutory Repository</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Explore Indian Central Bare Acts
            </h2>
            <p className="text-gray-400 text-xs sm:text-sm mt-1">
              Select an Act to explore sections, punishments, and historical IPC/CrPC transitions.
            </p>
          </div>

          {selectedAct && (
            <button
              onClick={() => setSelectedAct(null)}
              className="flex items-center gap-2 px-4 py-2 rounded-full bg-[#141722] border border-[#272d3e] hover:border-[#d4af37] text-xs font-semibold text-amber-300 transition-all self-start sm:self-auto"
            >
              <Globe className="w-3.5 h-3.5 text-[#f59e0b]" />
              <span>Show 3D Jurisprudence Globe</span>
            </button>
          )}
        </div>

        {/* 2-Column Split: Acts List vs. Interactive Section / 3D Globe */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Acts Directory (4 cols) */}
          <div className="lg:col-span-4 flex flex-col">
            <div className="flex items-center justify-between mb-3 px-1">
              <span className="text-[11px] font-mono font-bold text-gray-400 uppercase tracking-wider">
                {isLoadingActs ? 'Loading Directory...' : `${acts.length} Live Acts`}
              </span>
              <span className="text-[10px] text-amber-400/80 font-mono">BNS • BNSS • BSA Compliant</span>
            </div>

            {isLoadingActs ? (
              <div className="flex items-center gap-2 text-gray-400 py-8 px-4 rounded-2xl bg-[#0f1118] border border-[#1d212e]">
                <Loader2 className="w-4 h-4 animate-spin text-[#f59e0b]" />
                <span className="text-xs">Loading legal acts index...</span>
              </div>
            ) : (
              <div className="space-y-1.5 max-h-[72vh] overflow-y-auto pr-1">
                {acts.map((act) => {
                  const isSelected = selectedAct === act.act_name;
                  return (
                    <button
                      key={act.act_name}
                      onClick={() => handleSelectAct(act.act_name)}
                      className={`w-full text-left px-4 py-3 rounded-xl text-xs font-semibold transition-all flex items-center justify-between border ${
                        isSelected
                          ? 'bg-[#1a1e2b] text-amber-200 border-[#d4af37]/70 shadow-sm'
                          : 'bg-[#0f1118] text-gray-300 hover:text-white border-[#1d212e] hover:border-[#2f354a] hover:bg-[#141722]'
                      }`}
                    >
                      <span className="truncate pr-3">{act.act_name}</span>
                      <ChevronRight className={`w-3.5 h-3.5 shrink-0 ${isSelected ? 'text-[#f59e0b]' : 'text-gray-500'}`} />
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Right Column: Sections Viewer OR 3D Globe Showcase (8 cols) */}
          <div className="lg:col-span-8">
            {selectedAct ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-2xl bg-[#0f1118] border border-[#1d212e]">
                  <div className="flex items-center gap-2.5">
                    <BookOpen className="w-5 h-5 text-[#f59e0b]" />
                    <div>
                      <h3 className="text-sm sm:text-base font-bold text-white">{selectedAct}</h3>
                      <p className="text-[11px] text-gray-400">{sections.length} Sections Indexed</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedAct(null)}
                    className="text-xs text-gray-400 hover:text-white px-2.5 py-1 rounded-lg bg-[#161822] border border-[#242838]"
                  >
                    Close Act
                  </button>
                </div>

                {isLoadingSections ? (
                  <div className="flex flex-col items-center justify-center py-20 bg-[#0f1118] border border-[#1d212e] rounded-2xl">
                    <Loader2 className="w-6 h-6 animate-spin text-[#f59e0b] mb-3" />
                    <span className="text-xs text-gray-400">Loading statutory sections...</span>
                  </div>
                ) : sections.length === 0 ? (
                  <div className="p-8 text-center bg-[#0f1118] border border-[#1d212e] rounded-2xl text-gray-400 text-xs">
                    No sections found for this act.
                  </div>
                ) : (
                  <div className="space-y-2.5 max-h-[70vh] overflow-y-auto pr-1">
                    {sections.map((section) => (
                      <SectionCard key={section.id} section={section} />
                    ))}
                  </div>
                )}
              </div>
            ) : (
              /* THE 3D JURISPRUDENCE GLOBE SHOWCASE PEDESTAL */
              <div className="w-full rounded-2xl bg-[#0a0b10] border border-[#1f2330] overflow-hidden flex flex-col shadow-2xl">
                {/* Micro Header */}
                <div className="flex items-center justify-between px-5 py-3 border-b border-[#1b1f2b] bg-[#0c0e14] text-[11px] font-mono">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-[#f59e0b] animate-pulse" />
                    <span className="text-gray-200 font-bold uppercase tracking-wider">
                      ALL-INDIA JURISPRUDENCE MATRIX
                    </span>
                  </div>
                  <span className="text-[10px] text-gray-500 font-bold">FIG 06 • 3D TEXT-ON-A-PATH GLOBE</span>
                </div>

                {/* Globe Canvas Container */}
                <div className="relative w-full h-[460px] bg-[#08090a]">
                  <GlobeStudy mode="dark" scale={1} opacity={1} />
                </div>

                {/* Interactive Footer Navigation Bar */}
                <div className="px-5 py-3 border-t border-[#1b1f2b] bg-[#0c0e14] flex flex-col sm:flex-row items-center justify-between gap-2 text-xs">
                  <span className="font-mono text-[10px] text-gray-500 tracking-wider">
                    DRAG TO ROTATE • SCROLL TO ZOOM • CLICK TO PIN NODES
                  </span>
                  <span className="text-amber-400 font-semibold text-xs flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Select any Central Act on the left to explore sections</span>
                  </span>
                </div>
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
    <div
      className="p-4 rounded-xl bg-[#0f1118] border border-[#1d212e] hover:border-[#2f354a] cursor-pointer transition-all"
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <span className="text-[11px] font-mono font-bold text-amber-300 bg-[#1e1a14] px-2.5 py-0.5 rounded-full border border-[#3d311f]">
            § {section.section_number}
          </span>
          <h4 className="font-bold text-sm text-white mt-2">{section.title}</h4>
        </div>
        <ChevronDown className={`w-4 h-4 text-gray-500 shrink-0 mt-1 transition-transform ${expanded ? 'rotate-180 text-amber-400' : ''}`} />
      </div>
      {expanded && (
        <div className="mt-3 pt-3 border-t border-[#1b1f2b] space-y-3">
          <p className="text-xs text-gray-300 leading-relaxed">{section.description}</p>
          {section.punishment && (
            <div className="bg-[#1c1215] border border-[#3d1a21] rounded-xl px-3.5 py-2">
              <span className="text-[11px] font-bold text-red-400 uppercase tracking-wider">Punishment: </span>
              <span className="text-xs text-red-200">{section.punishment}</span>
            </div>
          )}
          {section.old_law_reference && (
            <p className="text-xs text-gray-400">
              <span className="font-semibold text-gray-300">Old Law Equivalent: </span>
              {section.old_law_reference}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
