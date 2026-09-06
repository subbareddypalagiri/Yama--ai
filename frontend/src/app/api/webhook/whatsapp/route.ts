import { NextRequest, NextResponse } from 'next/server';

// WhatsApp Cloud API Verification (GET)
export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const mode = searchParams.get('hub.mode');
  const token = searchParams.get('hub.verify_token');
  const challenge = searchParams.get('hub.challenge');

  const VERIFY_TOKEN = process.env.WHATSAPP_VERIFY_TOKEN || 'yama_ai_webhook_verify_secret';

  if (mode === 'subscribe' && token === VERIFY_TOKEN) {
    console.log('WhatsApp Webhook verified successfully');
    return new Response(challenge, { status: 200 });
  }

  return NextResponse.json({ error: 'Verification token mismatch' }, { status: 403 });
}

// WhatsApp Incoming Message Webhook (POST)
export async function POST(req: NextRequest) {
  try {
    const contentType = req.headers.get('content-type') || '';
    let incomingMessage = '';
    let senderNumber = '';

    // Handle Twilio Webhook (application/x-www-form-urlencoded)
    if (contentType.includes('application/x-www-form-urlencoded')) {
      const formData = await req.formData();
      incomingMessage = formData.get('Body')?.toString() || '';
      senderNumber = formData.get('From')?.toString() || '';
    } else {
      // Handle Meta WhatsApp Cloud API (application/json)
      const body = await req.json();
      const entry = body.entry?.[0];
      const change = entry?.changes?.[0];
      const messageObj = change?.value?.messages?.[0];
      incomingMessage = messageObj?.text?.body || '';
      senderNumber = messageObj?.from || '';
    }

    if (!incomingMessage) {
      return NextResponse.json({ status: 'ignored', reason: 'no text body' });
    }

    // Call Gemini for legal analysis
    const apiKey = process.env.GOOGLE_API_KEY ||
                   process.env.GEMINI_API_KEY ||
                   'AIzaSyDuUX9eeFapUJMgmckRUy_wUxNMI_p3CME';

    const prompt = `You are YAMA AI — WhatsApp Senior Legal Assistant for India.
User query from citizen: "${incomingMessage}"

Give a concise, punchy WhatsApp reply in maximum 3 bullet points:
1. Exact statutory section (e.g. § 318 BNS [Old IPC § 420], or § 35 BNSS, or § 136A MV Act).
2. Actionable advice / next legal step for citizen.
3. Relevant mandatory notice or Lok Adalat waiver rule.
End with: "⚖️ YAMA AI • Senior Advocate Assistant"`;

    const geminiRes = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ role: 'user', parts: [{ text: prompt }] }],
          generationConfig: { maxOutputTokens: 500, temperature: 0.3 }
        })
      }
    );

    let replyText = 'YAMA AI: Legal intelligence processed. Consult counsel.';
    if (geminiRes.ok) {
      const gData = await geminiRes.json();
      replyText = gData.candidates?.[0]?.content?.parts?.[0]?.text || replyText;
    }

    // Return TwiML response if Twilio, otherwise JSON
    if (contentType.includes('application/x-www-form-urlencoded')) {
      const twiml = `<?xml version="1.0" encoding="UTF-8"?><Response><Message>${replyText}</Message></Response>`;
      return new Response(twiml, {
        headers: { 'Content-Type': 'text/xml' },
        status: 200
      });
    }

    return NextResponse.json({
      status: 'success',
      sender: senderNumber,
      reply: replyText
    });
  } catch (err: any) {
    console.error('WhatsApp Webhook Error:', err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
