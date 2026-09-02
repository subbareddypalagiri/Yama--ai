'use client';

import Link from 'next/link';
import dynamic from 'next/dynamic';
import {
  Scale, Zap, Brain, Shield, ArrowRight, Briefcase,
  Search, BookOpen, FolderOpen, Home as HomeIcon, Car, ShieldAlert,
  Lock, ArrowUpRight, CheckCircle2, ChevronRight
} from 'lucide-react';
import LegalChatInput from '@/components/LegalChatInput';
import UnifiedNavbar from '@/components/layout/UnifiedNavbar';
import { useLanguage } from '@/context/LanguageContext';

const NeuralBackground = dynamic(() => import('@/components/NeuralBackground'), {
  ssr: false,
  loading: () => <div className="absolute inset-0 bg-[#06070a]" />,
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
      badgeColor: 'bg-[#d4af37]/15 text-amber-200 border-[#d4af37]/30',
    },
    {
      href: '/search',
      icon: Search,
      title: '12,036+ National Laws',
      statute: 'Supreme Court & 25 High Courts',
      badge: 'ALL INDIA',
      leverage: 'Zero-Latency Lexical & Precedent Search',
      desc: 'Search across Bharatiya Nyaya Sanhita (BNS), BNSS, BSA, Central Bare Acts, and 28 State Enactments with chronological sorting.',
      iconColor: 'text-[#d4af37]',
      badgeColor: 'bg-[#d4af37]/15 text-amber-200 border-[#d4af37]/30',
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
      badgeColor: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
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
      badgeColor: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
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
      badgeColor: 'bg-red-500/15 text-red-300 border-red-500/30',
    },
    {
      href: '/lawyer',
      icon: Lock,
      title: 'SHA-256 Evidence Vault',
      statute: 'BSA 2023 § 63 (Old 65B) & Arjun Panditrao',
      badge: 'CRYPTO VERIFIED',
      leverage: 'Tamper-Proof Electronic Admissibility',
      desc: 'Cryptographically freeze WhatsApp screenshots, call recordings, and UPI receipts with court-certified Section 63 BSA certificates.',
      iconColor: 'text-cyan-400',
      badgeColor: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#06070a] text-white overflow-x-hidden font-sans">
      {/* Unified Luxury Navbar */}
      <UnifiedNavbar />

      {/* HERO SECTION */}
      <section className="relative flex flex-col items-center justify-center min-h-[88vh] px-6 pt-16 pb-20 overflow-hidden">
        <NeuralBackground particleCount={600} connectionDistance={120} speed={0.15} />
        
        {/* Subtle Ambient Gold & Amber Light Glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[750px] h-[750px] pointer-events-none">
          <div 
            className="absolute inset-0 rounded-full animate-glow-pulse"
            style={{
              background: 'radial-gradient(circle at 50% 50%, rgba(212, 175, 55, 0.15) 0%, transparent 60%)',
              filter: 'blur(90px)',
            }}
          />
        </div>

        {/* Top/bottom fade gradients */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#06070a] via-transparent to-[#06070a] pointer-events-none z-[1]" />
        
        <div className="relative z-10 w-full max-w-4xl mx-auto text-center">
          {/* Status Badge */}
          <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full border border-[#d4af37]/30 bg-[#d4af37]/10 backdrop-blur-xl mb-8 shadow-lg shadow-[#d4af37]/5">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-[11px] font-bold text-amber-200 tracking-wider uppercase">
              BHARAT&apos;S SENIOR AI LEGAL STRATEGIST • 12,036+ LIVE RECORDS
            </span>
          </div>

          {/* Master Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight leading-[1.08] mb-6 font-display">
            <span className="text-white">The Intelligence of a</span>{' '}
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#d4af37] via-[#f59e0b] to-[#fbbf24]">
              Senior Advocate.
            </span>
            <br />
            <span className="text-white/90">The Speed of Pure AI.</span>
          </h1>

          <p className="text-sm sm:text-base text-white/50 max-w-2xl mx-auto mb-10 leading-relaxed font-normal">
            Autonomous statutory defense under the 2023 Sanhitas &amp; 28 State Acts, instant contract clause audits, court-standard notice drafting with gold seals, and Lok Adalat waivers.
          </p>

          {/* Chat Input */}
          <LegalChatInput />

          {/* Quick Metrics */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-white/40">
            <span className="flex items-center gap-1.5 font-medium">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              BNS, BNSS &amp; BSA 2023 Compliant
            </span>
            <span className="flex items-center gap-1.5 font-medium">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#d4af37]" />
              28 State Acts &amp; 25 High Courts
            </span>
            <span className="flex items-center gap-1.5 font-medium">
              <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />
              English &amp; తెలుగు Native Voice
            </span>
          </div>
        </div>
      </section>

      {/* SUPERPOWERS ARSENAL SHOWCASE - REDESIGNED LUXURY GRID */}
      <section className="relative z-10 py-24 px-6 border-t border-white/[0.07] bg-[#07080c] overflow-hidden">
        {/* Subtle Ambient Radial Lighting */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-gradient-to-b from-[#d4af37]/10 via-transparent to-transparent blur-3xl pointer-events-none" />

        <div className="max-w-6xl mx-auto relative z-10">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-[#d4af37]/30 bg-[#d4af37]/10 text-amber-200 text-[11px] font-bold uppercase tracking-widest mb-4 shadow-sm">
              <Zap className="w-3.5 h-3.5 text-[#f59e0b]" />
              <span>Court-Admissible Legal Suites</span>
            </div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-white mb-4 tracking-tight">
              Real Legal Leverage for{' '}
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#d4af37] via-[#f59e0b] to-[#fbbf24]">
                Every Indian Citizen
              </span>
            </h2>
            <p className="text-white/45 text-sm sm:text-base max-w-xl mx-auto leading-relaxed">
              Engineered with exact statutory citations, court-standard templates, and mathematical evidence verification.
            </p>
          </div>

          {/* 6 Luxury Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {superPowerCards.map((card, i) => {
              const Icon = card.icon;
              return (
                <Link
                  key={i}
                  href={card.href}
                  className="group relative p-7 rounded-3xl bg-gradient-to-b from-white/[0.035] to-white/[0.01] border border-white/[0.08] hover:border-[#d4af37]/45 hover:bg-white/[0.045] transition-all duration-300 flex flex-col justify-between shadow-2xl hover:shadow-[#d4af37]/10 hover:-translate-y-1"
                >
                  <div>
                    {/* Top Row: Medallion Icon & Statutory Tag */}
                    <div className="flex items-center justify-between mb-5">
                      <div className="w-13 h-13 rounded-2xl bg-gradient-to-br from-[#181a24] to-[#0c0d14] border border-white/[0.1] group-hover:border-[#d4af37]/50 flex items-center justify-center p-3 shadow-lg group-hover:scale-105 transition-all">
                        <Icon className={`w-6 h-6 ${card.iconColor}`} />
                      </div>
                      <span className={`text-[9px] font-extrabold px-2.5 py-1 rounded-full border tracking-wider uppercase ${card.badgeColor}`}>
                        {card.badge}
                      </span>
                    </div>

                    {/* Title & Statutory Grounding */}
                    <h3 className="text-lg font-bold text-white mb-1 group-hover:text-amber-200 transition-colors tracking-tight">
                      {card.title}
                    </h3>
                    <p className="text-[10px] font-semibold text-[#d4af37]/80 tracking-wide uppercase mb-3 font-mono">
                      {card.statute}
                    </p>

                    {/* Leverage Point & Description */}
                    <div className="mb-2">
                      <span className="inline-block text-[11px] font-bold text-white/90 mb-1">
                        {card.leverage}
                      </span>
                      <p className="text-xs text-white/50 leading-relaxed font-normal">
                        {card.desc}
                      </p>
                    </div>
                  </div>

                  {/* Action Link Footer */}
                  <div className="mt-6 pt-4 border-t border-white/[0.06] flex items-center justify-between text-xs font-semibold text-white/40 group-hover:text-amber-200 transition-colors">
                    <span className="tracking-wide">Launch Power Suite</span>
                    <div className="w-7 h-7 rounded-full bg-white/[0.04] group-hover:bg-[#d4af37]/20 flex items-center justify-center transition-colors">
                      <ArrowRight className="w-3.5 h-3.5 text-white/40 group-hover:text-amber-200 group-hover:translate-x-0.5 transition-transform" />
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="relative py-12 px-6 border-t border-white/[0.07] bg-[#040507]">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#d4af37] via-[#f59e0b] to-[#92400e] p-[1px] shadow-md shadow-[#d4af37]/10">
              <div className="w-full h-full rounded-[15px] bg-[#0c0d12] flex items-center justify-center">
                <Scale className="w-5 h-5 text-[#f59e0b]" />
              </div>
            </div>
            <div>
              <span className="font-extrabold text-sm text-white tracking-tight">YAMA AI</span>
              <p className="text-[10px] text-white/35">Bharat&apos;s Senior AI Legal Strategist</p>
            </div>
          </div>
          
          <div className="flex flex-wrap items-center gap-6 text-xs text-white/40 font-medium">
            <Link href="/lawyer" className="hover:text-amber-200 transition-colors">Your Lawyer</Link>
            <Link href="/search" className="hover:text-amber-200 transition-colors">Search 12,036+ Laws</Link>
            <Link href="/explore" className="hover:text-amber-200 transition-colors">Explore Acts</Link>
            <Link href="/cases" className="hover:text-amber-200 transition-colors">Case Diary</Link>
            <Link href="/chat" className="hover:text-amber-200 transition-colors">Legal Chat</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
