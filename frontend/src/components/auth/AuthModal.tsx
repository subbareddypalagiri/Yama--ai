'use client';

import React, { useState, useEffect } from 'react';
import {
  X, Mail, Lock, User, Shield, CheckCircle2, AlertCircle,
  Loader2, Sparkles, Scale, LogOut, ArrowRight
} from 'lucide-react';
import { supabase, isSupabaseConfigured } from '@/lib/supabase';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAuthSuccess?: (user: any) => void;
}

export default function AuthModal({ isOpen, onClose, onAuthSuccess }: AuthModalProps) {
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<'citizen' | 'advocate'>('citizen');
  const [barId, setBarId] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [currentUser, setCurrentUser] = useState<any>(null);

  useEffect(() => {
    // Check active session
    if (isSupabaseConfigured) {
      supabase.auth.getSession().then(({ data: { session } }) => {
        setCurrentUser(session?.user || null);
      });

      const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
        setCurrentUser(session?.user || null);
      });

      return () => subscription.unsubscribe();
    } else {
      // Local fallback user
      const localUser = localStorage.getItem('yama_auth_user');
      if (localUser) {
        try {
          setCurrentUser(JSON.parse(localUser));
        } catch {}
      }
    }
  }, []);

  if (!isOpen) return null;

  const handleEmailSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    setLoading(true);
    setMessage(null);

    try {
      if (isSupabaseConfigured) {
        const { error } = await supabase.auth.signInWithOtp({
          email,
          options: {
            data: {
              full_name: fullName,
              role,
              bar_council_id: role === 'advocate' ? barId : undefined,
            },
            emailRedirectTo: typeof window !== 'undefined' ? window.location.origin : undefined,
          },
        });
        if (error) throw error;
        setMessage({
          type: 'success',
          text: `Magic sign-in link sent to ${email}! Check your inbox to sign in instantly.`,
        });
      } else {
        // Local simulation when Supabase keys are pending
        await new Promise((r) => setTimeout(r, 600));
        const dummyUser = {
          id: 'user_' + Math.random().toString(36).substring(2, 9),
          email,
          user_metadata: {
            full_name: fullName || email.split('@')[0],
            role,
            bar_council_id: barId,
          },
        };
        localStorage.setItem('yama_auth_user', JSON.stringify(dummyUser));
        setCurrentUser(dummyUser);
        setMessage({
          type: 'success',
          text: `Signed in as ${dummyUser.email} (Local session active. Sync enabled).`,
        });
        if (onAuthSuccess) onAuthSuccess(dummyUser);
        setTimeout(() => onClose(), 1500);
      }
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Authentication failed' });
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    setLoading(true);
    try {
      if (isSupabaseConfigured) {
        await supabase.auth.signOut();
      }
      localStorage.removeItem('yama_auth_user');
      setCurrentUser(null);
      setMessage({ type: 'success', text: 'Signed out successfully.' });
      setTimeout(() => onClose(), 1200);
    } catch (e: any) {
      setMessage({ type: 'error', text: e.message || 'Sign out failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="relative w-full max-w-md rounded-3xl bg-[#0c0e14] border border-amber-500/40 shadow-2xl p-6 sm:p-8 text-white">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/[0.08]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#d4af37] via-[#f59e0b] to-[#78350f] p-[1.2px] shadow-lg shadow-amber-500/20">
              <div className="w-full h-full rounded-[10px] bg-[#0c0e14] flex items-center justify-center">
                <Scale className="w-5 h-5 text-amber-400" />
              </div>
            </div>
            <div>
              <h3 className="text-base font-bold text-white tracking-tight">
                {currentUser ? 'Your Advocate Account' : 'Sign in to YAMA AI'}
              </h3>
              <p className="text-[11px] text-neutral-400">
                Multi-Device Cloud Sync &amp; Case Diary
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-neutral-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Message Banner */}
        {message && (
          <div
            className={`mt-4 p-3 rounded-xl border text-xs flex items-start gap-2 ${
              message.type === 'success'
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                : 'bg-red-500/10 border-red-500/30 text-red-300'
            }`}
          >
            {message.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            )}
            <span>{message.text}</span>
          </div>
        )}

        {currentUser ? (
          /* Logged In View */
          <div className="mt-6 space-y-5">
            <div className="p-4 rounded-2xl bg-[#11131c] border border-white/[0.08]">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-300 font-bold text-sm">
                  {currentUser.email?.charAt(0).toUpperCase()}
                </div>
                <div>
                  <h4 className="font-bold text-white text-sm">
                    {currentUser.user_metadata?.full_name || currentUser.email?.split('@')[0]}
                  </h4>
                  <p className="text-xs text-neutral-400 font-mono">{currentUser.email}</p>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs pt-2 border-t border-white/[0.04]">
                <span className="text-neutral-500">Account Role:</span>
                <span className="font-mono font-bold text-amber-300 uppercase">
                  {currentUser.user_metadata?.role || 'Citizen'}
                </span>
              </div>
              {currentUser.user_metadata?.bar_council_id && (
                <div className="flex items-center justify-between text-xs pt-1">
                  <span className="text-neutral-500">Bar Enrollment:</span>
                  <span className="font-mono text-neutral-300">
                    {currentUser.user_metadata.bar_council_id}
                  </span>
                </div>
              )}
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleSignOut}
                disabled={loading}
                className="w-full py-2.5 rounded-xl border border-red-500/30 hover:bg-red-500/10 text-red-300 text-xs font-bold flex items-center justify-center gap-2 transition-colors cursor-pointer"
              >
                <LogOut className="w-4 h-4" />
                Sign Out
              </button>
              <button
                onClick={onClose}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black text-xs font-bold transition-all shadow-md cursor-pointer"
              >
                Continue
              </button>
            </div>
          </div>
        ) : (
          /* Sign In Form */
          <form onSubmit={handleEmailSignIn} className="mt-5 space-y-4">
            <div>
              <label className="text-[11px] font-mono text-neutral-400 block mb-1.5 uppercase font-medium">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="advocate@example.com or user@gmail.com"
                  className="w-full pl-10 pr-4 py-2.5 bg-[#12141c] border border-white/10 rounded-xl text-white placeholder-neutral-500 text-sm focus:outline-none focus:border-amber-400/80 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="text-[11px] font-mono text-neutral-400 block mb-1.5 uppercase font-medium">
                Full Name / Firm Name
              </label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="K. Subba Reddy"
                  className="w-full pl-10 pr-4 py-2.5 bg-[#12141c] border border-white/10 rounded-xl text-white placeholder-neutral-500 text-sm focus:outline-none focus:border-amber-400/80 transition-colors"
                />
              </div>
            </div>

            {/* Role Switcher */}
            <div>
              <label className="text-[11px] font-mono text-neutral-400 block mb-1.5 uppercase font-medium">
                Profile Type
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setRole('citizen')}
                  className={`py-2 px-3 rounded-xl border text-xs font-semibold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                    role === 'citizen'
                      ? 'bg-amber-500/15 border-amber-500/40 text-amber-300'
                      : 'bg-white/[0.02] border-white/10 text-neutral-400 hover:text-white'
                  }`}
                >
                  <User className="w-3.5 h-3.5" />
                  Citizen / Litigant
                </button>
                <button
                  type="button"
                  onClick={() => setRole('advocate')}
                  className={`py-2 px-3 rounded-xl border text-xs font-semibold flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                    role === 'advocate'
                      ? 'bg-amber-500/15 border-amber-500/40 text-amber-300'
                      : 'bg-white/[0.02] border-white/10 text-neutral-400 hover:text-white'
                  }`}
                >
                  <Shield className="w-3.5 h-3.5" />
                  Practicing Advocate
                </button>
              </div>
            </div>

            {role === 'advocate' && (
              <div>
                <label className="text-[11px] font-mono text-neutral-400 block mb-1.5 uppercase font-medium">
                  State Bar Council Enrollment Number
                </label>
                <input
                  type="text"
                  value={barId}
                  onChange={(e) => setBarId(e.target.value)}
                  placeholder="e.g. AP/1234/2021"
                  className="w-full px-4 py-2.5 bg-[#12141c] border border-white/10 rounded-xl text-white placeholder-neutral-500 text-sm focus:outline-none focus:border-amber-400/80 transition-colors uppercase font-mono"
                />
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !email.trim()}
              className="w-full mt-2 py-3 rounded-xl bg-gradient-to-r from-amber-500 via-amber-400 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black font-extrabold text-sm flex items-center justify-center gap-2 shadow-lg shadow-amber-500/25 transition-all disabled:opacity-40 cursor-pointer"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin text-black" />
              ) : (
                <Sparkles className="w-4 h-4" />
              )}
              Sign In with Magic Link
            </button>

            <p className="text-[11px] text-neutral-500 text-center pt-2">
              Passwordless &amp; secure via Supabase Auth. Your legal notices &amp; cases sync automatically.
            </p>
          </form>
        )}
      </div>
    </div>
  );
}
