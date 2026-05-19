'use client';

import React from 'react';
import { useTheme } from '@/context/ThemeContext';
import { Sun, Moon } from 'lucide-react';

export function DarkModeToggle() {
  const { theme, toggleTheme, isDark } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="relative p-2 rounded-xl transition-all duration-300 
                 bg-white/5 hover:bg-white/10 dark:bg-white/5 dark:hover:bg-white/10
                 light:bg-navy-100 light:hover:bg-navy-200
                 border border-white/10 hover:border-white/20
                 group"
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      <div className="relative w-5 h-5">
        {/* Sun icon - shown in dark mode */}
        <Sun 
          className={`absolute inset-0 w-5 h-5 transition-all duration-300 
                      ${isDark 
                        ? 'opacity-100 rotate-0 scale-100 text-amber-400' 
                        : 'opacity-0 rotate-90 scale-50 text-amber-400'
                      }`}
        />
        {/* Moon icon - shown in light mode */}
        <Moon 
          className={`absolute inset-0 w-5 h-5 transition-all duration-300
                      ${isDark 
                        ? 'opacity-0 -rotate-90 scale-50 text-violet-400' 
                        : 'opacity-100 rotate-0 scale-100 text-violet-600'
                      }`}
        />
      </div>
      
      {/* Glow effect on hover */}
      <div className={`absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 
                       transition-opacity duration-300 pointer-events-none
                       ${isDark 
                         ? 'bg-amber-500/10 shadow-[0_0_15px_rgba(251,191,36,0.3)]' 
                         : 'bg-violet-500/10 shadow-[0_0_15px_rgba(139,92,246,0.3)]'
                       }`} 
      />
    </button>
  );
}

// Compact version for mobile/sidebar
export function DarkModeToggleCompact() {
  const { toggleTheme, isDark } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200
                 hover:bg-white/5 text-white/70 hover:text-white"
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      {isDark ? (
        <>
          <Sun className="w-4 h-4 text-amber-400" />
          <span className="text-sm">Light Mode</span>
        </>
      ) : (
        <>
          <Moon className="w-4 h-4 text-violet-400" />
          <span className="text-sm">Dark Mode</span>
        </>
      )}
    </button>
  );
}
