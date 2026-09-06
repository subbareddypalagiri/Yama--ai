import { createClient, SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://mock-yama-ai.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'mock-anon-key-yama-ai-2026';

export const isSupabaseConfigured = Boolean(
  process.env.NEXT_PUBLIC_SUPABASE_URL && 
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY &&
  !process.env.NEXT_PUBLIC_SUPABASE_URL.includes('mock-yama-ai')
);

export const supabase: SupabaseClient = createClient(supabaseUrl, supabaseAnonKey);

export interface SupabaseProfile {
  id: string;
  email?: string;
  full_name?: string;
  phone?: string;
  role?: 'citizen' | 'advocate';
  bar_council_id?: string;
  state?: string;
  created_at?: string;
}

export interface SupabaseCase {
  id?: string;
  user_id?: string;
  case_uid: string;
  cnr_number?: string;
  title: string;
  court: string;
  case_type: string;
  status: 'active' | 'pending' | 'resolved' | 'closed' | 'draft';
  next_hearing_date?: string;
  stage?: string;
  bench?: string;
  petitioner?: string;
  respondent?: string;
  details?: string;
  orders_json?: any;
  created_at?: string;
}

export interface SupabaseNotice {
  id?: string;
  user_id?: string;
  ref_number: string;
  title: string;
  sender_name: string;
  recipient_name: string;
  statute: string;
  claim_amount?: string;
  digital_hash: string;
  content_body: string;
  created_at?: string;
}

// ─── Database Sync Helpers ──────────────────────────────────────────────────

export async function syncCaseToCloud(caseData: Partial<SupabaseCase>): Promise<SupabaseCase | null> {
  if (!isSupabaseConfigured) {
    try {
      const existing = JSON.parse(localStorage.getItem('yama_cloud_cases') || '[]');
      const updated = [caseData, ...existing.filter((c: any) => c.case_uid !== caseData.case_uid)];
      localStorage.setItem('yama_cloud_cases', JSON.stringify(updated));
    } catch (e) {
      console.warn('Local case cache failed', e);
    }
    return caseData as SupabaseCase;
  }

  try {
    const { data, error } = await supabase
      .from('cases')
      .upsert(caseData, { onConflict: 'case_uid' })
      .select()
      .single();

    if (error) throw error;
    return data;
  } catch (err) {
    console.error('Failed to sync case to Supabase:', err);
    return null;
  }
}

export async function fetchCloudCases(): Promise<SupabaseCase[]> {
  if (!isSupabaseConfigured) {
    try {
      return JSON.parse(localStorage.getItem('yama_cloud_cases') || '[]');
    } catch {
      return [];
    }
  }

  try {
    const { data, error } = await supabase
      .from('cases')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) throw error;
    return data || [];
  } catch (err) {
    console.error('Failed to fetch cases from Supabase:', err);
    return [];
  }
}

export async function syncNoticeToCloud(noticeData: Partial<SupabaseNotice>): Promise<SupabaseNotice | null> {
  if (!isSupabaseConfigured) {
    try {
      const existing = JSON.parse(localStorage.getItem('yama_cloud_notices') || '[]');
      const updated = [noticeData, ...existing.filter((n: any) => n.ref_number !== noticeData.ref_number)];
      localStorage.setItem('yama_cloud_notices', JSON.stringify(updated));
    } catch (e) {
      console.warn('Local notice cache failed', e);
    }
    return noticeData as SupabaseNotice;
  }

  try {
    const { data, error } = await supabase
      .from('notices')
      .upsert(noticeData, { onConflict: 'ref_number' })
      .select()
      .single();

    if (error) throw error;
    return data;
  } catch (err) {
    console.error('Failed to sync notice to Supabase:', err);
    return null;
  }
}
