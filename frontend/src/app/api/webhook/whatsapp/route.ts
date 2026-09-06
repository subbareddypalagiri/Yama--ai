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
    let isImage = false;

    // 1. Handle Twilio Webhook (application/x-www-form-urlencoded)
    if (contentType.includes('application/x-www-form-urlencoded')) {
      const formData = await req.formData();
      incomingMessage = formData.get('Body')?.toString() || '';
      senderNumber = formData.get('From')?.toString() || '';
      const numMedia = parseInt(formData.get('NumMedia')?.toString() || '0', 10);
      if (numMedia > 0) isImage = true;
    } else {
      // 2. Handle Meta WhatsApp Cloud API (application/json)
      const body = await req.json();
      const entry = body.entry?.[0];
      const change = entry?.changes?.[0];
      const messageObj = change?.value?.messages?.[0];

      if (messageObj?.type === 'text') {
        incomingMessage = messageObj.text?.body || '';
      } else if (messageObj?.type === 'image') {
        isImage = true;
        incomingMessage = messageObj.image?.caption || 'Citizen uploaded traffic challan photo or legal document for review.';
      }
      senderNumber = messageObj?.from || '';
    }

    if (!incomingMessage && !isImage) {
      return NextResponse.json({ status: 'ignored', reason: 'no content' });
    }

    // 3. Call Gemini 2.5 Flash for statutory deduction
    const apiKey = process.env.GOOGLE_API_KEY ||
                   process.env.GEMINI_API_KEY ||
                   'AIzaSyDuUX9eeFapUJMgmckRUy_wUxNMI_p3CME';

    const systemPrompt = isImage
      ? `You are YAMA AI — WhatsApp Senior Legal Assistant for India.
The citizen forwarded a photo of a Traffic Challan, Rent Notice, or Police Summons.
Caption/Context: "${incomingMessage}"

Provide an immediate, authoritative 3-bullet action guide:
1. 📌 Applicable Sections: Mention MV Act § 136A (uncalibrated speed camera waiver) or BNSS § 35 (notice mandate) or Tenancy Act § 21.
2. ⚖️ Immediate Relief: How to get 50-75% discount in National Lok Adalat or challenge illegal custody.
3. 📄 Next Step: Type "PETITION" for ready-to-file court draft.
End with: "🏛️ Advocate YAMA AI • WhatsApp Legal Helpdesk"`
      : `You are YAMA AI — WhatsApp Senior Legal Assistant for India.
User query from citizen: "${incomingMessage}"

Give a concise, punchy WhatsApp reply in maximum 3 bullet points:
1. 📌 Exact statutory section (e.g. § 318 BNS [Old IPC § 420], or § 35 BNSS, or § 136A MV Act).
2. 🛡️ Actionable advice / next legal step for citizen.
3. ⚖️ Relevant mandatory notice or Lok Adalat waiver rule.
End with: "🏛️ Advocate YAMA AI • Senior Legal Helpdesk"`;

    let replyText = '🏛️ Advocate YAMA AI: Your legal query is received. Under the 2023 Sanhitas and 28 State Acts, legal protections are active.';

    try {
      const geminiRes = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [{ role: 'user', parts: [{ text: systemPrompt }] }],
            generationConfig: { maxOutputTokens: 500, temperature: 0.3 }
          })
        }
      );

      if (geminiRes.ok) {
        const gData = await geminiRes.json();
        replyText = gData.candidates?.[0]?.content?.parts?.[0]?.text || replyText;
      }
    } catch (e) {
      console.warn('Gemini call failed in WhatsApp webhook', e);
    }

    // 4. Outbound Meta WhatsApp Cloud API Dispatcher
    const metaAccessToken = process.env.WHATSAPP_ACCESS_TOKEN;
    const metaPhoneId = process.env.WHATSAPP_PHONE_NUMBER_ID;

    if (metaAccessToken && metaPhoneId && senderNumber) {
      try {
        await fetch(`https://graph.facebook.com/v18.0/${metaPhoneId}/messages`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${metaAccessToken}`
          },
          body: JSON.stringify({
            messaging_product: 'whatsapp',
            to: senderNumber,
            type: 'text',
            text: { body: replyText }
          })
        });
      } catch (metaErr) {
        console.error('Meta Cloud API outbound message failed:', metaErr);
      }
    }

    // 5. Return TwiML response if Twilio
    if (contentType.includes('application/x-www-form-urlencoded')) {
      const twiml = `<?xml version="1.0" encoding="UTF-8"?><Response><Message>${replyText.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</Message></Response>`;
      return new Response(twiml, {
        headers: { 'Content-Type': 'text/xml' },
        status: 200
      });
    }

    return NextResponse.json({
      status: 'success',
      sender: senderNumber,
      isImage,
      reply: replyText
    });
  } catch (err: any) {
    console.error('WhatsApp Webhook Error:', err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
