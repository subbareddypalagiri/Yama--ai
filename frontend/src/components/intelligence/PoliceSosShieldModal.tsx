'use client';

import React, { useState } from 'react';
import { ShieldAlert, Volume2, VolumeX, PhoneCall, X, UserCheck, AlertTriangle, Scale, Check, Copy } from 'lucide-react';

interface PoliceSosShieldModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultState?: string;
}

export default function PoliceSosShieldModal({
  isOpen,
  onClose,
  defaultState = 'Andhra Pradesh',
}: PoliceSosShieldModalProps) {
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState<'english' | 'telugu'>('english');
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const englishRightsScript = `OFFICIAL CITIZEN RIGHTS & STATUTORY POLICE SHIELD
UNDER BHARATIYA NAGARIK SURAKSHA SANHITA, 2023 (BNSS) & CONSTITUTION OF INDIA

1. RIGHT TO NOTICE OF APPEARANCE (SECTION 35 BNSS / ARNESH KUMAR MANDATE):
   "Officer, under Section 35 of the BNSS, 2023, for any offense punishable with imprisonment up to 7 years, the police CANNOT arrest directly. You are statutorily required to issue a formal Notice of Appearance. An arrest made without satisfying Section 35(1) constitutes contempt of court."

2. WOMEN ARREST RESTRICTION (SECTION 43(5) BNSS):
   "No woman can be arrested between SUNSET and SUNRISE without the prior written permission of a Judicial Magistrate of the First Class. Furthermore, only a female police officer may effectuate the arrest."

3. RIGHT TO GROUNDS & LEGAL COUNSEL (ARTICLE 22(1) CONSTITUTION):
   "I have a fundamental constitutional right to be informed of the exact grounds of detention and to consult my designated advocate immediately."

4. ARREST MEMO & FAMILY INTIMATION (D.K. BASU SUPREME COURT MANDATE):
   "You must prepare an Arrest Memo attested by an independent witness and immediately inform my family/friend within 8 hours."

5. 24-HOUR MAGISTRATE PRODUCTION (ARTICLE 22(2) & SECTION 58 BNSS):
   "I must be produced before the nearest Judicial Magistrate within 24 hours of arrest, excluding travel time."`;

  const teluguRightsScript = `భారత పౌర హక్కులు & పోలీస్ అరెస్ట్ రక్షణ చట్టం (BNSS 2023 & రాజ్యాంగం)

1. నేరుగా అరెస్ట్ చేయకూడదు (సెక్షన్ 35 BNSS - ఆర్నేష్ కుమార్ సుప్రీంకోర్టు తీర్పు):
   "ఆఫీసర్ గారూ, 7 సంవత్సరాల లోపు శిక్ష పడే కేసుల్లో పోలీసు నేరుగా అరెస్ట్ చేయకూడదు. నాకు చట్టబద్ధమైన నోటీస్ (Notice of Appearance) మాత్రమే ఇవ్వాలి. నోటీస్ ఇవ్వకుండా అరెస్ట్ చేయడం సుప్రీంకోర్టు నిబంధనల ఉల్లంఘన."

2. మహిళల అరెస్ట్ రక్షణ (సెక్షన్ 43(5) BNSS):
   "సూర్యాస్తమయం (Sunset) తర్వాత లేదా సూర్యోదయం (Sunrise) కంటే ముందు మహిళను జ్యుడీషియల్ మేజిస్ట్రేట్ లిఖితపూర్వక అనుమతి లేకుండా అరెస్ట్ చేయకూడదు. మహిళా పోలీస్ మాత్రమే అరెస్ట్ చేయాలి."

3. అరెస్ట్ కారణం & లాయర్ హక్కు (ఆర్టికల్ 22(1)):
   "నన్ను ఏ కారణంతో అదుపులోకి తీసుకుంటున్నారో చెప్పాలి. నా అడ్వకేట్ తో వెంటనే మాట్లాడే ప్రాథమిక హక్కు నాకు రాజ్యాంగం ఇచ్చింది."

4. 24 గంటల్లో మేజిస్ట్రేట్ ముందు హాజరుపరచాలి (సెక్షన్ 58 BNSS):
   "అరెస్ట్ చేసిన 24 గంటల లోపు సమీప మేజిస్ట్రేట్ ముందు హాజరుపరచడం పోలీసు తప్పనిసరి కర్తవ్యం."`;

  const handleSpeak = () => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) return;
    if (isPlayingAudio) {
      window.speechSynthesis.cancel();
      setIsPlayingAudio(false);
      return;
    }

    window.speechSynthesis.cancel();
    const scriptToSpeak =
      selectedLanguage === 'telugu'
        ? "ఆఫీసర్ గారూ, భారత చట్టం సెక్షన్ 35 బి ఎన్ ఎస్ ఎస్ ప్రకారం, 7 సంవత్సరాల లోపు శిక్ష ఉండే కేసుల్లో పౌరుడిని నేరుగా అరెస్ట్ చేయకూడదు. నోటీస్ ఆఫ్ అప్పియరెన్స్ మాత్రమే ఇవ్వాలి. సుప్రీంకోర్టు ఆర్నేష్ కుమార్ మార్గదర్శకాల ప్రకారం చట్టబద్ధంగా వ్యవహరించండి."
        : "Officer, under Section 35 of Bharatiya Nagarik Suraksha Sanhita, 2023, you cannot arrest directly for offenses punishable under 7 years. You must issue a statutory Notice of Appearance. Please respect constitutional Article 22.";

    const utterance = new SpeechSynthesisUtterance(scriptToSpeak);
    utterance.rate = 0.95;
    utterance.onend = () => setIsPlayingAudio(false);
    utterance.onerror = () => setIsPlayingAudio(false);
    setIsPlayingAudio(true);
    window.speechSynthesis.speak(utterance);
  };

  const handleCopy = () => {
    const text = selectedLanguage === 'english' ? englishRightsScript : teluguRightsScript;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 font-sans">
      <div className="bg-[#110e14] border border-red-500/30 w-full max-w-2xl rounded-3xl p-6 shadow-2xl relative max-h-[92vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/[0.08]">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-red-600 to-rose-600 flex items-center justify-center shadow-lg shadow-red-500/30 animate-pulse">
              <ShieldAlert className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>1-Tap Police Interrogation &amp; Arrest Shield</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-500/20 text-red-300 border border-red-500/30">
                  BNSS SEC 35 &amp; ART 22
                </span>
              </h3>
              <p className="text-xs text-white/40">Immediate Legal Rights &amp; Advocate Voice Announcement to Police</p>
            </div>
          </div>
          <button
            onClick={() => {
              if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
                window.speechSynthesis.cancel();
              }
              onClose();
            }}
            className="p-1.5 rounded-xl text-white/40 hover:text-white hover:bg-white/[0.06] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Action Bar */}
        <div className="my-3 flex flex-wrap items-center justify-between gap-2 p-3 rounded-2xl bg-red-500/10 border border-red-500/25">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSelectedLanguage('english')}
              className={`px-3 py-1 rounded-xl text-xs font-bold transition-all ${
                selectedLanguage === 'english' ? 'bg-red-500 text-white' : 'text-white/60 hover:text-white'
              }`}
            >
              English Script
            </button>
            <button
              onClick={() => setSelectedLanguage('telugu')}
              className={`px-3 py-1 rounded-xl text-xs font-bold transition-all ${
                selectedLanguage === 'telugu' ? 'bg-red-500 text-white' : 'text-white/60 hover:text-white'
              }`}
            >
              తెలుగు స్క్రిప్ట్
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleSpeak}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all shadow-md ${
                isPlayingAudio
                  ? 'bg-amber-500 text-black animate-pulse'
                  : 'bg-gradient-to-r from-red-600 to-rose-600 text-white hover:brightness-110'
              }`}
              title="Play Advocate Rights Announcement to Police"
            >
              {isPlayingAudio ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              <span>{isPlayingAudio ? 'Stop Voice' : 'Advocate Voice Play'}</span>
            </button>

            <button
              onClick={handleCopy}
              className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-white/[0.05] border border-white/[0.1] text-xs text-white/80 hover:text-white"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>
        </div>

        {/* Rights Content Scroll */}
        <div className="flex-1 overflow-y-auto space-y-3 pr-1">
          <div className="p-4 rounded-2xl bg-black/40 border border-white/[0.08] font-mono text-xs text-white/90 leading-relaxed whitespace-pre-wrap select-all">
            {selectedLanguage === 'english' ? englishRightsScript : teluguRightsScript}
          </div>

          {/* Emergency Hotlines Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
            <a
              href="tel:112"
              className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06] hover:border-red-500/30 flex items-center justify-between"
            >
              <span className="text-white/70 font-semibold">Police Emergency</span>
              <span className="font-bold text-red-400 font-mono">112</span>
            </a>
            <a
              href="tel:1090"
              className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06] hover:border-pink-500/30 flex items-center justify-between"
            >
              <span className="text-white/70 font-semibold">Women Helpline</span>
              <span className="font-bold text-pink-400 font-mono">1090 / 181</span>
            </a>
            <a
              href="tel:15100"
              className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06] hover:border-blue-500/30 flex items-center justify-between col-span-2 sm:col-span-1"
            >
              <span className="text-white/70 font-semibold">Free Legal Aid (NALSA)</span>
              <span className="font-bold text-blue-400 font-mono">15100</span>
            </a>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-white/[0.08] flex items-center justify-between text-xs text-white/40">
          <span>Protected under Supreme Court judgment in Arnesh Kumar v. State of Bihar.</span>
          <button
            onClick={() => {
              if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
                window.speechSynthesis.cancel();
              }
              onClose();
            }}
            className="px-4 py-1.5 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] text-white font-medium text-xs transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
