'use client';

import React from 'react';
import { useTheme } from '@/context/ThemeContext';
import { Sun, Moon } from 'lucide-react';

export function DarkModeToggle() {
  const { toggleTheme, isDark } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="relative flex items-center justify-center w-9 h-9 rounded-full bg-[#12141c] border border-[#222736] hover:border-[#d4af37] transition-all text-gray-300 hover:text-amber-300 shadow-sm cursor-pointer"
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      {isDark ? (
        <Sun className="w-4 h-4 text-[#f59e0b] hover:rotate-45 transition-transform duration-300" />
      ) : (
        <Moon className="w-4 h-4 text-amber-200 hover:-rotate-12 transition-transform duration-300" />
      )}
    </button>
  );
}

export default DarkModeToggle;
