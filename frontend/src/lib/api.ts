const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL?.trim();

export const API_BASE = configuredApiUrl
  ? `${configuredApiUrl.replace(/\/$/, '')}/api/v1`
  : 'http://localhost:8080/api/v1';

export type ChatResponseStyle = 'default' | 'roman_english';

export async function sendChatMessage(
  message: string, 
  sessionId?: string, 
  responseStyle: ChatResponseStyle = 'default', 
  responseLanguage?: string,
  customApiKey?: string,
  customModel?: string
) {
  // Keeping this for backward compatibility (e.g. if we switch back to non-stream)
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 180000);
  
  try {
    const res = await fetch(`${API_BASE}/chat/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        message, 
        session_id: sessionId, 
        response_style: responseStyle,
        response_language: responseLanguage,
        custom_api_key: customApiKey,
        custom_model: customModel
      }),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    if (!res.ok) throw new Error(`Chat failed: ${res.statusText}`);
    return res.json();
  } catch (err: unknown) {
    clearTimeout(timeoutId);
    if (err instanceof Error && err.name === 'AbortError') {
      throw new Error('Request timed out. The AI is taking too long to respond.');
    }
    throw err;
  }
}

export async function sendChatMessageStream(
  message: string, 
  onChunk: (text: string) => void,
  sessionId?: string, 
  responseStyle: ChatResponseStyle = 'default', 
  responseLanguage?: string,
  customApiKey?: string,
  customModel?: string
): Promise<{session_id: string, analysis: string}> {
  return new Promise((resolve, reject) => {
    let fullAnalysis = "";
    
    // Lazy import so it doesn't break Next.js server components if imported
    import('@microsoft/fetch-event-source').then(({ fetchEventSource }) => {
      fetchEventSource(`${API_BASE}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          session_id: sessionId,
          response_style: responseStyle,
          custom_api_key: customApiKey?.trim() || undefined,
          custom_model: customModel?.trim() || undefined
        }),
        onmessage(ev) {
          if (ev.data === '[DONE]') return;
          
          let actualText = ev.data;
          try {
            const json = JSON.parse(ev.data);
            if (json.candidates?.[0]?.content?.parts?.[0]?.text) {
               actualText = json.candidates[0].content.parts[0].text;
            } else {
               actualText = "";
            }
          } catch(e) { }
          
          if (actualText) {
            fullAnalysis += actualText;
            onChunk(actualText);
          }
        },
        onclose() {
          resolve({ session_id: sessionId || "stream_session", analysis: fullAnalysis });
        },
        onerror(err) {
          reject(err);
          throw err;
        }
      });
    }).catch(reject);
  });
}

export async function uploadChatMessage(
  file: File,
  message: string, 
  sessionId?: string, 
  responseStyle: ChatResponseStyle = 'default', 
  responseLanguage?: string,
  customApiKey?: string,
  customModel?: string
) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 180000);
  
  const formData = new FormData();
  formData.append('file', file);
  formData.append('message', message);
  if (sessionId) formData.append('session_id', sessionId);
  formData.append('response_style', responseStyle);
  if (responseLanguage) formData.append('response_language', responseLanguage);
  if (customApiKey) formData.append('custom_api_key', customApiKey);
  if (customModel) formData.append('custom_model', customModel);

  try {
    const res = await fetch(`${API_BASE}/chat/upload`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    if (!res.ok) throw new Error(`Chat upload failed: ${res.statusText}`);
    return res.json();
  } catch (err: unknown) {
    clearTimeout(timeoutId);
    if (err instanceof Error && err.name === 'AbortError') {
      throw new Error('Request timed out. The AI is taking too long to respond.');
    }
    throw err;
  }
}

export async function searchLaws(query: string, category?: string, limit = 20) {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  if (category) params.set('category', category);
  const res = await fetch(`${API_BASE}/laws/search?${params}`);
  if (!res.ok) throw new Error(`Search failed: ${res.statusText}`);
  return res.json();
}

export async function searchStateLaws(query: string, stateCode?: string, limit = 20) {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  if (stateCode) params.set('state_code', stateCode);
  const res = await fetch(`${API_BASE}/laws/state?${params}`);
  if (!res.ok) throw new Error(`State search failed: ${res.statusText}`);
  return res.json();
}

