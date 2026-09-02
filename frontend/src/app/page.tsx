'use client';

import Link from 'next/link';
import dynamic from 'next/dynamic';
import {
  Scale, Sparkles, Zap, Brain, Shield, ArrowRight, Briefcase,
  Search, BookOpen, FolderOpen, Home as HomeIcon, Car, ShieldAlert,
  Lock, ArrowUpRight
} from 'lucide-react';
import LegalChatInput from '@/components/LegalChatInput';
import TiltCard from '@/components/ui/TiltCard';
import UnifiedNavbar from '@/components/layout/UnifiedNavbar';
import { useLanguage } from '@/context/LanguageContext';

const NeuralBackground = dynamic(() => import('@/components/NeuralBackground'), {
  ssr: false,
  loading: () => <div className="absolute inset-0 bg-[#030304]" />,
});

export default function Home() {
  const { t } = useLanguage();
  
  const superPowerCards = [
    {
      href: '/lawyer',
      icon: Briefcase,
      title: 'Your Personal Lawyer',
      badge: 'PRO ADVOCATE',
      desc: 'Interactive consultation in Telugu/English, clause-by-clause contract scanner & audio advice.',
      gradient: 'from-violet-500 to-purple-600',
      border: 'hover:border-violet-500/50',
    },
    {
      href: '/search',
      icon: Search,
      title: '12,036+ National Laws',
      badge: 'ALL INDIA',
      desc: 'Instant search across BNS, BNSS, BSA, Supreme Court & 25 High Court precedents.',
      gradient: 'from-amber-500 to-orange-600',
      border: 'hover:border-amber-500/50',
    },
    {
      href: '/lawyer',
      icon: HomeIcon,
      title: 'Tenant Deposit Recovery',
      badge: '18% INTEREST',
      desc: 'Statutory 15-day notice under AP/TS Tenancy Act Sec 21 for immediate refund with damages.',
      gradient: 'from-emerald-500 to-teal-600',
      border: 'hover:border-emerald-500/50',
    },
    {
      href: '/lawyer',
      icon: Car,
      title: 'Challan Lok Adalat Waiver',
      badge: '50-75% OFF',
      desc: 'Challenge camera calibration under MV Act Sec 136A & draft DLSA compounding petition.',
      gradient: 'from-amber-500 to-red-600',
      border: 'hover:border-amber-500/50',
    },
    {
      href: '/lawyer',
      icon: ShieldAlert,
      title: '1-Tap Police SOS Shield',
      badge: 'BNSS SEC 35',
      desc: 'Instant statutory arrest rights script & authoritative advocate voice announcement to police.',
      gradient: 'from-red-600 to-rose-600',
      border: 'hover:border-red-500/50',
    },
    {
      href: '/lawyer',
      icon: Lock,
      title: 'SHA-256 Evidence Vault',
      badge: 'SEC 63 BSA',
      desc: 'Freeze WhatsApp chats, audio & screenshots with tamper-proof cryptographic court certificates.',
      gradient: 'from-cyan-500 to-blue-600',
      border: 'hover:border-cyan-500/50',
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#050508] text-white overflow-x-hidden font-sans">
      {/* Unified FAANG Navbar */}
      <UnifiedNavbar />

      {/* HERO SECTION */}
      <section className="relative flex flex-col items-center justify-center min-h-[90vh] px-6 pt-16 pb-20 overflow-hidden">
        <NeuralBackground particleCount={800} connectionDistance={120} speed={0.2} />
        
        {/* Ambient Glowing Orbs */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] pointer-events-none">
          <div 
            className="absolute inset-0 rounded-full animate-glow-pulse"
            style={{
              background: 'radial-gradient(circle at 40% 40%, rgba(139, 92, 246, 0.45) 0%, transparent 55%)',
              filter: 'blur(70px)',
            }}
          />
          <div 
            className="absolute inset-0 rounded-full animate-glow-pulse"
            style={{
              background: 'radial-gradient(circle at 60% 60%, rgba(236, 72, 153, 0.35) 0%, transparent 50%)',
              filter: 'blur(60px)',
              animationDelay: '1.5s',
            }}
          />
        </div>

        {/* Top/bottom fade gradients */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#050508] via-transparent to-[#050508] pointer-events-none z-[1]" />
        
        <div className="relative z-10 w-full max-w-4xl mx-auto text-center">
          {/* Status Badge */}
          <div className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full border border-violet-500/30 bg-violet-500/10 backdrop-blur-xl mb-8 shadow-lg shadow-violet-500/10">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-[11px] font-bold text-violet-200 tracking-wider uppercase">
              BHARAT&apos;S SENIOR AI LEGAL STRATEGIST • 12,036+ LIVE RECORDS
            </span>
          </div>

          {/* Master Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight leading-[1.08] mb-6 font-display">
            <span className="text-white">The Intelligence of a</span>{' '}
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-violet-400 via-fuchsia-400 to-amber-300">
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
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              BNS, BNSS &amp; BSA 2023 Compliant
            </span>
            <span className="flex items-center gap-1.5 font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
              28 State Acts &amp; 25 High Courts
            </span>
            <span className="flex items-center gap-1.5 font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400"></span>
              English &amp; తెలుగు Native Voice
            </span>
          </div>
        </div>
      </section>

      {/* SUPERPOWERS ARSENAL SHOWCASE */}
      <section className="relative z-10 py-20 px-6 border-t border-white/[0.06] bg-gradient-to-b from-[#050508] via-[#090912] to-[#050508]">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-violet-500/25 bg-violet-500/10 text-violet-300 text-[11px] font-bold uppercase tracking-wider mb-4">
              <Zap className="w-3.5 h-3.5" />
              <span>Court-Admissible Legal Suites</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-white mb-3 tracking-tight">
              Real Legal Leverage for <span className="bg-clip-text text-transparent bg-gradient-to-r from-violet-400 to-pink-400">Every Indian Citizen</span>
            </h2>
            <p className="text-white/40 text-sm max-w-lg mx-auto">
              Engineered with exact statutory citations, court-standard templates, and mathematical evidence verification.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {superPowerCards.map((card, i) => {
              const Icon = card.icon;
              return (
                <Link
                  key={i}
                  href={card.href}
                  className={`group relative p-6 rounded-3xl bg-white/[0.02] border border-white/[0.08] ${card.border} hover:bg-white/[0.04] transition-all duration-300 flex flex-col justify-between shadow-xl`}
                >
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${card.gradient} flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform`}>
                        <Icon className="w-6 h-6 text-white" />
                      </div>
                      <span className="text-[9px] font-extrabold px-2.5 py-1 rounded-full bg-white/[0.06] border border-white/[0.08] text-white/80 tracking-wider">
                        {card.badge}
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-white mb-2 group-hover:text-violet-300 transition-colors">
                      {card.title}
                    </h3>
                    <p className="text-xs text-white/50 leading-relaxed">
                      {card.desc}
                    </p>
                  </div>

                  <div className="mt-5 pt-4 border-t border-white/[0.06] flex items-center justify-between text-xs font-semibold text-white/40 group-hover:text-white transition-colors">
                    <span>Open Suite</span>
                    <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform text-violet-400" />
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="relative py-12 px-6 border-t border-white/[0.06] bg-[#030305]">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center shadow-lg shadow-violet-500/20">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-extrabold text-sm text-white">YAMA AI</span>
              <p className="text-[10px] text-white/35">Bharat&apos;s Senior AI Legal Strategist</p>
            </div>
          </div>
          
          <div className="flex flex-wrap items-center gap-6 text-xs text-white/40">
            <Link href="/lawyer" className="hover:text-white transition-colors">Your Lawyer</Link>
            <Link href="/search" className="hover:text-white transition-colors">Search 12,036+ Laws</Link>
            <Link href="/explore" className="hover:text-white transition-colors">Explore Acts</Link>
            <Link href="/cases" className="hover:text-white transition-colors">Case Diary</Link>
            <Link href="/chat" className="hover:text-white transition-colors">AI Chat</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
