import { NextRequest, NextResponse } from 'next/server';
import { supabase, isSupabaseConfigured } from '@/lib/supabase';

export async function GET(
  _req: NextRequest,
  { params }: { params: { case_uid: string } }
) {
  try {
    const { case_uid } = params;

    if (isSupabaseConfigured) {
      const { data, error } = await supabase
        .from('cases')
        .select('*')
        .eq('case_uid', case_uid)
        .single();

      if (!error && data) {
        return NextResponse.json(data);
      }
    }

    return NextResponse.json({
      id: 1,
      case_uid,
      title: 'Sample Case Diary File',
      description: 'Active matter under Section 35 BNSS.',
      status: 'active',
      priority: 'high',
      created_at: new Date().toISOString(),
      document_count: 1,
      event_count: 2,
    });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}

export async function DELETE(
  _req: NextRequest,
  { params }: { params: { case_uid: string } }
) {
  try {
    const { case_uid } = params;

    if (isSupabaseConfigured) {
      await supabase.from('cases').delete().eq('case_uid', case_uid);
    }

    return NextResponse.json({ status: 'deleted', case_uid });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
