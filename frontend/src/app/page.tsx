'use client';

import Link from 'next/link';
import dynamic from 'next/dynamic';
import {
  Scale, Zap, ArrowRight, Briefcase, Search, BookOpen, FolderOpen,
  Home as HomeIcon, Car, ShieldAlert, Lock, CheckCircle2, Sparkles
} from 'lucide-react';
import LegalChatInput from '@/components/LegalChatInput';
import UnifiedNavbar from '@/components/layout/UnifiedNavbar';
import { useLanguage } from '@/context/LanguageContext';

const NeuralBackground = dynamic(() => import('@/components/NeuralBackground'), {
  ssr: false,
  loading: () => <div className="absolute inset-0 bg-[#08090d]" />,
});

export default function Home() {
  const { t } = useLanguage();
  
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
    <div className="min-h-screen flex flex-col bg-[#08090d] text-white font-sans">
      {/* 100% Solid Precision Navbar */}
      <UnifiedNavbar />

      {/* HERO SECTION - ACETERNITY-STYLE ASYMMETRIC RICH TYPOGRAPHY */}
      <section className="relative px-6 sm:px-10 lg:px-16 pt-16 pb-24 overflow-hidden border-b border-[#1b1f2b]">
        {/* Interactive Neural Constellation in Background */}
        <NeuralBackground particleCount={650} connectionDistance={110} speed={0.15} />

        {/* Aceternity Glowing Horizon Arc at the Bottom */}
        <div className="absolute bottom-0 inset-x-0 h-44 bg-[radial-gradient(ellipse_90%_100%_at_50%_100%,rgba(212,175,55,0.14),transparent_70%)] pointer-events-none z-[2]" />
        <div className="absolute bottom-0 inset-x-0 h-[1px] bg-gradient-to-r from-transparent via-[#d4af37]/45 to-transparent pointer-events-none z-[2]" />

        {/* Ambient Top/Fade */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#08090d]/60 via-transparent to-[#08090d] pointer-events-none z-[1]" />

        <div className="max-w-7xl mx-auto relative z-10">
          {/* Top Aceternity-style Pill Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/[0.1] bg-[#10121a]/90 mb-10 shadow-sm backdrop-blur-sm">
            <span className="px-2 py-0.5 rounded-full bg-white/[0.08] text-white font-black text-[10px] tracking-wider uppercase">
              YAMA AI
            </span>
            <span className="text-gray-300 text-xs font-medium pr-1">
              Bharat&apos;s Senior AI Legal Strategist • 12,036+ Laws
            </span>
          </div>

          {/* Asymmetric Split Layout (Left: Giant Headline | Right: Subtext & Action Button) */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-14 items-end mb-14">
            
            {/* Left Column: Gigantic, Bold, Left-Aligned Statement (8 cols) */}
            <div className="lg:col-span-8 text-left">
              <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-[76px] font-black tracking-tight leading-[1.03] text-white font-display">
                The Intelligence of a{' '}
                <span className="text-[#f59e0b]">Senior Advocate.</span>
                <br />
                <span className="text-white/95">The Speed of Pure AI.</span>
              </h1>
            </div>

            {/* Right Column: Balanced Subtitle & Direct Action Button (4 cols) */}
            <div className="lg:col-span-4 flex flex-col justify-end items-start space-y-6 text-left lg:pb-2">
              <p className="text-sm sm:text-base text-gray-300 leading-relaxed font-normal">
                Autonomous statutory defense under the 2023 Sanhitas &amp; 28 State Acts, instant contract clause audits, court-standard notice drafting with gold seals, and Lok Adalat waivers.
              </p>

              {/* High-Tech Action Button (Aceternity style) */}
              <Link
                href="/lawyer"
                className="inline-flex items-center gap-3 px-5 py-3 rounded-2xl bg-[#12141c] border border-[#272d3e] hover:border-[#d4af37] text-white text-sm font-bold transition-all group shadow-xl hover:shadow-[#d4af37]/10"
              >
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#d4af37] to-[#f59e0b] flex items-center justify-center text-black font-black shadow-md group-hover:scale-105 transition-transform">
                  <Scale className="w-4 h-4 text-black" />
                </div>
                <span>Consult Advocate YAMA</span>
                <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-[#f59e0b] group-hover:translate-x-1 transition-all" />
              </Link>
            </div>

          </div>

          {/* Full-Width Expansive Chat Input Container */}
          <div className="w-full max-w-4xl text-left">
            <LegalChatInput />

            {/* Quick Metrics */}
            <div className="mt-8 flex flex-wrap items-center gap-6 text-xs text-gray-400 font-medium">
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
      <section className="py-20 px-6 sm:px-10 bg-[#0b0c12]">
        <div className="max-w-7xl mx-auto">
          {/* Section Header */}
          <div className="text-left mb-14">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-[#2c3244] bg-[#141620] text-amber-300 text-[11px] font-bold uppercase tracking-widest mb-3">
              <Zap className="w-3.5 h-3.5 text-[#f59e0b]" />
              <span>Court-Admissible Legal Suites</span>
            </div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white mb-3 tracking-tight">
              Real Legal Leverage for <span className="text-[#f59e0b]">Every Indian Citizen</span>
            </h2>
            <p className="text-gray-400 text-sm sm:text-base max-w-2xl leading-relaxed">
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
                  className="group relative p-7 rounded-2xl bg-[#10121a] border border-[#1f2332] hover:border-[#d4af37] hover:bg-[#141622] transition-all duration-200 flex flex-col justify-between"
                >
                  <div>
                    {/* Top Row: Medallion Icon & Statutory Tag */}
                    <div className="flex items-center justify-between mb-5">
                      <div className="w-12 h-12 rounded-xl bg-[#171924] border border-[#272d3e] group-hover:border-[#d4af37]/60 flex items-center justify-center p-3 transition-colors">
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
                      <span className="inline-block text-xs font-bold text-gray-200 mb-1">
                        {card.leverage}
                      </span>
                      <p className="text-xs text-gray-400 leading-relaxed">
                        {card.desc}
                      </p>
                    </div>
                  </div>

                  {/* Action Link Footer */}
                  <div className="mt-6 pt-4 border-t border-[#1b1e2a] flex items-center justify-between text-xs font-semibold text-gray-400 group-hover:text-amber-200 transition-colors">
                    <span className="tracking-wide">Launch Power Suite</span>
                    <div className="w-7 h-7 rounded-lg bg-[#171924] group-hover:bg-[#d4af37] flex items-center justify-center transition-colors">
                      <ArrowRight className="w-3.5 h-3.5 text-gray-300 group-hover:text-black transition-colors" />
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* SOLID FOOTER */}
      <footer className="py-12 px-6 sm:px-10 border-t border-[#1a1d27] bg-[#07080b]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#12141c] border border-[#262a38] flex items-center justify-center">
              <Scale className="w-5 h-5 text-[#f59e0b]" />
            </div>
            <div>
              <span className="font-extrabold text-sm text-white tracking-tight">YAMA AI</span>
              <p className="text-[10px] text-gray-500">Bharat&apos;s Senior AI Legal Strategist</p>
            </div>
          </div>
          
          <div className="flex flex-wrap items-center gap-6 text-xs text-gray-400 font-medium">
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
