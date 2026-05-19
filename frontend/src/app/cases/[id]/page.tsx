'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  Scale, ArrowLeft, FileText, Calendar, Upload, Download, Trash2, 
  Edit, Plus, Clock, AlertCircle, CheckCircle, Loader2, Brain,
  File, Image, FileType, X, MoreVertical, RefreshCw
} from 'lucide-react';
import { 
  getCase, updateCase, deleteCase, getCaseEvents, createCaseEvent,
  getDocuments, uploadDocument, deleteDocument, analyzeDocument,
  generateReport, getReportDownloadUrl,
  Case, CaseEvent, Document
} from '@/lib/api';

const STATUS_OPTIONS = ['draft', 'active', 'pending', 'resolved', 'closed'];
const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-gray-500/20 text-gray-400',
  active: 'bg-green-500/20 text-green-400',
  pending: 'bg-yellow-500/20 text-yellow-400',
  resolved: 'bg-blue-500/20 text-blue-400',
  closed: 'bg-purple-500/20 text-purple-400',
};

const DOC_TYPE_ICONS: Record<string, any> = {
  complaint: FileText,
  fir: FileText,
  evidence: File,
  contract: FileType,
  court_order: FileText,
  legal_notice: FileText,
  affidavit: FileText,
  other: File,
};

