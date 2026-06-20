'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Scale, Search, Loader2, ChevronLeft, AlertCircle, X, ArrowRight, FileText,
  Shield, Lock, Car, Users, ShoppingBag, Briefcase, Gavel, FileCheck 
} from 'lucide-react';
import { searchLaws } from '@/lib/api';
import type { LawSection } from '@/types';
import TiltCard from '@/components/ui/TiltCard';

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

const CATEGORY_META: Record<string, { icon: any; color: string; bg: string; border: string }> = {
  constitutional: { icon: Shield, color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/20' },
  criminal: { icon: Scale, color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/20' },
  cyber: { icon: Lock, color: 'text-cyan-400', bg: 'bg-cyan-500/10', border: 'border-cyan-500/20' },
  motor_vehicle: { icon: Car, color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20' },
  family: { icon: Users, color: 'text-pink-400', bg: 'bg-pink-500/10', border: 'border-pink-500/20' },
  consumer: { icon: ShoppingBag, color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
  civil: { icon: Gavel, color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' },
  corporate: { icon: Briefcase, color: 'text-indigo-400', bg: 'bg-indigo-500/10', border: 'border-indigo-500/20' },
  other: { icon: FileCheck, color: 'text-gray-400', bg: 'bg-gray-500/10', border: 'border-gray-500/20' },
};

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [results, setResults] = useState<LawSection[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [selectedLaw, setSelectedLaw] = useState<LawSection | null>(null);

  const fetchLaws = async (searchQuery: string, searchCategory: string) => {
    setIsLoading(true);
    setSearched(true);
    try {
      const data = await searchLaws(searchQuery, searchCategory || undefined, 20);
      setResults(data.results);
    } catch {
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLaws('', '');
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchLaws(query, category);
  };

  const handleCategoryChange = (newCategory: string) => {
    setCategory(newCategory);
    fetchLaws(query, newCategory);
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
              onChange={(e) => handleCategoryChange(e.target.value)}
              className="px-4 py-3.5 bg-white/[0.05] border border-white/10 rounded-xl text-sm text-white/70 focus:outline-none focus:border-gold-500/50 transition-colors"
            >
              {CATEGORIES.map((cat) => (
                <option key={cat.slug} value={cat.slug} className="bg-navy-950 text-white">{cat.label}</option>
              ))}
            </select>
            <button
              type="submit"
              disabled={isLoading}
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
          <div className="space-y-6 animate-fade-in">
            {results.length > 0 && <p className="text-xs text-white/30 mb-2">{results.length} result(s) found</p>}
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {results.map((law) => (
                <LawCard key={law.id} law={law} onClick={() => setSelectedLaw(law)} />
              ))}
            </div>
          </div>
        )}

        {/* Law Details Modal */}
        {selectedLaw && (
          <LawDetailsModal
            law={selectedLaw}
            onClose={() => setSelectedLaw(null)}
          />
        )}
      </div>
    </div>
  );
}

function LawCard({ law, onClick }: { law: LawSection; onClick: () => void }) {
  const meta = CATEGORY_META[law.category] || CATEGORY_META.other;
  const Icon = meta.icon;

  return (
    <TiltCard tiltAmount={8} scale={1.02} className="h-full">
      <div 
        onClick={onClick}
        className="group p-6 rounded-2xl card-premium h-full cursor-pointer flex flex-col justify-between hover:border-gold-500/20 transition-all active:scale-[0.98] aspect-square relative overflow-hidden bg-gradient-to-br from-white/[0.02] via-gold-500/[0.005] to-purple-500/[0.02] hover:from-white/[0.04] hover:via-gold-500/[0.01] hover:to-purple-500/[0.04]"
      >
        {/* Glow effect in background */}
        <div className="absolute -right-10 -top-10 w-24 h-24 rounded-full bg-gold-500/5 blur-xl group-hover:bg-gold-500/10 transition-all duration-500" />
        
        <div className="flex flex-col h-full justify-between z-10 w-full">
          <div>
            {/* Section & Category Badge */}
            <div className="flex items-center justify-between mb-3.5">
              <span className="bg-gold-500/15 text-gold-300 text-[10px] font-semibold px-2.5 py-1 rounded-lg border border-gold-500/20 tracking-wider">
                § {law.section_number}
              </span>
              <span className={`flex items-center gap-1 text-[10px] px-2.5 py-1 rounded-lg capitalize font-medium ${meta.bg} ${meta.color} border ${meta.border}`}>
                <Icon className="w-3 h-3" />
                {law.category}
              </span>
            </div>

            {/* Title */}
            <h3 className="font-semibold text-white group-hover:text-gold-400 transition-colors line-clamp-2 leading-snug mb-2.5 text-sm md:text-[15px]">
              {law.title}
            </h3>

            {/* Description Preview */}
            <p className="text-xs text-white/40 line-clamp-3 leading-relaxed mb-4">
              {law.description}
            </p>
          </div>

          {/* Card Footer */}
          <div className="flex items-center justify-between pt-3.5 border-t border-white/5 mt-auto w-full">
            <span className="text-[10px] text-white/30 truncate max-w-[80%] font-medium">
              {law.act_name}
            </span>
            <ArrowRight className="w-4 h-4 text-white/30 group-hover:text-gold-400 group-hover:translate-x-1 transition-all" />
          </div>
        </div>
      </div>
    </TiltCard>
  );
}

function LawDetailsModal({ law, onClose }: { law: LawSection; onClose: () => void }) {
  const meta = CATEGORY_META[law.category] || CATEGORY_META.other;
  const Icon = meta.icon;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md animate-fade-in">
      <div className="w-full max-w-2xl bg-[#0a0a0c] border border-white/10 rounded-2xl shadow-2xl overflow-hidden animate-fadeIn">
        
        {/* Cover Header Graphic - "The Image" */}
        <div className="relative h-44 bg-gradient-to-br from-navy-950 via-[#0c0c16] to-[#120a1c] border-b border-white/5 flex items-center justify-between px-8 overflow-hidden">
          {/* Abstract SVG Grid/Dots Background */}
          <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:16px_16px]" />
          
          {/* Ambient Glows */}
          <div className="absolute -left-10 -bottom-10 w-44 h-44 rounded-full bg-gold-500/10 blur-3xl pointer-events-none" />
          <div className="absolute -right-10 -top-10 w-44 h-44 rounded-full bg-purple-500/10 blur-3xl pointer-events-none" />
          
          {/* Header Content */}
          <div className="z-10 flex-1 pr-6">
            <div className="flex items-center gap-2 mb-3">
              <span className="bg-gold-500/15 text-gold-300 text-xs font-bold px-3 py-1 rounded-lg border border-gold-500/20 tracking-wider">
                § {law.section_number}
              </span>
              <span className={`flex items-center gap-1 text-[11px] px-3 py-1 rounded-lg capitalize font-medium ${meta.bg} ${meta.color} border ${meta.border}`}>
                <Icon className="w-3.5 h-3.5" />
                {law.category}
              </span>
            </div>
            <h2 className="text-xl font-bold text-white leading-snug">{law.title}</h2>
            <p className="text-xs text-gold-500/60 mt-1.5 font-semibold tracking-wider uppercase">{law.act_name}</p>
          </div>

          {/* Cover Badge Graphic */}
          <div className="z-10 hidden sm:flex items-center justify-center w-24 h-24 rounded-2xl bg-white/[0.02] border border-white/10 relative group overflow-hidden">
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-gold-500/10 to-purple-500/10 opacity-50" />
            <Icon className={`w-10 h-10 ${meta.color} filter drop-shadow-[0_0_8px_rgba(251,191,36,0.3)]`} />
          </div>

          {/* Close Button */}
          <button 
            onClick={onClose}
            className="absolute top-4 right-4 p-1.5 rounded-lg bg-white/5 text-white/40 hover:text-white hover:bg-white/10 transition-all z-20"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 max-h-[50vh] overflow-y-auto scrollbar-thin">
          <div className="space-y-2">
            <h4 className="text-[11px] font-bold text-white/30 uppercase tracking-wider">Description</h4>
            <p className="text-sm text-white/70 leading-relaxed bg-white/[0.01] border border-white/[0.03] rounded-xl p-4 whitespace-pre-wrap">{law.description}</p>
          </div>

          {law.punishment && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-5 py-4">
              <h4 className="text-[10px] font-bold text-red-400/60 uppercase tracking-wider mb-1.5">Punishment</h4>
              <p className="text-sm text-red-300 font-medium">{law.punishment}</p>
            </div>
          )}

          {law.old_law_reference && (
            <div className="bg-white/[0.03] border border-white/5 rounded-xl px-5 py-4">
              <h4 className="text-[10px] font-bold text-white/30 uppercase tracking-wider mb-1.5">Old Law Reference</h4>
              <p className="text-xs text-white/50 leading-relaxed">{law.old_law_reference}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 bg-[#050507] border-t border-white/5 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2.5 rounded-xl text-xs font-semibold bg-white/5 text-white hover:bg-white/10 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

