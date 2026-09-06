import { NextResponse } from 'next/server';
import lawsData from '@/data/laws_dataset.json';

export async function GET() {
  try {
    const catMap = new Map<string, number>();

    for (const law of lawsData.central_acts) {
      const cat = law.category || 'other';
      catMap.set(cat, (catMap.get(cat) || 0) + 1);
    }

    const categories = Array.from(catMap.entries()).map(([name, count]) => ({
      name,
      count,
    })).sort((a, b) => b.count - a.count);

    return NextResponse.json(categories);
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
