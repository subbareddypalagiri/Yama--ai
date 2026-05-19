'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import {
  Scale, Briefcase, ArrowLeft, Send, Sparkles, User, MapPin,
  FileText, Shield, Zap, ChevronDown, Copy, Check, RotateCcw,
  AlertCircle, BookOpen, Gavel, HelpCircle, X, Plus, Loader2,
} from 'lucide-react';
import { API_BASE } from '@/lib/api';

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
    desc: 'Fast, direct answer to your question',
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
    desc: 'What are your rights in this situation?',
    color: 'from-orange-500 to-amber-600',
  },
  {
    id: 'document',
    label: 'Draft / Review',
    icon: <FileText className="w-4 h-4" />,
    desc: 'Draft legal notices, agreements or FIR templates',
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
      {/* Online indicator */}
      <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 rounded-full border-2 border-[#0a0a0b]" />
    </div>
  );
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1 px-4 py-3">
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
    'Nagaland','Odisha','Punjab','Rajasthan','Sikkim','Tamil Nadu','Telangana',
    'Tripura','Uttar Pradesh','Uttarakhand','West Bengal',
    'Delhi','Jammu & Kashmir','Ladakh','Puducherry','Chandigarh',
  ];

  const CONCERNS = [
    'Criminal / FIR', 'Civil Dispute', 'Property / Land', 'Family / Divorce',
    'Consumer Rights', 'Labour / Employment', 'Cyber Crime', 'Motor Accident',
    'Tax / Finance', 'Constitutional Rights', 'Corporate / Business', 'Other',
  ];

  const steps = [
    {
      title: "What's your name?",
      subtitle: 'Your lawyer needs to know who they\'re helping',
      content: (
        <input
          autoFocus
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && name.trim() && setStep(1)}
          placeholder="Enter your name…"
          className="w-full bg-white/[0.04] border border-white/10 rounded-2xl px-5 py-4 text-white placeholder-white/30 text-lg focus:outline-none focus:border-violet-500/50 focus:bg-white/[0.06] transition-all"
        />
      ),
      canProceed: !!name.trim(),
    },
    {
      title: `Which state are you in, ${name}?`,
      subtitle: 'Laws vary by state — this helps give you accurate advice',
      content: (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-64 overflow-y-auto pr-1 custom-scroll">
          {INDIAN_STATES.map((s) => (
            <button
              key={s}
              onClick={() => { setState(s); }}
              className={`px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-left ${
                state === s
                  ? 'bg-violet-500/30 border border-violet-500/60 text-violet-300'
                  : 'bg-white/[0.03] border border-white/[0.06] text-white/60 hover:bg-white/[0.07] hover:text-white/80'
              }`}
            >
              <MapPin className="w-3 h-3 inline mr-1.5 opacity-60" />
              {s}
            </button>
          ))}
        </div>
      ),
      canProceed: !!state,
    },
    {
      title: 'What\'s your primary concern?',
      subtitle: 'This helps your lawyer focus on the most relevant laws',
      content: (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {CONCERNS.map((c) => (
            <button
              key={c}
              onClick={() => setConcern(c)}
              className={`px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-left ${
                concern === c
                  ? 'bg-gradient-to-r from-violet-500/30 to-pink-500/20 border border-violet-500/60 text-violet-300'
                  : 'bg-white/[0.03] border border-white/[0.06] text-white/60 hover:bg-white/[0.07] hover:text-white/80'
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      ),
      canProceed: !!concern,
    },
  ];

  const current = steps[step];

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-6 bg-[#0a0a0b] text-white">
      {/* Ambient glow */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/3 w-[500px] h-[500px] bg-violet-600/[0.07] rounded-full blur-[150px]" />
        <div className="absolute bottom-1/4 right-1/3 w-[400px] h-[400px] bg-fuchsia-600/[0.05] rounded-full blur-[120px]" />
      </div>

      <div className="relative w-full max-w-lg">
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-12">
          <div className="relative w-12 h-12 rounded-xl flex items-center justify-center overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-violet-500 via-fuchsia-500 to-pink-500" />
            <div className="absolute inset-0 bg-gradient-to-br from-violet-500 via-fuchsia-500 to-pink-500 blur-xl opacity-60" />
            <Briefcase className="relative w-6 h-6 text-white" />
          </div>
          <div>
            <p className="font-bold text-xl tracking-tight text-gradient-hero">Your Lawyer</p>
            <p className="text-[11px] text-white/40">Powered by YAMA AI</p>
          </div>
        </div>

        {/* Step progress dots */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {steps.map((_, i) => (
            <div
              key={i}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                i === step ? 'w-8 bg-violet-500' : i < step ? 'w-4 bg-violet-500/50' : 'w-4 bg-white/10'
              }`}
            />
          ))}
        </div>

        {/* Card */}
        <div className="card-premium rounded-3xl p-8">
          <h2 className="text-2xl font-bold text-white mb-2">{current.title}</h2>
          <p className="text-white/40 text-sm mb-6">{current.subtitle}</p>

          {current.content}

          <div className="flex items-center gap-3 mt-6">
            {step > 0 && (
              <button
                onClick={() => setStep(s => s - 1)}
                className="px-5 py-3 rounded-xl text-sm font-medium text-white/50 hover:text-white bg-white/[0.03] border border-white/[0.06] hover:bg-white/[0.07] transition-all"
              >
                Back
              </button>
            )}
            <button
              disabled={!current.canProceed}
              onClick={() => {
                if (step < steps.length - 1) setStep(s => s + 1);
                else onStart({ name, state, concern });
              }}
              className={`flex-1 px-5 py-3 rounded-xl text-sm font-semibold transition-all ${
                current.canProceed
                  ? 'btn-glow text-white'
                  : 'bg-white/[0.03] text-white/20 cursor-not-allowed border border-white/[0.06]'
              }`}
            >
              {step < steps.length - 1 ? 'Continue →' : 'Meet Your Lawyer →'}
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
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Welcome message on mount
  useEffect(() => {
    const welcome: Message = {
      id: 'welcome',
      role: 'lawyer',
      content: `Namaste ${profile.name} 🙏 I'm your personal legal advisor powered by YAMA AI.\n\nI can see you're based in **${profile.state}** and your primary concern is **${profile.concern}**. I'm fully aware of applicable central laws and ${profile.state} state laws.\n\nYou can ask me anything — describe your situation in your own words, even in Telugu, Hindi, or English. I'll give you honest, clear legal guidance.\n\n*Disclaimer: This is legal information, not formal legal advice. For court matters, consult a licensed advocate.*`,
      timestamp: new Date(),
      mode: 'quick',
    };
    setMessages([welcome]);
  // eslint-disable-next-line react-hooks/exhaustive-deps
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
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setError(null);
    setIsLoading(true);
    if (textareaRef.current) textareaRef.current.style.height = 'auto';

    try {
      // Build lawyer-specific system context
      const lawyerContext = `You are a personal legal advisor for ${profile.name}, based in ${profile.state}, India. Their primary concern area is ${profile.concern}. Mode: ${mode}. ${
        mode === 'quick' ? 'Give a direct, concise answer in 3-5 sentences.' :
        mode === 'deep' ? 'Give a full IRAC analysis with relevant sections, case laws, and step-by-step guidance.' :
        mode === 'rights' ? 'Focus specifically on their legal rights and what protections the law offers them.' :
        'Help draft or review the legal document they describe.'
      } Always mention specific Indian law sections (IPC/BNS, CrPC/BNSS, etc). Speak like a trusted personal lawyer, not a formal AI.`;

      const res = await fetch(`${API_BASE}/lawyer/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageText,
          session_id: sessionId,
          lawyer_context: lawyerContext,
          mode,
          client_profile: profile,
        }),
      });

      if (!res.ok) throw new Error('Lawyer API failed');
      const data = await res.json();

      const lawyerMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'lawyer',
        content: data.analysis || data.response || 'I need more details about your situation. Can you describe what happened?',
        timestamp: new Date(),
        mode,
      };
      setMessages(prev => [...prev, lawyerMsg]);
    } catch {
      // Fallback: use main chat endpoint
      try {
        const res = await fetch(`${API_BASE}/chat/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: `[Personal Lawyer Mode - ${mode}] Client: ${profile.name}, State: ${profile.state}, Concern: ${profile.concern}. Question: ${messageText}`,
            session_id: sessionId,
          }),
        });
        if (!res.ok) throw new Error();
        const data = await res.json();
        setMessages(prev => [...prev, {
          id: (Date.now() + 1).toString(),
          role: 'lawyer',
          content: data.analysis,
          timestamp: new Date(),
          mode,
        }]);
      } catch {
        setError('Could not reach your lawyer right now. Please check if the backend is running.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const copyMessage = async (id: string, content: string) => {
    await navigator.clipboard.writeText(content);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(); }
  };

  const currentMode = MODES.find(m => m.id === mode)!;

  return (
    <div className="flex flex-col h-screen bg-[#0a0a0b] text-white overflow-hidden">
      {/* Ambient background */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-violet-600/[0.07] rounded-full blur-[150px]" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-fuchsia-600/[0.05] rounded-full blur-[120px]" />
      </div>

      {/* ── Header ── */}
      <header className="relative z-20 flex-shrink-0 border-b border-white/[0.04]">
        <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0b] via-[#0a0a0b]/95 to-transparent" />
        <div className="relative flex items-center gap-4 px-4 py-3">
          {/* Back */}
          <Link
            href="/"
            className="flex items-center gap-1.5 text-white/40 hover:text-white transition-colors text-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="hidden sm:inline">Home</span>
          </Link>

          {/* Lawyer identity */}
          <div className="flex items-center gap-3 flex-1">
            <LawyerAvatar />
            <div>
              <p className="font-semibold text-white text-sm leading-tight">Your Lawyer</p>
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                <span className="text-[11px] text-green-400">Available now</span>
              </div>
            </div>
          </div>

          {/* Profile button */}
          <button
            onClick={() => setShowProfile(p => !p)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/[0.04] border border-white/[0.06] hover:bg-white/[0.07] transition-all text-sm text-white/60 hover:text-white"
          >
            <User className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">{profile.name}</span>
          </button>

          {/* Reset */}
          <button
            onClick={() => { if (confirm('Start fresh with a new profile?')) onReset(); }}
            title="Change profile"
            className="p-2 rounded-xl text-white/30 hover:text-white/70 hover:bg-white/[0.05] transition-all"
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
          } bg-[#0e0e10] border-r border-white/[0.05] flex flex-col`}
        >
          <div className="p-5 border-b border-white/[0.05] flex items-center justify-between">
            <span className="font-semibold text-sm text-white/80">Client Profile</span>
            <button onClick={() => setShowProfile(false)} className="sm:hidden text-white/40 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="p-5 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500/20 to-pink-500/20 border border-violet-500/20 flex items-center justify-center">
                <User className="w-5 h-5 text-violet-400" />
              </div>
              <div>
                <p className="font-semibold text-white">{profile.name}</p>
                <p className="text-xs text-white/40">Client</p>
              </div>
            </div>

            <div className="space-y-2.5">
              <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <p className="text-[10px] text-white/30 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                  <MapPin className="w-3 h-3" /> State Jurisdiction
                </p>
                <p className="text-sm text-white/80 font-medium">{profile.state}</p>
              </div>
              <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <p className="text-[10px] text-white/30 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                  <Gavel className="w-3 h-3" /> Primary Concern
                </p>
                <p className="text-sm text-white/80 font-medium">{profile.concern}</p>
              </div>
            </div>

            {/* Suggested questions */}
            <div>
              <p className="text-[10px] text-white/30 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <HelpCircle className="w-3 h-3" /> Suggested Questions
              </p>
              <div className="space-y-1.5">
                {getSuggestedQuestions(profile.concern).map((q, i) => (
                  <button
                    key={i}
                    onClick={() => { handleSubmit(q); setShowProfile(false); }}
                    className="w-full text-left px-3 py-2 rounded-lg text-xs text-white/50 hover:text-white/80 bg-white/[0.02] hover:bg-white/[0.05] border border-white/[0.04] hover:border-violet-500/20 transition-all"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </aside>

        {/* ── Messages ── */}
        <main className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 scroll-smooth">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
              >
                {/* Avatar */}
                {msg.role === 'lawyer' ? (
                  <LawyerAvatar />
                ) : (
                  <div className="relative flex-shrink-0 w-10 h-10 rounded-xl bg-white/[0.06] border border-white/[0.08] flex items-center justify-center">
                    <User className="w-5 h-5 text-white/50" />
                  </div>
                )}

                {/* Bubble */}
                <div className={`group max-w-[75%] ${msg.role === 'user' ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
                  {msg.role === 'lawyer' && msg.mode && msg.id !== 'welcome' && (
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium bg-gradient-to-r ${MODES.find(m => m.id === msg.mode)?.color} bg-opacity-20 text-white/60`}>
                      {MODES.find(m => m.id === msg.mode)?.label}
                    </span>
                  )}
                  <div
                    className={`relative px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
                      msg.role === 'user'
                        ? 'bg-gradient-to-br from-violet-600/40 to-fuchsia-600/30 border border-violet-500/20 text-white rounded-tr-sm'
                        : 'bg-white/[0.04] border border-white/[0.07] text-white/85 rounded-tl-sm'
                    }`}
                  >
                    {msg.content}
                  </div>
                  <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="text-[10px] text-white/20">
                      {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    {msg.role === 'lawyer' && (
                      <button
                        onClick={() => copyMessage(msg.id, msg.content)}
                        className="flex items-center gap-1 text-[10px] text-white/30 hover:text-white/60 transition-colors"
                      >
                        {copiedId === msg.id ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3" />}
                        {copiedId === msg.id ? 'Copied' : 'Copy'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {isLoading && (
              <div className="flex gap-3">
                <LawyerAvatar pulse />
                <div className="bg-white/[0.04] border border-white/[0.07] rounded-2xl rounded-tl-sm">
                  <TypingDots />
                </div>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {error}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* ── Mode selector + Input ── */}
          <div className="flex-shrink-0 p-4 border-t border-white/[0.04]">
            {/* Mode pills */}
            <div className="flex gap-2 mb-3 overflow-x-auto pb-1 no-scrollbar">
              {MODES.map((m) => (
                <button
                  key={m.id}
                  onClick={() => setMode(m.id)}
                  title={m.desc}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition-all flex-shrink-0 ${
                    mode === m.id
                      ? `bg-gradient-to-r ${m.color} text-white shadow-lg shadow-violet-500/20`
                      : 'bg-white/[0.03] border border-white/[0.06] text-white/40 hover:text-white/70 hover:bg-white/[0.06]'
                  }`}
                >
                  {m.icon}
                  {m.label}
                </button>
              ))}
            </div>

            {/* Input box */}
            <div
              className={`relative flex items-end gap-3 px-4 py-3 rounded-2xl border transition-all ${
                input
                  ? 'bg-white/[0.05] border-violet-500/30'
                  : 'bg-white/[0.03] border-white/[0.08]'
              }`}
            >
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  e.target.style.height = 'auto';
                  e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px';
                }}
                onKeyDown={handleKeyDown}
                placeholder={`Ask your lawyer… (${currentMode.label})`}
                rows={1}
                className="flex-1 bg-transparent resize-none text-white placeholder-white/25 text-sm focus:outline-none leading-relaxed"
                style={{ maxHeight: '160px' }}
              />
              <button
                onClick={() => handleSubmit()}
                disabled={!input.trim() || isLoading}
                className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center transition-all ${
                  input.trim() && !isLoading
                    ? `bg-gradient-to-br ${currentMode.color} text-white shadow-lg hover:scale-105`
                    : 'bg-white/[0.04] text-white/20 cursor-not-allowed'
                }`}
              >
                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </button>
            </div>

            <p className="text-center text-[10px] text-white/20 mt-2">
              Legal information only — not a substitute for a licensed advocate
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}

// ─── Suggested questions per concern ─────────────────────────────────────────
function getSuggestedQuestions(concern: string): string[] {
  const map: Record<string, string[]> = {
    'Criminal / FIR': [
      'Police refused to file my FIR. What can I do?',
      'Can I get anticipatory bail? How?',
      'What happens after an FIR is filed against me?',
    ],
    'Civil Dispute': [
      'My neighbour is encroaching on my land. What are my options?',
      'How do I file a civil suit? What are the steps?',
      'What is the time limit to file a case?',
    ],
    'Property / Land': [
      'Seller is refusing to register the property. What can I do?',
      'What documents should I check before buying land?',
      'How do I add a co-owner to my property?',
    ],
    'Family / Divorce': [
      'What are the grounds for divorce in India?',
      'How is custody of children decided?',
      'What is my wife\'s right in my property?',
    ],
    'Consumer Rights': [
      'The company is not refunding my money. What to do?',
      'How do I file a consumer complaint?',
      'Can I get compensation for mental harassment by a company?',
    ],
    'Labour / Employment': [
      'My employer is not paying my salary. What can I do?',
      'I was wrongfully terminated. Do I have a case?',
      'What is the minimum wage in my state?',
    ],
    'Cyber Crime': [
      'Someone is blackmailing me online. What should I do?',
      'My bank account was hacked. Who do I report to?',
      'Is posting someone\'s private photos online a crime?',
    ],
    'Motor Accident': [
      'I was hit by a vehicle. How do I claim compensation?',
      'The other driver has no insurance. Now what?',
      'What is the time limit for a motor accident claim?',
    ],
  };
  return map[concern] || [
    'What are my basic legal rights as a citizen?',
    'How do I file a complaint in court?',
    'What is the difference between civil and criminal cases?',
  ];
}

// ─── Root component ───────────────────────────────────────────────────────────
export default function YourLawyerPage() {
  const [profile, setProfile] = useState<ClientProfile | null>(null);

  if (!profile) {
    return <OnboardingScreen onStart={setProfile} />;
  }

  return <LawyerChat profile={profile} onReset={() => setProfile(null)} />;
}
