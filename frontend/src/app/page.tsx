'use client';

import { useState, useRef, KeyboardEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  Scale, Zap, ArrowRight, Briefcase, Search, BookOpen, FolderOpen,
  Home as HomeIcon, Car, ShieldAlert, Lock, CheckCircle2, ChevronRight,
  Send, Sparkles, Paperclip, Mic, ArrowUp
} from 'lucide-react';
import UnifiedNavbar from '@/components/layout/UnifiedNavbar';
import VoiceConsultation from '@/components/intelligence/VoiceConsultation';

export default function Home() {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [isFocused, setIsFocused] = useState(false);

  const handleSearchSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const text = query.trim();
    if (!text) return;
    router.push(`/chat?q=${encodeURIComponent(text)}`);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSearchSubmit();
    }
  };

  const suggestionChips = [
    'Landlord won\'t return deposit',
    'False speed camera challan',
    'Unlawful police custody rights',
    'Company terminated without notice',
    'Online UPI cyber extortion',
  ];

  const superPowerCards = [
    {
      href: '/lawyer',
      icon: Briefcase,
      title: 'Your Senior AI Advocate',
      statute: 'Bar Enrolled AP/BCI/2021',
      badge: 'PRO ADVOCATE',
      leverage: 'Real-Time Voice & Clause Scanner',
      desc: 'Hands-free consultation in Telugu & English, clause-by-clause contract risk audit, and state High Court defense strategies.',
      iconColor: 'text-amber-400',
      badgeStyle: 'bg-[#1e1a14] text-amber-300 border-[#3d311f]',
    },
    {
      href: '/search',
      icon: Search,
      title: '12,036+ National Laws',
      statute: 'Supreme Court & 25 High Courts',
      badge: 'ALL INDIA',
      leverage: 'Zero-Latency Precedent Search',
      desc: 'Search across Bharatiya Nyaya Sanhita (BNS), BNSS, BSA, Central Bare Acts, and 28 State Enactments with chronological sorting.',
      iconColor: 'text-[#d4af37]',
      badgeStyle: 'bg-[#1e1a14] text-amber-300 border-[#3d311f]',
    },
    {
      href: '/lawyer',
      icon: HomeIcon,
      title: 'Tenant Security Recovery',
      statute: 'AP/TS Tenancy Act § 21 & Contract Act § 73',
      badge: '18% PENAL INTEREST',
      leverage: '15-Day Statutory Legal Demand Notice',
      desc: 'Mandatory 30-day deposit refund enforcement with 18% statutory penal interest and ready-to-file Rent Court petition drafts.',
      iconColor: 'text-emerald-400',
      badgeStyle: 'bg-[#121c16] text-emerald-300 border-[#1f3a29]',
    },
    {
      href: '/lawyer',
      icon: Car,
      title: 'Challan Lok Adalat Waiver',
      statute: 'MV Act § 136A & Legal Services Act § 19',
      badge: '50-75% DISCOUNT',
      leverage: 'Speed Camera Calibration Challenge',
      desc: 'Challenge uncertified speed gun cameras under Section 136A and generate compounding settlement petitions for the National Lok Adalat.',
      iconColor: 'text-amber-400',
      badgeStyle: 'bg-[#1f1a12] text-amber-300 border-[#403318]',
    },
    {
      href: '/lawyer',
      icon: ShieldAlert,
      title: '1-Tap Police SOS Shield',
      statute: 'BNSS § 35, § 43(5) & Art 22',
      badge: 'ARREST SHIELD',
      leverage: 'Arnesh Kumar Notice Mandate',
      desc: 'Instant arrest rights script in Telugu/English with authoritative advocate voice playback prohibiting unlawful custody without notice.',
      iconColor: 'text-red-400',
      badgeStyle: 'bg-[#201416] text-red-300 border-[#4a1f26]',
    },
    {
      href: '/lawyer',
      icon: Lock,
      title: 'SHA-256 Evidence Vault',
      statute: 'BSA 2023 § 63 & Arjun Panditrao',
      badge: 'CRYPTO VERIFIED',
      leverage: 'Tamper-Proof Electronic Admissibility',
      desc: 'Cryptographically freeze WhatsApp screenshots, call recordings, and UPI receipts with court-certified Section 63 BSA certificates.',
      iconColor: 'text-cyan-400',
      badgeStyle: 'bg-[#121b22] text-cyan-300 border-[#1c3848]',
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#050608] text-white font-sans selection:bg-[#f59e0b]/30 selection:text-white">
      {/* 100% Solid Precision Navbar */}
      <UnifiedNavbar />

      {/* HERO SECTION - ACETERNITY UI PRECISION REPLICA */}
      <section className="relative px-6 sm:px-12 lg:px-20 pt-16 pb-32 overflow-hidden border-b border-[#141620]">
        
        {/* 1. Aceternity Perspective Background Grid */}
        <div 
          className="absolute inset-0 pointer-events-none"
          style={{
            backgroundImage: `
              linear-gradient(to right, rgba(255, 255, 255, 0.035) 1px, transparent 1px),
              linear-gradient(to bottom, rgba(255, 255, 255, 0.035) 1px, transparent 1px)
            `,
            backgroundSize: '56px 56px',
            maskImage: 'radial-gradient(ellipse 85% 65% at 50% 15%, #000 65%, transparent 100%)',
            WebkitMaskImage: 'radial-gradient(ellipse 85% 65% at 50% 15%, #000 65%, transparent 100%)',
          }}
        />

        {/* 2. Aceternity Glowing Horizon Arc (Exact match to reference image) */}
        <div className="absolute -bottom-16 left-1/2 -translate-x-1/2 w-[125%] h-[320px] pointer-events-none overflow-hidden z-[2]">
          <div 
            className="w-full h-full rounded-[100%] border-t border-[#f59e0b]/60"
            style={{
              background: 'radial-gradient(ellipse at 50% 0%, rgba(245, 158, 11, 0.22) 0%, rgba(245, 158, 11, 0.05) 45%, transparent 70%)',
              boxShadow: '0 -15px 50px -5px rgba(245, 158, 11, 0.35)',
            }}
          />
        </div>

        {/* Top Vignette Fade */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#050608]/80 via-transparent to-[#050608] pointer-events-none z-[1]" />

        <div className="max-w-7xl mx-auto relative z-10">
          
          {/* Top Aceternity Pill Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-neutral-800/80 bg-[#0d0f17]/90 mb-10 shadow-sm">
            <span className="px-2 py-0.5 rounded-full bg-neutral-800 text-neutral-200 font-bold text-[11px] tracking-wider uppercase">
              YAMA AI
            </span>
            <span className="text-neutral-400 text-xs font-medium pr-1.5 flex items-center gap-1.5">
              <span>Bharat&apos;s Senior AI Legal Strategist • 12,036+ Laws</span>
              <ChevronRight className="w-3.5 h-3.5 text-neutral-500" />
            </span>
          </div>

          {/* ASYMMETRIC SPLIT: Left Bold Statement vs. Right Subtext & Action Button */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-16 items-end mb-14">
            
            {/* Left Column (8 cols): Huge, Left-Aligned Headline */}
            <div className="lg:col-span-8 text-left">
              <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-[76px] font-bold tracking-[-0.04em] leading-[1.02] text-white">
                The Intelligence of a <br />
                Senior Advocate. <br />
                <span className="text-[#f59e0b]">The Speed of Pure AI.</span>
              </h1>
            </div>

            {/* Right Column (4 cols): Concise Subtext + Bespoke Action Pill */}
            <div className="lg:col-span-4 flex flex-col justify-end items-start space-y-6 text-left lg:pb-3">
              <p className="text-neutral-400 text-sm sm:text-base leading-relaxed font-normal">
                Autonomous statutory defense under the 2023 Sanhitas &amp; 28 State Acts, instant contract clause audits, court-standard notice drafting with gold seals, and Lok Adalat waivers.
              </p>

              {/* Exact twin of Aceternity's "Chat with Alex" button */}
              <Link
                href="/lawyer"
                className="inline-flex items-center gap-3.5 px-4 py-2.5 rounded-xl border border-neutral-800 bg-black/90 hover:bg-neutral-900 hover:border-neutral-700 text-white text-sm font-medium transition-all group shadow-2xl"
              >
                <div className="w-8 h-8 rounded-lg bg-[#f59e0b] flex items-center justify-center text-black font-black shadow-md shadow-[#f59e0b]/30 group-hover:scale-105 transition-transform">
                  <Scale className="w-4.5 h-4.5 text-black" />
                </div>
                <span className="text-sm font-semibold tracking-wide text-neutral-100">
                  Consult Advocate YAMA
                </span>
              </Link>
            </div>

          </div>

          {/* SLEEK, LEFT-ALIGNED SEARCH & PROMPT COMMAND BAR */}
          <div className="w-full max-w-3xl text-left">
            <form onSubmit={handleSearchSubmit} className="relative">
              <div
                className={`relative flex items-center rounded-2xl bg-[#0c0e14] border transition-all duration-300 p-2 shadow-2xl ${
                  isFocused
                    ? 'border-[#f59e0b]/70 shadow-[0_0_25px_rgba(245,158,11,0.15)] bg-[#0f1118]'
                    : 'border-[#1f2332] hover:border-[#2f354a]'
                }`}
              >
                <div className="pl-3 text-neutral-500">
                  <Search className="w-5 h-5 text-neutral-400" />
                </div>

                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onFocus={() => setIsFocused(true)}
                  onBlur={() => setIsFocused(false)}
                  onKeyDown={handleKeyDown}
                  placeholder="Describe your legal situation, dispute, or section..."
                  className="w-full px-3.5 py-2.5 bg-transparent text-sm sm:text-base text-white placeholder-neutral-500 focus:outline-none"
                />

                <div className="flex items-center gap-2 pr-1">
                  <VoiceConsultation
                    onTranscript={(transcript) => {
                      setQuery(transcript);
                    }}
                  />

                  <button
                    type="submit"
                    disabled={!query.trim()}
                    className={`w-9 h-9 rounded-xl flex items-center justify-center transition-all ${
                      query.trim()
                        ? 'bg-[#f59e0b] text-black hover:bg-[#fbbf24] shadow-md shadow-[#f59e0b]/20 cursor-pointer'
                        : 'bg-neutral-800 text-neutral-500 cursor-not-allowed'
                    }`}
                  >
                    <ArrowUp className="w-4 h-4 font-bold" />
                  </button>
                </div>
              </div>
            </form>

            {/* Left-Aligned Clean Suggestion Chips */}
            <div className="mt-4 flex flex-wrap items-center gap-2">
              <span className="text-[11px] font-mono text-neutral-500 uppercase tracking-wider pl-1">
                Try:
              </span>
              {suggestionChips.map((chip, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setQuery(chip);
                    router.push(`/chat?q=${encodeURIComponent(chip)}`);
                  }}
                  className="text-xs text-neutral-400 hover:text-amber-200 px-3 py-1 rounded-lg bg-[#0e1017] border border-[#1b1f2b] hover:border-[#f59e0b]/40 transition-colors"
                >
                  {chip}
                </button>
              ))}
            </div>

            {/* Metric Verification Indicators */}
            <div className="mt-8 flex flex-wrap items-center gap-6 text-xs text-neutral-500 font-medium">
              <span className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                BNS, BNSS &amp; BSA 2023 Compliant
              </span>
              <span className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#d4af37]" />
                28 State Acts &amp; 25 High Courts
              </span>
              <span className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-blue-400" />
                English &amp; తెలుగు Native Voice
              </span>
            </div>
          </div>

        </div>
      </section>

      {/* SUPERPOWERS ARSENAL - 100% SOLID OPAQUE CARDS */}
      <section className="py-24 px-6 sm:px-12 lg:px-20 bg-[#090a0f]">
        <div className="max-w-7xl mx-auto">
          {/* Section Header */}
          <div className="text-left mb-16">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-[#2c3244] bg-[#141620] text-amber-300 text-[11px] font-bold uppercase tracking-widest mb-3">
              <Zap className="w-3.5 h-3.5 text-[#f59e0b]" />
              <span>Court-Admissible Legal Suites</span>
            </div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white mb-3 tracking-tight">
              Real Legal Leverage for <span className="text-[#f59e0b]">Every Indian Citizen</span>
            </h2>
            <p className="text-neutral-400 text-sm sm:text-base max-w-2xl leading-relaxed">
              Engineered with exact statutory citations, court-standard templates, and mathematical evidence verification.
            </p>
          </div>

          {/* 6 Solid High-Contrast Precision Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {superPowerCards.map((card, i) => {
              const Icon = card.icon;
              return (
                <Link
                  key={i}
                  href={card.href}
                  className="group relative p-7 rounded-2xl bg-[#0e1017] border border-[#1b1f2b] hover:border-[#d4af37] hover:bg-[#12151e] transition-all duration-200 flex flex-col justify-between shadow-xl"
                >
                  <div>
                    {/* Top Row: Medallion Icon & Statutory Tag */}
                    <div className="flex items-center justify-between mb-5">
                      <div className="w-12 h-12 rounded-xl bg-[#151822] border border-[#252a3a] group-hover:border-[#d4af37]/60 flex items-center justify-center p-3 transition-colors">
                        <Icon className={`w-6 h-6 ${card.iconColor}`} />
                      </div>
                      <span className={`text-[9px] font-black px-2.5 py-1 rounded-full border tracking-wider uppercase ${card.badgeStyle}`}>
                        {card.badge}
                      </span>
                    </div>

                    {/* Title & Statutory Grounding */}
                    <h3 className="text-lg font-bold text-white mb-1 group-hover:text-amber-200 transition-colors tracking-tight">
                      {card.title}
                    </h3>
                    <p className="text-[10px] font-bold text-[#d4af37] tracking-wide uppercase mb-3 font-mono">
                      {card.statute}
                    </p>

                    {/* Leverage Point & Description */}
                    <div className="mb-2">
                      <span className="inline-block text-xs font-bold text-neutral-200 mb-1">
                        {card.leverage}
                      </span>
                      <p className="text-xs text-neutral-400 leading-relaxed">
                        {card.desc}
                      </p>
                    </div>
                  </div>

                  {/* Action Link Footer */}
                  <div className="mt-6 pt-4 border-t border-[#171a24] flex items-center justify-between text-xs font-semibold text-neutral-400 group-hover:text-amber-200 transition-colors">
                    <span className="tracking-wide">Launch Power Suite</span>
                    <div className="w-7 h-7 rounded-lg bg-[#151822] group-hover:bg-[#d4af37] flex items-center justify-center transition-colors">
                      <ArrowRight className="w-3.5 h-3.5 text-neutral-300 group-hover:text-black transition-colors" />
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* SOLID FOOTER */}
      <footer className="py-12 px-6 sm:px-12 lg:px-20 border-t border-[#141620] bg-[#050608]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#0f1118] border border-[#222736] flex items-center justify-center">
              <Scale className="w-5 h-5 text-[#f59e0b]" />
            </div>
            <div>
              <span className="font-extrabold text-sm text-white tracking-tight">YAMA AI</span>
              <p className="text-[10px] text-neutral-500">Bharat&apos;s Senior AI Legal Strategist</p>
            </div>
          </div>
          
          <div className="flex flex-wrap items-center gap-6 text-xs text-neutral-400 font-medium">
            <Link href="/lawyer" className="hover:text-amber-300 transition-colors">Your Lawyer</Link>
            <Link href="/search" className="hover:text-amber-300 transition-colors">Search 12,036+ Laws</Link>
            <Link href="/explore" className="hover:text-amber-300 transition-colors">Explore Acts</Link>
            <Link href="/cases" className="hover:text-amber-300 transition-colors">Case Diary</Link>
            <Link href="/chat" className="hover:text-amber-300 transition-colors">Legal Chat</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
