import { NextRequest, NextResponse } from 'next/server';

const SYSTEM_INSTRUCTION = `You are YAMA AI — Bharat's Senior AI Legal Strategist and High Court Bar enrolled Senior Advocate counsel.
Your primary role is to provide authoritative, court-grade statutory legal intelligence for citizens, advocates, and enterprises in India.

CRITICAL RULES:
1. Ground your legal analysis in the new criminal codes:
   - Bharatiya Nyaya Sanhita, 2023 (BNS) replacing IPC 1860.
   - Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) replacing CrPC 1973.
   - Bharatiya Sakshya Adhiniyam, 2023 (BSA) replacing Indian Evidence Act 1872.
2. Whenever citing a new law, always provide the old law equivalent (e.g. § 318 BNS [Old IPC § 420], § 35 BNSS [Old CrPC § 41A]).
3. Provide actionable next steps:
   - Specific statutory section & whether bailable/cognizable.
   - 15-day or 30-day legal notice requirement if applicable.
   - Relevant Supreme Court landmark judgments (e.g., Arnesh Kumar, Lalita Kumari, D.K. Basu).
4. If the user asks in Telugu or Roman English/Telugu, respond naturally with accurate legal terms.
5. Maintain a bold, senior advocate cadence with crisp markdown headings, bullet points, and high-impact legal leverage.`;

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { message, session_id, response_style, response_language, custom_api_key, custom_model } = body;

    if (!message || typeof message !== 'string') {
      return NextResponse.json({ error: 'Message is required' }, { status: 400 });
    }

    const apiKey = (custom_api_key && custom_api_key.trim()) ||
                   process.env.GOOGLE_API_KEY ||
                   process.env.GEMINI_API_KEY ||
                   'AIzaSyDuUX9eeFapUJMgmckRUy_wUxNMI_p3CME';

    const modelName = 'gemini-2.5-flash';

    let prompt = message;
    if (response_style === 'roman_english') {
      prompt = `${message}\n\n[Please reply in clear Romanized English/Hinglish/Tanglish style as requested by user.]`;
    }
    if (response_language && response_language !== 'auto' && response_language !== 'english') {
      prompt = `${prompt}\n\n[Please respond in ${response_language} language.]`;
    }

    const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${apiKey}`;

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

    if (!geminiRes.ok) {
      const errText = await geminiRes.text();
      console.error('Gemini API Error:', errText);
      return NextResponse.json(
        { error: `AI provider error: ${geminiRes.statusText}` },
        { status: geminiRes.status }
      );
    }

    const geminiData = await geminiRes.json();
    const analysis = geminiData.candidates?.[0]?.content?.parts?.[0]?.text ||
                     'No statutory analysis could be generated. Please consult counsel.';

    return NextResponse.json({
      session_id: session_id || 'session_' + Math.random().toString(36).substring(2, 9),
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
