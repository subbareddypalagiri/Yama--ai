export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  relevantSections?: LawSection[];
}

export interface LawSection {
  id: number;
  act_name: string;
  section_number: string;
  title: string;
  description: string;
  keywords: string | null;
  category: string;
  punishment: string | null;
  old_law_reference: string | null;
}

export interface ChatApiResponse {
  session_id: string;
  analysis: string;
  relevant_sections: LawSection[];
  timestamp: string;
}

export interface SearchApiResponse {
  query: string;
  results: LawSection[];
  total: number;
}
