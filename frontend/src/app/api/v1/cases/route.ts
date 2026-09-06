import { NextRequest, NextResponse } from 'next/server';
import { supabase, isSupabaseConfigured } from '@/lib/supabase';

export const dynamic = 'force-dynamic';

let inMemoryCases: any[] = [
  {
    id: 1,
    case_uid: 'CNR-APHC010123452024',
    title: 'K. Subba Reddy vs State of Andhra Pradesh',
    description: 'Writ Petition challenging illegal speed camera challan and tenant security deduction.',
    category: 'property',
    status: 'active',
    priority: 'high',
    client_name: 'K. Subba Reddy',
    opponent_name: 'State of Andhra Pradesh',
    court_name: 'High Court of Andhra Pradesh',
    case_number: 'WP(C) 1234/2024',
    next_hearing_date: '2026-09-28',
    ai_summary: 'Strong statutory defense under Section 35 BNSS and MV Act Section 136A.',
    created_at: new Date().toISOString(),
    document_count: 2,
    event_count: 3,
  },
];

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const search = (searchParams.get('search') || '').toLowerCase();
    const status = (searchParams.get('status') || '').toLowerCase();

    if (isSupabaseConfigured) {
      let query = supabase.from('cases').select('*').order('created_at', { ascending: false });
      if (status) query = query.eq('status', status);
      const { data, error } = await query;
      if (!error && data) {
        let results = data;
        if (search) {
          results = results.filter((c: any) =>
            c.title?.toLowerCase().includes(search) ||
            c.case_uid?.toLowerCase().includes(search) ||
            c.cnr_number?.toLowerCase().includes(search)
          );
        }
        return NextResponse.json(results);
      }
    }

    // In-memory fallback
    let filtered = inMemoryCases;
    if (status) {
      filtered = filtered.filter((c) => c.status?.toLowerCase() === status);
    }
    if (search) {
      filtered = filtered.filter(
        (c) =>
          c.title?.toLowerCase().includes(search) ||
          c.case_uid?.toLowerCase().includes(search) ||
          c.client_name?.toLowerCase().includes(search)
      );
    }

    return NextResponse.json(filtered);
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const caseUid = body.case_uid || `CASE-${Date.now().toString(36).toUpperCase()}`;

    const newCase = {
      ...body,
      case_uid: caseUid,
      created_at: new Date().toISOString(),
      document_count: 0,
      event_count: 1,
    };

    if (isSupabaseConfigured) {
      const { data, error } = await supabase
        .from('cases')
        .insert([newCase])
        .select()
        .single();

      if (!error && data) {
        return NextResponse.json(data, { status: 201 });
      }
    }

    inMemoryCases.unshift(newCase);
    return NextResponse.json(newCase, { status: 201 });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
