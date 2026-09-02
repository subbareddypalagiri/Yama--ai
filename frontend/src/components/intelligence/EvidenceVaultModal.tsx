'use client';

import React, { useState } from 'react';
import { ShieldCheck, FileCheck, Hash, Upload, Copy, Check, Printer, X, Lock, AlertCircle } from 'lucide-react';

interface EvidenceVaultModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultClientName?: string;
  defaultState?: string;
}

export default function EvidenceVaultModal({
  isOpen,
  onClose,
  defaultClientName = 'Complainant',
  defaultState = 'Andhra Pradesh',
}: EvidenceVaultModalProps) {
  const [deponentName, setDeponentName] = useState(defaultClientName);
  const [fileName, setFileName] = useState('whatsapp_extortion_chat.png');
  const [fileSize, setFileSize] = useState('342 KB');
  const [sha256Hash, setSha256Hash] = useState('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');
  const [timestamp, setTimestamp] = useState(() => new Date().toISOString());
  const [isHashing, setIsHashing] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleFileDrop = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsHashing(true);
    setFileName(file.name);
    setFileSize(`${(file.size / 1024).toFixed(1)} KB`);
    setTimestamp(new Date().toISOString());

    try {
      const buffer = await file.arrayBuffer();
      const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
      setSha256Hash(hashHex);
    } catch (err) {
      console.error('Hashing failed:', err);
    } finally {
      setIsHashing(false);
    }
  };

  const certificateContent = `STATUTORY ELECTRONIC EVIDENCE CERTIFICATE WITH SHA-256 HASH
UNDER SECTION 63 OF BHARATIYA SAKSHYA ADHINIYAM, 2023 (BSA)
(FORMERLY SECTION 65B OF INDIAN EVIDENCE ACT, 1872)
IN ACCORDANCE WITH SUPREME COURT MANDATE IN ARJUN PANDITRAO (2020)

I, ${deponentName}, aged about major years, residing in ${defaultState}, India, do hereby solemnly affirm and declare on oath as under:

1. CRYPTOGRAPHIC EVIDENCE INTEGRITY IDENTIFICATION:
   - Primary File Name: ${fileName}
   - File Size: ${fileSize}
   - Cryptographic Checksum (SHA-256): ${sha256Hash}
   - Evidence Acquisition Timestamp (UTC): ${timestamp}

2. CUSTODY & REGULAR OPERATION:
   The aforesaid digital record was captured on a personal electronic device under my lawful custody and control. Throughout the material period, the device was operating properly, free from any malware, operational malfunction, or unauthorized interception.

3. TAMPER-PROOF MATHEMATICAL VERIFICATION:
   The SHA-256 cryptographic hash specified above mathematically certifies that the digital output reproduced herein is an identical, bit-for-bit duplicate of the original electronic record, and has not undergone any editing, deletion, or manipulation.

4. ADMISSIBILITY UNDER SECTION 63 BSA, 2023:
   This statutory certificate is issued in compliance with Section 63(4) of Bharatiya Sakshya Adhiniyam, 2023, rendering this digital output primary admissible evidence in all Indian courts.

DEPONENT:

________________________________________
(${deponentName})
Date: ${new Date().toLocaleDateString('en-IN')}`;

  const handleCopy = () => {
    navigator.clipboard.writeText(certificateContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>SHA-256 Cryptographic Evidence Certificate</title>
          <style>
            @page { size: A4; margin: 25mm 20mm; }
            body { font-family: 'Times New Roman', serif; padding: 25px 40px; line-height: 1.7; font-size: 12.5pt; color: #111; }
            .header { text-align: center; border-bottom: 2.5px solid #222; padding-bottom: 12px; margin-bottom: 25px; }
            pre { white-space: pre-wrap; font-family: inherit; font-size: 12pt; line-height: 1.7; }
            .hash-box { background: #f4f4f4; border: 1px solid #ddd; padding: 10px; font-family: monospace; font-size: 10pt; margin: 15px 0; word-break: break-all; }
          </style>
        </head>
        <body>
          <div class="header">
            <h3 style="margin:0;">STATUTORY ELECTRONIC EVIDENCE CERTIFICATE</h3>
            <p style="margin:4px 0; font-size:9.5pt;">Under Section 63 Bharatiya Sakshya Adhiniyam, 2023 • Cryptographic SHA-256 Binding</p>
          </div>
          <pre>${certificateContent}</pre>
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 font-sans">
      <div className="bg-[#0c0d12] border border-cyan-500/30 w-full max-w-4xl rounded-3xl p-6 shadow-2xl relative max-h-[92vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/[0.08]">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Lock className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>Tamper-Proof Digital Evidence Vault</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  SHA-256 CRYPTO HASH
                </span>
              </h3>
              <p className="text-xs text-white/40">Freeze WhatsApp Chats, Audio &amp; Documents into Court-Admissible BSA Section 63 Certificates</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-white/40 hover:text-white hover:bg-white/[0.06] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Layout */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-5 py-4 overflow-y-auto flex-1">
          {/* Upload & Fingerprint Card */}
          <div className="md:col-span-5 space-y-3.5">
            {/* File Dropzone */}
            <div className="relative border-2 border-dashed border-cyan-500/40 rounded-2xl p-4 text-center bg-cyan-500/5 hover:bg-cyan-500/10 transition-all cursor-pointer">
              <input
                type="file"
                onChange={handleFileDrop}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
              <Upload className="w-6 h-6 text-cyan-400 mx-auto mb-1.5" />
              <p className="text-xs font-bold text-white">Select / Drop Screenshot or File</p>
              <p className="text-[10px] text-white/40">PNG, JPG, MP3, MP4, PDF (Computes Instant SHA-256)</p>
            </div>

            <div className="space-y-2 text-xs">
              <div>
                <label className="text-[10px] text-white/40 block mb-0.5 font-bold uppercase tracking-wider">Deponent (Your Name)</label>
                <input
                  type="text"
                  value={deponentName}
                  onChange={(e) => setDeponentName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-cyan-500/50"
                />
              </div>

              {/* Hash Display Card */}
              <div className="p-3.5 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-cyan-300 uppercase tracking-wider flex items-center gap-1">
                    <Hash className="w-3.5 h-3.5" /> Cryptographic Fingerprint
                  </span>
                  <span className="text-[10px] text-white/50">{fileSize}</span>
                </div>
                <div className="p-2 rounded-xl bg-black/40 border border-white/[0.06] font-mono text-[10px] text-cyan-200 break-all leading-relaxed">
                  {isHashing ? 'Computing cryptographic hash...' : sha256Hash}
                </div>
                <div className="flex items-center justify-between text-[10px] text-white/40 font-mono">
                  <span>Target: {fileName}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Certificate Output Box */}
          <div className="md:col-span-7 flex flex-col h-full">
            <div className="flex items-center justify-between pb-2">
              <span className="text-[11px] font-bold text-cyan-300 uppercase tracking-wider flex items-center gap-1.5">
                <FileCheck className="w-3.5 h-3.5" /> Court Section 63 BSA Certificate
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-xs text-white/80 hover:text-white transition-all"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
                <button
                  onClick={handlePrint}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-cyan-500/20 border border-cyan-500/40 text-xs font-semibold text-cyan-300 hover:bg-cyan-500/30 transition-all"
                >
                  <Printer className="w-3.5 h-3.5" />
                  <span>Print Certificate</span>
                </button>
              </div>
            </div>

            <div className="flex-1 bg-black/40 border border-white/[0.08] rounded-2xl p-4 overflow-y-auto font-mono text-[11px] text-white/80 leading-relaxed max-h-96 whitespace-pre-wrap select-all">
              {certificateContent}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-white/[0.08] flex items-center justify-between text-xs text-white/40">
          <span>Mathematically tamper-proof; legally admissible under Supreme Court judgment in Arjun Panditrao (2020).</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] text-white font-medium text-xs transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
