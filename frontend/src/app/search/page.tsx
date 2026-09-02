'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Scale, Search, Loader2, ChevronLeft, AlertCircle, X, ArrowRight, FileText,
  Shield, Lock, Car, Users, ShoppingBag, Briefcase, Gavel, FileCheck, Landmark, Building2, BookOpen
} from 'lucide-react';
import { 
  searchLaws, searchStateLaws, searchSupremeCourt, searchHighCourts, getLegalDatabaseStats 
} from '@/lib/api';
import type { LawSection } from '@/types';
import TiltCard from '@/components/ui/TiltCard';

const TABS = [
  { id: 'central', label: 'Central Bare Acts', icon: BookOpen },
  { id: 'state', label: 'State Acts (28 States)', icon: Building2 },
  { id: 'sc', label: 'Supreme Court Precedents', icon: Scale },
  { id: 'hc', label: '25 State High Courts', icon: Landmark },
];

const STATES = [
  { code: '', name: 'All States & UTs' },
  { code: 'TG', name: 'Telangana' },
  { code: 'AP', name: 'Andhra Pradesh' },
  { code: 'MH', name: 'Maharashtra' },
  { code: 'DL', name: 'Delhi NCR' },
  { code: 'KA', name: 'Karnataka' },
  { code: 'TN', name: 'Tamil Nadu' },
  { code: 'WB', name: 'West Bengal' },
  { code: 'UP', name: 'Uttar Pradesh' },
  { code: 'KL', name: 'Kerala' },
  { code: 'GJ', name: 'Gujarat' },
];

const HIGH_COURTS = [
  { code: '', name: 'All 25 High Courts' },
  { code: 'HCTG', name: 'High Court of Telangana (Hyderabad)' },
  { code: 'HCAP', name: 'High Court of Andhra Pradesh (Amaravati)' },
  { code: 'HCDL', name: 'High Court of Delhi (New Delhi)' },
  { code: 'HCMH', name: 'Bombay High Court (Mumbai)' },
  { code: 'HCMDS', name: 'Madras High Court (Chennai)' },
  { code: 'HCCAL', name: 'Calcutta High Court (Kolkata)' },
  { code: 'HCALL', name: 'Allahabad High Court (Prayagraj)' },
  { code: 'HCKA', name: 'High Court of Karnataka (Bengaluru)' },
  { code: 'HCKL', name: 'High Court of Kerala (Kochi)' },
  { code: 'HCGJ', name: 'Gujarat High Court (Ahmedabad)' },
];

const CATEGORIES = [
  { slug: '', label: 'All Categories' },
  { slug: 'criminal', label: 'Criminal Law' },
  { slug: 'constitutional', label: 'Constitutional Law' },
  { slug: 'consumer', label: 'Consumer Protection' },
  { slug: 'cyber', label: 'Cyber & IT Law' },
  { slug: 'motor_vehicle', label: 'Motor Vehicle Law' },
  { slug: 'civil', label: 'Civil Law' },
  { slug: 'family', label: 'Family Law' },
];

