'use client';

import React, { useState } from 'react';

interface SosShieldModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type Lang = 'english' | 'hindi' | 'telugu';

export default function SosShieldModal({ isOpen, onClose }: SosShieldModalProps) {
  const [lang, setLang] = useState<Lang>('english');
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const content = {
    english: {
      title: '🚨 EMERGENCY POLICE ENCOUNTER & ARREST RIGHTS SHIELD',
      subtitle: 'Official Statutory Safeguards under Bharatiya Nagarik Suraksha Sanhita (BNSS 2023) & Supreme Court D.K. Basu Mandates.',
      cards: [
        {
          code: 'Section 35 BNSS, 2023',
          title: 'Mandatory Notice Before Arrest & Grounds',
          body: 'Police CANNOT arrest arbitrarily without written notice under Section 35(3) for offenses punishable under 7 years where you cooperate with inquiry. You have the absolute right to know full grounds of arrest immediately.',
        },
        {
          code: 'Supreme Court Mandate (D.K. Basu v. State of WB)',
          title: 'Right to Inspection Memo & Family Notification',
          body: 'Every arresting officer MUST wear clear name tags, prepare an Arrest Memo signed by at least one family member/witness, and notify a relative or friend immediately upon arrest or detention.',
        },
        {
          code: 'Section 482 BNSS, 2023 (Old CrPC 438)',
          title: 'Immediate Right to Anticipatory Bail & Lawyer',
          body: 'You have the right to consult an advocate of your choice during interrogation. If threatened with arbitrary arrest, High Court / Sessions Court grants immediate Anticipatory Bail protection.',
        },
        {
          code: 'Section 173 BNSS, 2023',
          title: 'Zero FIR & E-FIR Registration Mandate',
          body: 'If local police refuse to register your complaint, Section 173(1) allows electronic filing (E-FIR) or Zero FIR at any police station regardless of jurisdiction, mandating immediate SP intervention.',
        },
      ],
      sosContact: 'National Emergency Helpline: 112 | Cyber Helpline: 1930',
      actionPrompt: 'Show this screen directly to law enforcement officials if threatened or detained without formal warrant.',
    },
    hindi: {
      title: '🚨 आपातकालीन पुलिस अधिकार और गिरफ्तारी सुरक्षा कवच (SOS SHIELD)',
      subtitle: 'भारतीय नागरिक सुरक्षा संहिता (BNSS 2023) और सर्वोच्च न्यायालय (D.K. Basu) के वैधानिक अधिकार।',
      cards: [
        {
          code: 'धारा 35 BNSS, 2023',
          title: 'गिरफ्तारी से पहले अनिवार्य नोटिस और कारण जानना',
          body: '7 साल से कम सजा वाले मामलों में पुलिस बिना लिखित नोटिस (धारा 35-3) के मनमाने ढंग से गिरफ्तार नहीं कर सकती। आपको गिरफ्तारी का स्पष्ट कारण जानने का पूर्ण कानूनी अधिकार है।',
        },
        {
          code: 'सुप्रीम कोर्ट निर्देश (D.K. Basu केस)',
          title: 'अरेस्ट मेमो और परिवार को सूचना का अधिकार',
          body: 'पुलिस अधिकारी की नेमप्लेट स्पष्ट होनी चाहिए। गिरफ्तारी के समय अरेस्ट मेमो बनाना अनिवार्य है जिस पर परिवार के सदस्य के हस्ताक्षर होंगे और तुरंत किसी रिश्तेदार को सूचना देनी होगी।',
        },
        {
          code: 'धारा 482 BNSS, 2023 (पुराना CrPC 438)',
          title: 'अग्रिम जमानत (Anticipatory Bail) और वकील का अधिकार',
          body: 'पूछताछ के दौरान आपको अपने पसंद के वकील से परामर्श करने का अधिकार है। अवैध गिरफ्तारी की धमकी पर हाई कोर्ट या सत्र न्यायालय से तुरंत अग्रिम जमानत ली जा सकती है।',
        },
        {
          code: 'धारा 173 BNSS, 2023',
          title: 'जीरो FIR और E-FIR पंजीकरण का अधिकार',
          body: 'यदि स्थानीय पुलिस शिकायत दर्ज करने से मना करती है, तो धारा 173(1) के तहत इलेक्ट्रॉनिक माध्यम (E-FIR) या किसी भी पुलिस स्टेशन में जीरो FIR दर्ज कराने का अधिकार है।',
        },
      ],
      sosContact: 'राष्ट्रीय आपातकालीन नंबर: 112 | साइबर हेल्पलाइन: 1930',
      actionPrompt: 'बिना वारंट या अवैध पूछताछ के समय यह स्क्रीन सीधे पुलिस अधिकारी को दिखाएं।',
    },
    telugu: {
      title: '🚨 అత్యవసర పోలీసు & అరెస్ట్ రక్షణ కవచం (SOS SHIELD)',
      subtitle: 'భారతీయ నాగరిక్ సురక్షా సంహిత (BNSS 2023) & సుప్రీంకోర్టు D.K. బసు తీర్పుల ప్రకారం మీ చట్టపరమైన హక్కులు.',
      cards: [
        {
          code: 'సెక్షన్ 35 BNSS, 2023',
          title: 'అరెస్ట్‌కు ముందు నోటీసు & కారణాలు తెలుసుకునే హక్కు',
          body: '7 సంవత్సరాల లోపు శిక్ష పడే కేసుల్లో విచారణకు సహకరిస్తే, రాతపూర్వక నోటీసు లేకుండా పోలీసులు ఇష్టానుసారంగా అరెస్ట్ చేయకూడదు. అరెస్ట్‌కు గల పూర్తి కారణాలను వెంటనే తెలుసుకునే హక్కు మీకు ఉంది.',
        },
        {
          code: 'సుప్రీంకోర్టు ఆదేశాలు (D.K. బసు తీర్పు)',
          title: 'అరెస్ట్ మెమో & కుటుంబ సభ్యులకు సమాచారం',
          body: 'పోలీసుల నేమ్‌ప్లేట్ స్పష్టంగా ఉండాలి. అరెస్ట్ సమయంలో కుటుంబ సభ్యుడి సంతకంతో అరెస్ట్ మెమో తయారు చేయాలి మరియు వెంటనే మీ బంధువులు లేదా స్నేహితులకు సమాచారం అందించాలి.',
        },
        {
          code: 'సెక్షన్ 482 BNSS, 2023 (పాత CrPC 438)',
          title: 'ముందస్తు బెయిల్ & న్యాయవాదిని సంప్రదించే హక్కు',
          body: 'విచారణ సమయంలో మీ న్యాయవాదిని సంప్రదించే హక్కు మీకు ఉంది. అక్రమ అరెస్ట్ ముప్పు ఉంటే సెషన్స్ కోర్టు లేదా హైకోర్టు ద్వారా వెంటనే ముందస్తు బెయిల్ (Anticipatory Bail) పొందవచ్చు.',
        },
        {
          code: 'సెక్షన్ 173 BNSS, 2023',
          title: 'జీరో FIR & ఈ-FIR నమోదు హక్కు',
          body: 'స్థానిక పోలీసులు ఫిర్యాదు తీసుకోవడానికి నిరాకరిస్తే, సెక్షన్ 173(1) ప్రకారం ఆన్‌లైన్ ద్వారా E-FIR లేదా ఏ పోలీస్ స్టేషన్‌లోనైనా జీరో FIR నమోదు చేయవచ్చు.',
        },
      ],
      sosContact: 'జాతీయ అత్యవసర నంబర్: 112 | సైబర్ హెల్ప్‌లైన్: 1930',
      actionPrompt: 'అక్రమంగా నిర్బంధించినా లేదా విచారణ పేరిట ఇబ్బంది పెట్టినా ఈ స్క్రీన్‌ను నేరుగా అధికారులకు చూపించండి.',
    },
  };

  const current = content[lang];

  const handleCopyText = () => {
    const textToCopy = `${current.title}\n${current.subtitle}\n\n` +
      current.cards.map(c => `[${c.code}] ${c.title}\n${c.body}`).join('\n\n') +
      `\n\n${current.sosContact}`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-rose-950/90 backdrop-blur-xl animate-fadeIn">
      <div className="relative w-full max-w-4xl max-h-[92vh] rounded-3xl bg-slate-950 border-2 border-rose-500 shadow-[0_0_100px_rgba(244,63,94,0.4)] flex flex-col overflow-hidden">
        {/* Urgent Header Banner */}
        <div className="p-6 bg-gradient-to-r from-rose-600 via-red-600 to-rose-700 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-rose-400/40">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-2xl bg-white text-rose-600 font-black text-2xl flex items-center justify-center shadow-xl animate-pulse">
              🚨
            </div>
            <div>
              <h2 className="text-xl sm:text-2xl font-black text-white tracking-wide leading-tight">
                {current.title}
              </h2>
              <p className="text-xs sm:text-sm text-rose-100 font-medium mt-0.5">
                {current.subtitle}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2 self-end sm:self-auto">
            {/* Language Selector */}
            <div className="flex rounded-xl bg-slate-900/80 p-1 border border-rose-400/40">
              <button
                onClick={() => setLang('english')}
                className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${lang === 'english' ? 'bg-rose-600 text-white shadow-md' : 'text-slate-300'}`}
              >
                ENG
              </button>
              <button
                onClick={() => setLang('hindi')}
                className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${lang === 'hindi' ? 'bg-rose-600 text-white shadow-md' : 'text-slate-300'}`}
              >
                हिन्दी
              </button>
              <button
                onClick={() => setLang('telugu')}
                className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${lang === 'telugu' ? 'bg-rose-600 text-white shadow-md' : 'text-slate-300'}`}
              >
                తెలుగు
              </button>
            </div>

            <button
              onClick={onClose}
              className="w-10 h-10 rounded-xl bg-slate-900/80 hover:bg-white text-white hover:text-rose-600 font-bold flex items-center justify-center text-lg transition-all"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Action Prompt flash banner */}
        <div className="bg-amber-500/20 border-b border-amber-500/40 px-6 py-2.5 flex items-center space-x-2 text-amber-300 text-xs sm:text-sm font-bold">
          <span>💡</span>
          <span>{current.actionPrompt}</span>
        </div>

        {/* Cards Grid */}
        <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          {current.cards.map((card, idx) => (
            <div
              key={idx}
              className="p-5 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-900/80 border border-rose-500/30 hover:border-rose-500/60 transition-all flex flex-col justify-between space-y-3 shadow-lg"
            >
              <div>
                <span className="inline-block px-2.5 py-1 rounded-lg bg-rose-500/20 border border-rose-500/40 text-[11px] font-mono font-bold text-rose-300 uppercase tracking-wider mb-2">
                  {card.code}
                </span>
                <h4 className="text-base font-black text-white leading-snug">{card.title}</h4>
              </div>
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-normal">{card.body}</p>
            </div>
          ))}
        </div>

        {/* Footer actions */}
        <div className="p-5 bg-slate-900 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2 text-rose-400 font-mono text-xs sm:text-sm font-bold">
            <span>📞</span>
            <span>{current.sosContact}</span>
          </div>

          <div className="flex items-center space-x-3 w-full sm:w-auto">
            <button
              onClick={handleCopyText}
              className="flex-1 sm:flex-initial px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs sm:text-sm border border-slate-700 transition-all flex items-center justify-center space-x-1.5"
            >
              <span>{copied ? '✓ Copied Shield Text' : '📋 Copy All Rights'}</span>
            </button>
            <button
              onClick={onClose}
              className="flex-1 sm:flex-initial px-6 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-black text-xs sm:text-sm shadow-xl shadow-rose-600/30 transition-all"
            >
              Done / Return to Chat
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
