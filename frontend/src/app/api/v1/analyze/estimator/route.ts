import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const { situation } = await req.json();
    if (!situation) {
      return NextResponse.json({ error: 'Situation is required' }, { status: 400 });
    }

    const apiKey = process.env.GOOGLE_API_KEY ||
                   process.env.GEMINI_API_KEY ||
                   'AIzaSyDuUX9eeFapUJMgmckRUy_wUxNMI_p3CME';

    const prompt = `Estimate litigation duration, court fees, and advocate cost for: "${situation}".
Return ONLY a JSON matching:
{
  "case_type": "e.g. Tenancy / Contract / Cheque Bounce",
  "estimated_duration": "e.g. 3 - 6 Months",
  "court_fee_stamp_duty": "e.g. ₹500 - ₹2,500 (ad-valorem)",
  "lawyer_fee_range": "e.g. ₹15,000 - ₹35,000",
  "fast_track_remedy": "e.g. Pre-Litigation Mediation via NALSA / Lok Adalat",
  "key_steps_count": 4
}`;

    try {
      const res = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [{ role: 'user', parts: [{ text: prompt }] }],
            generationConfig: {
              temperature: 0.2,
              responseMimeType: 'application/json',
            },
          }),
        }
      );

      if (res.ok) {
        const data = await res.json();
        const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
        if (jsonText) {
          return NextResponse.json(JSON.parse(jsonText));
        }
      }
    } catch (e) {
      console.warn('Gemini estimator call failed, falling back', e);
    }

    return NextResponse.json({
      case_type: 'Summary Statutory Recovery / Notice Stage',
      estimated_duration: '45 - 90 Days (Pre-Litigation) / 6-12 Months (Full Trial)',
      court_fee_stamp_duty: '₹500 - ₹2,000 (State Court Fees Act Schedule 1)',
      lawyer_fee_range: '₹10,000 - ₹25,000 (Notice & Settlement Drafting)',
      fast_track_remedy: 'National Lok Adalat Settlement / Commercial Courts Pre-Institution Mediation',
      key_steps_count: 4,
    });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
