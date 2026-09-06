import { NextRequest, NextResponse } from 'next/server';
import lawsData from '@/data/laws_dataset.json';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const q = (searchParams.get('q') || '').toLowerCase().trim();
    const category = (searchParams.get('category') || '').toLowerCase().trim();
    const actName = (searchParams.get('act_name') || '').toLowerCase().trim();
    const page = Math.max(1, parseInt(searchParams.get('page') || '1', 10));
    const limit = Math.min(200, Math.max(1, parseInt(searchParams.get('limit') || '30', 10)));

    let filtered = lawsData.central_acts as any[];

    if (category && category !== 'all') {
      filtered = filtered.filter((law) => law.category?.toLowerCase() === category);
    }

    if (actName) {
      filtered = filtered.filter((law) => law.act_name?.toLowerCase().includes(actName));
    }

    if (q) {
      filtered = filtered.filter(
        (law) =>
          law.section_number?.toLowerCase() === q ||
          law.title?.toLowerCase().includes(q) ||
          law.description?.toLowerCase().includes(q) ||
          law.act_name?.toLowerCase().includes(q) ||
          law.old_law_reference?.toLowerCase().includes(q)
      );
    }

    const total = filtered.length;
    const totalPages = Math.ceil(total / limit);
    const offset = (page - 1) * limit;
    const paginated = filtered.slice(offset, offset + limit);

    return NextResponse.json({
      results: paginated,
      total,
      page,
      limit,
      total_pages: totalPages,
    });
  } catch (err: any) {
    console.error('Laws search API error:', err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
