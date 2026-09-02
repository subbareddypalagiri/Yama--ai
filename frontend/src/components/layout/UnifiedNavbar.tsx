'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Scale, Briefcase, Search, BookOpen, FolderOpen, MessageSquare,
  Settings2, Shield, Globe, Menu, X
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
      {/* 100% Solid Precision Header - Zero Glassmorphism */}
      <header className="sticky top-0 z-50 w-full border-b border-[#1f2330] bg-[#090a0f] font-sans">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
          {/* Brand Identity */}
          <Link href="/" className="flex items-center gap-3 group shrink-0">
            <div className="w-10 h-10 rounded-xl bg-[#12141c] border border-[#262a38] group-hover:border-[#d4af37] flex items-center justify-center transition-colors">
              <Scale className="w-5 h-5 text-[#f59e0b]" />
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-sm tracking-tight text-white group-hover:text-[#f59e0b] transition-colors">
                  YAMA AI
                </span>
                <span className="px-1.5 py-0.5 rounded text-[8px] font-black tracking-widest uppercase bg-[#181b24] text-[#fbbf24] border border-[#2c3244]">
                  BHARAT
                </span>
              </div>
              <span className="text-[10px] text-gray-400 font-medium">
                Senior Legal Strategist
              </span>
            </div>
          </Link>

          {/* Solid Navigation Pill Island */}
          <nav className="hidden md:flex items-center gap-1 bg-[#10121a] p-1.5 rounded-full border border-[#1f2332]">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-[#1c202d] text-amber-200 border border-[#d4af37]/60 shadow-sm'
                      : link.highlight
                      ? 'text-amber-300 hover:text-amber-100 hover:bg-[#161922]'
                      : 'text-gray-300 hover:text-white hover:bg-[#161922]'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-[#f59e0b]' : ''}`} />
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Solid Action Buttons */}
          <div className="flex items-center gap-2.5">
            {/* Cyber Emergency 1930 / Jurisdiction Badge */}
            <button
              onClick={() => setIsJurisdictionOpen(true)}
              className="hidden sm:flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#181216] border border-[#401c24] hover:border-red-500/60 text-red-300 text-xs font-bold transition-all"
              title="Locate District Cyber Police Station & Emergency Helpline"
            >
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
              <span className="font-mono">1930</span>
              <span className="text-gray-600">|</span>
              <Shield className="w-3.5 h-3.5 text-red-400" />
              <span className="hidden xl:inline text-[11px] font-medium text-gray-300">Police Locator</span>
            </button>

            {/* Language Pill Switcher */}
            <button
              onClick={handleToggleLang}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-[#12141c] border border-[#222736] hover:border-[#373d52] text-xs text-gray-200 hover:text-white font-medium transition-all"
              title="Toggle English / Telugu"
            >
              <Globe className="w-3.5 h-3.5 text-[#d4af37]" />
              <span className="text-[11px] font-semibold">{currentLang}</span>
            </button>

            {/* Settings Button */}
            <button
              onClick={() => setIsSettingsOpen(true)}
              className="w-9 h-9 rounded-full bg-[#12141c] border border-[#222736] hover:border-[#373d52] flex items-center justify-center text-gray-400 hover:text-white transition-all"
              title="Configure API Key & Models"
            >
              <Settings2 className="w-4 h-4" />
            </button>

            {/* Mobile Menu Hamburger */}
            <button
              onClick={() => setIsMobileMenuOpen((o) => !o)}
              className="md:hidden w-9 h-9 rounded-full bg-[#12141c] border border-[#222736] flex items-center justify-center text-gray-300 hover:text-white"
            >
              {isMobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-[#0c0e14] border-b border-[#1f2330] px-4 py-4 space-y-2">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={`flex items-center justify-between px-4 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-[#1c202d] border border-[#d4af37]/60 text-amber-200'
                      : 'text-gray-300 hover:bg-[#151720] hover:text-white'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4 text-[#f59e0b]" />
                    <span>{link.label}</span>
                  </div>
                  {link.highlight && (
                    <span className="text-[9px] px-2 py-0.5 rounded-full font-bold bg-[#262118] text-amber-300 border border-[#4d3a1f]">
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
              className="w-full flex items-center justify-between px-4 py-2.5 rounded-xl text-xs font-bold bg-[#181216] border border-[#401c24] text-red-300 hover:bg-[#20151c] transition-all mt-2"
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
