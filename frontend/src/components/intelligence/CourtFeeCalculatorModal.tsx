'use client';

import React, { useState } from 'react';
import { Calculator, X, DollarSign, Clock, FileSpreadsheet, ShieldAlert, Award, ChevronRight } from 'lucide-react';

interface CourtFeeCalculatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultState?: string;
}

export default function CourtFeeCalculatorModal({
  isOpen,
  onClose,
  defaultState = 'Andhra Pradesh',
}: CourtFeeCalculatorModalProps) {
  const [selectedState, setSelectedState] = useState(defaultState);
  const [suitType, setSuitType] = useState<'money' | 'cheque' | 'consumer' | 'tenancy' | 'property'>('money');
  const [claimAmount, setClaimAmount] = useState<number>(200000);

  if (!isOpen) return null;

  // Ad-valorem court fee calculation according to Indian State Court Fees Acts
  const calculateCourtFee = () => {
    if (suitType === 'consumer') {
      if (claimAmount <= 500000) return 0; // Free up to 5 Lakhs under CPA 2019
      if (claimAmount <= 1000000) return 200;
      if (claimAmount <= 2000000) return 400;
      if (claimAmount <= 5000000) return 1000;
      return 2000;
    }

    if (suitType === 'cheque') {
      // Criminal complaint under Sec 138 NI Act usually has fixed nominal court fee + process fee
      if (claimAmount <= 100000) return 500;
      if (claimAmount <= 500000) return 1500;
      if (claimAmount <= 2500000) return 5000;
      return 10000;
    }

    // Money suit / Summary Suit Order 37 CPC:
    // Roughly 2.5% - 3.5% of the claimed sum up to certain slabs, capped or graduated
    if (claimAmount <= 50000) return Math.max(500, Math.round(claimAmount * 0.05));
    if (claimAmount <= 100000) return Math.round(2500 + (claimAmount - 50000) * 0.04);
    if (claimAmount <= 500000) return Math.round(4500 + (claimAmount - 100000) * 0.03);
    return Math.round(16500 + (claimAmount - 500000) * 0.02);
  };

  const courtFee = calculateCourtFee();
  const processFee = 750;
  const advocateDraftingFeeBand = claimAmount < 100000 ? '₹5,000 - ₹12,000' : '₹15,000 - ₹35,000';
  const totalFilingExpenses = courtFee + processFee;

  const getDisposalTimeline = () => {
    switch (suitType) {
      case 'cheque':
        return '6 to 14 Months (Summary Trial under Sec 143 NI Act)';
      case 'consumer':
        return '4 to 10 Months (Consumer Commission E-Daakhil Procedure)';
      case 'money':
        return '12 to 24 Months (Civil Judge Senior Division / District Court)';
      case 'tenancy':
        return '8 to 18 Months (Rent Controller & Civil Court)';
      default:
        return '12 to 36 Months';
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 font-sans">
      <div className="bg-[#0e0e12] border border-white/[0.12] w-full max-w-2xl rounded-3xl p-6 shadow-2xl relative max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/[0.08]">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center shadow-lg shadow-amber-500/20">
              <Calculator className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>Indian Court Fees &amp; Litigation Cost Estimator</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  STATUTORY VALUATION
                </span>
              </h3>
              <p className="text-xs text-white/40">State Ad-valorem Court Fees, Process Fees &amp; Expected Timelines</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-white/40 hover:text-white hover:bg-white/[0.06] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="py-4 space-y-4 overflow-y-auto flex-1">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="text-[10px] text-white/40 block mb-1 uppercase tracking-wider font-bold">State Jurisdiction</label>
              <select
                value={selectedState}
                onChange={(e) => setSelectedState(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-amber-500/50"
              >
                <option value="Andhra Pradesh" className="bg-[#131316]">Andhra Pradesh (AP Court Fees Act 1956)</option>
                <option value="Telangana" className="bg-[#131316]">Telangana (TS Court Fees Act 1956)</option>
                <option value="Delhi NCR" className="bg-[#131316]">Delhi (Court Fees Delhi Amendment Act)</option>
                <option value="Maharashtra" className="bg-[#131316]">Maharashtra (Bombay Court Fees Act)</option>
                <option value="Karnataka" className="bg-[#131316]">Karnataka (Karnataka Court Fees Act 1958)</option>
                <option value="Tamil Nadu" className="bg-[#131316]">Tamil Nadu (TN Court Fees Act 1955)</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] text-white/40 block mb-1 uppercase tracking-wider font-bold">Dispute Nature / Suit Category</label>
              <select
                value={suitType}
                onChange={(e: any) => setSuitType(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-amber-500/50"
              >
                <option value="money" className="bg-[#131316]">Civil Money Recovery / Breach (Order 37 CPC)</option>
                <option value="cheque" className="bg-[#131316]">Cheque Bounce (Sec 138 NI Act)</option>
                <option value="consumer" className="bg-[#131316]">Consumer Forum Dispute (Consumer Protection Act 2019)</option>
                <option value="tenancy" className="bg-[#131316]">Tenancy Eviction &amp; Rent Recovery</option>
                <option value="property" className="bg-[#131316]">Property Partition / Declaration Suit</option>
              </select>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-[10px] text-white/40 uppercase tracking-wider font-bold">Claim / Disputed Amount</label>
              <span className="text-xs font-mono font-bold text-amber-300">₹{claimAmount.toLocaleString('en-IN')}</span>
            </div>
            <input
              type="range"
              min={10000}
              max={5000000}
              step={10000}
              value={claimAmount}
              onChange={(e) => setClaimAmount(Number(e.target.value))}
              className="w-full accent-amber-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-white/30 font-mono mt-1">
              <span>₹10,000</span>
              <span>₹10,00,000</span>
              <span>₹25,00,000</span>
              <span>₹50,00,000</span>
            </div>
          </div>

          {/* Results Breakdown Grid */}
          <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/25 space-y-3">
            <h4 className="text-xs font-bold text-amber-300 uppercase tracking-wider flex items-center gap-1.5">
              <FileSpreadsheet className="w-4 h-4" /> Estimated Litigation Expenses Breakdown
            </h4>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
              <div className="p-3 rounded-xl bg-black/30 border border-white/[0.05]">
                <span className="text-[10px] text-white/40 block">Statutory Court Fee</span>
                <span className="text-sm font-bold text-white font-mono">₹{courtFee.toLocaleString('en-IN')}</span>
              </div>

              <div className="p-3 rounded-xl bg-black/30 border border-white/[0.05]">
                <span className="text-[10px] text-white/40 block">Summons &amp; Process Fee</span>
                <span className="text-sm font-bold text-white font-mono">₹{processFee.toLocaleString('en-IN')}</span>
              </div>

              <div className="p-3 rounded-xl bg-black/30 border border-white/[0.05] col-span-2 sm:col-span-1">
                <span className="text-[10px] text-white/40 block">Advocate Drafting Band</span>
                <span className="text-xs font-bold text-emerald-400 font-mono">{advocateDraftingFeeBand}</span>
              </div>
            </div>

            <div className="pt-2 border-t border-white/[0.08] flex items-center justify-between text-xs">
              <span className="text-white/60">Estimated Total Initial Filing Cost:</span>
              <span className="font-bold text-base text-amber-300 font-mono">₹{totalFilingExpenses.toLocaleString('en-IN')}*</span>
            </div>
          </div>

          {/* Timeline estimate */}
          <div className="p-3.5 rounded-2xl bg-white/[0.02] border border-white/[0.06] flex items-center gap-3">
            <Clock className="w-5 h-5 text-indigo-400 flex-shrink-0" />
            <div>
              <span className="text-[10px] text-white/40 uppercase tracking-wider block font-bold">Judicial Disposal Timeline Estimate</span>
              <span className="text-xs font-semibold text-white/90">{getDisposalTimeline()}</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-white/[0.08] flex items-center justify-between text-xs text-white/40">
          <span>*Statutory court fees refundable up to 100% if settled in Lok Adalat.</span>
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
