import { NextResponse } from 'next/server';
import lawsData from '@/data/laws_dataset.json';

export async function GET() {
  try {
    const actMap = new Map<string, { name: string; count: number; category: string }>();

    for (const law of lawsData.central_acts) {
      const existing = actMap.get(law.act_name);
      if (existing) {
        existing.count += 1;
      } else {
        actMap.set(law.act_name, {
          name: law.act_name,
          count: 1,
          category: law.category || 'general',
        });
      }
    }

    const acts = Array.from(actMap.values()).sort((a, b) => b.count - a.count);

    return NextResponse.json(acts);
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
