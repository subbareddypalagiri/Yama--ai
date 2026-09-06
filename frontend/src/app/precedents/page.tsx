'use client';

import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import {
  Scale,
  Search,
  BookOpen,
  Copy,
  Check,
  Shield,
  Gavel,
  ExternalLink,
  Filter,
  FileText,
  Sparkles,
  Award
} from 'lucide-react';
import UnifiedNavbar from '@/components/layout/UnifiedNavbar';
import { PRECEDENTS_DATA, type Precedent } from '@/data/precedents_data';

export default function PrecedentsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const categories = [
    { id: 'all', label: 'All Precedents' },
    { id: 'arrest_bail', label: 'Arrest & Bail' },
    { id: 'cheque_bounce', label: 'Section 138 Cheque' },
    { id: 'tenancy_property', label: 'Tenancy & Property' },
    { id: 'consumer_fraud', label: 'Consumer Rights' },
    { id: 'cyber_privacy', label: 'Cyber & Privacy' },
    { id: 'motor_accidents', label: 'Motor Accidents' },
  ];

  const filteredPrecedents = useMemo(() => {
    return PRECEDENTS_DATA.filter((p) => {
      const matchesCategory =
        selectedCategory === 'all' || p.category === selectedCategory;

      const q = searchQuery.toLowerCase().trim();
      if (!q) return matchesCategory;

      const matchesSearch =
        p.title.toLowerCase().includes(q) ||
        p.citation.toLowerCase().includes(q) ||
        p.bench.toLowerCase().includes(q) ||
        p.ratio_decidendi.toLowerCase().includes(q) ||
        p.summary.toLowerCase().includes(q) ||
        p.applicable_statutes.some((s) => s.toLowerCase().includes(q)) ||
        p.key_principles.some((k) => k.toLowerCase().includes(q));

      return matchesCategory && matchesSearch;
    });
  }, [searchQuery, selectedCategory]);

  const handleCopyCitation = (precedent: Precedent) => {
    navigator.clipboard.writeText(precedent.copyable_citation);
    setCopiedId(precedent.id);
    setTimeout(() => {
      setCopiedId(null);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-[#07080b] text-gray-100 flex flex-col font-sans">
      <UnifiedNavbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8">
        {/* Header Banner */}
        <div className="relative rounded-2xl bg-gradient-to-b from-[#12151e] to-[#0c0e14] border border-[#212738] p-6 sm:p-10 mb-8 overflow-hidden shadow-2xl">
          <div className="absolute -right-16 -top-16 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10 max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold uppercase tracking-wider mb-4">
              <Award className="w-3.5 h-3.5" />
              Supreme Court & High Court Authority Vault
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
              Landmark Judicial Precedents & Legal Rulings
            </h1>
            <p className="mt-3 text-sm sm:text-base text-gray-400 leading-relaxed">
              Direct, court-verified citations from the Supreme Court of India and High Courts. 
              Search binding ratios, fundamental rights safeguards, and copy verified legal citations 
              directly into your court petitions, legal notices, and case diaries.
            </p>
          </div>
        </div>

        {/* Search & Category Filter Bar */}
        <div className="space-y-4 mb-8">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by case name, citation (e.g. 2014 8 SCC 273), Section 41A, Bail, Cheque, Arnesh Kumar..."
              className="w-full pl-12 pr-4 py-3.5 bg-[#0f121a] border border-[#23293a] focus:border-amber-500 rounded-xl text-sm text-gray-100 placeholder-gray-500 focus:outline-none transition-all shadow-inner"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-xs text-gray-400 hover:text-white px-2 py-1 bg-[#1a1f2c] rounded"
              >
                Clear
              </button>
            )}
          </div>

          {/* Category Chips */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
            {categories.map((cat) => {
              const isActive = selectedCategory === cat.id;
              return (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all flex items-center gap-1.5 ${
                    isActive
                      ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-black shadow-lg shadow-amber-500/20 font-bold'
                      : 'bg-[#11141d] border border-[#202636] text-gray-300 hover:border-gray-600 hover:text-white'
                  }`}
                >
                  {cat.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Results Counter */}
        <div className="flex items-center justify-between text-xs text-gray-400 mb-4 px-1">
          <span>
            Found <strong className="text-amber-400">{filteredPrecedents.length}</strong> authoritative rulings
          </span>
          <span className="hidden sm:inline">
            Standard: Supreme Court Reports (SCC / SCR / AIR)
          </span>
        </div>

        {/* Precedents Grid */}
        <div className="grid grid-cols-1 gap-6">
          {filteredPrecedents.map((precedent) => {
            const isCopied = copiedId === precedent.id;

            return (
              <div
                key={precedent.id}
                className="rounded-2xl bg-[#0f121a] border border-[#1f2535] hover:border-[#38435d] transition-all p-6 sm:p-8 flex flex-col justify-between group shadow-xl"
              >
                <div>
                  {/* Top Badges */}
                  <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="px-2.5 py-1 rounded-lg text-[11px] font-bold tracking-wide uppercase bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        {precedent.category_label}
                      </span>
                      <span className="px-2.5 py-1 rounded-lg text-[11px] font-mono font-medium bg-[#1a1f2d] text-gray-300 border border-[#2c344a]">
                        {precedent.court} • {precedent.year}
                      </span>
                    </div>

                    {/* Quick Citation Copy */}
                    <button
                      onClick={() => handleCopyCitation(precedent)}
                      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all border ${
                        isCopied
                          ? 'bg-emerald-950/80 border-emerald-500/50 text-emerald-300'
                          : 'bg-[#171b26] border-[#293247] text-gray-300 hover:text-white hover:border-amber-500/50'
                      }`}
                    >
                      {isCopied ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                          <span>Citation Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5" />
                          <span>Copy Citation</span>
                        </>
                      )}
                    </button>
                  </div>

                  {/* Title & Citation Header */}
                  <h2 className="text-xl sm:text-2xl font-bold text-white group-hover:text-amber-400 transition-colors">
                    {precedent.title}
                  </h2>
                  <div className="mt-1 text-sm font-mono text-amber-400/90 font-semibold">
                    {precedent.citation}
                  </div>
                  <div className="mt-1 text-xs text-gray-400 italic">
                    Coram: {precedent.bench}
                  </div>

                  {/* Summary */}
                  <p className="mt-4 text-sm text-gray-300 leading-relaxed">
                    {precedent.summary}
                  </p>

                  {/* Ratio Decidendi Box */}
                  <div className="mt-4 p-4 rounded-xl bg-[#090b10] border-l-4 border-amber-500 border border-[#1b212f]">
                    <div className="text-[11px] font-extrabold uppercase tracking-wider text-amber-400 mb-1 flex items-center gap-1.5">
                      <Gavel className="w-3.5 h-3.5" />
                      Binding Ratio Decidendi
                    </div>
                    <p className="text-xs sm:text-sm text-gray-200 italic font-serif leading-relaxed">
                      "{precedent.ratio_decidendi}"
                    </p>
                  </div>

                  {/* Key Legal Principles */}
                  <div className="mt-5 space-y-2">
                    <div className="text-xs font-bold uppercase tracking-wider text-gray-400">
                      Key Directives & Safeguards:
                    </div>
                    <ul className="space-y-1.5">
                      {precedent.key_principles.map((principle, idx) => (
                        <li
                          key={idx}
                          className="text-xs text-gray-300 flex items-start gap-2"
                        >
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                          <span>{principle}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Applicable Statutes */}
                  <div className="mt-5 pt-4 border-t border-[#1d2332] flex flex-wrap items-center gap-2">
                    <span className="text-[11px] font-semibold text-gray-400">
                      Governing Laws:
                    </span>
                    {precedent.applicable_statutes.map((statute, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 rounded text-[10px] bg-[#141824] text-gray-300 border border-[#252e42]"
                      >
                        {statute}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Bottom Action Footer */}
                <div className="mt-6 pt-4 border-t border-[#191f2c] flex flex-wrap items-center justify-between gap-3">
                  <div className="text-[11px] text-gray-400">
                    Authority: Supreme Court of India (Article 141 Binding Precedent)
                  </div>
                  <div className="flex items-center gap-2">
                    <Link
                      href={`/draft?precedent=${encodeURIComponent(precedent.id)}`}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#1a2130] hover:bg-amber-500 hover:text-black text-amber-300 border border-[#2b354e] transition-all"
                    >
                      <FileText className="w-3.5 h-3.5" />
                      Draft Notice With This Precedent
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {filteredPrecedents.length === 0 && (
          <div className="p-12 text-center rounded-2xl bg-[#0f121a] border border-[#23293a]">
            <Gavel className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-gray-200">No Precedents Found</h3>
            <p className="text-xs text-gray-400 mt-1">
              Try searching with keywords like "Bail", "Arrest", "Cheque", or "Privacy".
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
