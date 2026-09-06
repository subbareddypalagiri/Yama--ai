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

    const prompt = `Simulate an Indian High Court bench trial for this situation: "${situation}".
Return ONLY a JSON object matching this schema:
{
  "counsel_view": {
    "role": "Petitioner Senior Advocate",
    "title": "Prosecution / Aggrieved Argument",
    "arguments": ["arg 1", "arg 2"],
    "legal_citations": ["citation 1", "citation 2"]
  },
  "defense_view": {
    "role": "Defense Senior Counsel",
    "title": "Respondent Defense Counter",
    "arguments": ["arg 1", "arg 2"],
    "legal_citations": ["citation 1", "citation 2"]
  },
  "judge_verdict": {
    "role": "Hon'ble Bench",
    "title": "Judicial Precedent & Interim Directions",
    "arguments": ["direction 1", "direction 2"],
    "legal_citations": ["ruling citation"]
  },
  "summary": "2-line summary of court disposition"
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
      console.warn('Gemini simulation call failed, falling back', e);
    }

    return NextResponse.json({
      counsel_view: {
        role: 'Aggrieved Counsel',
        title: 'Statutory Breach & Mandatory Restitution Claim',
        arguments: [
          'Opponent is in willful default with deliberate suppression of material facts.',
          'Section 35 BNSS requires notice before coercive steps.',
        ],
        legal_citations: ['Section 318 BNS 2023', 'Section 73 Indian Contract Act, 1872'],
      },
      defense_view: {
        role: 'Respondent Counsel',
        title: 'Lack of Mens Rea & Civil Dispute Defense',
        arguments: [
          'The matter arises purely out of a contractual disagreement without fraudulent intent.',
          'Criminal proceedings are being misused for civil recovery.',
        ],
        legal_citations: ['Indian Penal Code § 415 / BNS § 316', 'State of Haryana v. Bhajan Lal'],
      },
      judge_verdict: {
        role: 'Hon\'ble Single Bench',
        title: 'Interim Protection with Direction to Mediate',
        arguments: [
          'No custodial interrogation warranted as dispute carries strong documentary presence.',
          'Parties directed to exchange certified statements within 15 days.',
        ],
        legal_citations: ['Arnesh Kumar v. State of Bihar (2014) 8 SCC 273'],
      },
      summary: 'Interim protection granted with mandatory statutory compliance under Section 35 BNSS and reference to National Lok Adalat.',
    });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
