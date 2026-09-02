'use client';

import Link from 'next/link';
import dynamic from 'next/dynamic';
import {
  Scale, Zap, ArrowRight, Briefcase, Search, BookOpen, FolderOpen,
  Home as HomeIcon, Car, ShieldAlert, Lock, CheckCircle2
} from 'lucide-react';
import LegalChatInput from '@/components/LegalChatInput';
import UnifiedNavbar from '@/components/layout/UnifiedNavbar';
import { useLanguage } from '@/context/LanguageContext';

const NeuralBackground = dynamic(() => import('@/components/NeuralBackground'), {
  ssr: false,
  loading: () => <div className="absolute inset-0 bg-[#090a0f]" />,
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
    <div className="min-h-screen flex flex-col bg-[#090a0f] text-white font-sans">
      {/* 100% Solid Precision Navbar */}
      <UnifiedNavbar />

      {/* HERO SECTION - INTERACTIVE NEURAL NETWORK */}
      <section className="relative flex flex-col items-center justify-center min-h-[85vh] px-6 pt-16 pb-20 overflow-hidden border-b border-[#1b1f2b]">
        <NeuralBackground particleCount={800} connectionDistance={120} speed={0.2} />
        
        {/* Subtle Ambient Contrast Fade */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#090a0f]/60 via-transparent to-[#090a0f] pointer-events-none z-[1]" />

        <div className="relative z-10 w-full max-w-4xl mx-auto text-center">
          {/* Status Badge */}
          <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full border border-[#2a2f40] bg-[#11131b] mb-8">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[11px] font-bold text-gray-200 tracking-wider uppercase">
              BHARAT&apos;S SENIOR AI LEGAL STRATEGIST • 12,036+ LIVE RECORDS
            </span>
          </div>

          {/* Master Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-black tracking-tight leading-[1.08] mb-6 font-display">
            <span className="text-white">The Intelligence of a</span>{' '}
            <span className="text-[#f59e0b]">
              Senior Advocate.
            </span>
            <br />
            <span className="text-gray-300">The Speed of Pure AI.</span>
          </h1>

          <p className="text-sm sm:text-base text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed font-normal">
            Autonomous statutory defense under the 2023 Sanhitas &amp; 28 State Acts, instant contract clause audits, court-standard notice drafting with gold seals, and Lok Adalat waivers.
          </p>

          {/* Chat Input */}
          <LegalChatInput />

          {/* Quick Metrics */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-gray-400 font-medium">
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
      </section>

      {/* SUPERPOWERS ARSENAL - 100% SOLID OPAQUE CARDS */}
      <section className="py-20 px-6 bg-[#0c0d14]">
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
            <p className="text-gray-400 text-sm sm:text-base max-w-xl mx-auto leading-relaxed">
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
      <footer className="py-12 px-6 border-t border-[#1a1d27] bg-[#08090d]">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
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
