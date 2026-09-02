'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Scale, Briefcase, Search, BookOpen, FolderOpen, MessageSquare,
  Settings2, PhoneCall, Shield, Globe, Menu, X
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
    { href: '/lawyer', label: 'Your Lawyer', icon: Briefcase, badge: 'PRO' },
    { href: '/search', label: '12,036+ Laws', icon: Search },
    { href: '/explore', label: 'Explore Acts', icon: BookOpen },
    { href: '/cases', label: 'Case Diary', icon: FolderOpen },
    { href: '/chat', label: 'AI Chat', icon: MessageSquare },
  ];

  const handleToggleLang = () => {
    const nextLang = currentLang === 'English' ? 'తెలుగు' : 'English';
    setCurrentLang(nextLang);
    if (onLanguageChange) onLanguageChange(nextLang);
  };

  return (
    <>
      <header className="h-16 border-b border-white/[0.08] bg-[#0c0c0f]/90 backdrop-blur-md sticky top-0 z-40 font-sans">
        <div className="max-w-7xl mx-auto px-4 h-full flex items-center justify-between">
          {/* Brand Logo */}
          <div className="flex items-center gap-3">
            <Link href="/" className="flex items-center gap-2.5 group">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 via-fuchsia-500 to-pink-500 flex items-center justify-center shadow-lg shadow-violet-500/20 group-hover:scale-105 transition-transform">
                <Scale className="w-4.5 h-4.5 text-white" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="font-extrabold text-sm text-white tracking-tight">YAMA AI</span>
                  <span className="px-1.5 py-0.2 rounded text-[8px] font-extrabold bg-violet-500/20 text-violet-300 border border-violet-500/30">
                    BHARAT
                  </span>
                </div>
                <p className="text-[9px] text-white/40 hidden sm:block">Senior AI Legal Strategist</p>
              </div>
            </Link>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-1 bg-white/[0.03] p-1 rounded-2xl border border-white/[0.06]">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-violet-500 to-pink-500 text-white shadow-md shadow-violet-500/20'
                      : 'text-white/60 hover:text-white hover:bg-white/[0.05]'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{link.label}</span>
                  {link.badge && (
                    <span className="text-[8px] px-1 py-0.2 rounded font-black bg-white/20 text-white">
                      {link.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Header Right Actions */}
          <div className="flex items-center gap-2">
            {/* Cyber Emergency 1930 */}
            <a
              href="tel:1930"
              className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-red-500/15 border border-red-500/30 text-red-300 text-xs font-bold hover:bg-red-500/25 transition-all"
              title="National Cyber Helpline"
            >
              <PhoneCall className="w-3.5 h-3.5" />
              <span>1930</span>
            </a>

            {/* Jurisdiction Locator Button */}
            <button
              onClick={() => setIsJurisdictionOpen(true)}
              className="hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-white/70 hover:text-white text-xs font-semibold transition-all"
              title="Find Cyber Police Station"
            >
              <Shield className="w-3.5 h-3.5 text-blue-400" />
              <span className="hidden xl:inline">Police Locator</span>
            </button>

            {/* Language Switcher */}
            <button
              onClick={handleToggleLang}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-xs text-white/70 hover:text-white font-semibold transition-all"
              title="Switch English / Telugu"
            >
              <Globe className="w-3.5 h-3.5 text-amber-400" />
              <span>{currentLang}</span>
            </button>

            {/* Settings Modal Toggle */}
            <button
              onClick={() => setIsSettingsOpen(true)}
              className="p-2 rounded-xl text-white/50 hover:text-white hover:bg-white/[0.06] transition-all"
              title="Configure API Key"
            >
              <Settings2 className="w-4 h-4" />
            </button>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen((o) => !o)}
              className="md:hidden p-2 rounded-xl text-white/60 hover:text-white hover:bg-white/[0.06]"
            >
              {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-[#0c0c0f] border-b border-white/[0.08] px-4 py-3 space-y-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={`flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold ${
                    isActive
                      ? 'bg-gradient-to-r from-violet-500 to-pink-500 text-white'
                      : 'text-white/70 hover:bg-white/[0.05]'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Icon className="w-4 h-4" />
                    <span>{link.label}</span>
                  </div>
                  {link.badge && (
                    <span className="text-[9px] px-1.5 py-0.5 rounded font-black bg-white/20 text-white">
                      {link.badge}
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
              className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold text-blue-300 hover:bg-white/[0.05]"
            >
              <Shield className="w-4 h-4 text-blue-400" />
              <span>District Cyber Police Locator</span>
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
