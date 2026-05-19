'use client';

import { useState, useRef, KeyboardEvent } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowUp, Loader2, Paperclip, X, FileText, Image as ImageIcon, File, Sparkles } from 'lucide-react';
import { useLanguage } from '@/context/LanguageContext';

interface AttachedFile {
  file: File;
  id: string;
  preview?: string;
}

export default function LegalChatInput() {
  const { t, language } = useLanguage();
  
  // Examples in different languages
  const EXAMPLES: Record<string, string[]> = {
    en: [
      'Someone hacked my Instagram account',
      'My employer didn\'t pay my salary',
      'Landlord won\'t return security deposit',
      'Received fake product online',
      'Friend borrowed money, won\'t return',
    ],
    hi: [
      'किसी ने मेरा इंस्टाग्राम अकाउंट हैक कर लिया',
      'मेरे मालिक ने मेरी सैलरी नहीं दी',
      'मकान मालिक सिक्योरिटी डिपॉजिट नहीं लौटा रहा',
      'ऑनलाइन नकली प्रोडक्ट मिला',
      'दोस्त ने पैसे उधार लिए, वापस नहीं कर रहा',
    ],
    ta: [
      'யாரோ என் இன்ஸ்டாகிராம் கணக்கை ஹேக் செய்தார்கள்',
      'என் முதலாளி எனக்கு சம்பளம் தரவில்லை',
      'வீட்டு உரிமையாளர் பாதுகாப்பு வைப்புத்தொகையை திருப்பித் தரவில்லை',
      'ஆன்லைனில் போலி பொருள் கிடைத்தது',
      'நண்பர் கடன் வாங்கினார், திருப்பித் தரவில்லை',
    ],
    te: [
      'ఎవరో నా ఇన్‌స్టాగ్రామ్ ఖాతాను హ్యాక్ చేశారు',
      'నా యజమాని నాకు జీతం ఇవ్వలేదు',
      'ఇంటి యజమాని సెక్యూరిటీ డిపాజిట్ తిరిగి ఇవ్వడం లేదు',
      'ఆన్‌లైన్‌లో నకిలీ ఉత్పత్తి వచ్చింది',
      'స్నేహితుడు డబ్బు అప్పు తీసుకున్నాడు, తిరిగి ఇవ్వడం లేదు',
    ],
    'roman_en': [
      'Kisi ne mere Instagram account ko hack kar diya',
      'Mere employer ne mujhe salary nahi diya',
      'Landlord security deposit nahi de raha',
      'Online fake product mila',
      'Dost ne paisa udhar liya, wapas nahi de raha',
    ],
  };

  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [attachments, setAttachments] = useState<AttachedFile[]>([]);
  const [isFocused, setIsFocused] = useState(false);
  const [responseLanguage, setResponseLanguage] = useState<'auto' | 'english' | 'hindi' | 'tamil' | 'telugu' | 'kannada' | 'roman_english'>('auto');
  const router = useRouter();
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = () => {
    const text = query.trim();
    if (!text || loading) return;
    setLoading(true);
    if (attachments.length > 0) {
      const fileInfo = attachments.map(a => ({ name: a.file.name, type: a.file.type, size: a.file.size }));
      sessionStorage.setItem('pendingAttachments', JSON.stringify(fileInfo));
    }
    const params = new URLSearchParams({
      q: text,
      responseLanguage: responseLanguage !== 'auto' ? responseLanguage : 'english',
    });
    router.push(`/chat?${params.toString()}`);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const newAttachments: AttachedFile[] = files.map(file => ({
      file,
      id: Math.random().toString(36).slice(2),
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined,
    }));
    setAttachments(prev => [...prev, ...newAttachments].slice(0, 5));
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const removeAttachment = (id: string) => {
    setAttachments(prev => {
      const removed = prev.find(a => a.id === id);
      if (removed?.preview) URL.revokeObjectURL(removed.preview);
      return prev.filter(a => a.id !== id);
    });
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return <ImageIcon className="w-4 h-4" />;
    if (type.includes('pdf') || type.includes('document')) return <FileText className="w-4 h-4" />;
    return <File className="w-4 h-4" />;
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setQuery(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
  };

  const handleExample = (text: string) => {
    setQuery(text);
    textareaRef.current?.focus();
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  };

  const currentExamples = EXAMPLES[language] || EXAMPLES.en;

  return (
    <div className="w-full max-w-2xl mx-auto px-4">
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Language selector */}
      <div className="mb-4 flex items-center gap-3">
        <label className="text-xs text-white/50 uppercase tracking-wider">Response Language:</label>
        <select
          value={responseLanguage}
          onChange={(e) => setResponseLanguage(e.target.value as any)}
          className="px-3 py-1.5 rounded-lg bg-white/[0.05] border border-white/[0.1] text-white/80 text-sm hover:bg-white/[0.08] transition-colors focus:outline-none focus:border-purple-500/40"
        >
          <option value="auto">Auto (Default)</option>
          <option value="english">English</option>
          <option value="hindi">हिंदी (Hindi)</option>
          <option value="tamil">தமிழ் (Tamil)</option>
          <option value="telugu">తెలుగు (Telugu)</option>
          <option value="kannada">ಕನ್ನಡ (Kannada)</option>
          <option value="roman_english">Hinglish (Roman)</option>
        </select>
      </div>

      {/* Main input container with premium glow */}
      <div 
        className={`relative rounded-3xl transition-all duration-500 ${
          isFocused 
            ? 'shadow-[0_0_0_1px_rgba(168,85,247,0.5),0_0_60px_-10px_rgba(168,85,247,0.4),0_0_80px_-20px_rgba(236,72,153,0.3)]' 
            : 'shadow-[0_0_0_1px_rgba(255,255,255,0.06),0_8px_40px_-10px_rgba(0,0,0,0.6)]'
        }`}
        style={{
          background: 'linear-gradient(180deg, rgba(20,18,30,0.98) 0%, rgba(12,10,20,0.99) 100%)',
        }}
      >
        {/* Animated gradient border on focus */}
        {isFocused && (
          <div 
            className="absolute inset-0 rounded-3xl pointer-events-none animate-border-glow"
            style={{
              background: 'linear-gradient(135deg, rgba(168,85,247,0.3), rgba(236,72,153,0.3), rgba(249,115,22,0.3))',
              padding: '1px',
              mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
              maskComposite: 'exclude',
            }}
          />
        )}
        
        {/* Top highlight line */}
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-purple-500/40 to-transparent rounded-t-3xl" />
        
        {/* Attachments */}
        {attachments.length > 0 && (
          <div className="px-5 pt-4 pb-2">
            <div className="flex flex-wrap gap-2">
              {attachments.map((att) => (
                <div
                  key={att.id}
                  className="group flex items-center gap-2.5 bg-white/[0.03] hover:bg-white/[0.08] border border-white/[0.06] hover:border-purple-500/30 rounded-xl px-3 py-2 text-xs transition-all duration-300"
                >
                  {att.preview ? (
                    <img src={att.preview} alt="" className="w-8 h-8 rounded-lg object-cover" />
                  ) : (
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center text-purple-400">
                      {getFileIcon(att.file.type)}
                    </div>
                  )}
                  <span className="text-white/70 max-w-[100px] truncate">{att.file.name}</span>
                  <button
                    onClick={() => removeAttachment(att.id)}
                    className="opacity-0 group-hover:opacity-100 text-white/40 hover:text-red-400 transition-all"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Input area */}
        <div className="flex items-end gap-2 p-3">
          {/* Attach button with hover glow */}
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={loading || attachments.length >= 5}
            className="relative flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center text-white/30 hover:text-purple-400 hover:bg-purple-500/10 transition-all duration-300 disabled:opacity-30 group"
          >
            <div className="absolute inset-0 rounded-xl bg-purple-500/0 group-hover:bg-purple-500/10 transition-colors" />
            <Paperclip className="relative w-5 h-5" />
          </button>

          {/* Textarea */}
          <div className="flex-1 min-h-[44px] flex items-center">
            <textarea
              ref={textareaRef}
              value={query}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder={t.chat.placeholder}
              rows={1}
              disabled={loading}
              className="w-full resize-none bg-transparent text-[15px] text-white placeholder-white/30 focus:outline-none leading-relaxed py-2.5 max-h-[200px]"
            />
          </div>

          {/* Submit button with gradient glow */}
          <button
            onClick={handleSubmit}
            disabled={!query.trim() || loading}
            className={`relative flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300 overflow-hidden ${
              query.trim() && !loading
                ? 'text-white'
                : 'bg-white/[0.03] text-white/20'
            }`}
          >
            {query.trim() && !loading && (
              <>
                {/* Gradient background */}
                <div className="absolute inset-0 bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 opacity-90" />
                {/* Glow effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 blur-xl opacity-60" />
                {/* Hover brighten */}
                <div className="absolute inset-0 bg-white/0 hover:bg-white/10 transition-colors" />
              </>
            )}
            <div className="relative">
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <ArrowUp className="w-5 h-5" />
              )}
            </div>
          </button>
        </div>
      </div>

      {/* Keyboard hint with subtle styling */}
      <div className="flex items-center justify-center gap-4 mt-4 text-[11px] text-white/25">
        <span className="flex items-center gap-1.5">
          <kbd className="px-1.5 py-0.5 rounded bg-white/[0.03] border border-white/[0.08] font-mono">↵</kbd>
          <span>{t.chat.send}</span>
        </span>
        <span className="flex items-center gap-1.5">
          <kbd className="px-1.5 py-0.5 rounded bg-white/[0.03] border border-white/[0.08] font-mono">⇧↵</kbd>
          <span>new line</span>
        </span>
      </div>

      {/* Example prompts with hover glow */}
      <div className="mt-10">
        <div className="flex items-center justify-center gap-2 mb-5">
          <div className="relative">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <div className="absolute inset-0 blur-md bg-purple-500/50" />
          </div>
          <span className="text-[11px] font-semibold text-white/40 uppercase tracking-widest">Try asking</span>
        </div>
        <div className="flex flex-wrap justify-center gap-2.5">
          {currentExamples.map((ex, i) => (
            <button
              key={ex}
              onClick={() => handleExample(ex)}
              className="group relative px-4 py-2.5 rounded-full text-[13px] text-white/50 bg-white/[0.02] border border-white/[0.06] hover:text-white hover:border-purple-500/40 transition-all duration-300 overflow-hidden"
              style={{ animationDelay: `${i * 100}ms` }}
            >
              {/* Hover gradient background */}
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500/0 via-purple-500/10 to-pink-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <span className="relative">{ex}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
