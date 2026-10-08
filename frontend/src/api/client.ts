import type {
  Case,
  Evidence,
  FindingsResponse,
  HealthStatus,
  Decision,
  Review,
  OfficialRecord
} from '../types';

const API_BASE = '/api';

export const api = {
  async getHealth(): Promise<HealthStatus> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Failed to fetch system health');
    return res.json();
  },

  async listCases(status?: string): Promise<Case[]> {
    const url = status ? `${API_BASE}/cases?status=${encodeURIComponent(status)}` : `${API_BASE}/cases`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch cases');
    return res.json();
  },

  async getCase(id: string): Promise<Case> {
    const res = await fetch(`${API_BASE}/cases/${encodeURIComponent(id)}`);
    if (!res.ok) throw new Error('Failed to fetch case');
    return res.json();
  },

  async createCase(data: {
    title: string;
    category?: string;
    location?: string;
    reporter?: string;
    description?: string;
  }): Promise<Case> {
    const res = await fetch(`${API_BASE}/cases`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create case');
    return res.json();
  },

  async getCaseEvidence(id: string): Promise<Evidence[]> {
    const res = await fetch(`${API_BASE}/cases/${encodeURIComponent(id)}/evidence`);
    if (!res.ok) throw new Error('Failed to fetch evidence');
    return res.json();
  },

  async uploadEvidence(
    caseId: string,
    file?: File | null,
    textContent?: string,
    sourceType?: string,
    location?: string,
    uploader?: string
  ): Promise<Evidence> {
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    }
    if (textContent) {
      formData.append('text_content', textContent);
    }
    if (sourceType) {
      formData.append('source_type', sourceType);
    }
    if (location) {
      formData.append('location', location);
    }
    if (uploader) {
      formData.append('uploader', uploader);
    }

    const res = await fetch(`${API_BASE}/cases/${encodeURIComponent(caseId)}/evidence`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to upload evidence');
    }
    return res.json();
  },

  async extractEvidence(evidenceId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/evidence/${encodeURIComponent(evidenceId)}/extract`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to extract evidence');
    return res.json();
  },

  async analyzeCase(caseId: string): Promise<Decision> {
    const res = await fetch(`${API_BASE}/cases/${encodeURIComponent(caseId)}/analyze`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to analyze case');
    return res.json();
  },

  async getCaseFindings(caseId: string): Promise<FindingsResponse> {
    const res = await fetch(`${API_BASE}/cases/${encodeURIComponent(caseId)}/findings`);
    if (!res.ok) throw new Error('Failed to fetch case findings');
    return res.json();
  },

  async submitReview(
    caseId: string,
    reviewer: string,
    newDecision: string,
    reason: string
  ): Promise<Review> {
    const res = await fetch(`${API_BASE}/cases/${encodeURIComponent(caseId)}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviewer, new_decision: newDecision, reason }),
    });
    if (!res.ok) throw new Error('Failed to submit human review');
    return res.json();
  },

  async requestMoreEvidence(
    caseId: string,
    requestedBy: string,
    evidenceTypeNeeded: string,
    notes?: string
  ): Promise<any> {
    const res = await fetch(`${API_BASE}/cases/${encodeURIComponent(caseId)}/request-evidence`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        requested_by: requestedBy,
        evidence_type_needed: evidenceTypeNeeded,
        notes,
      }),
    });
    if (!res.ok) throw new Error('Failed to request additional evidence');
    return res.json();
  },

  async getCaseReportUrl(caseId: string, format: 'json' | 'html' = 'html'): Promise<string> {
    return `${API_BASE}/cases/${encodeURIComponent(caseId)}/report?format=${format}`;
  },

  async getDemoCases(): Promise<{ count: number; cases: any[] }> {
    const res = await fetch(`${API_BASE}/demo/cases`);
    if (!res.ok) throw new Error('Failed to load demo cases catalog');
    return res.json();
  },

  async seedHeroDemo(runAnalysis: boolean = true): Promise<{ case_id: string; message: string }> {
    return this.seedDemoCase('DEMO-001', runAnalysis);
  },

  async seedDemoCase(caseIdOrType: string | number, runAnalysis: boolean = true): Promise<{ case_id: string; message: string }> {
    const caseMap: Record<string, string> = {
      '1': 'DEMO-001',
      '2': 'DEMO-002',
      '3': 'DEMO-003',
      '4': 'DEMO-004',
      '5': 'DEMO-005',
    };
    const targetCase = caseMap[String(caseIdOrType)] || String(caseIdOrType);
    const res = await fetch(`${API_BASE}/demo/cases/${encodeURIComponent(targetCase)}/seed?run_analysis=${runAnalysis}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error(`Failed to seed Demo Case ${targetCase}`);
    return res.json();
  },

  async seedAllDemoCases(runAnalysis: boolean = true): Promise<{ message: string; cases: any[] }> {
    const res = await fetch(`${API_BASE}/demo/cases/seed-all?run_analysis=${runAnalysis}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to seed all demo cases');
    return res.json();
  },

  async getOfficialRecords(location?: string): Promise<OfficialRecord[]> {
    const url = location && location.trim()
      ? `${API_BASE}/official-records?location=${encodeURIComponent(location.trim())}`
      : `${API_BASE}/official-records`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch official records');
    return res.json();
  },

  async getAllEvidence(): Promise<Evidence[]> {
    const res = await fetch(`${API_BASE}/evidence`);
    if (!res.ok) throw new Error('Failed to fetch all evidence items');
    return res.json();
  },

  getEvidenceFileUrl(evidenceId: string): string {
    return `${API_BASE}/evidence/${encodeURIComponent(evidenceId)}/file`;
  },
};