export async function searchSupremeCourt(query: string, limit = 20) {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  const res = await fetch(`${API_BASE}/laws/supreme-court?${params}`);
  if (!res.ok) throw new Error(`Supreme Court search failed: ${res.statusText}`);
  return res.json();
}

export async function searchHighCourts(query: string, courtCode?: string, stateCode?: string, limit = 20) {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  if (courtCode) params.set('court_code', courtCode);
  if (stateCode) params.set('state_code', stateCode);
  const res = await fetch(`${API_BASE}/laws/high-courts?${params}`);
  if (!res.ok) throw new Error(`High Court search failed: ${res.statusText}`);
  return res.json();
}

export async function getLegalDatabaseStats() {
  const res = await fetch(`${API_BASE}/laws/stats`);
  if (!res.ok) throw new Error(`Stats fetch failed: ${res.statusText}`);
  return res.json();
}

export async function getSectionsByAct(actName: string) {
  const res = await fetch(`${API_BASE}/laws/sections/${encodeURIComponent(actName)}`);
  if (!res.ok) throw new Error(`Failed to load sections: ${res.statusText}`);
  return res.json();
}

export async function getLawById(id: number) {
  const res = await fetch(`${API_BASE}/laws/${id}`);
  if (!res.ok) throw new Error(`Failed to load law: ${res.statusText}`);
  return res.json();
}

export async function getActs() {
  const res = await fetch(`${API_BASE}/laws/acts`);
  if (!res.ok) throw new Error(`Failed to load acts: ${res.statusText}`);
  return res.json();
}

export async function getCategories() {
  const res = await fetch(`${API_BASE}/laws/categories`);
  if (!res.ok) throw new Error(`Failed to load categories: ${res.statusText}`);
  return res.json();
}

export async function healthCheck() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

// ============ CASES ============

export interface Case {
  id: number;
  case_uid: string;
  title: string;
  description?: string;
  category?: string;
  status: string;
  priority: string;
  client_name?: string;
  opponent_name?: string;
  court_name?: string;
  case_number?: string;
  next_hearing_date?: string;
  ai_summary?: string;
  relevant_laws?: string;
  risk_assessment?: string;
  created_at: string;
  updated_at?: string;
  document_count: number;
  event_count: number;
}

export interface CaseCreate {
  title: string;
  description?: string;
  category?: string;
  priority?: string;
  client_name?: string;
  opponent_name?: string;
  court_name?: string;
  case_number?: string;
  next_hearing_date?: string;
}

export interface CaseEvent {
  id: number;
  event_type: string;
  title: string;
  description?: string;
  event_date: string;
  created_at: string;
}

