/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // New premium AI color palette
        cosmos: {
          950: '#030304',
          900: '#0a0a0c',
          800: '#101014',
          700: '#18181d',
          600: '#1f1f26',
        },
        neon: {
          purple: '#a855f7',
          violet: '#8b5cf6',
          fuchsia: '#d946ef',
          pink: '#ec4899',
          orange: '#f97316',
          amber: '#f59e0b',
        },
        glow: {
          purple: 'rgba(168, 85, 247, 0.5)',
          violet: 'rgba(139, 92, 246, 0.5)',
          orange: 'rgba(249, 115, 22, 0.5)',
          pink: 'rgba(236, 72, 153, 0.5)',
        },
        gold: {
          50:  '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        saffron: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316',
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
        },
        navy: {
          50:  '#f0f4ff',
          100: '#dce6ff',
          200: '#b8ccff',
          300: '#85a5f8',
          400: '#5278e8',
          500: '#3155cc',
          600: '#2040aa',
          700: '#1a3488',
          800: '#162b6e',
          900: '#0f1f52',
          950: '#080e2e',
        },
        justice: {
          dark:   '#080e2e',
          mid:    '#0f1f52',
          accent: '#1a3488',
          gold:   '#e2b659',
          light:  '#f0f4ff',
        },
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Space Grotesk', 'Outfit', 'system-ui', 'sans-serif'],
        serif: ['Georgia', 'Cambria', 'serif'],
      },
      boxShadow: {
        'gold':    '0 0 20px rgba(226,182,89,0.25)',
        'gold-lg': '0 0 40px rgba(226,182,89,0.35)',
        'glass':   '0 8px 32px rgba(0,0,0,0.24)',
        'card':    '0 4px 24px rgba(8,14,46,0.12)',
        'card-hover': '0 8px 40px rgba(8,14,46,0.2)',
        // Premium glow shadows
        'glow-purple': '0 0 60px rgba(168, 85, 247, 0.4)',
        'glow-orange': '0 0 60px rgba(249, 115, 22, 0.4)',
        'glow-pink': '0 0 60px rgba(236, 72, 153, 0.4)',
        'glow-violet': '0 0 40px rgba(139, 92, 246, 0.5)',
        'glow-btn': '0 4px 30px rgba(168, 85, 247, 0.4)',
        'glow-btn-hover': '0 8px 50px rgba(168, 85, 247, 0.6)',
        'inner-glow': 'inset 0 0 30px rgba(168, 85, 247, 0.1)',
      },
      backgroundImage: {
        'hero-gradient': 'linear-gradient(135deg, #080e2e 0%, #0f1f52 40%, #1a3488 70%, #0f1f52 100%)',
        'card-gradient': 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%)',
        'gold-gradient': 'linear-gradient(135deg, #f59e0b 0%, #e2b659 50%, #d97706 100%)',
        // Premium AI gradients
        'gradient-cosmic': 'radial-gradient(ellipse at center, #1a1625 0%, #0a0a0c 70%)',
        'gradient-orb': 'radial-gradient(circle, rgba(168, 85, 247, 0.8) 0%, rgba(236, 72, 153, 0.6) 30%, rgba(249, 115, 22, 0.4) 60%, transparent 80%)',
        'gradient-orb-alt': 'radial-gradient(circle, rgba(139, 92, 246, 0.7) 0%, rgba(217, 70, 239, 0.5) 40%, rgba(249, 115, 22, 0.3) 70%, transparent 90%)',
        'gradient-shine': 'linear-gradient(135deg, transparent 0%, rgba(255,255,255,0.05) 50%, transparent 100%)',
        'gradient-btn': 'linear-gradient(135deg, #a855f7 0%, #ec4899 50%, #f97316 100%)',
        'gradient-btn-hover': 'linear-gradient(135deg, #c084fc 0%, #f472b6 50%, #fb923c 100%)',
        'gradient-text': 'linear-gradient(135deg, #ffffff 0%, #a855f7 30%, #ec4899 60%, #f97316 100%)',
        'gradient-border': 'linear-gradient(135deg, rgba(168, 85, 247, 0.5), rgba(236, 72, 153, 0.5), rgba(249, 115, 22, 0.5))',
      },
      animation: {
        'fade-up':   'fadeUp 0.6s ease-out',
        'fade-in':   'fadeIn 0.4s ease-out',
        'pulse-gold':'pulseGold 2s ease-in-out infinite',
        'shimmer':   'shimmer 2s linear infinite',
        // Premium animations
        'glow-pulse': 'glowPulse 4s ease-in-out infinite',
        'orb-float': 'orbFloat 8s ease-in-out infinite',
        'orb-rotate': 'orbRotate 20s linear infinite',
        'shine': 'shine 3s ease-in-out infinite',
        'gradient-shift': 'gradientShift 8s ease infinite',
        'border-glow': 'borderGlow 3s ease-in-out infinite',
        'float-up': 'floatUp 6s ease-in-out infinite',
      },
      keyframes: {
        fadeUp:    { '0%': { opacity: 0, transform: 'translateY(20px)' }, '100%': { opacity: 1, transform: 'translateY(0)' } },
        fadeIn:    { '0%': { opacity: 0 }, '100%': { opacity: 1 } },
        pulseGold: { '0%,100%': { boxShadow: '0 0 10px rgba(226,182,89,0.2)' }, '50%': { boxShadow: '0 0 30px rgba(226,182,89,0.5)' } },
        shimmer:   { '0%': { backgroundPosition: '-200% 0' }, '100%': { backgroundPosition: '200% 0' } },
        // Premium keyframes
        glowPulse: { 
          '0%, 100%': { opacity: '0.5', transform: 'scale(1)' }, 
          '50%': { opacity: '0.8', transform: 'scale(1.05)' } 
        },
        orbFloat: { 
          '0%, 100%': { transform: 'translateY(0) translateX(0)' }, 
          '25%': { transform: 'translateY(-20px) translateX(10px)' },
          '50%': { transform: 'translateY(-10px) translateX(-5px)' },
          '75%': { transform: 'translateY(-30px) translateX(5px)' }
        },
        orbRotate: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' }
        },
        shine: {
          '0%': { backgroundPosition: '-200% center' },
          '100%': { backgroundPosition: '200% center' }
        },
        gradientShift: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' }
        },
        borderGlow: {
          '0%, 100%': { opacity: '0.5' },
          '50%': { opacity: '1' }
        },
        floatUp: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' }
        },
      },
    },
  },
  plugins: [],
};