export default function CaseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params.id as string;

  const [caseData, setCaseData] = useState<Case | null>(null);
  const [events, setEvents] = useState<CaseEvent[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'documents' | 'timeline'>('overview');
  
  // Modals
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showEventModal, setShowEventModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  
  // Actions
  const [uploading, setUploading] = useState(false);
  const [generatingPdf, setGeneratingPdf] = useState(false);
  const [analyzingDoc, setAnalyzingDoc] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const [caseRes, eventsRes, docsRes] = await Promise.all([
        getCase(caseId),
        getCaseEvents(caseId),
        getDocuments(caseId),
      ]);
      setCaseData(caseRes);
      setEvents(eventsRes);
      setDocuments(docsRes);
    } catch (err) {
      console.error('Failed to fetch case:', err);
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleStatusChange = async (newStatus: string) => {
    if (!caseData) return;
    try {
      const updated = await updateCase(caseId, { status: newStatus });
      setCaseData(updated);
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

  const handleDeleteCase = async () => {
    if (!confirm('Are you sure you want to delete this case? This action cannot be undone.')) return;
    try {
      await deleteCase(caseId);
      router.push('/cases');
    } catch (err) {
      console.error('Failed to delete case:', err);
    }
  };

  const handleUpload = async (file: File, docType: string) => {
    try {
      setUploading(true);
      await uploadDocument(file, caseId, docType);
      setShowUploadModal(false);
      const docsRes = await getDocuments(caseId);
      setDocuments(docsRes);
    } catch (err) {
      console.error('Failed to upload:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDoc = async (docUid: string) => {
    if (!confirm('Delete this document?')) return;
    try {
      await deleteDocument(docUid);
      setDocuments(documents.filter(d => d.doc_uid !== docUid));
    } catch (err) {
      console.error('Failed to delete document:', err);
    }
  };

  const handleAnalyzeDoc = async (docUid: string) => {
    try {
      setAnalyzingDoc(docUid);
      await analyzeDocument(docUid);
      const docsRes = await getDocuments(caseId);
      setDocuments(docsRes);
    } catch (err) {
      console.error('Failed to analyze:', err);
    } finally {
      setAnalyzingDoc(null);
    }
  };

  const handleGeneratePdf = async () => {
    if (!caseData) return;
    try {
      setGeneratingPdf(true);
      const report = await generateReport({
        case_uid: caseId,
        report_type: 'case_summary',
        title: `Case Summary - ${caseData.title}`,
        include_documents: true,
        include_timeline: true,
        include_analysis: true,
      });
      
      // Download the report
      const downloadUrl = getReportDownloadUrl(report.report_uid);
      window.open(downloadUrl, '_blank');
    } catch (err) {
      console.error('Failed to generate PDF:', err);
    } finally {
      setGeneratingPdf(false);
    }
  };

  const handleAddEvent = async (data: { event_type: string; title: string; description?: string; event_date: string }) => {
    try {
      await createCaseEvent(caseId, data);
      const eventsRes = await getCaseEvents(caseId);
      setEvents(eventsRes);
      setShowEventModal(false);
    } catch (err) {
      console.error('Failed to add event:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#030304] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
      </div>
    );
  }

  if (!caseData) {
    return (
      <div className="min-h-screen bg-[#030304] flex items-center justify-center text-white/60">
        Case not found
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#030304] text-white">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-white/5 backdrop-blur-xl bg-[#030304]/80">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/cases" className="p-2 rounded-lg hover:bg-white/5 transition-colors">
              <ArrowLeft className="w-5 h-5 text-white/60" />
            </Link>
            <div>
              <h1 className="text-lg font-semibold line-clamp-1">{caseData.title}</h1>
              <div className="flex items-center gap-2 mt-0.5">
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${STATUS_COLORS[caseData.status]}`}>
                  {caseData.status.toUpperCase()}
                </span>
                {caseData.category && (
                  <span className="text-xs text-white/40">{caseData.category}</span>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleGeneratePdf}
              disabled={generatingPdf}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-sm transition-colors disabled:opacity-50"
            >
              {generatingPdf ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
              Export PDF
            </button>
            <button
              onClick={() => setShowUploadModal(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg btn-glow text-sm"
            >
              <Upload className="w-4 h-4" />
              Upload
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Tabs */}
        <div className="flex items-center gap-1 mb-8 p-1 bg-white/[0.03] rounded-xl w-fit">
          {(['overview', 'documents', 'timeline'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab 
                  ? 'bg-purple-500/20 text-purple-400' 
                  : 'text-white/50 hover:text-white/80'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Main Info */}
            <div className="lg:col-span-2 space-y-6">
              {/* Description */}
              <div className="p-6 rounded-2xl card-premium">
                <h3 className="text-sm font-medium text-white/50 mb-3">Description</h3>
                <p className="text-white/80 leading-relaxed">
                  {caseData.description || 'No description provided.'}
                </p>
              </div>

              {/* AI Summary */}
              {caseData.ai_summary && (
                <div className="p-6 rounded-2xl card-premium border-l-4 border-purple-500">
                  <div className="flex items-center gap-2 mb-3">
                    <Brain className="w-4 h-4 text-purple-400" />
                    <h3 className="text-sm font-medium text-purple-400">AI Analysis</h3>
                  </div>
                  <p className="text-white/70 leading-relaxed text-sm">
                    {caseData.ai_summary}
                  </p>
                </div>
              )}

              {/* Relevant Laws */}
              {caseData.relevant_laws && (
                <div className="p-6 rounded-2xl card-premium">
                  <h3 className="text-sm font-medium text-white/50 mb-3">Relevant Laws</h3>
                  <p className="text-white/70 text-sm">{caseData.relevant_laws}</p>
                </div>
              )}
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Status */}
              <div className="p-6 rounded-2xl card-premium">
                <h3 className="text-sm font-medium text-white/50 mb-3">Status</h3>
                <select
                  value={caseData.status}
                  onChange={(e) => handleStatusChange(e.target.value)}
                  className="w-full px-3 py-2 bg-white/[0.03] border border-white/10 rounded-lg text-sm focus:outline-none focus:border-purple-500/50"
                >
                  {STATUS_OPTIONS.map((s) => (
                    <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
                  ))}
                </select>
              </div>

              {/* Details */}
              <div className="p-6 rounded-2xl card-premium space-y-4">
                <h3 className="text-sm font-medium text-white/50 mb-3">Details</h3>
                
                {caseData.client_name && (
                  <div>
                    <span className="text-xs text-white/40">Client</span>
                    <p className="text-sm text-white/80">{caseData.client_name}</p>
                  </div>
                )}
                
                {caseData.opponent_name && (
                  <div>
                    <span className="text-xs text-white/40">Opponent</span>
                    <p className="text-sm text-white/80">{caseData.opponent_name}</p>
                  </div>
                )}
                
                {caseData.court_name && (
                  <div>
                    <span className="text-xs text-white/40">Court</span>
                    <p className="text-sm text-white/80">{caseData.court_name}</p>
                  </div>
                )}
                
                {caseData.case_number && (
                  <div>
                    <span className="text-xs text-white/40">Case Number</span>
                    <p className="text-sm text-white/80">{caseData.case_number}</p>
                  </div>
                )}

                {caseData.next_hearing_date && (
                  <div>
                    <span className="text-xs text-white/40">Next Hearing</span>
                    <p className="text-sm text-white/80">
                      {new Date(caseData.next_hearing_date).toLocaleDateString()}
                    </p>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="p-6 rounded-2xl card-premium">
                <h3 className="text-sm font-medium text-white/50 mb-3">Actions</h3>
                <div className="space-y-2">
                  <button
                    onClick={() => setShowEditModal(true)}
                    className="w-full flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-sm transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                    Edit Case
                  </button>
                  <button
                    onClick={handleDeleteCase}
                    className="w-full flex items-center gap-2 px-4 py-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 text-sm transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete Case
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Documents Tab */}
        {activeTab === 'documents' && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold">Documents ({documents.length})</h2>
              <button
                onClick={() => setShowUploadModal(true)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg btn-glow text-sm"
              >
                <Upload className="w-4 h-4" />
                Upload Document
              </button>
            </div>

            {documents.length === 0 ? (
              <div className="text-center py-16 rounded-2xl card-premium">
                <FileText className="w-12 h-12 mx-auto text-white/20 mb-4" />
                <p className="text-white/40">No documents uploaded yet</p>
              </div>
            ) : (
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {documents.map((doc) => {
                  const IconComponent = DOC_TYPE_ICONS[doc.document_type] || File;
                  return (
                    <div key={doc.doc_uid} className="p-4 rounded-xl card-premium group">
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                          <IconComponent className="w-5 h-5 text-purple-400" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-white/90 truncate">
                            {doc.title || doc.original_filename}
                          </p>
                          <p className="text-xs text-white/40 mt-0.5">
                            {doc.document_type} • {(doc.file_size || 0 / 1024).toFixed(1)} KB
                          </p>
                        </div>
                      </div>

                      {doc.ai_analysis && (
                        <div className="mt-3 p-2 rounded-lg bg-purple-500/10 text-xs text-purple-300 line-clamp-2">
                          {doc.ai_analysis.slice(0, 100)}...
                        </div>
                      )}

                      <div className="flex items-center gap-2 mt-4 pt-3 border-t border-white/5">
                        <button
                          onClick={() => handleAnalyzeDoc(doc.doc_uid)}
                          disabled={analyzingDoc === doc.doc_uid}
                          className="flex items-center gap-1 px-2 py-1 rounded text-xs bg-white/5 hover:bg-white/10 transition-colors disabled:opacity-50"
                        >
                          {analyzingDoc === doc.doc_uid ? (
                            <Loader2 className="w-3 h-3 animate-spin" />
                          ) : (
                            <Brain className="w-3 h-3" />
                          )}
                          Analyze
                        </button>
                        <button
                          onClick={() => handleDeleteDoc(doc.doc_uid)}
                          className="flex items-center gap-1 px-2 py-1 rounded text-xs bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Timeline Tab */}
        {activeTab === 'timeline' && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold">Timeline ({events.length})</h2>
              <button
                onClick={() => setShowEventModal(true)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg btn-glow text-sm"
              >
                <Plus className="w-4 h-4" />
                Add Event
              </button>
            </div>

            {events.length === 0 ? (
              <div className="text-center py-16 rounded-2xl card-premium">
                <Calendar className="w-12 h-12 mx-auto text-white/20 mb-4" />
                <p className="text-white/40">No events added yet</p>
              </div>
            ) : (
              <div className="space-y-4">
                {events.sort((a, b) => new Date(b.event_date).getTime() - new Date(a.event_date).getTime()).map((event) => (
                  <div key={event.id} className="flex gap-4 p-4 rounded-xl card-premium">
                    <div className="w-12 text-center flex-shrink-0">
                      <p className="text-lg font-bold text-purple-400">
                        {new Date(event.event_date).getDate()}
                      </p>
                      <p className="text-[10px] text-white/40 uppercase">
                        {new Date(event.event_date).toLocaleDateString('en', { month: 'short' })}
                      </p>
                    </div>
                    <div className="flex-1">
                      <span className="inline-block px-2 py-0.5 rounded text-[10px] font-medium bg-white/5 text-white/50 mb-1">
                        {event.event_type}
                      </span>
                      <h4 className="text-sm font-medium text-white/90">{event.title}</h4>
                      {event.description && (
                        <p className="text-xs text-white/50 mt-1">{event.description}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Upload Modal */}
      {showUploadModal && (
        <UploadModal
          onClose={() => setShowUploadModal(false)}
          onUpload={handleUpload}
          loading={uploading}
        />
      )}

      {/* Event Modal */}
      {showEventModal && (
        <EventModal
          onClose={() => setShowEventModal(false)}
          onSubmit={handleAddEvent}
        />
      )}
    </div>
  );
}

function UploadModal({ onClose, onUpload, loading }: { onClose: () => void; onUpload: (file: File, type: string) => void; loading: boolean }) {
  const [file, setFile] = useState<File | null>(null);
  const [docType, setDocType] = useState('other');
  const [dragActive, setDragActive] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-md bg-[#0a0a0c] border border-white/10 rounded-2xl">
        <div className="p-6 border-b border-white/5 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Upload Document</h2>
          <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-lg transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-6 space-y-5">
          <div
            onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
              dragActive ? 'border-purple-500 bg-purple-500/10' : 'border-white/10'
            }`}
          >
            {file ? (
              <div className="flex items-center gap-3">
                <FileText className="w-8 h-8 text-purple-400" />
                <div className="text-left">
                  <p className="text-sm font-medium">{file.name}</p>
                  <p className="text-xs text-white/40">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
                <button onClick={() => setFile(null)} className="ml-auto p-1 hover:bg-white/10 rounded">
                  <X className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <>
                <Upload className="w-10 h-10 mx-auto text-white/30 mb-3" />
                <p className="text-white/50 text-sm">Drag & drop or click to upload</p>
                <input
                  type="file"
                  onChange={(e) => e.target.files?.[0] && setFile(e.target.files[0])}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                  accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                />
              </>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Document Type</label>
            <select
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              className="w-full px-4 py-3 bg-white/[0.03] border border-white/10 rounded-xl text-sm focus:outline-none focus:border-purple-500/50"
            >
              <option value="complaint">Complaint</option>
              <option value="fir">FIR</option>
              <option value="evidence">Evidence</option>
              <option value="contract">Contract</option>
              <option value="court_order">Court Order</option>
              <option value="legal_notice">Legal Notice</option>
              <option value="affidavit">Affidavit</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div className="flex items-center justify-end gap-3 pt-4">
            <button onClick={onClose} className="px-5 py-2.5 text-sm text-white/60 hover:text-white transition-colors">
              Cancel
            </button>
            <button
              onClick={() => file && onUpload(file, docType)}
              disabled={!file || loading}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium btn-glow text-white disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
              Upload
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function EventModal({ onClose, onSubmit }: { onClose: () => void; onSubmit: (data: any) => void }) {
  const [formData, setFormData] = useState({
    event_type: 'note',
    title: '',
    description: '',
    event_date: new Date().toISOString().split('T')[0],
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim()) return;
    onSubmit({
      ...formData,
      event_date: new Date(formData.event_date).toISOString(),
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-md bg-[#0a0a0c] border border-white/10 rounded-2xl">
        <div className="p-6 border-b border-white/5 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Add Event</h2>
          <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-lg transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Event Type</label>
            <select
              value={formData.event_type}
              onChange={(e) => setFormData({ ...formData, event_type: e.target.value })}
              className="w-full px-4 py-3 bg-white/[0.03] border border-white/10 rounded-xl text-sm focus:outline-none focus:border-purple-500/50"
            >
              <option value="note">Note</option>
              <option value="hearing">Hearing</option>
              <option value="document">Document Filed</option>
              <option value="milestone">Milestone</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Title</label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Event title..."
              className="w-full px-4 py-3 bg-white/[0.03] border border-white/10 rounded-xl text-sm focus:outline-none focus:border-purple-500/50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Date</label>
            <input
              type="date"
              value={formData.event_date}
              onChange={(e) => setFormData({ ...formData, event_date: e.target.value })}
              className="w-full px-4 py-3 bg-white/[0.03] border border-white/10 rounded-xl text-sm focus:outline-none focus:border-purple-500/50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Description (optional)</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Additional details..."
              rows={3}
              className="w-full px-4 py-3 bg-white/[0.03] border border-white/10 rounded-xl text-sm focus:outline-none focus:border-purple-500/50 resize-none"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-4">
            <button type="button" onClick={onClose} className="px-5 py-2.5 text-sm text-white/60 hover:text-white transition-colors">
              Cancel
            </button>
            <button
              type="submit"
              disabled={!formData.title.trim()}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium btn-glow text-white disabled:opacity-50"
            >
              <Plus className="w-4 h-4" />
              Add Event
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
