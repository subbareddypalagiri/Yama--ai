'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Scale, Search, Loader2, ChevronLeft, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import { searchLaws } from '@/lib/api';
import type { LawSection } from '@/types';

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
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [results, setResults] = useState<LawSection[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setIsLoading(true);
    setSearched(true);
    try {
      const data = await searchLaws(query.trim(), category || undefined, 20);
      setResults(data.results);
    } catch {
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-justice-dark text-white">
      <header className="border-b border-white/[0.07] glass-dark sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
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
                <p className="text-[10px] text-white/35 mt-0.5">Law Search Engine</p>
              </div>
            </div>
          </div>
          <nav className="flex gap-1">
            <Link href="/chat"    className="px-3 py-1.5 text-white/45 hover:text-white hover:bg-white/5 rounded-lg text-xs transition-colors">Chat</Link>
            <Link href="/explore" className="px-3 py-1.5 text-white/45 hover:text-white hover:bg-white/5 rounded-lg text-xs transition-colors">Explore Acts</Link>
          </nav>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-10">
        <h2 className="text-2xl font-bold text-white mb-1">Search Indian Laws</h2>
        <p className="text-white/40 text-sm mb-8">Search across 42+ Acts including BNS, BNSS, IT Act, Consumer Protection Act &amp; more.</p>

        <form onSubmit={handleSearch} className="mb-8">
          <div className="flex flex-col md:flex-row gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search by keyword (e.g., theft, bail, cheating, FIR)..."
                className="w-full pl-11 pr-4 py-3.5 bg-white/[0.05] border border-white/10 rounded-xl text-sm text-white placeholder-white/25 focus:outline-none focus:border-gold-500/50 focus:ring-1 focus:ring-gold-500/30 transition-colors"
              />
            </div>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="px-4 py-3.5 bg-white/[0.05] border border-white/10 rounded-xl text-sm text-white/70 focus:outline-none focus:border-gold-500/50 transition-colors"
            >
              {CATEGORIES.map((cat) => (
                <option key={cat.slug} value={cat.slug} className="bg-navy-950 text-white">{cat.label}</option>
              ))}
            </select>
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="px-7 py-3.5 rounded-xl font-semibold text-sm text-justice-dark transition-all disabled:opacity-30 shadow-gold hover:shadow-gold-lg flex items-center gap-2 flex-shrink-0"
              style={{ background: 'linear-gradient(135deg, #fbbf24, #e2b659)' }}
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              Search
            </button>
          </div>
        </form>

        {isLoading ? (
          <div className="text-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-gold-400 mx-auto mb-3" />
            <p className="text-white/40 text-sm">Searching laws...</p>
          </div>
        ) : searched && results.length === 0 ? (
          <div className="glass rounded-2xl p-12 text-center">
            <AlertCircle className="w-10 h-10 text-white/20 mx-auto mb-3" />
            <p className="text-white/50">No results found for &ldquo;{query}&rdquo;</p>
            <p className="text-white/25 text-xs mt-1">Try different keywords or a broader category</p>
          </div>
        ) : (
          <div className="space-y-3">
            {results.length > 0 && <p className="text-xs text-white/30 mb-4">{results.length} result(s) found</p>}
            {results.map((law) => <LawCard key={law.id} law={law} />)}
          </div>
        )}
      </div>
    </div>
  );
}

function LawCard({ law }: { law: LawSection }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="glass rounded-2xl p-5 hover:border-gold-500/20 transition-all">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span className="bg-gold-500/15 text-gold-300 text-[11px] font-medium px-2.5 py-0.5 rounded-lg border border-gold-500/20">§ {law.section_number}</span>
            <span className="bg-white/5 text-white/40 text-[11px] px-2.5 py-0.5 rounded-lg capitalize">{law.category}</span>
          </div>
          <h3 className="font-semibold text-white">{law.title}</h3>
          <p className="text-xs text-white/35 mt-1">{law.act_name}</p>
        </div>
        <button onClick={() => setExpanded(!expanded)} className="text-white/30 hover:text-gold-400 transition-colors flex-shrink-0 mt-1">
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>
      {expanded && (
        <div className="mt-4 pt-4 border-t border-white/[0.07] space-y-3">
          <p className="text-sm text-white/65 leading-relaxed">{law.description}</p>
          {law.punishment && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3">
              <p className="text-[11px] font-medium text-red-400/70 uppercase tracking-wider mb-1">Punishment</p>
              <p className="text-sm text-red-300">{law.punishment}</p>
            </div>
          )}
          {law.old_law_reference && (
            <div className="bg-white/[0.03] rounded-xl px-4 py-3">
              <p className="text-[11px] font-medium text-white/30 uppercase tracking-wider mb-1">Old Law Reference</p>
              <p className="text-xs text-white/45">{law.old_law_reference}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
