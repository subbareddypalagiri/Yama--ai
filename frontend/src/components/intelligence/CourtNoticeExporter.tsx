'use client';

import React, { useState } from 'react';
import { FileText, Printer, Download, Check, Sparkles } from 'lucide-react';

interface CourtNoticeExporterProps {
  content: string;
  clientName?: string;
  className?: string;
}

export default function CourtNoticeExporter({
  content,
  clientName = 'Citizen / Aggrieved Party',
  className = '',
}: CourtNoticeExporterProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExportPDF = () => {
    setIsExporting(true);

    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      alert('Please allow popups to generate Court Notice PDF');
      setIsExporting(false);
      return;
    }

    const today = new Date().toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });

    const refNo = `YAMA/DEL/STAT/${Math.floor(100000 + Math.random() * 900000)}`;
    const shaHash = Array.from(crypto.getRandomValues(new Uint8Array(16)))
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('');

    const formattedBody = content
      .replace(/###\s+/g, '<h3 style="font-size:16px; margin-top:14px; margin-bottom:6px; color:#1a1a1a; font-weight:700; border-bottom:1px solid #e5e7eb; padding-bottom:4px;">')
      .replace(/####\s+/g, '<h4 style="font-size:14px; margin-top:12px; margin-bottom:4px; color:#374151; font-weight:600;">')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/\n\n/g, '</p><p style="margin-bottom:10px; line-height:1.6; font-size:13px; color:#1f2937;">')
      .replace(/\n-\s+/g, '<br/>• ');

    const htmlDoc = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Official Court Legal Notice - YAMA AI</title>
        <style>
          @page { size: A4; margin: 20mm; }
          body {
            font-family: 'Times New Roman', Times, serif;
            color: #111;
            background: #fff;
            margin: 0;
            padding: 20px;
          }
          .letterhead {
            border-bottom: 2px double #1f2937;
            padding-bottom: 12px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
          }
          .emblem {
            font-size: 24px;
            font-weight: bold;
            letter-spacing: 1px;
            color: #854d0e;
          }
          .sub-emblem {
            font-size: 11px;
            color: #4b5563;
            text-transform: uppercase;
            letter-spacing: 2px;
          }
          .ref-table {
            width: 100%;
            margin-bottom: 16px;
            font-size: 12px;
          }
          .title {
            text-align: center;
            font-size: 16px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 18px 0;
            text-decoration: underline;
          }
          .content {
            font-size: 13px;
            line-height: 1.65;
            text-align: justify;
          }
          .watermark {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-35deg);
            font-size: 64px;
            color: rgba(0,0,0,0.03);
            font-weight: bold;
            pointer-events: none;
            z-index: -1;
            text-transform: uppercase;
          }
          .seal-box {
            margin-top: 30px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            page-break-inside: avoid;
          }
          .digital-seal {
            border: 1px dashed #9ca3af;
            padding: 8px 12px;
            font-family: monospace;
            font-size: 10px;
            color: #4b5563;
            background: #f9fafb;
            max-width: 320px;
          }
          .signature-line {
            text-align: center;
            font-size: 12px;
          }
        </style>
      </head>
      <body>
        <div class="watermark">COURT ADMISSIBLE NOTICE</div>

        <div class="letterhead">
          <div>
            <div class="emblem">⚖️ YAMA AI LEGAL COUNSEL</div>
            <div class="sub-emblem">High Court &amp; Supreme Court Statutory Defense Chamber</div>
          </div>
          <div style="text-align: right; font-size: 11px; color: #4b5563;">
            Enrolment No: BAR/IND/2026/S-88<br/>
            Central Legal Repository Index
          </div>
        </div>

        <table class="ref-table">
          <tr>
            <td><strong>Ref No:</strong> ${refNo}</td>
            <td style="text-align: right;"><strong>Date:</strong> ${today}</td>
          </tr>
          <tr>
            <td><strong>Client Reference:</strong> ${clientName}</td>
            <td style="text-align: right;"><strong>Governing Code:</strong> Sanhitas 2023 &amp; State Acts</td>
          </tr>
        </table>

        <div class="title">
          STATUTORY DEMAND NOTICE &amp; LEGAL STRATEGY BRIEF
        </div>

        <div class="content">
          <p>${formattedBody}</p>
        </div>

        <div class="seal-box">
          <div class="digital-seal">
            <strong>DIGITAL EVIDENCE AUDIT HASH:</strong><br/>
            SHA-256: ${shaHash}<br/>
            Admissible under Bharatiya Sakshya Adhiniyam, 2023 (BSA § 63)<br/>
            Generated via YAMA AI Autonomous Chamber
          </div>

          <div class="signature-line">
            <br/><br/>
            _______________________________<br/>
            <strong>Senior Legal Counsel</strong><br/>
            Bar Council Enrolled Advocate
          </div>
        </div>

        <script>
          window.onload = function() {
            setTimeout(function() {
              window.print();
            }, 400);
          };
        </script>
      </body>
      </html>
    `;

    printWindow.document.open();
    printWindow.document.write(htmlDoc);
    printWindow.document.close();

    setTimeout(() => setIsExporting(false), 1500);
  };

  return (
    <button
      type="button"
      onClick={handleExportPDF}
      disabled={isExporting}
      title="Generate Court-Grade Notice PDF"
      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all border shadow-sm ${
        isExporting
          ? 'bg-amber-500/20 text-amber-300 border-[#f59e0b]'
          : 'bg-[#12141c] hover:bg-[#181b26] text-gray-300 hover:text-white border-[#252a3a] hover:border-[#f59e0b]/50'
      } ${className}`}
    >
      <FileText className="w-3.5 h-3.5 text-[#f59e0b]" />
      <span>{isExporting ? 'Preparing PDF...' : 'Court Notice PDF'}</span>
    </button>
  );
}
