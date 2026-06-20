import React, { useState, useEffect } from 'react';
import { X, Settings2, Key, Cpu, Save } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (apiKey: string, model: string) => void;
  initialApiKey?: string;
  initialModel?: string;
}

const AVAILABLE_MODELS = [
  "Gemini 2.5 Flash",
  "Gemini 2.5 Flash Preview TTS",
  "Gemini 2.5 Flash-Lite",
  "Nano Banana",
  "Gemini 2.0 Flash",
  "Gemini 2.0 Flash 001",
  "Gemini 2.0 Flash-Lite 001",
  "Gemini 2.0 Flash-Lite",
  "Gemma 4 26B A4B IT",
  "Gemma 4 31B IT",
  "Gemini Flash Latest",
  "Gemini Flash-Lite Latest",
  "Gemini 3 Flash Preview",
  "Gemini 3.1 Flash Lite Preview",
  "Gemini 3.1 Flash Lite",
  "Nano Banana 2",
  "Gemini 3.5 Flash",
  "Lyria 3 Clip Preview",
  "Gemini 3.1 Flash TTS Preview",
  "Gemini Robotics-ER 1.5 Preview",
  "Gemini Robotics-ER 1.6 Preview",
  "Gemini 2.5 Computer Use Preview 10-2025",
  "Antigravity Agent Preview",
  // Premium / Pro Models
  "Gemini 2.5 Pro",
  "Gemini 2.5 Pro Preview TTS",
  "Gemini Pro Latest",
  "Gemini 3 Pro Preview",
  "Gemini 3.1 Pro Preview",
  "Gemini 3.1 Pro Preview Custom Tools",
  "Nano Banana Pro",
  "Lyria 3 Pro Preview",
  "Deep Research Pro Preview (Dec-12-2025)",
  "Deep Research Max Preview (Apr-21-2026)",
  "Deep Research Preview (Apr-21-2026)"
];

export function SettingsModal({ isOpen, onClose, onSave, initialApiKey = '', initialModel = 'Gemini 2.5 Flash' }: SettingsModalProps) {
  const [apiKey, setApiKey] = useState(initialApiKey);
  const [model, setModel] = useState(initialModel);

  useEffect(() => {
    if (isOpen) {
      setApiKey(initialApiKey);
      setModel(initialModel || 'Gemini 2.5 Flash');
    }
  }, [isOpen, initialApiKey, initialModel]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      {/* Modal Container */}
      <div className="relative w-full max-w-md bg-[#0f0f12] border border-white/10 rounded-2xl shadow-2xl shadow-violet-500/10 overflow-hidden">
        {/* Top Gradient */}
        <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-violet-500 via-fuchsia-500 to-violet-500" />
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/5">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-violet-500/10 flex items-center justify-center border border-violet-500/20">
              <Settings2 className="w-4 h-4 text-violet-400" />
            </div>
            <h2 className="text-lg font-semibold text-white tracking-tight">AI Settings</h2>
          </div>
          <button 
            onClick={onClose}
            className="p-2 text-white/40 hover:text-white/80 hover:bg-white/5 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Info banner */}
          <div className="px-4 py-3 bg-violet-500/5 border border-violet-500/10 rounded-xl">
            <p className="text-xs text-violet-300/80 leading-relaxed">
              If the default AI is unavailable or you want to use a specific model, enter your custom API Key and select your preferred model below.
            </p>
          </div>

          {/* Model Selection */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-medium text-white/80 ml-1">
              <Cpu className="w-4 h-4 text-white/40" />
              Model Destination
            </label>
            <div className="relative">
              <select 
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full appearance-none bg-[#16161a] border border-white/10 hover:border-white/20 focus:border-violet-500/50 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-violet-500/20 transition-all"
              >
                {AVAILABLE_MODELS.map(m => (
                  <option key={m} value={m} className="bg-[#16161a] text-white py-2">{m}</option>
                ))}
              </select>
              <div className="absolute inset-y-0 right-4 flex items-center pointer-events-none">
                <svg className="w-4 h-4 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
              </div>
            </div>
          </div>

          {/* API Key */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-medium text-white/80 ml-1">
              <Key className="w-4 h-4 text-white/40" />
              Custom API Key
            </label>
            <input 
              type="password" 
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter API Key (Optional)"
              className="w-full bg-[#16161a] border border-white/10 hover:border-white/20 focus:border-violet-500/50 rounded-xl px-4 py-3 text-sm text-white placeholder-white/20 focus:outline-none focus:ring-2 focus:ring-violet-500/20 transition-all"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-white/[0.02] border-t border-white/5 flex justify-end gap-3">
          <button 
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-white/60 hover:text-white hover:bg-white/5 rounded-xl transition-all"
          >
            Cancel
          </button>
          <button 
            onClick={() => {
              onSave(apiKey, model);
              onClose();
            }}
            className="flex items-center gap-2 px-5 py-2 text-sm font-medium text-white bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 rounded-xl shadow-lg shadow-violet-500/25 hover:shadow-violet-500/40 transition-all"
          >
            <Save className="w-4 h-4" />
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
}
