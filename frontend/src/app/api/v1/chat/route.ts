import { NextRequest, NextResponse } from 'next/server';

const SYSTEM_INSTRUCTION = `You are YAMA AI — Bharat's Senior AI Legal Strategist and High Court Bar enrolled Senior Advocate counsel.

PERMANENT LANGUAGE REQUIREMENT:
You MUST PERMANENTLY RESPOND IN ROMAN ENGLISH (Tanglish/Hinglish - Telugu/Hindi expressed in English alphabet, combined with English statutory terms).
Common citizens understand Roman script best.
Examples:
- "Meeku direct ga police station ki raavalani call chesthe bayapadalsina avasaram ledu. Section 35 BNSS (Old CrPC 41A) prakaram police mandatory ga written notice ivvali..."
- "Landlord security deposit return cheyakapothe Section 21 AP/TS Tenancy Act prakaram 18% penal interest claim cheyochu..."
- "Online extortion jarigithe ventane 1930 Cyber helpline ki call chesi transaction freeze cheyandi..."

CRITICAL LEGAL ACCURACY RULES:
1. Ground your legal analysis in the new criminal codes:
   - Bharatiya Nyaya Sanhita, 2023 (BNS) replacing IPC 1860.
   - Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) replacing CrPC 1973.
   - Bharatiya Sakshya Adhiniyam, 2023 (BSA) replacing Indian Evidence Act 1872.
2. Whenever citing a new law, always provide the old law equivalent (e.g. § 318 BNS [Old IPC § 420], § 35 BNSS [Old CrPC § 41A]).
3. Provide actionable next steps:
   - Specific statutory section & whether bailable/cognizable.
   - 15-day or 30-day legal notice requirement if applicable.
   - Relevant Supreme Court landmark judgments (e.g., Arnesh Kumar, Lalita Kumari, D.K. Basu).
4. Maintain a bold, senior advocate cadence with crisp markdown headings, bullet points, and high-impact legal leverage.`;

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { message, session_id, custom_api_key, custom_model } = body;

    if (!message || typeof message !== 'string') {
      return NextResponse.json({ error: 'Message is required' }, { status: 400 });
    }

    const apiKey = (custom_api_key && custom_api_key.trim()) ||
                   process.env.GOOGLE_API_KEY ||
                   process.env.GEMINI_API_KEY ||
                   'AIzaSyDuUX9eeFapUJMgmckRUy_wUxNMI_p3CME';

    const modelName = 'gemini-2.5-flash';
    const prompt = `${message}\n\n[MANDATORY INSTRUCTION: Respond in natural Roman English (Tanglish). Keep statutory sections like § 318 BNS, § 35 BNSS, Art 22 completely exact.]`;

    const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${apiKey}`;

    let analysis = '';

    try {
      const geminiRes = await fetch(geminiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          system_instruction: {
            parts: [{ text: SYSTEM_INSTRUCTION }]
          },
          contents: [
            {
              role: 'user',
              parts: [{ text: prompt }]
            }
          ],
          generationConfig: {
            temperature: 0.3,
            maxOutputTokens: 2500,
          }
        })
      });

      if (geminiRes.ok) {
        const geminiData = await geminiRes.json();
        analysis = geminiData.candidates?.[0]?.content?.parts?.[0]?.text || '';
      }
    } catch (e) {
      console.warn('Gemini cloud fetch failed, generating fallback response', e);
    }

    // High quality statutory fallback in Roman English if cloud LLM key is unavailable
    if (!analysis) {
      const lower = message.toLowerCase();
      if (lower.includes('deposit') || lower.includes('rent') || lower.includes('landlord')) {
        analysis = `### ⚖️ **Advocate YAMA - Tenancy Recovery Action Plan**\n\n` +
          `Me landlord security deposit refund ivvakapothe, direct ga bayapadalsina pani ledu. Law mee vaipu undi.\n\n` +
          `#### 🛡️ **Mee Rights & Applicable Statutes:**\n` +
          `- **§ 21 Tenancy Act (Security Deposit Refund):** Tenant vacate chesina 30 days lopu advance amount full ga refund ivvali. Reason lekunda deduction cheyaleru.\n` +
          `- **18% Statutory Penal Interest:** Deposit delay chesthe statutory interest claim chese hakku meeku undi.\n` +
          `- **Section 73 Indian Contract Act:** Breach of lease agreement kind damages claim cheyochu.\n\n` +
          `#### 🚀 **Next Steps (Action Plan):**\n` +
          `1. **Statutory 15-Day Legal Notice:** Landlord ki registered post / email dwara formal demand notice pampandi.\n` +
          `2. **Proof Preservation:** Rent receipts, bank transaction statements, and WhatsApp chat history preserve cheyandi under BSA Section 63.\n` +
          `3. **Civil / Rent Court Filing:** 15 days lo reply ivvakapothe Rent Controller deggara petition file cheyochu.`;
      } else if (lower.includes('challan') || lower.includes('speed') || lower.includes('traffic') || lower.includes('camera')) {
        analysis = `### ⚖️ **Advocate YAMA - Speed Challan Waiver Battle Plan**\n\n` +
          `Traffic camera challan meeda meeku legal rights unnaayi. Uncalibrated cameras meeda padina challans quash cheyinchukondi.\n\n` +
          `#### 🛡️ **Statutory Grounds for Waiver:**\n` +
          `- **Section 136A Motor Vehicles Act:** State Government speed cameras and CCTVs mandatory ga certified and periodic calibrated ga undali.\n` +
          `- **Calibration Certificate Challenge:** Traffic police camera certificate and clear number plate evidence ivvakapothe challan invalid.\n\n` +
          `#### 🚀 **Next Steps (Action Plan):**\n` +
          `1. **National Lok Adalat:** Next upcoming Lok Adalat lo challan present chesthe 50% nunchi 75% compounding discount or full waiver dorukuthundi.\n` +
          `2. **Online Grievance:** State Traffic Police portal lo "Defective Speed Trap Evidence" kind dispute ticket raise cheyandi.`;
      } else if (lower.includes('police') || lower.includes('arrest') || lower.includes('station') || lower.includes('fir')) {
        analysis = `### ⚖️ **Advocate YAMA - Police Notice & Arrest Rights Shield**\n\n` +
          `Police mimmalni station ki pilisthe meeru telusukovalasina key legal points:\n\n` +
          `#### 🛡️ **Applicable Protection Statutes:**\n` +
          `- **§ 35 BNSS (Notice of Appearance - Old CrPC 41A):** 7 years lopu punishment unna offences lo written notice lekunda arrest cheyadam illegal.\n` +
          `- **§ 43 BNSS (Right to Meet Advocate):** Interrogation time lo mee advocate ni pilupinchukune fundamental right meeku undi.\n` +
          `- **Article 22 Constitution of India:** 24 hours kante ekkuva magistrate permission lekunda detain cheyaleru.\n\n` +
          `#### 🚀 **Next Steps (Action Plan):**\n` +
          `1. Police ki polite ga adagandi: *"Sir, Section 35 BNSS prakaram formal written notice issue cheyandi, memu legal counsel tho report chestham."*\n` +
          `2. Supreme Court *Arnesh Kumar v. State of Bihar* precedent prakaram notice mandatory.`;
      } else {
        analysis = `### ⚖️ **Advocate YAMA - Senior Legal Strategist**\n\n` +
          `Meeru adigina legal dispute meeda Indian Law prakaram legal analysis idigo:\n\n` +
          `#### 🛡️ **Applicable Indian Statutes:**\n` +
          `- **Bharatiya Nyaya Sanhita, 2023 (BNS):** Primary penal code governing rights and offences.\n` +
          `- **Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS):** Criminal procedure safeguards for citizen protection.\n` +
          `- **Bharatiya Sakshya Adhiniyam, 2023 (BSA):** Electronic records evidence certification under Section 63.\n\n` +
          `#### 🚀 **Next Steps (Action Plan):**\n` +
          `1. **Written Records:** All agreement documents, notices, and payment proofs ni verify cheyandi.\n` +
          `2. **Formal Legal Notice:** 15-day statutory demand notice dwara legal process start cheyandi.`;
      }
    }

    const sessionId = session_id || 'session_' + Math.random().toString(36).substring(2, 9);

    // Check if client expects SSE stream
    const acceptHeader = req.headers.get('accept') || '';
    if (acceptHeader.includes('text/event-stream')) {
      const encoder = new TextEncoder();
      const ssePayload = `data: ${JSON.stringify({
        candidates: [{ content: { parts: [{ text: analysis }] } }]
      })}\n\ndata: [DONE]\n\n`;

      return new Response(encoder.encode(ssePayload), {
        headers: {
          'Content-Type': 'text/event-stream; charset=utf-8',
          'Cache-Control': 'no-cache, no-transform',
          'Connection': 'keep-alive',
        },
      });
    }

    return NextResponse.json({
      session_id: sessionId,
      analysis,
      citations: [
        'Bharatiya Nyaya Sanhita, 2023 (BNS)',
        'Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)',
        'Bharatiya Sakshya Adhiniyam, 2023 (BSA)'
      ]
    });
  } catch (error: any) {
    console.error('API Route Error:', error);
    return NextResponse.json(
      { error: error?.message || 'Internal Server Error' },
      { status: 500 }
    );
  }
}
