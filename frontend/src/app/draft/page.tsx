'use client';

import React, { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import UnifiedNavbar from '@/components/layout/UnifiedNavbar';
import LegalNoticeStudio from '@/components/drafting/LegalNoticeStudio';
import { FileText, Award, Shield, Sparkles } from 'lucide-react';

function DraftPageContent() {
  const searchParams = useSearchParams();
  const initialTemplate = searchParams.get('template') || searchParams.get('precedent') || undefined;

  return (
    <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8">
      {/* Header Banner */}
      <div className="relative rounded-2xl bg-gradient-to-b from-[#131620] to-[#0c0e14] border border-[#232a3d] p-6 sm:p-10 mb-8 overflow-hidden shadow-2xl">
        <div className="absolute -right-16 -top-16 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold uppercase tracking-wider mb-4">
            <Award className="w-3.5 h-3.5" />
            Official Indian Legal Drafter Studio
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
            Court-Ready Legal Notice & Petition Generator
          </h1>
          <p className="mt-3 text-sm sm:text-base text-gray-400 leading-relaxed">
            Generate formal 15-day Section 138 Cheque Bounce Notices, Tenant Advance Refund Demands, 
            Consumer Protection Claims, Police BNSS § 35 Appearances, and Virtual Court Challan Contests. 
            Export ready-to-print Court PDFs with authentic legal typography, advocate letterhead, and RPAD headers.
          </p>
        </div>
      </div>

      {/* Main Studio Component */}
      <LegalNoticeStudio initialTemplate={initialTemplate} />
    </main>
  );
}

export default function DraftPage() {
  return (
    <div className="min-h-screen bg-[#07080b] text-gray-100 flex flex-col font-sans">
      <UnifiedNavbar />
      <Suspense fallback={<div className="p-12 text-center text-gray-400">Loading Legal Drafter...</div>}>
        <DraftPageContent />
      </Suspense>
    </div>
  );
}
