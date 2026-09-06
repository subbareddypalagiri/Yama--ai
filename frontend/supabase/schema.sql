-- 🏛️ YAMA AI - Complete Supabase PostgreSQL Schema
-- Run this in your Supabase SQL Editor to initialize all tables with Row Level Security (RLS)

-- 1. Profiles Table (Citizens & Advocates)
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT,
  full_name TEXT,
  phone TEXT,
  role TEXT DEFAULT 'citizen' CHECK (role IN ('citizen', 'advocate')),
  bar_council_id TEXT,
  state TEXT DEFAULT 'All India',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Cases Table (Case Diary & eCourts CNR Sync)
CREATE TABLE IF NOT EXISTS public.cases (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  case_uid TEXT UNIQUE NOT NULL,
  cnr_number TEXT,
  title TEXT NOT NULL,
  court TEXT NOT NULL,
  case_type TEXT DEFAULT 'civil',
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'pending', 'resolved', 'closed', 'draft')),
  next_hearing_date DATE,
  stage TEXT,
  bench TEXT,
  petitioner TEXT,
  respondent TEXT,
  details TEXT,
  orders_json JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Consultations & Chats Table
CREATE TABLE IF NOT EXISTS public.consultations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  session_id TEXT UNIQUE NOT NULL,
  query TEXT NOT NULL,
  response_summary TEXT,
  irac_analysis JSONB,
  applicable_statutes JSONB,
  response_style TEXT DEFAULT 'roman_english',
  language TEXT DEFAULT 'en',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Court Legal Notices Table
CREATE TABLE IF NOT EXISTS public.notices (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  ref_number TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  sender_name TEXT NOT NULL,
  recipient_name TEXT NOT NULL,
  statute TEXT NOT NULL,
  claim_amount TEXT,
  digital_hash TEXT NOT NULL,
  content_body TEXT NOT NULL,
  status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'dispatched', 'settled', 'contested')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Evidence Vault Table (BSA 2023 § 63 Cryptographic Record)
CREATE TABLE IF NOT EXISTS public.evidence_vault (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  item_uid TEXT UNIQUE NOT NULL,
  file_name TEXT NOT NULL,
  file_type TEXT NOT NULL,
  file_size_bytes BIGINT,
  sha256_hash TEXT NOT NULL,
  bsa_section TEXT DEFAULT 'BSA 2023 § 63',
  metadata JSONB DEFAULT '{}'::jsonb,
  certified_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_cases_user_id ON public.cases(user_id);
CREATE INDEX IF NOT EXISTS idx_cases_cnr ON public.cases(cnr_number);
CREATE INDEX IF NOT EXISTS idx_notices_user_id ON public.notices(user_id);
CREATE INDEX IF NOT EXISTS idx_notices_hash ON public.notices(digital_hash);
CREATE INDEX IF NOT EXISTS idx_evidence_hash ON public.evidence_vault(sha256_hash);

-- Enable RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.consultations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.evidence_vault ENABLE ROW LEVEL SECURITY;

-- Public read/write policies for authenticated or anon demo sessions
CREATE POLICY "Allow public read of profiles" ON public.profiles FOR SELECT USING (true);
CREATE POLICY "Allow user update own profile" ON public.profiles FOR ALL USING (auth.uid() = id);

CREATE POLICY "Allow read cases" ON public.cases FOR SELECT USING (true);
CREATE POLICY "Allow insert cases" ON public.cases FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow update cases" ON public.cases FOR UPDATE USING (true);

CREATE POLICY "Allow read notices" ON public.notices FOR SELECT USING (true);
CREATE POLICY "Allow insert notices" ON public.notices FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow read evidence" ON public.evidence_vault FOR SELECT USING (true);
CREATE POLICY "Allow insert evidence" ON public.evidence_vault FOR INSERT WITH CHECK (true);
