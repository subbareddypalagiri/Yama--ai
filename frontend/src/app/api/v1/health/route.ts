import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'ok',
    backend: 'vercel-serverless-nextjs',
    laws_indexed: 12036,
    engine: 'gemini-2.5-flash',
    cloud_database: 'supabase-postgresql',
    timestamp: new Date().toISOString(),
  });
}
