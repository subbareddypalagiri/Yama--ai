'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import {
  Scale, Briefcase, ArrowLeft, Send, Sparkles, User, MapPin,
  FileText, Shield, Zap, ChevronDown, Copy, Check, RotateCcw,
  AlertCircle, BookOpen, Gavel, HelpCircle, X, Plus, Loader2,
  Settings2, PhoneCall, ExternalLink, MessageSquare, ChevronRight
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { API_BASE, sendChatMessageStream, type ChatResponseStyle } from '@/lib/api';
import { SettingsModal } from '@/components/chat/SettingsModal';

// ─── Types ───────────────────────────────────────────────────────────────────
interface Message {
  id: string;
  role: 'user' | 'lawyer';
  content: string;
  timestamp: Date;
  mode?: LawyerMode;
}

interface ClientProfile {
  name: string;
  state: string;
  concern: string;
}

type LawyerMode = 'quick' | 'deep' | 'rights' | 'document';

const MODES: { id: LawyerMode; label: string; icon: React.ReactNode; desc: string; color: string }[] = [
  {
    id: 'quick',
    label: 'Quick Advice',
    icon: <Zap className="w-4 h-4" />,
    desc: 'Fast, direct answer with exact statutory sections',
    color: 'from-violet-500 to-purple-600',
  },
  {
    id: 'deep',
    label: 'Deep Analysis',
    icon: <BookOpen className="w-4 h-4" />,
    desc: 'Full IRAC breakdown with sections & case laws',
    color: 'from-pink-500 to-rose-600',
  },
  {
    id: 'rights',
    label: 'Know Your Rights',
    icon: <Shield className="w-4 h-4" />,
    desc: 'What are your statutory rights & evidence protections?',
    color: 'from-orange-500 to-amber-600',
  },
  {
    id: 'document',
    label: 'Draft / Review',
    icon: <FileText className="w-4 h-4" />,
    desc: 'Draft formal police complaints, FIRs, or legal notices',
    color: 'from-teal-500 to-cyan-600',
  },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────
function LawyerAvatar({ pulse = false }: { pulse?: boolean }) {
  return (
    <div className="relative flex-shrink-0">
      <div className="relative w-10 h-10 rounded-xl flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-500 via-fuchsia-500 to-pink-500" />
        {pulse && (
          <div className="absolute inset-0 bg-gradient-to-br from-violet-500 via-fuchsia-500 to-pink-500 blur-xl opacity-60 animate-pulse" />
        )}
        <Briefcase className="relative w-5 h-5 text-white drop-shadow-lg" />
      </div>
      <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 rounded-full border-2 border-[#0a0a0b]" />
    </div>
  );
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1.5 px-4 py-3">
      {[0, 150, 300].map((delay) => (
        <span
          key={delay}
          className="w-2 h-2 bg-violet-400 rounded-full animate-bounce"
          style={{ animationDelay: `${delay}ms` }}
        />
      ))}
    </div>
  );
}

// ─── Onboarding Screen ───────────────────────────────────────────────────────
function OnboardingScreen({ onStart }: { onStart: (profile: ClientProfile) => void }) {
  const [name, setName] = useState('');
  const [state, setState] = useState('');
  const [concern, setConcern] = useState('');
  const [step, setStep] = useState(0);

  const INDIAN_STATES = [
    'Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chhattisgarh',
    'Goa','Gujarat','Haryana','Himachal Pradesh','Jharkhand','Karnataka',
    'Kerala','Madhya Pradesh','Maharashtra','Manipur','Meghalaya','Mizoram',
    'Nagaland','Odisha','Punjab','Rajasthan','Sikkim','Tamil Nadu',
    'Telangana','Tripura','Uttar Pradesh','Uttarakhand','West Bengal',
    'Delhi NCR','Chandigarh','Jammu & Kashmir','Ladakh','Puducherry',
  ];

  const CONCERNS = [
    { id: 'Cyber Crime & Hacking', label: 'Cyber Crime, Hacking & Online Fraud', icon: '💻' },
    { id: 'Property & Tenancy', label: 'Property, Tenancy & Eviction', icon: '🏠' },
    { id: 'Employment & Salary', label: 'Employment, Salary & Wrongful Termination', icon: '💼' },
    { id: 'Criminal & Police', label: 'Criminal Law, Police FIR & Bail Rights', icon: '⚖️' },
    { id: 'Consumer & Cheque Bounce', label: 'Cheque Bounce (Sec 138) & Consumer Issues', icon: '💳' },
    { id: 'Family & Matrimonial', label: 'Family, Matrimonial & Domestic Matters', icon: '👨‍👩‍👧' },
    { id: 'Other', label: 'Other Legal Guidance', icon: '📋' },
  ];

  const steps = [
    {
      title: 'What should your lawyer call you?',
      subtitle: 'Your advocate will address you with this name.',
      content: (
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter your name..."
          className="w-full px-4 py-3.5 rounded-2xl bg-white/[0.04] border border-white/[0.1] text-white placeholder-white/30 text-base focus:outline-none focus:border-violet-500/60 focus:bg-white/[0.06] transition-all"
          autoFocus
          onKeyDown={(e) => e.key === 'Enter' && name.trim() && setStep(1)}
        />
      ),
      isValid: name.trim().length > 0,
    },
    {
      title: 'Which Indian State or UT are you in?',
      subtitle: 'Enables precise application of 28 State Acts & your specific High Court precedents.',
      content: (
        <select
          value={state}
          onChange={(e) => setState(e.target.value)}
          className="w-full px-4 py-3.5 rounded-2xl bg-[#131316] border border-white/[0.1] text-white text-base focus:outline-none focus:border-violet-500/60 transition-all"
        >
          <option value="" disabled>Select your State / UT...</option>
          {INDIAN_STATES.map((s) => (
            <option key={s} value={s} className="bg-[#131316] text-white">{s}</option>
          ))}
        </select>
      ),
      isValid: state.length > 0,
    },
    {
      title: 'What is your primary legal concern?',
      subtitle: 'Your advocate will tailor statutory strategies to this field.',
      content: (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 max-h-60 overflow-y-auto pr-1">
          {CONCERNS.map((c) => (
            <button
              key={c.id}
              onClick={() => setConcern(c.id)}
              className={`flex items-center gap-3 p-3 rounded-xl border text-left text-sm transition-all ${
                concern === c.id
                  ? 'bg-violet-500/20 border-violet-500/60 text-white'
                  : 'bg-white/[0.02] border-white/[0.06] text-white/60 hover:text-white hover:bg-white/[0.05]'
              }`}
            >
              <span className="text-xl">{c.icon}</span>
              <span className="font-medium text-xs leading-snug">{c.label}</span>
            </button>
          ))}
        </div>
      ),
      isValid: concern.length > 0,
    },
  ];

  return (
    <div className="min-h-screen bg-[#070709] flex flex-col items-center justify-center p-4 relative overflow-hidden font-sans">
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl pointer-events-none" />
      
      <div className="w-full max-w-lg relative z-10">
        <div className="flex items-center justify-center gap-2.5 mb-8">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center shadow-lg shadow-violet-500/20">
            <Briefcase className="w-5 h-5 text-white" />
          </div>
          <span className="font-extrabold text-xl tracking-tight text-white">Your Personal Lawyer</span>
          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-violet-500/20 text-violet-300 border border-violet-500/30">
            PRO
          </span>
        </div>

        <div className="bg-white/[0.03] border border-white/[0.08] backdrop-blur-xl rounded-3xl p-8 shadow-2xl">
          <div className="flex gap-1.5 mb-6">
            {steps.map((_, i) => (
              <div
                key={i}
                className={`h-1 flex-1 rounded-full transition-all duration-300 ${
                  i <= step ? 'bg-gradient-to-r from-violet-500 to-pink-500' : 'bg-white/10'
                }`}
              />
            ))}
          </div>

          <h2 className="text-xl font-bold text-white mb-1.5">{steps[step].title}</h2>
          <p className="text-xs text-white/50 mb-6">{steps[step].subtitle}</p>

          <div className="mb-8">{steps[step].content}</div>

          <div className="flex items-center justify-between">
            {step > 0 ? (
              <button
                onClick={() => setStep((s) => s - 1)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-white/50 hover:text-white transition-colors"
              >
                ← Back
              </button>
            ) : <div />}

            <button
              onClick={() => {
                if (step < steps.length - 1) {
                  setStep((s) => s + 1);
                } else {
                  onStart({ name, state, concern });
                }
              }}
              disabled={!steps[step].isValid}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-violet-500 to-pink-500 text-white font-bold text-xs hover:brightness-110 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-lg shadow-violet-500/20"
            >
              {step < steps.length - 1 ? 'Continue →' : 'Meet Your Advocate →'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Main Lawyer Chat ─────────────────────────────────────────────────────────
function LawyerChat({ profile, onReset }: { profile: ClientProfile; onReset: () => void }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState<LawyerMode>('quick');
  const [sessionId] = useState(() => Math.random().toString(36).slice(2));
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [showProfile, setShowProfile] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Welcome message on mount
  useEffect(() => {
    const welcome: Message = {
      id: 'welcome',
      role: 'lawyer',
      content: `Namaste ${profile.name} 🙏 I am **Advocate YAMA**, your personal AI legal strategist.\n\nI have locked your jurisdiction to **${profile.state}** and your primary concern to **${profile.concern}**.\n\nI am connected directly to our **12,036+ National Legal Knowledge Base** covering all Central Bare Acts (BNS, BNSS, BSA, IT Act), ${profile.state} State Enactments, and High Court Precedents.\n\nTell me what happened in your own words (English, Telugu, or Hindi) — I will give you immediate, actionable legal leverage.`,
      timestamp: new Date(),
      mode: 'quick',
    };
    setMessages([welcome]);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = async (text?: string) => {
    const messageText = (text || input).trim();
    if (!messageText || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);
    if (textareaRef.current) textareaRef.current.style.height = 'auto';

    const lawyerMsgId = (Date.now() + 1).toString();
    setMessages((prev) => [
      ...prev,
      {
        id: lawyerMsgId,
        role: 'lawyer',
        content: '',
        timestamp: new Date(),
        mode,
      },
    ]);

    try {
      const stateCodeMap: Record<string, string> = {
        'Telangana': 'TG', 'Andhra Pradesh': 'AP', 'Maharashtra': 'MH', 'Delhi NCR': 'DL',
        'Karnataka': 'KA', 'Tamil Nadu': 'TN', 'West Bengal': 'WB', 'Uttar Pradesh': 'UP',
        'Kerala': 'KL', 'Gujarat': 'GJ', 'Rajasthan': 'RJ', 'Punjab': 'PB', 'Haryana': 'HR',
      };
      const stateCode = stateCodeMap[profile.state] || '';

      const settings = typeof window !== 'undefined' ? JSON.parse(localStorage.getItem('yama_ai_settings') || '{}') : {};
      const customKey = settings.apiKey || '';
      const customModel = settings.model || '';

      let streamedText = '';

      await sendChatMessageStream(
        `[Mode: ${mode.toUpperCase()} | Client: ${profile.name} | State: ${profile.state} (${stateCode}) | Concern: ${profile.concern}] ${messageText}`,
        (chunk) => {
          streamedText += chunk;
          setMessages((prev) =>
            prev.map((m) => (m.id === lawyerMsgId ? { ...m, content: streamedText } : m))
          );
        },
        sessionId,
        'default',
        undefined,
        customKey || undefined,
        customModel || undefined
      );
    } catch (err: any) {
      console.error('Lawyer streaming failed:', err);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === lawyerMsgId && !m.content
            ? {
                ...m,
                content:
                  '⚠️ **Advocate YAMA Alert:** Could not stream response. Please ensure backend is running or update your Gemini API key via the Settings gear (⚙️) above.',
              }
            : m
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const copyMessage = async (id: string, content: string) => {
    await navigator.clipboard.writeText(content);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getSuggestedQuestions = (concern: string) => {
    if (concern.includes('Cyber')) {
      return [
        'My account was hacked and they are extorting money. What do I do right now?',
        'How do I file an FIR under IT Act Section 66C/66D?',
        'Can police freeze the extortionist bank or UPI account via 1930?',
      ];
    }
    if (concern.includes('Property') || concern.includes('Tenancy')) {
      return [
        'Can my landlord evict me without 15-day notice or court decree?',
        'My landlord disconnected electricity and water. What is my legal remedy?',
        'How to recover my security deposit from an uncooperative landlord?',
      ];
    }
    if (concern.includes('Employment')) {
      return [
        'My company terminated me without 30-day notice or severance pay.',
        'Employer is refusing to release my experience letter and gratuity.',
        'Is putting an employee on 30-day PIP and firing legally valid?',
      ];
    }
    return [
      'What are my immediate legal rights in this situation?',
      'Which exact sections of Indian law penalize this action?',
      'Draft a formal legal notice / police complaint for me.',
    ];
  };

  return (
    <div className="min-h-screen bg-[#070709] text-white flex flex-col font-sans">
      {/* Header */}
      <header className="h-16 px-4 border-b border-white/[0.08] bg-[#0c0c0f]/90 backdrop-blur-md flex items-center justify-between sticky top-0 z-30">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="flex items-center gap-1 text-xs text-white/50 hover:text-white px-2.5 py-1.5 rounded-lg hover:bg-white/[0.05] transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="hidden sm:inline">Home</span>
          </Link>
          <div className="h-4 w-px bg-white/10" />
          <div className="flex items-center gap-2.5">
            <LawyerAvatar />
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm text-white">Advocate YAMA</span>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-extrabold bg-violet-500/20 text-violet-300 border border-violet-500/30">
                  {profile.state}
                </span>
              </div>
              <p className="text-[10px] text-white/40">12,036+ Indian Laws &amp; Precedents Active</p>
            </div>
          </div>
        </div>

        {/* Header Right Actions */}
        <div className="flex items-center gap-2">
          {/* Cyber Emergency 1930 Pill */}
          <a
            href="tel:1930"
            className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-lg bg-red-500/15 border border-red-500/30 text-red-300 text-xs font-semibold hover:bg-red-500/25 transition-all"
            title="National Cyber Crime Helpline"
          >
            <PhoneCall className="w-3.5 h-3.5" />
            <span>Cyber Helpline: 1930</span>
          </a>

          {/* Laws Explore Link */}
          <Link
            href="/search"
            className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white/70 hover:text-white text-xs font-semibold transition-all"
          >
            <BookOpen className="w-3.5 h-3.5 text-gold-400" />
            <span className="hidden sm:inline">Bare Acts &amp; Precedents</span>
          </Link>

          {/* Settings Modal Toggle */}
          <button
            onClick={() => setIsSettingsOpen(true)}
            className="p-2 rounded-xl text-white/50 hover:text-white hover:bg-white/[0.06] transition-all"
            title="Configure Gemini API Key"
          >
            <Settings2 className="w-4 h-4" />
          </button>

          {/* Profile Details Toggle */}
          <button
            onClick={() => setShowProfile((p) => !p)}
            className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white/70 hover:text-white text-xs font-medium transition-all"
          >
            <User className="w-3.5 h-3.5 text-violet-400" />
            <span className="hidden sm:inline">{profile.name}</span>
          </button>

          {/* Reset Profile */}
          <button
            onClick={() => {
              if (confirm('Start fresh with a new client profile?')) onReset();
            }}
            title="Reset Profile"
            className="p-2 rounded-xl text-white/30 hover:text-white hover:bg-white/[0.06] transition-all"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative z-10">
        {/* ── Profile Sidebar ── */}
        <aside
          className={`absolute sm:relative top-0 bottom-0 left-0 z-30 w-72 flex-shrink-0 transition-transform duration-300 ${
            showProfile ? 'translate-x-0' : '-translate-x-full sm:translate-x-0 sm:hidden'
          } bg-[#0c0c0f] border-r border-white/[0.08] flex flex-col`}
        >
          <div className="p-4 border-b border-white/[0.08] flex items-center justify-between">
            <span className="font-bold text-xs text-white/80 uppercase tracking-wider">Client Context</span>
            <button onClick={() => setShowProfile(false)} className="sm:hidden text-white/40 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="p-4 space-y-4 overflow-y-auto">
            <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
              <p className="text-[10px] text-white/35 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                <MapPin className="w-3 h-3 text-violet-400" /> Jurisdiction
              </p>
              <p className="text-sm font-semibold text-white">{profile.state}</p>
            </div>

            <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
              <p className="text-[10px] text-white/35 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                <Gavel className="w-3 h-3 text-pink-400" /> Primary Matter
              </p>
              <p className="text-sm font-semibold text-white">{profile.concern}</p>
            </div>

            <div>
              <p className="text-[10px] text-white/40 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <HelpCircle className="w-3 h-3" /> Quick Questions
              </p>
              <div className="space-y-1.5">
                {getSuggestedQuestions(profile.concern).map((q, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      handleSubmit(q);
                      setShowProfile(false);
                    }}
                    className="w-full text-left px-3 py-2 rounded-xl text-xs text-white/60 hover:text-white bg-white/[0.02] hover:bg-white/[0.05] border border-white/[0.05] hover:border-violet-500/30 transition-all flex items-center justify-between group"
                  >
                    <span className="line-clamp-2">{q}</span>
                    <ChevronRight className="w-3.5 h-3.5 text-white/20 group-hover:text-violet-400 flex-shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        </aside>

        {/* ── Messages Stream ── */}
        <main className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto px-4 py-6 space-y-5 scroll-smooth">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-4xl mx-auto ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
              >
                {/* Avatar */}
                {msg.role === 'lawyer' ? (
                  <LawyerAvatar pulse={isLoading && msg.id === messages[messages.length - 1]?.id} />
                ) : (
                  <div className="w-9 h-9 rounded-xl bg-white/[0.06] border border-white/[0.08] flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-white/60" />
                  </div>
                )}

                {/* Bubble */}
                <div className={`group max-w-[85%] md:max-w-[78%] flex flex-col gap-1.5 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                  {msg.role === 'lawyer' && msg.mode && msg.id !== 'welcome' && (
                    <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-violet-500/15 text-violet-300 border border-violet-500/25 uppercase tracking-wider">
                      {MODES.find((m) => m.id === msg.mode)?.label}
                    </span>
                  )}

                  <div
                    className={`px-5 py-4 rounded-2xl text-sm leading-relaxed ${
                      msg.role === 'user'
                        ? 'bg-gradient-to-br from-violet-600/40 to-fuchsia-600/30 border border-violet-500/30 text-white rounded-tr-sm shadow-md'
                        : 'bg-white/[0.03] border border-white/[0.08] text-white/90 rounded-tl-sm shadow-xl'
                    }`}
                  >
                    {msg.role === 'lawyer' ? (
                      <div className="prose prose-invert prose-sm max-w-none prose-headings:font-bold prose-headings:text-white prose-p:text-white/80 prose-li:text-white/80 prose-strong:text-violet-300">
                        <ReactMarkdown>{msg.content || '...'}</ReactMarkdown>
                      </div>
                    ) : (
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                    )}
                  </div>

                  <div className="flex items-center gap-2 px-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="text-[10px] text-white/30">
                      {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    {msg.role === 'lawyer' && msg.content && (
                      <button
                        onClick={() => copyMessage(msg.id, msg.content)}
                        className="flex items-center gap-1 text-[10px] text-white/40 hover:text-white transition-colors"
                      >
                        {copiedId === msg.id ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                        {copiedId === msg.id ? 'Copied' : 'Copy'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Typing indicator when waiting for stream */}
            {isLoading && messages[messages.length - 1]?.role === 'user' && (
              <div className="flex gap-3 max-w-4xl mx-auto">
                <LawyerAvatar pulse />
                <div className="bg-white/[0.03] border border-white/[0.08] rounded-2xl rounded-tl-sm">
                  <TypingDots />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* ── Mode selector + Input Bar ── */}
          <div className="flex-shrink-0 p-4 border-t border-white/[0.08] bg-[#0c0c0f]/90 backdrop-blur-md">
            <div className="max-w-4xl mx-auto">
              {/* Mode Pills */}
              <div className="flex gap-2 mb-3 overflow-x-auto pb-1 no-scrollbar">
                {MODES.map((m) => (
                  <button
                    key={m.id}
                    onClick={() => setMode(m.id)}
                    title={m.desc}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all flex-shrink-0 ${
                      mode === m.id
                        ? 'bg-gradient-to-r from-violet-500 to-pink-500 text-white shadow-lg shadow-violet-500/20'
                        : 'bg-white/[0.03] border border-white/[0.07] text-white/50 hover:text-white hover:bg-white/[0.06]'
                    }`}
                  >
                    {m.icon}
                    <span>{m.label}</span>
                  </button>
                ))}
              </div>

              {/* Input Box */}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSubmit();
                }}
                className="relative flex items-center rounded-2xl bg-white/[0.04] border border-white/[0.1] focus-within:border-violet-500/60 focus-within:bg-white/[0.06] transition-all p-1"
              >
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={(e) => {
                    setInput(e.target.value);
                    e.target.style.height = 'auto';
                    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmit();
                    }
                  }}
                  rows={1}
                  placeholder={`Consult your advocate (${MODES.find((m) => m.id === mode)?.label})...`}
                  className="flex-1 bg-transparent px-4 py-2.5 text-sm text-white placeholder-white/30 focus:outline-none resize-none max-h-32"
                />

                <button
                  type="submit"
                  disabled={!input.trim() || isLoading}
                  className="p-2.5 rounded-xl bg-gradient-to-r from-violet-500 to-pink-500 text-white hover:brightness-110 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-md flex-shrink-0"
                >
                  {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                </button>
              </form>
            </div>
          </div>
        </main>
      </div>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onSave={() => setIsSettingsOpen(false)}
      />
    </div>
  );
}

export default function LawyerPage() {
  const [profile, setProfile] = useState<ClientProfile | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem('yama_lawyer_profile');
    if (saved) {
      try {
        setProfile(JSON.parse(saved));
      } catch {}
    }
  }, []);

  const handleStart = (p: ClientProfile) => {
    setProfile(p);
    localStorage.setItem('yama_lawyer_profile', JSON.stringify(p));
  };

  const handleReset = () => {
    setProfile(null);
    localStorage.removeItem('yama_lawyer_profile');
  };

  if (!profile) {
    return <OnboardingScreen onStart={handleStart} />;
  }

  return <LawyerChat profile={profile} onReset={handleReset} />;
}
