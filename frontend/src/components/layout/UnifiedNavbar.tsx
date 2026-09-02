'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Scale, Briefcase, Search, BookOpen, FolderOpen, MessageSquare,
  Settings2, PhoneCall, Shield, Globe, Menu, X, Sparkles
} from 'lucide-react';
import { SettingsModal } from '@/components/chat/SettingsModal';
import CyberJurisdictionModal from '@/components/intelligence/CyberJurisdictionModal';

interface UnifiedNavbarProps {
  onLanguageChange?: (lang: string) => void;
}

export default function UnifiedNavbar({ onLanguageChange }: UnifiedNavbarProps) {
  const pathname = usePathname();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isJurisdictionOpen, setIsJurisdictionOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [currentLang, setCurrentLang] = useState('English');

  const navLinks = [
    { href: '/lawyer', label: 'Your Lawyer', icon: Briefcase, highlight: true },
    { href: '/search', label: '12,036+ Laws', icon: Search },
    { href: '/explore', label: 'Explore Acts', icon: BookOpen },
    { href: '/cases', label: 'Case Diary', icon: FolderOpen },
    { href: '/chat', label: 'Legal Chat', icon: MessageSquare },
  ];

  const handleToggleLang = () => {
    const nextLang = currentLang === 'English' ? 'తెలుగు' : 'English';
    setCurrentLang(nextLang);
    if (onLanguageChange) onLanguageChange(nextLang);
  };

  return (
    <>
      <header className="sticky top-0 z-50 w-full border-b border-white/[0.07] bg-[#07080b]/90 backdrop-blur-2xl transition-all font-sans">
        {/* Top Gold Refraction Hairline */}
        <div className="absolute top-0 inset-x-0 h-[1px] bg-gradient-to-r from-transparent via-[#d4af37]/35 to-transparent pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
          {/* Brand Logo & Authority Seal */}
          <Link href="/" className="flex items-center gap-3 group shrink-0">
            <div className="relative w-10 h-10 rounded-2xl bg-gradient-to-br from-[#d4af37] via-[#f59e0b] to-[#92400e] p-[1px] shadow-lg shadow-[#d4af37]/10 group-hover:shadow-[#d4af37]/25 transition-all">
              <div className="w-full h-full rounded-[15px] bg-[#0c0d12] flex items-center justify-center">
                <Scale className="w-5 h-5 text-[#f59e0b] group-hover:scale-110 transition-transform duration-300" />
              </div>
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-sm tracking-tight text-white group-hover:text-amber-200 transition-colors">
                  YAMA AI
                </span>
                <span className="px-1.5 py-0.5 rounded text-[8px] font-black tracking-widest uppercase bg-[#d4af37]/15 text-[#fbbf24] border border-[#d4af37]/30">
                  BHARAT
                </span>
              </div>
              <span className="text-[10px] text-white/40 font-medium tracking-wide">
                Senior Legal Strategist
              </span>
            </div>
          </Link>

          {/* Center Navigation Capsule Island (Vercel/Apple Style) */}
          <nav className="hidden md:flex items-center gap-1 bg-[#101218]/80 p-1.5 rounded-full border border-white/[0.08] shadow-inner backdrop-blur-xl">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`relative flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-[#d4af37]/20 to-[#f59e0b]/15 text-[#fef3c7] border border-[#d4af37]/40 shadow-sm shadow-[#d4af37]/10 font-semibold'
                      : link.highlight
                      ? 'text-amber-300/90 hover:text-amber-200 hover:bg-white/[0.04]'
                      : 'text-white/60 hover:text-white hover:bg-white/[0.04]'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-[#f59e0b]' : ''}`} />
                  <span>{link.label}</span>
                  {link.highlight && !isActive && (
                    <span className="w-1.5 h-1.5 rounded-full bg-[#f59e0b] animate-pulse" />
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Right Action Controls */}
          <div className="flex items-center gap-2.5">
            {/* Cyber Emergency 1930 / Jurisdiction Badge */}
            <button
              onClick={() => setIsJurisdictionOpen(true)}
              className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-red-500/[0.08] border border-red-500/25 text-red-300 hover:bg-red-500/15 hover:border-red-500/40 text-xs font-semibold transition-all shadow-sm"
              title="Locate District Cyber Police Station & Emergency Helpline"
            >
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
              </span>
              <span className="font-mono">1930</span>
              <span className="text-white/30">|</span>
              <Shield className="w-3.5 h-3.5 text-red-400" />
              <span className="hidden xl:inline text-[11px] font-medium text-white/70">Police Locator</span>
            </button>

            {/* Language Pill Switcher */}
            <button
              onClick={handleToggleLang}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/[0.03] border border-white/[0.08] hover:border-white/[0.18] text-xs text-white/80 hover:text-white font-medium transition-all"
              title="Toggle English / Telugu"
            >
              <Globe className="w-3.5 h-3.5 text-[#d4af37]" />
              <span className="text-[11px]">{currentLang}</span>
            </button>

            {/* Settings Control Button */}
            <button
              onClick={() => setIsSettingsOpen(true)}
              className="w-9 h-9 rounded-full bg-white/[0.03] border border-white/[0.08] hover:border-white/[0.18] flex items-center justify-center text-white/50 hover:text-white transition-all"
              title="Configure API Key & Models"
            >
              <Settings2 className="w-4 h-4" />
            </button>

            {/* Mobile Menu Hamburger */}
            <button
              onClick={() => setIsMobileMenuOpen((o) => !o)}
              className="md:hidden w-9 h-9 rounded-full bg-white/[0.03] border border-white/[0.08] flex items-center justify-center text-white/60 hover:text-white"
            >
              {isMobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-[#0a0b10] border-b border-white/[0.08] px-4 py-4 space-y-1.5">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={`flex items-center justify-between px-4 py-2.5 rounded-xl text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-[#d4af37]/15 border border-[#d4af37]/30 text-amber-200 font-semibold'
                      : 'text-white/70 hover:bg-white/[0.04] hover:text-white'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4 text-[#d4af37]" />
                    <span>{link.label}</span>
                  </div>
                  {link.highlight && (
                    <span className="text-[9px] px-2 py-0.5 rounded-full font-bold bg-[#d4af37]/20 text-amber-300">
                      PRO
                    </span>
                  )}
                </Link>
              );
            })}

            <button
              onClick={() => {
                setIsJurisdictionOpen(true);
                setIsMobileMenuOpen(false);
              }}
              className="w-full flex items-center justify-between px-4 py-2.5 rounded-xl text-xs font-semibold bg-red-500/10 border border-red-500/20 text-red-300 hover:bg-red-500/20 transition-all mt-2"
            >
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-red-400" />
                <span>District Cyber Police Locator</span>
              </div>
              <span className="font-mono text-[11px]">1930</span>
            </button>
          </div>
        )}
      </header>

      {/* Modals */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onSave={() => setIsSettingsOpen(false)}
      />

      <CyberJurisdictionModal
        isOpen={isJurisdictionOpen}
        onClose={() => setIsJurisdictionOpen(false)}
      />
    </>
  );
}
