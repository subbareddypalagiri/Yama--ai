'use client';

import Link from 'next/link';
import dynamic from 'next/dynamic';
import { Scale, Sparkles, Zap, Brain, Shield, ArrowRight } from 'lucide-react';
import LegalChatInput from '@/components/LegalChatInput';
import TiltCard from '@/components/ui/TiltCard';
import LanguageSelector from '@/components/LanguageSelector';
import { DarkModeToggle } from '@/components/ui/DarkModeToggle';
import { useLanguage } from '@/context/LanguageContext';

const NeuralBackground = dynamic(() => import('@/components/NeuralBackground'), {
  ssr: false,
  loading: () => <div className="absolute inset-0 bg-[#030304]" />,
});

export default function Home() {
  const { t } = useLanguage();
  
  return (
    <div className="min-h-screen flex flex-col bg-[#030304] text-white overflow-x-hidden">
      {/* NAV - Premium glass with gradient border */}
      <header className="fixed top-0 inset-x-0 z-50">
        <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-purple-500/30 to-transparent" />
        <div 
          className="backdrop-blur-2xl"
          style={{ 
            background: 'linear-gradient(to bottom, rgba(3,3,4,0.9), rgba(3,3,4,0.7))',
          }}
        >
          <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
            <TiltCard tiltAmount={20} scale={1.05} className="cursor-pointer">
              <div className="flex items-center gap-3 group">
                <div className="relative w-11 h-11 rounded-xl flex items-center justify-center overflow-hidden">
                  {/* Animated gradient background */}
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 opacity-90 group-hover:opacity-100 transition-opacity" />
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 blur-xl opacity-50 group-hover:opacity-70 transition-opacity" />
                  <Scale className="relative w-5 h-5 text-white drop-shadow-lg" />
                </div>
                <div>
                  <span className="font-bold text-lg tracking-tight text-gradient-hero">{t.hero.title}</span>
                  <span className="hidden sm:block text-[11px] text-white/40">{t.hero.subtitle}</span>
                </div>
              </div>
            </TiltCard>
            <nav className="flex items-center gap-1">
              <Link href="/cases" className="px-4 py-2 text-[13px] text-white/50 hover:text-white transition-all rounded-xl hover:bg-white/5">
                {t.nav.cases}
              </Link>
              <Link href="/search" className="px-4 py-2 text-[13px] text-white/50 hover:text-white transition-all rounded-xl hover:bg-white/5">
                Search Laws
              </Link>
              <Link href="/explore" className="px-4 py-2 text-[13px] text-white/50 hover:text-white transition-all rounded-xl hover:bg-white/5">
                Explore
              </Link>
              <Link href="/lawyer" className="px-4 py-2 text-[13px] text-white/50 hover:text-white transition-all rounded-xl hover:bg-white/5">
                Your Lawyer
              </Link>
              {/* Language Selector */}
              <LanguageSelector />
              {/* Dark Mode Toggle */}
              <DarkModeToggle />
              <TiltCard tiltAmount={15} scale={1.08}>
                <Link 
                  href="/chat" 
                  className="ml-2 px-5 py-2.5 text-[13px] font-semibold rounded-xl text-white btn-glow inline-block"
                >
                  {t.hero.openChat}
                </Link>
              </TiltCard>
            </nav>
          </div>
        </div>
      </header>

      {/* HERO */}
      <section className="relative flex flex-col items-center justify-center min-h-screen px-6 pt-24 pb-16 overflow-hidden">
        <NeuralBackground particleCount={800} connectionDistance={120} speed={0.2} />
        
        {/* VenusHawk-style glowing orb - purple/pink/orange */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] pointer-events-none">
          {/* Core purple glow */}
          <div 
            className="absolute inset-0 rounded-full animate-glow-pulse"
            style={{
              background: 'radial-gradient(circle at 40% 40%, rgba(168, 85, 247, 0.8) 0%, transparent 50%)',
              filter: 'blur(60px)',
            }}
          />
          {/* Pink middle layer */}
          <div 
            className="absolute inset-0 rounded-full animate-glow-pulse"
            style={{
              background: 'radial-gradient(circle at 50% 50%, rgba(236, 72, 153, 0.6) 0%, transparent 45%)',
              filter: 'blur(50px)',
              animationDelay: '1s',
            }}
          />
          {/* Orange outer ring */}
          <div 
            className="absolute inset-0 rounded-full animate-glow-pulse"
            style={{
              background: 'radial-gradient(circle at 60% 60%, rgba(249, 115, 22, 0.7) 0%, transparent 40%)',
              filter: 'blur(70px)',
              animationDelay: '2s',
            }}
          />
          {/* Dark center void */}
          <div 
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[200px] h-[200px] rounded-full"
            style={{
              background: 'radial-gradient(circle, #030304 0%, transparent 70%)',
            }}
          />
        </div>

        {/* Top/bottom fade gradients */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#030304] via-transparent to-[#030304] pointer-events-none z-[1]" />
        
        <div className="relative z-10 w-full max-w-3xl mx-auto text-center">
          {/* Live Badge - VenusHawk style */}
          <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full border border-white/10 bg-white/[0.03] backdrop-blur-xl mb-8 shine-line">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            <span className="text-[13px] text-white/70 font-medium">{t.hero.tagline}</span>
          </div>

          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight leading-[1.1] mb-12 font-display">
            <span className="text-white">The dawn of</span>
            <br />
            <span className="text-gradient-hero inline-block mt-2">
              {t.features.legalAnalysis}
            </span>
          </h1>

          {/* Chat Input */}
          <LegalChatInput />
        </div>
      </section>

      {/* Features section - Premium cards */}
      <section className="relative z-10 py-28 px-6">
        {/* Section gradient background */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#030304] via-[#080810] to-[#030304]" />
        <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-purple-500/20 to-transparent" />
        
        <div className="relative max-w-5xl mx-auto">
          <div className="text-center mb-20">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-purple-500/20 bg-purple-500/5 text-purple-400 text-[11px] font-semibold uppercase tracking-wider mb-6">
              <Zap className="w-3 h-3" />
              <span>{t.features.title}</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4 font-display">
              Powered by <span className="text-gradient-hero">Advanced AI</span>
            </h2>
            <p className="text-white/35 max-w-md mx-auto">Experience the next generation of legal analysis technology</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { 
                icon: <Brain className="w-6 h-6" />, 
                title: t.features.legalAnalysis, 
                desc: t.features.legalAnalysisDesc,
                gradient: 'from-purple-500 to-violet-600'
              },
              { 
                icon: <Shield className="w-6 h-6" />, 
                title: t.features.caseTracking, 
                desc: t.features.caseTrackingDesc,
                gradient: 'from-pink-500 to-rose-600'
              },
              { 
                icon: <Sparkles className="w-6 h-6" />, 
                title: t.features.documentUpload, 
                desc: t.features.documentUploadDesc,
                gradient: 'from-orange-500 to-amber-600'
              },
            ].map((item, i) => (
              <TiltCard key={i} tiltAmount={10} scale={1.03}>
                <div 
                  className="group relative p-8 rounded-2xl card-premium overflow-hidden h-full"
                >
                  {/* Hover glow effect */}
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none">
                    <div className={`absolute top-0 left-1/2 -translate-x-1/2 w-40 h-40 bg-gradient-to-b ${item.gradient} rounded-full blur-[80px] opacity-30`} />
                  </div>
                  
                  {/* Icon with gradient */}
                  <div className={`relative w-14 h-14 rounded-xl bg-gradient-to-br ${item.gradient} flex items-center justify-center mb-6 shadow-lg`}>
                    <div className={`absolute inset-0 rounded-xl bg-gradient-to-br ${item.gradient} blur-xl opacity-50`} />
                    <div className="relative text-white">{item.icon}</div>
                  </div>
                  
                  <h3 className="text-xl font-semibold text-white mb-3 group-hover:text-gradient-hero transition-all duration-300">{item.title}</h3>
                  <p className="text-[15px] text-white/40 leading-relaxed group-hover:text-white/60 transition-colors">{item.desc}</p>
                  
                  {/* Arrow indicator on hover */}
                  <div className="mt-6 flex items-center gap-2 text-white/30 group-hover:text-purple-400 transition-all duration-300">
                    <span className="text-sm font-medium">Learn more</span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </TiltCard>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-24 px-6">
        <div className="relative max-w-3xl mx-auto text-center">
          {/* Background glow */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] rounded-full bg-gradient-to-br from-purple-500/20 via-pink-500/10 to-orange-500/20 blur-[100px] pointer-events-none" />
          
          <div className="relative">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4 font-display">
              Ready to understand your <span className="text-gradient-hero">legal rights</span>?
            </h2>
            <p className="text-white/40 mb-8 max-w-md mx-auto">
              Get started with YAMA AI today and experience the future of legal intelligence
            </p>
            <Link 
              href="/chat" 
              className="inline-flex items-center gap-2 px-8 py-4 text-base font-semibold rounded-2xl text-white btn-glow"
            >
              Get in touch
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer - Minimal */}
      <footer className="relative py-10 px-6 border-t border-white/[0.03]" style={{ background: '#020203' }}>
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 flex items-center justify-center">
              <Scale className="w-4 h-4 text-white" />
            </div>
            <span className="text-white/40 text-[13px]">{t.hero.title} — {t.footer.madeWith}</span>
          </div>
          <div className="flex items-center gap-8">
            <Link href="/search" className="text-[13px] text-white/30 hover:text-white transition-colors">Search</Link>
            <Link href="/explore" className="text-[13px] text-white/30 hover:text-white transition-colors">Explore</Link>
            <Link href="/lawyer" className="text-[13px] text-white/30 hover:text-white transition-colors">Your Lawyer</Link>
            <Link href="/chat" className="text-[13px] text-white/30 hover:text-white transition-colors">{t.nav.chat}</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
