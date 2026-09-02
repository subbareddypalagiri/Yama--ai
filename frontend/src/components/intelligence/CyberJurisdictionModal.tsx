'use client';

import React, { useState } from 'react';
import { MapPin, Phone, Shield, Search, X, Building, Navigation, FileText, ExternalLink } from 'lucide-react';

interface StationInfo {
  district: string;
  state: string;
  stationName: string;
  address: string;
  shoPhone: string;
  controlRoomPhone: string;
  spOfficePhone: string;
  email: string;
}

const POLICE_STATIONS: StationInfo[] = [
  // Andhra Pradesh Districts
  {
    district: 'YSR Kadapa',
    state: 'Andhra Pradesh',
    stationName: 'District Cyber Crime Police Station, Kadapa',
    address: 'District Police Office (DPO) Compound, Opp. Collectorate, Kadapa - 516004',
    shoPhone: '08562-244300',
    controlRoomPhone: '08562-244100 / 112',
    spOfficePhone: '08562-244400',
    email: 'cyber-kadapa@ap.gov.in',
  },
  {
    district: 'Visakhapatnam',
    state: 'Andhra Pradesh',
    stationName: 'Visakhapatnam Cyber Crime Police Station',
    address: 'Commissioner of Police Office Compound, Suryabagh, Visakhapatnam - 530020',
    shoPhone: '0891-2565455',
    controlRoomPhone: '0891-2565100 / 112',
    spOfficePhone: '0891-2562709',
    email: 'cyber-vsp@ap.gov.in',
  },
  {
    district: 'Vijayawada / NTR',
    state: 'Andhra Pradesh',
    stationName: 'Vijayawada City Cyber Crime Police Station',
    address: 'Police Commissionerate Complex, MG Road, Labbipet, Vijayawada - 520010',
    shoPhone: '0866-2576100',
    controlRoomPhone: '0866-2579999 / 112',
    spOfficePhone: '0866-2575555',
    email: 'cyber-vja@ap.gov.in',
  },
  {
    district: 'Guntur',
    state: 'Andhra Pradesh',
    stationName: 'Guntur District Cyber Crime Police Station',
    address: 'DPO Complex, Nagarampalem, Guntur - 522004',
    shoPhone: '0863-2234000',
    controlRoomPhone: '0863-2234100 / 112',
    spOfficePhone: '0863-2234200',
    email: 'cyber-guntur@ap.gov.in',
  },
  {
    district: 'Tirupati',
    state: 'Andhra Pradesh',
    stationName: 'Tirupati District Cyber Crime Police Station',
    address: 'Police Parade Grounds, Beside SP Office, Tirupati - 517501',
    shoPhone: '0877-2289100',
    controlRoomPhone: '0877-2289104 / 112',
    spOfficePhone: '0877-2289102',
    email: 'cyber-tirupati@ap.gov.in',
  },
  {
    district: 'Kurnool',
    state: 'Andhra Pradesh',
    stationName: 'Kurnool Cyber Crime Police Station',
    address: 'District Police Headquarters, Near Collectorate, Kurnool - 518002',
    shoPhone: '08518-225300',
    controlRoomPhone: '08518-225100 / 112',
    spOfficePhone: '08518-225400',
    email: 'cyber-kurnool@ap.gov.in',
  },
  {
    district: 'Nellore (SPSR)',
    state: 'Andhra Pradesh',
    stationName: 'Nellore District Cyber Police Station',
    address: 'DPO Compound, Dargamitta, Nellore - 524003',
    shoPhone: '0861-2331400',
    controlRoomPhone: '0861-2331100 / 112',
    spOfficePhone: '0861-2331200',
    email: 'cyber-nellore@ap.gov.in',
  },
  {
    district: 'Anantapur',
    state: 'Andhra Pradesh',
    stationName: 'Anantapuramu Cyber Crime Police Station',
    address: 'DPO Campus, Clock Tower Road, Anantapur - 515001',
    shoPhone: '08554-274100',
    controlRoomPhone: '08554-274200 / 112',
    spOfficePhone: '08554-274300',
    email: 'cyber-atp@ap.gov.in',
  },

  // Telangana Districts
  {
    district: 'Hyderabad City',
    state: 'Telangana',
    stationName: 'Hyderabad City Cyber Crime Police Station (CCPS)',
    address: 'Hyderabad Police Commissionerate, Basheerbagh / Banjara Hills, Hyderabad - 500034',
    shoPhone: '040-27852400',
    controlRoomPhone: '040-27852333 / 112',
    spOfficePhone: '040-27852200',
    email: 'cybercrime-hyd@tspolice.gov.in',
  },
  {
    district: 'Cyberabad (HITEC City)',
    state: 'Telangana',
    stationName: 'Cyberabad Cyber Crime Police Station',
    address: 'Cyberabad Police Commissionerate, Gachibowli, Hyderabad - 500032',
    shoPhone: '040-27853400',
    controlRoomPhone: '040-27853333 / 112',
    spOfficePhone: '040-27853200',
    email: 'cybercrime-cyb@tspolice.gov.in',
  },
  {
    district: 'Rachakonda',
    state: 'Telangana',
    stationName: 'Rachakonda Cyber Crime Police Station',
    address: 'Rachakonda Commissionerate, Neredmet, Hyderabad - 500056',
    shoPhone: '040-27854400',
    controlRoomPhone: '040-27854333 / 112',
    spOfficePhone: '040-27854200',
    email: 'cybercrime-rck@tspolice.gov.in',
  },
  {
    district: 'Warangal',
    state: 'Telangana',
    stationName: 'Warangal Cyber Crime Police Station',
    address: 'Warangal Police Commissionerate, Subedari, Hanamkonda - 506001',
    shoPhone: '0870-2444100',
    controlRoomPhone: '0870-2444200 / 112',
    spOfficePhone: '0870-2444300',
    email: 'cyber-wgl@tspolice.gov.in',
  },

  // National Metros
  {
    district: 'New Delhi / Central',
    state: 'Delhi NCR',
    stationName: 'Special Cell Cyber Crime Unit (IFSO)',
    address: 'Sector 16-C, Dwarka / Special Cell HQ, Lodhi Colony, New Delhi - 110078',
    shoPhone: '011-20892622',
    controlRoomPhone: '011-20892600 / 112',
    spOfficePhone: '011-23469100',
    email: 'ifso-specialcell@delhipolice.gov.in',
  },
  {
    district: 'Bengaluru Urban',
    state: 'Karnataka',
    stationName: 'Bengaluru City Cyber Crime Police Station (CEN)',
    address: 'CID Headquarters, Palace Road, Bengaluru - 560001',
    shoPhone: '080-22375526',
    controlRoomPhone: '080-22942222 / 112',
    spOfficePhone: '080-22201000',
    email: 'cybercrime-bcp@ksp.gov.in',
  },
];

