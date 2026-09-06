import { NextResponse } from 'next/server';
import lawsData from '@/data/laws_dataset.json';

export async function GET() {
  try {
    const totalCentral = lawsData.central_acts.length;
    const totalState = lawsData.state_acts.length;

    return NextResponse.json({
      total_laws: totalCentral + totalState,
      central_acts: totalCentral,
      state_acts: totalState,
      supreme_court_precedents: 12,
      high_court_precedents: 30,
      status: 'active',
      engine: 'gemini-2.5-flash',
    });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
