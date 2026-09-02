'use client';

import { useState, KeyboardEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import {
  Scale, Zap, ArrowRight, Briefcase, Search, BookOpen, FolderOpen,
  Home as HomeIcon, Car, ShieldAlert, Lock, CheckCircle2, ChevronRight,
  ArrowUp, Sparkles
} from 'lucide-react';
import UnifiedNavbar from '@/components/layout/UnifiedNavbar';
import VoiceConsultation from '@/components/intelligence/VoiceConsultation';
import BorderBeam from '@/components/ui/BorderBeam';

const NeuralBackground = dynamic(() => import('@/components/NeuralBackground'), {
  ssr: false,
  loading: () => <div className="absolute inset-0 bg-[#07080b]" />,
});

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
    <div className="min-h-screen flex flex-col bg-[#07080b] text-white font-sans selection:bg-[#f59e0b]/30 selection:text-white">
      {/* 100% Solid Precision Navbar */}
      <UnifiedNavbar />

      {/* HERO SECTION - DARK MODE DESIGN INSPIRATION */}
      <section className="relative flex flex-col items-center justify-center min-h-[86vh] px-6 sm:px-8 pt-16 pb-24 overflow-hidden border-b border-[#141620]">
        
        {/* PRESERVED: Interactive 3D Three.js Neural Constellation Simulation */}
        <NeuralBackground particleCount={750} connectionDistance={125} speed={0.18} />

        {/* Ambient Subtle Vignette */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#07080b]/75 via-transparent to-[#07080b] pointer-events-none z-[1]" />

        <div className="relative z-10 w-full max-w-4xl mx-auto flex flex-col items-center text-center">
          
          {/* Micro Pill Badge */}
          <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full border border-white/[0.08] bg-[#0e1017]/80 shadow-sm backdrop-blur-md mb-8">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[11px] font-mono font-medium tracking-widest text-neutral-300 uppercase">
              BHARAT&apos;S SENIOR AI LEGAL STRATEGIST • 12,036+ LAWS
            </span>
          </div>

          {/* Master Headline - Dark Mode Design Precision Typography */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-[66px] font-bold tracking-[-0.035em] leading-[1.1] text-white mb-6">
            The Intelligence of a{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#f59e0b] via-[#fbbf24] to-[#d4af37]">
              Senior Advocate.
            </span>
            <br />
            <span className="text-neutral-200">The Speed of Pure AI.</span>
          </h1>

          {/* Refined Subtitle */}
          <p className="text-sm sm:text-base text-neutral-400 max-w-2xl mx-auto mb-10 leading-relaxed font-normal">
            Autonomous statutory defense under the 2023 Sanhitas &amp; 28 State Acts, instant contract clause audits, court-standard notice drafting with gold seals, and Lok Adalat waivers.
          </p>

          {/* Sleek Command Search Bar with BorderBeam Animated Glow */}
          <div className="w-full max-w-2xl mx-auto mb-6">
            <BorderBeam
              size="md"
              colorVariant="sunset"
              theme="dark"
              duration={3}
              borderRadius={16}
              className="w-full"
            >
              <form onSubmit={handleSearchSubmit} className="relative w-full">
                <div
                  className={`relative flex items-center rounded-2xl bg-[#0c0e14]/95 border transition-all duration-300 p-2 sm:p-2.5 shadow-2xl backdrop-blur-md ${
                    isFocused
                      ? 'border-[#f59e0b]/70 shadow-[0_0_30px_rgba(245,158,11,0.18)] bg-[#0f111a]'
                      : 'border-white/[0.1] hover:border-white/[0.2]'
                  }`}
                >
                  <div className="pl-3 text-neutral-400">
                    <Search className="w-5 h-5 text-neutral-400" />
                  </div>

                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    onKeyDown={handleKeyDown}
                    placeholder="Describe your legal situation, dispute, or section (e.g. 318 BNS)..."
                    className="w-full px-3.5 py-2 bg-transparent text-sm sm:text-base text-white placeholder-neutral-500 focus:outline-none"
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
                      className={`w-9 h-9 sm:w-10 sm:h-10 rounded-xl flex items-center justify-center transition-all ${
                        query.trim()
                          ? 'bg-[#f59e0b] text-black hover:bg-[#fbbf24] shadow-md shadow-[#f59e0b]/20 cursor-pointer'
                          : 'bg-white/[0.05] text-neutral-500 cursor-not-allowed'
                      }`}
                    >
                      <ArrowUp className="w-4 h-4 font-bold" />
                    </button>
                  </div>
                </div>
              </form>
            </BorderBeam>

          </div>

        </div>
      </section>

      {/* SUPERPOWERS ARSENAL - 100% SOLID OPAQUE CARDS */}
      <section className="py-20 px-6 bg-[#0a0b10]">
        <div className="max-w-6xl mx-auto">
          {/* Section Header */}
          <div className="text-center mb-14">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-[#2c3244] bg-[#141620] text-amber-300 text-[11px] font-bold uppercase tracking-widest mb-4">
              <Zap className="w-3.5 h-3.5 text-[#f59e0b]" />
              <span>Court-Admissible Legal Suites</span>
            </div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white mb-4 tracking-tight">
              Real Legal Leverage for <span className="text-[#f59e0b]">Every Indian Citizen</span>
            </h2>
            <p className="text-neutral-400 text-sm sm:text-base max-w-xl mx-auto leading-relaxed">
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
      <footer className="py-12 px-6 border-t border-[#141620] bg-[#050608]">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
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
