const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

function getAuthHeader(): Record<string, string> {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("raven_token");
    if (token) {
      return { Authorization: `Bearer ${token}` };
    }
  }
  return {};
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    ...getAuthHeader(),
    ...options.headers,
  };

  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    let errMessage = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const errData = await response.json();
      if (errData.detail) {
        errMessage = typeof errData.detail === "string" ? errData.detail : JSON.stringify(errData.detail);
      }
    } catch (_) {}
    throw new Error(errMessage);
  }

  return response.json();
}

export const api = {
  // Auth
  async demoLogin() {
    const res = await request<{ access_token: string; user: any }>("/auth/demo-login", {
      method: "POST"
    });
    if (typeof window !== "undefined") {
      localStorage.setItem("raven_token", res.access_token);
      localStorage.setItem("raven_user", JSON.stringify(res.user));
    }
    return res;
  },

  async login(email: string, password: string) {
    const res = await request<{ access_token: string; user: any }>("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    if (typeof window !== "undefined") {
      localStorage.setItem("raven_token", res.access_token);
      localStorage.setItem("raven_user", JSON.stringify(res.user));
    }
    return res;
  },

  async getMe() {
    return request<any>("/auth/me");
  },

  // Investigations
  async listInvestigations(status?: string, search?: string) {
    let q = "";
    const params = new URLSearchParams();
    if (status) params.append("status", status);
    if (search) params.append("search", search);
    if (params.toString()) q = `?${params.toString()}`;
    return request<any[]>(`/investigations${q}`);
  },

  async getInvestigation(id: string) {
    return request<any>(`/investigations/${id}`);
  },

  async createInvestigation(data: { title: string; description?: string; primary_language?: string; tags?: string[] }) {
    return request<any>("/investigations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
  },

  async deleteInvestigation(id: string) {
    return request<any>(`/investigations/${id}`, { method: "DELETE" });
  },

  // Audio & Transcription
  async uploadAudio(file: File, investigationId: string, sourceType = "upload") {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("investigation_id", investigationId);
    formData.append("source_type", sourceType);

    const headers = getAuthHeader();
    const res = await fetch(`${API_BASE}/audio/upload`, {
      method: "POST",
      headers,
      body: formData
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Upload failed");
    }
    return res.json();
  },

  async transcribeAudio(audioAssetId: string, languageCode = "indic-auto", model = "prisma-v3.0") {
    return request<any>("/audio/transcribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        audio_asset_id: audioAssetId,
        language_code: languageCode,
        model
      })
    });
  },

  getAudioFileUrl(audioAssetId: string) {
    return `${API_BASE}/audio/${audioAssetId}/file`;
  },

  // Transcripts
  async getTranscript(id: string) {
    return request<any>(`/transcripts/${id}`);
  },

  async updateSegment(jobId: string, segmentId: string, text: string, speakerLabel?: string, reason?: string) {
    return request<any>(`/transcripts/${jobId}/segments/${segmentId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, speaker_label: speakerLabel, reason })
    });
  },

  getTranscriptExportUrl(id: string, format: "srt" | "txt" | "json") {
    return `${API_BASE}/transcripts/${id}/export?format=${format}`;
  },

  // Claims
  async extractClaims(investigationId: string, jobId?: string) {
    return request<any>("/claims/extract", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ investigation_id: investigationId, job_id: jobId })
    });
  },

  async listClaims(investigationId: string, status?: string) {
    let q = `?investigation_id=${investigationId}`;
    if (status && status !== "all") q += `&status=${status}`;
    return request<any[]>(`/claims${q}`);
  },

  async reviewClaim(claimId: string, decision: string, analystNotes: string, confidenceRating = 4) {
    return request<any>(`/claims/${claimId}/review`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        decision,
        analyst_notes: analystNotes,
        confidence_rating: confidenceRating
      })
    });
  },

  // Evidence
  async addEvidence(data: {
    claim_id: string;
    title: string;
    url?: string;
    publisher?: string;
    excerpt?: string;
    reliability_tier?: string;
    supports_or_refutes?: string;
    relevance_rationale?: string;
  }) {
    return request<any>("/evidence", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
  },

  async listEvidence(investigationId: string, claimId?: string) {
    let q = `?investigation_id=${investigationId}`;
    if (claimId) q += `&claim_id=${claimId}`;
    return request<any[]>(`/evidence${q}`);
  },

  async removeEvidence(linkId: string) {
    return request<any>(`/evidence/${linkId}`, { method: "DELETE" });
  },

  // Reports
  async generateReport(investigationId: string, title: string, executiveSummary?: string) {
    return request<any>("/reports/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ investigation_id: investigationId, title, executive_summary: executiveSummary })
    });
  },

  async listReports(investigationId: string) {
    return request<any[]>(`/reports?investigation_id=${investigationId}`);
  },

  getReportExportUrl(reportId: string, format: "markdown" | "json") {
    return `${API_BASE}/reports/${reportId}/export?format=${format}`;
  },

  // Voice Briefing
  async synthesizeVoice(text: string, voice = "Nalini", language = "en-IN") {
    return request<any>("/voice/briefing", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, voice, language })
    });
  },

  // Providers & Health
  async getProvidersStatus() {
    return request<any>("/providers/status");
  },

  async testProviderConnection() {
    return request<any>("/providers/test-connection", { method: "POST" });
  },

  // Audit & Usage
  async getAuditTrail(action?: string) {
    let q = "";
    if (action) q = `?action=${action}`;
    return request<any[]>(`/audit${q}`);
  },

  async getUsageMetrics() {
    return request<any>("/usage");
  }
};