export async function getCases(params?: { status?: string; category?: string; search?: string }): Promise<Case[]> {
  const query = new URLSearchParams();
  if (params?.status) query.set('status', params.status);
  if (params?.category) query.set('category', params.category);
  if (params?.search) query.set('search', params.search);
  
  const res = await fetch(`${API_BASE}/cases?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch cases');
  return res.json();
}

export async function getCase(caseUid: string): Promise<Case> {
  const res = await fetch(`${API_BASE}/cases/${caseUid}`);
  if (!res.ok) throw new Error('Failed to fetch case');
  return res.json();
}

export async function createCase(data: CaseCreate): Promise<Case> {
  const res = await fetch(`${API_BASE}/cases`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create case');
  return res.json();
}

export async function updateCase(caseUid: string, data: Partial<CaseCreate & { status?: string }>): Promise<Case> {
  const res = await fetch(`${API_BASE}/cases/${caseUid}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to update case');
  return res.json();
}

export async function deleteCase(caseUid: string): Promise<void> {
  const res = await fetch(`${API_BASE}/cases/${caseUid}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete case');
}

export async function getCaseEvents(caseUid: string): Promise<CaseEvent[]> {
  const res = await fetch(`${API_BASE}/cases/${caseUid}/events`);
  if (!res.ok) throw new Error('Failed to fetch events');
  return res.json();
}

export async function createCaseEvent(caseUid: string, data: { event_type: string; title: string; description?: string; event_date: string }): Promise<CaseEvent> {
  const res = await fetch(`${API_BASE}/cases/${caseUid}/events`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create event');
  return res.json();
}

// ============ DOCUMENTS ============

export interface Document {
  id: number;
  doc_uid: string;
  case_id?: number;
  filename: string;
  original_filename: string;
  file_size?: number;
  mime_type?: string;
  document_type: string;
  title?: string;
  description?: string;
  extracted_text?: string;
  ocr_processed: boolean;
  ai_analysis?: string;
  detected_entities?: string;
  relevant_laws?: string;
  uploaded_at: string;
  analyzed_at?: string;
}

export async function uploadDocument(file: File, caseUid?: string, documentType?: string, title?: string): Promise<Document> {
  const formData = new FormData();
  formData.append('file', file);
  if (caseUid) formData.append('case_uid', caseUid);
  if (documentType) formData.append('document_type', documentType);
  if (title) formData.append('title', title);
  
  const res = await fetch(`${API_BASE}/documents`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to upload document');
  return res.json();
}

export async function getDocuments(caseUid?: string): Promise<Document[]> {
  const query = caseUid ? `?case_uid=${caseUid}` : '';
  const res = await fetch(`${API_BASE}/documents${query}`);
  if (!res.ok) throw new Error('Failed to fetch documents');
  return res.json();
}

export async function analyzeDocument(docUid: string): Promise<{ status: string; analysis?: string }> {
  const res = await fetch(`${API_BASE}/documents/${docUid}/analyze`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to analyze document');
  return res.json();
}

export async function deleteDocument(docUid: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${docUid}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete document');
}

// ============ REPORTS ============

export interface Report {
  id: number;
  report_uid: string;
  case_id?: number;
  report_type: string;
  title: string;
  file_size?: number;
  generated_at: string;
  download_url?: string;
}

export async function generateReport(data: {
  case_uid?: string;
  report_type?: string;
  title: string;
  include_documents?: boolean;
  include_timeline?: boolean;
  include_analysis?: boolean;
}): Promise<Report> {
  const res = await fetch(`${API_BASE}/reports`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to generate report');
  return res.json();
}

export async function getReports(caseUid?: string): Promise<Report[]> {
  const query = caseUid ? `?case_uid=${caseUid}` : '';
  const res = await fetch(`${API_BASE}/reports${query}`);
  if (!res.ok) throw new Error('Failed to fetch reports');
  return res.json();
}

export function getReportDownloadUrl(reportUid: string): string {
  return `${API_BASE}/reports/${reportUid}/download`;
}

// ============ INTELLIGENCE SUITE ============

export interface ScorecardData {
  win_probability: number;
  risk_level: 'Low' | 'Medium' | 'High' | 'Critical';
  primary_risk_factor: string;
  evidence_booster_tips: string[];
  applicable_bns_section: string;
}

export interface PersonaView {
  role: string;
  title: string;
  arguments: string[];
  legal_citations: string[];
}

export interface SimulationData {
  counsel_view: PersonaView;
  defense_view: PersonaView;
  judge_verdict: PersonaView;
  summary: string;
}

export interface EstimatorData {
  case_type: string;
  estimated_duration: string;
  court_fee_stamp_duty: string;
  lawyer_fee_range: string;
  fast_track_remedy: string;
  key_steps_count: number;
}

export async function analyzeScorecard(situation: string): Promise<ScorecardData> {
  const res = await fetch(`${API_BASE}/analyze/scorecard`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ situation }),
  });
  if (!res.ok) throw new Error('Failed to load scorecard');
  return res.json();
}

export async function analyzeSimulate(situation: string): Promise<SimulationData> {
  const res = await fetch(`${API_BASE}/analyze/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ situation }),
  });
  if (!res.ok) throw new Error('Failed to load courtroom simulation');
  return res.json();
}

export async function analyzeEstimator(situation: string): Promise<EstimatorData> {
  const res = await fetch(`${API_BASE}/analyze/estimator`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ situation }),
  });
  if (!res.ok) throw new Error('Failed to load cost estimator');
  return res.json();
}

