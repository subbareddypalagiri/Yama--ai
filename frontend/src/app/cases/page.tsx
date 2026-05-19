'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Scale, Plus, Search, Filter, FolderOpen, FileText, Calendar, 
  Clock, AlertCircle, CheckCircle, Loader2, ArrowRight, MoreVertical,
  Trash2, Edit, Download
} from 'lucide-react';
import { getCases, createCase, deleteCase, Case, CaseCreate } from '@/lib/api';
import TiltCard from '@/components/ui/TiltCard';
import LanguageSelector from '@/components/LanguageSelector';
import { useLanguage } from '@/context/LanguageContext';

const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  active: 'bg-green-500/20 text-green-400 border-green-500/30',
  pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  resolved: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  closed: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
};

const PRIORITY_COLORS: Record<string, string> = {
  low: 'text-gray-400',
  medium: 'text-yellow-400',
  high: 'text-orange-400',
  urgent: 'text-red-400',
};

const CATEGORIES = ['criminal', 'civil', 'family', 'property', 'corporate', 'consumer', 'labor', 'other'];

export default function CasesPage() {
  const { t } = useLanguage();
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [creating, setCreating] = useState(false);

  const fetchCases = async () => {
    try {
      setLoading(true);
      const data = await getCases({ 
        search: searchQuery || undefined, 
        status: statusFilter || undefined 
      });
      setCases(data);
    } catch (err) {
      console.error('Failed to fetch cases:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, [searchQuery, statusFilter]);

  const handleCreateCase = async (data: CaseCreate) => {
    try {
      setCreating(true);
      await createCase(data);
      setShowCreateModal(false);
      fetchCases();
    } catch (err) {
      console.error('Failed to create case:', err);
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteCase = async (caseUid: string) => {
    if (!confirm('Are you sure you want to delete this case?')) return;
    try {
      await deleteCase(caseUid);
      fetchCases();
    } catch (err) {
      console.error('Failed to delete case:', err);
    }
  };

  const getStatusLabel = (status: string) => {
    const statusMap: Record<string, string> = {
      draft: t.cases.draft,
      active: t.cases.active,
      pending: t.cases.pending,
      resolved: t.cases.resolved,
      closed: t.cases.closed,
    };
    return statusMap[status] || status;
  };

  return (
    <div className="min-h-screen bg-[#030304] text-white">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-white/5 backdrop-blur-xl bg-[#030304]/80">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-lg text-gradient-hero">{t.hero.title}</span>
              <span className="hidden sm:block text-[11px] text-white/40">{t.features.caseTracking}</span>
            </div>
          </Link>
          
          <nav className="flex items-center gap-4">
            <Link href="/chat" className="px-4 py-2 text-sm text-white/50 hover:text-white transition-colors">
              {t.nav.chat}
            </Link>
            <Link href="/search" className="px-4 py-2 text-sm text-white/50 hover:text-white transition-colors">
              Search Laws
            </Link>
            <LanguageSelector />
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Page Title & Actions */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-bold font-display">{t.cases.title}</h1>
            <p className="text-white/40 text-sm mt-1">{t.features.caseTrackingDesc}</p>
          </div>
          
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium btn-glow text-white"
          >
            <Plus className="w-4 h-4" />
            {t.cases.newCase}
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
            <input
              type="text"
              placeholder={t.cases.search}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-11 pr-4 py-3 bg-white/[0.03] border border-white/10 rounded-xl text-sm focus:outline-none focus:border-purple-500/50 transition-colors"
            />
          </div>
          
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-3 bg-white/[0.03] border border-white/10 rounded-xl text-sm text-white/70 focus:outline-none focus:border-purple-500/50 cursor-pointer"
          >
            <option value="">{t.cases.allCases}</option>
            <option value="draft">{t.cases.draft}</option>
            <option value="active">{t.cases.active}</option>
            <option value="pending">{t.cases.pending}</option>
            <option value="resolved">{t.cases.resolved}</option>
            <option value="closed">{t.cases.closed}</option>
          </select>
        </div>

        {/* Cases Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
          </div>
        ) : cases.length === 0 ? (
          <div className="text-center py-20">
            <FolderOpen className="w-16 h-16 mx-auto text-white/20 mb-4" />
            <h3 className="text-lg font-medium text-white/60 mb-2">{t.cases.noResults}</h3>
            <p className="text-white/40 text-sm mb-6">{t.cases.createCase}</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium btn-glow text-white"
            >
              <Plus className="w-4 h-4" />
              {t.cases.createCase}
            </button>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {cases.map((caseItem) => (
              <TiltCard key={caseItem.case_uid} tiltAmount={8} scale={1.02}>
                <Link href={`/cases/${caseItem.case_uid}`}>
                  <div className="group p-6 rounded-2xl card-premium h-full cursor-pointer">
                    {/* Status & Priority */}
                    <div className="flex items-center justify-between mb-4">
                      <span className={`px-2.5 py-1 rounded-full text-[11px] font-medium border ${STATUS_COLORS[caseItem.status] || STATUS_COLORS.draft}`}>
                        {getStatusLabel(caseItem.status).toUpperCase()}
                      </span>
                      <span className={`text-xs font-medium ${PRIORITY_COLORS[caseItem.priority] || PRIORITY_COLORS.medium}`}>
                        {caseItem.priority.toUpperCase()}
                      </span>
                    </div>

                    {/* Title */}
                    <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-gradient-hero transition-all line-clamp-2">
                      {caseItem.title}
                    </h3>

                    {/* Category */}
                    {caseItem.category && (
                      <span className="inline-block px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 text-xs mb-3">
                        {caseItem.category}
                      </span>
                    )}

                    {/* Description */}
                    {caseItem.description && (
                      <p className="text-white/40 text-sm line-clamp-2 mb-4">
                        {caseItem.description}
                      </p>
                    )}

                    {/* Stats */}
                    <div className="flex items-center gap-4 text-xs text-white/30 mt-auto pt-4 border-t border-white/5">
                      <span className="flex items-center gap-1">
                        <FileText className="w-3.5 h-3.5" />
                        {caseItem.document_count} {t.cases.documents.toLowerCase()}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5" />
                        {caseItem.event_count} {t.cases.timeline.toLowerCase()}
                      </span>
                    </div>

                    {/* Footer */}
                    <div className="flex items-center justify-between mt-4 pt-4 border-t border-white/5">
                      <span className="text-[11px] text-white/30">
                        {new Date(caseItem.created_at).toLocaleDateString()}
                      </span>
                      <ArrowRight className="w-4 h-4 text-white/30 group-hover:text-purple-400 group-hover:translate-x-1 transition-all" />
                    </div>
                  </div>
                </Link>
              </TiltCard>
            ))}
          </div>
        )}
      </main>

      {/* Create Case Modal */}
      {showCreateModal && (
        <CreateCaseModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateCase}
          loading={creating}
        />
      )}
    </div>
  );
}