export default function SearchPage() {
  const [activeTab, setActiveTab] = useState<'central' | 'state' | 'sc' | 'hc'>('central');
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [selectedState, setSelectedState] = useState('');
  const [selectedCourt, setSelectedCourt] = useState('');
  
  const [centralResults, setCentralResults] = useState<any[]>([]);
  const [stateResults, setStateResults] = useState<any[]>([]);
  const [scResults, setScResults] = useState<any[]>([]);
  const [hcResults, setHcResults] = useState<any[]>([]);
  
  const [stats, setStats] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedItem, setSelectedItem] = useState<any | null>(null);

  useEffect(() => {
    getLegalDatabaseStats().then(setStats).catch(() => {});
  }, []);

  const executeSearch = async () => {
    setIsLoading(true);
    try {
      if (activeTab === 'central') {
        const data = await searchLaws(query, category || undefined, 30);
        setCentralResults(data.results || []);
      } else if (activeTab === 'state') {
        const data = await searchStateLaws(query, selectedState || undefined, 30);
        setStateResults(data.results || []);
      } else if (activeTab === 'sc') {
        const data = await searchSupremeCourt(query, 30);
        setScResults(data.results || []);
      } else if (activeTab === 'hc') {
        const data = await searchHighCourts(query, selectedCourt || undefined, selectedState || undefined, 30);
        setHcResults(data.results || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    executeSearch();
  }, [activeTab, category, selectedState, selectedCourt]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeSearch();
  };

  return (
    <div className="min-h-screen bg-justice-dark text-white">
      {/* Header */}
      <header className="border-b border-white/[0.07] glass-dark sticky top-0 z-20">
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
                <p className="text-[10px] text-white/35 mt-0.5">Enterprise Indian Legal Knowledge Base</p>
              </div>
            </div>
          </div>
          <nav className="flex gap-1.5">
            <Link href="/chat" className="px-3 py-1.5 text-white/60 hover:text-white hover:bg-white/5 rounded-lg text-xs font-medium transition-colors">Chat</Link>
            <Link href="/lawyer" className="px-3 py-1.5 text-white/60 hover:text-white hover:bg-white/5 rounded-lg text-xs font-medium transition-colors">Your Lawyer</Link>
          </nav>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Title & Live Database Stats Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
              <span>National Law &amp; Court Precedents Repository</span>
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-normal">Live Zero-Latency</span>
            </h2>
            <p className="text-white/45 text-xs mt-1">Search through verified Central Acts, 28 State Enactments, Supreme Court, and all 25 State High Courts.</p>
          </div>

          {stats && (
            <div className="flex items-center gap-2 bg-white/[0.03] border border-white/[0.08] p-2 rounded-xl text-[11px]">
              <div className="px-2.5 py-1 text-center border-r border-white/[0.08]">
                <span className="text-gold-400 font-bold block">{stats.central_acts_count}</span>
                <span className="text-white/40 text-[9px]">Central Acts</span>
              </div>
              <div className="px-2.5 py-1 text-center border-r border-white/[0.08]">
                <span className="text-cyan-400 font-bold block">{stats.state_acts_count}</span>
                <span className="text-white/40 text-[9px]">State Acts</span>
              </div>
              <div className="px-2.5 py-1 text-center border-r border-white/[0.08]">
                <span className="text-purple-400 font-bold block">{stats.supreme_court_count}</span>
                <span className="text-white/40 text-[9px]">SC Landmark</span>
              </div>
              <div className="px-2.5 py-1 text-center">
                <span className="text-pink-400 font-bold block">{stats.high_courts_count}</span>
                <span className="text-white/40 text-[9px]">25 High Courts</span>
              </div>
            </div>
          )}
        </div>

        {/* 4 Tabs Selector */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-6">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center justify-center gap-2 p-3 rounded-xl border text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-gold-500/15 border-gold-500/50 text-gold-300 shadow-lg shadow-gold-500/5'
                    : 'bg-white/[0.02] border-white/[0.07] text-white/50 hover:text-white hover:bg-white/[0.05]'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-gold-400' : 'text-white/40'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Search Bar & Dynamic Tier Filters */}
        <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row gap-2.5 mb-8">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-white/30 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={
                activeTab === 'central' ? 'Search Central Acts (e.g., theft, 318, 420, bail, salary, FIR)...' :
                activeTab === 'state' ? 'Search State Acts (e.g., tenant eviction, land grabbing, dharani)...' :
                activeTab === 'sc' ? 'Search Supreme Court Rulings (e.g., mandatory FIR, bail guidelines, privacy)...' :
                'Search 25 High Courts (e.g., demolition, bank account freeze, tech termination)...'
              }
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white/[0.04] border border-white/[0.1] text-sm text-white placeholder-white/25 focus:outline-none focus:border-gold-500/50 transition-colors"
            />
          </div>

          {activeTab === 'central' && (
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="px-3.5 py-2.5 rounded-xl bg-white/[0.04] border border-white/[0.1] text-xs text-white/80 focus:outline-none focus:border-gold-500/50 transition-colors"
            >
              {CATEGORIES.map((c) => (
                <option key={c.slug} value={c.slug} className="bg-justice-dark text-white">{c.label}</option>
              ))}
            </select>
          )}

          {activeTab === 'state' && (
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              className="px-3.5 py-2.5 rounded-xl bg-white/[0.04] border border-white/[0.1] text-xs text-white/80 focus:outline-none focus:border-gold-500/50 transition-colors"
            >
              {STATES.map((s) => (
                <option key={s.code} value={s.code} className="bg-justice-dark text-white">{s.name}</option>
              ))}
            </select>
          )}

          {activeTab === 'hc' && (
            <select
              value={selectedCourt}
              onChange={(e) => setSelectedCourt(e.target.value)}
              className="px-3.5 py-2.5 rounded-xl bg-white/[0.04] border border-white/[0.1] text-xs text-white/80 focus:outline-none focus:border-gold-500/50 transition-colors"
            >
              {HIGH_COURTS.map((h) => (
                <option key={h.code} value={h.code} className="bg-justice-dark text-white">{h.name}</option>
              ))}
            </select>
          )}

          <button
            type="submit"
            className="px-6 py-2.5 rounded-xl bg-gold-gradient text-justice-dark font-bold text-xs hover:brightness-110 transition-all flex items-center justify-center gap-1.5 shadow-gold"
          >
            {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
            <span>Search</span>
          </button>
        </form>

        {/* Results Container */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20 gap-3">
            <Loader2 className="w-8 h-8 text-gold-400 animate-spin" />
            <p className="text-white/40 text-xs font-mono">Querying Indian Bare Acts &amp; Judicial Archives...</p>
          </div>
        ) : (
          <div>
            {/* Tab 1: Central Acts */}
            {activeTab === 'central' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                {centralResults.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => setSelectedItem({ type: 'central', ...item })}
                    className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.07] hover:border-gold-500/40 hover:bg-white/[0.04] transition-all cursor-pointer group flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-gold-500/10 text-gold-400 font-bold border border-gold-500/20">
                          Sec {item.section_number}
                        </span>
                        <span className="text-[10px] text-white/35 capitalize px-2 py-0.5 rounded bg-white/[0.03]">
                          {item.category}
                        </span>
                      </div>
                      <h4 className="text-sm font-bold text-white group-hover:text-gold-300 transition-colors mb-1 line-clamp-1">
                        {item.title}
                      </h4>
                      <p className="text-[11px] text-white/35 font-medium mb-2">{item.act_name}</p>
                      <p className="text-xs text-white/60 line-clamp-2 leading-relaxed">{item.description}</p>
                    </div>

                    {item.old_law_reference && (
                      <div className="mt-3 pt-2.5 border-t border-white/[0.05] flex items-center justify-between text-[10px] text-white/40">
                        <span>Old Ref: <strong className="text-white/70">{item.old_law_reference}</strong></span>
                        <ArrowRight className="w-3.5 h-3.5 text-white/20 group-hover:text-gold-400 transition-transform group-hover:translate-x-1" />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Tab 2: State Acts */}
            {activeTab === 'state' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                {stateResults.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => setSelectedItem({ type: 'state', ...item })}
                    className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.07] hover:border-cyan-500/40 hover:bg-white/[0.04] transition-all cursor-pointer group flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 font-bold border border-cyan-500/20">
                          {item.state_name} • Sec {item.section_number}
                        </span>
                        <span className="text-[10px] text-white/35 px-2 py-0.5 rounded bg-white/[0.03]">
                          {item.category}
                        </span>
                      </div>
                      <h4 className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors mb-1 line-clamp-1">
                        {item.title}
                      </h4>
                      <p className="text-[11px] text-white/35 font-medium mb-2">{item.act_name}</p>
                      <p className="text-xs text-white/60 line-clamp-2 leading-relaxed">{item.description}</p>
                    </div>

                    {item.punishment && (
                      <div className="mt-3 pt-2.5 border-t border-white/[0.05] text-[10px] text-cyan-400/80 line-clamp-1">
                        Relief: {item.punishment}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Tab 3: Supreme Court */}
            {activeTab === 'sc' && (
              <div className="grid grid-cols-1 gap-3.5">
                {scResults.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => setSelectedItem({ type: 'sc', ...item })}
                    className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.07] hover:border-purple-500/40 hover:bg-white/[0.04] transition-all cursor-pointer group"
                  >
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <span className="text-xs font-mono font-bold text-purple-300 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
                        {item.citation} ({item.year})
                      </span>
                      <span className="text-[10px] text-emerald-400 font-semibold px-2 py-0.5 rounded bg-emerald-500/10">
                        {item.verdict || 'Landmark Precedent'}
                      </span>
                    </div>
                    <h4 className="text-sm font-extrabold text-white group-hover:text-purple-300 transition-colors mb-1">
                      {item.case_name}
                    </h4>
                    {item.bench && <p className="text-[11px] text-white/40 mb-2 font-mono">Bench: {item.bench}</p>}
                    <p className="text-xs text-white/70 leading-relaxed font-sans line-clamp-2 bg-black/20 p-2.5 rounded-lg border border-white/[0.04]">
                      <strong>Holding:</strong> {item.ratio_decidendi}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {/* Tab 4: 25 High Courts */}
            {activeTab === 'hc' && (
              <div className="grid grid-cols-1 gap-3.5">
                {hcResults.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => setSelectedItem({ type: 'hc', ...item })}
                    className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.07] hover:border-pink-500/40 hover:bg-white/[0.04] transition-all cursor-pointer group"
                  >
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <span className="text-xs font-mono font-bold text-pink-300 bg-pink-500/10 px-2.5 py-0.5 rounded border border-pink-500/20">
                        {item.high_court_name} • {item.citation}
                      </span>
                      <span className="text-[10px] text-cyan-400 font-semibold px-2 py-0.5 rounded bg-cyan-500/10">
                        {item.disposition || 'Precedent'}
                      </span>
                    </div>
                    <h4 className="text-sm font-extrabold text-white group-hover:text-pink-300 transition-colors mb-1">
                      {item.case_name}
                    </h4>
                    <p className="text-xs text-white/70 leading-relaxed font-sans line-clamp-2 bg-black/20 p-2.5 rounded-lg border border-white/[0.04] mb-2">
                      <strong>Ratio:</strong> {item.ratio_decidendi}
                    </p>
                    <div className="flex items-center justify-between text-[10px] text-white/40">
                      <span>Sections: <strong className="text-white/60">{item.sections_referred}</strong></span>
                      <span className="font-mono text-white/30">{item.year}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Empty State */}
            {((activeTab === 'central' && centralResults.length === 0) ||
              (activeTab === 'state' && stateResults.length === 0) ||
              (activeTab === 'sc' && scResults.length === 0) ||
              (activeTab === 'hc' && hcResults.length === 0)) && (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <AlertCircle className="w-8 h-8 text-white/20 mb-2" />
                <p className="text-sm font-medium text-white/60">No records found for &quot;{query}&quot;</p>
                <p className="text-xs text-white/30 mt-0.5">Try searching for broader keywords like &quot;eviction&quot;, &quot;salary&quot;, &quot;fraud&quot;, or &quot;bail&quot;.</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Interactive Detail Modal */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-justice-card border border-white/[0.12] w-full max-w-2xl rounded-2xl p-6 shadow-2xl relative max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setSelectedItem(null)}
              className="absolute top-4 right-4 text-white/40 hover:text-white p-1 rounded-lg hover:bg-white/5 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            {selectedItem.type === 'central' && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-mono font-bold text-gold-400 bg-gold-500/10 border border-gold-500/20 px-2.5 py-1 rounded">
                    Sec {selectedItem.section_number}
                  </span>
                  <span className="text-xs text-white/40">{selectedItem.act_name}</span>
                </div>
                <h3 className="text-lg font-bold text-white mb-4">{selectedItem.title}</h3>
                
                <div className="bg-black/30 p-4 rounded-xl border border-white/[0.06] mb-4">
                  <h5 className="text-[11px] font-bold text-gold-400/80 uppercase tracking-wider mb-2">Statutory Provision</h5>
                  <p className="text-sm text-white/80 leading-relaxed font-sans whitespace-pre-wrap">{selectedItem.description}</p>
                </div>

                {selectedItem.punishment && (
                  <div className="bg-red-500/10 border border-red-500/20 p-3.5 rounded-xl text-xs text-red-300 mb-3">
                    <strong>⚖️ Punishment / Penalty:</strong> {selectedItem.punishment}
                  </div>
                )}

                {selectedItem.old_law_reference && (
                  <div className="bg-white/[0.03] border border-white/[0.08] p-3 rounded-xl text-xs text-white/60">
                    <strong>Old Law Reference:</strong> {selectedItem.old_law_reference}
                  </div>
                )}
              </div>
            )}

            {selectedItem.type === 'state' && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 px-2.5 py-1 rounded">
                    {selectedItem.state_name} • Sec {selectedItem.section_number}
                  </span>
                  <span className="text-xs text-white/40">{selectedItem.act_name}</span>
                </div>
                <h3 className="text-lg font-bold text-white mb-4">{selectedItem.title}</h3>
                
                <div className="bg-black/30 p-4 rounded-xl border border-white/[0.06] mb-4">
                  <h5 className="text-[11px] font-bold text-cyan-400/80 uppercase tracking-wider mb-2">State Law Provision</h5>
                  <p className="text-sm text-white/80 leading-relaxed font-sans">{selectedItem.description}</p>
                </div>

                {selectedItem.punishment && (
                  <div className="bg-cyan-500/10 border border-cyan-500/20 p-3.5 rounded-xl text-xs text-cyan-300">
                    <strong>⚖️ Statutory Relief / Legal Remedy:</strong> {selectedItem.punishment}
                  </div>
                )}
              </div>
            )}

            {(selectedItem.type === 'sc' || selectedItem.type === 'hc') && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-mono font-bold text-purple-400 bg-purple-500/10 border border-purple-500/20 px-2.5 py-1 rounded">
                    {selectedItem.citation} ({selectedItem.year})
                  </span>
                  <span className="text-xs text-white/40">{selectedItem.high_court_name || 'Supreme Court of India'}</span>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{selectedItem.case_name}</h3>
                {selectedItem.bench && <p className="text-xs font-mono text-white/40 mb-4">Bench: {selectedItem.bench}</p>}

                <div className="bg-black/30 p-4 rounded-xl border border-white/[0.06] mb-4">
                  <h5 className="text-[11px] font-bold text-purple-400/80 uppercase tracking-wider mb-2">Ratio Decidendi (Binding Legal Principle)</h5>
                  <p className="text-sm text-white/90 leading-relaxed font-sans">{selectedItem.ratio_decidendi}</p>
                </div>

                {selectedItem.sections_referred && (
                  <div className="bg-white/[0.03] border border-white/[0.08] p-3 rounded-xl text-xs text-white/60 mb-3">
                    <strong>Sections Referred:</strong> {selectedItem.sections_referred}
                  </div>
                )}

                {(selectedItem.verdict || selectedItem.disposition) && (
                  <div className="bg-emerald-500/10 border border-emerald-500/20 p-3 rounded-xl text-xs text-emerald-300 font-semibold">
                    <strong>Final Order / Disposition:</strong> {selectedItem.verdict || selectedItem.disposition}
                  </div>
                )}
              </div>
            )}

            <div className="mt-6 flex justify-end">
              <Link
                href={`/chat`}
                className="px-4 py-2 rounded-xl bg-gold-gradient text-justice-dark font-bold text-xs hover:brightness-110 transition-all flex items-center gap-1.5 shadow-gold"
              >
                <span>Consult YAMA on this Law</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