interface CyberJurisdictionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectStation?: (station: StationInfo) => void;
}

export default function CyberJurisdictionModal({
  isOpen,
  onClose,
  onSelectStation,
}: CyberJurisdictionModalProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedState, setSelectedState] = useState<string>('All');

  if (!isOpen) return null;

  const filtered = POLICE_STATIONS.filter((s) => {
    const matchesState = selectedState === 'All' || s.state === selectedState;
    const matchesSearch =
      s.district.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.stationName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.address.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesState && matchesSearch;
  });

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 font-sans">
      <div className="bg-[#0e0e12] border border-white/[0.12] w-full max-w-3xl rounded-3xl p-6 shadow-2xl relative max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/[0.08]">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>District Cyber Police Station &amp; SHO Jurisdiction Finder</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  AP &amp; TELANGANA LIVE
                </span>
              </h3>
              <p className="text-xs text-white/40">Find your jurisdictional Cyber Cell, SHO contact &amp; FIR filing address</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-white/40 hover:text-white hover:bg-white/[0.06] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Filter Controls */}
        <div className="my-3 grid grid-cols-1 sm:grid-cols-3 gap-2">
          <div className="relative sm:col-span-2">
            <Search className="w-4 h-4 text-white/40 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by District (e.g. Kadapa, Hyderabad, Guntur, Visakhapatnam)..."
              className="w-full pl-10 pr-4 py-2 rounded-xl bg-white/[0.04] border border-white/[0.08] text-xs text-white placeholder-white/30 focus:outline-none focus:border-blue-500/50"
              autoFocus
            />
          </div>

          <select
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
            className="w-full px-3 py-2 rounded-xl bg-white/[0.04] border border-white/[0.08] text-xs text-white focus:outline-none focus:border-blue-500/50"
          >
            <option value="All" className="bg-[#131316]">All States</option>
            <option value="Andhra Pradesh" className="bg-[#131316]">Andhra Pradesh</option>
            <option value="Telangana" className="bg-[#131316]">Telangana</option>
            <option value="Delhi NCR" className="bg-[#131316]">Delhi NCR</option>
            <option value="Karnataka" className="bg-[#131316]">Karnataka</option>
          </select>
        </div>

        {/* List of Stations */}
        <div className="flex-1 overflow-y-auto space-y-3 pr-1">
          {filtered.map((s, idx) => (
            <div
              key={idx}
              className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] hover:border-blue-500/30 hover:bg-white/[0.04] transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sm text-white">{s.district}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full font-semibold bg-blue-500/15 text-blue-300 border border-blue-500/30">
                    {s.state}
                  </span>
                </div>
                <p className="text-xs font-semibold text-white/90">{s.stationName}</p>
                <p className="text-[11px] text-white/50 flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
                  <span>{s.address}</span>
                </p>
                <div className="flex flex-wrap items-center gap-3 pt-1 text-[11px] text-white/60">
                  <span className="flex items-center gap-1">
                    <Phone className="w-3 h-3 text-emerald-400" />
                    <strong>SHO Helpline:</strong> <a href={`tel:${s.shoPhone}`} className="text-emerald-400 hover:underline">{s.shoPhone}</a>
                  </span>
                  <span><strong>Control Room:</strong> {s.controlRoomPhone}</span>
                </div>
              </div>

              {onSelectStation && (
                <button
                  onClick={() => {
                    onSelectStation(s);
                    onClose();
                  }}
                  className="px-3.5 py-2 rounded-xl bg-blue-500/20 border border-blue-500/40 text-blue-300 font-semibold text-xs hover:bg-blue-500/30 transition-all whitespace-nowrap flex items-center gap-1.5 self-start sm:self-center"
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>Draft FIR to this SHO</span>
                </button>
              )}
            </div>
          ))}

          {filtered.length === 0 && (
            <div className="text-center py-10 text-white/40 text-xs">
              No matching police station found. Dial National Helpline <strong>1930</strong> or visit <a href="https://cybercrime.gov.in" target="_blank" rel="noreferrer" className="text-blue-400 underline">cybercrime.gov.in</a>.
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-white/[0.08] flex items-center justify-between text-xs text-white/40">
          <span>National Emergency Helpline: Dial <strong>1930</strong> (24x7 Cyber Crime) or <strong>112</strong> (Police).</span>
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