function CreateCaseModal({ 
  onClose, 
  onSubmit, 
  loading 
}: { 
  onClose: () => void; 
  onSubmit: (data: CaseCreate) => void;
  loading: boolean;
}) {
  const { t } = useLanguage();
  const [formData, setFormData] = useState<CaseCreate>({
    title: '',
    description: '',
    category: '',
    priority: 'medium',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim()) return;
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-lg bg-[#0a0a0c] border border-white/10 rounded-2xl shadow-2xl">
        <div className="p-6 border-b border-white/5">
          <h2 className="text-xl font-semibold">{t.cases.createCase}</h2>
          <p className="text-white/40 text-sm mt-1">{t.features.caseTrackingDesc}</p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">{t.cases.caseTitle} *</label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="e.g., Property Dispute - XYZ vs ABC"
              className="w-full px-4 py-3 bg-white/[0.03] border border-white/10 rounded-xl text-sm focus:outline-none focus:border-purple-500/50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">{t.cases.description}</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder={t.cases.description}
              rows={3}
              className="w-full px-4 py-3 bg-white/[0.03] border border-white/10 rounded-xl text-sm focus:outline-none focus:border-purple-500/50 resize-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-white/70 mb-2">Category</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-4 py-3 bg-white/[0.03] border border-white/10 rounded-xl text-sm focus:outline-none focus:border-purple-500/50"
              >
                <option value="">Select...</option>
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-white/70 mb-2">{t.cases.priority}</label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                className="w-full px-4 py-3 bg-white/[0.03] border border-white/10 rounded-xl text-sm focus:outline-none focus:border-purple-500/50"
              >
                <option value="low">{t.cases.low}</option>
                <option value="medium">{t.cases.medium}</option>
                <option value="high">{t.cases.high}</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 text-sm text-white/60 hover:text-white transition-colors"
            >
              {t.common.cancel}
            </button>
            <button
              type="submit"
              disabled={loading || !formData.title.trim()}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium btn-glow text-white disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
              {t.cases.createCase}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
