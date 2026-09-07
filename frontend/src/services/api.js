const rawBase = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '');
const API_BASE = rawBase === '/api' || rawBase.endsWith('/api') ? rawBase : `${rawBase}/api`;

const getAuthHeaders = () => {
  const token = localStorage.getItem('formmind_token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

const authFetch = (url, options = {}) => {
  const headers = {
    ...getAuthHeaders(),
    ...(options.headers || {})
  };
  return fetch(url, { ...options, headers });
};

const handleResponse = async (res, defaultMsg = 'Request failed') => {
  if (!res.ok) {
    if (res.status === 401) {
      localStorage.removeItem('formmind_token');
    }
    let errorDetail = defaultMsg;
    try {
      const text = await res.text();
      if (text) {
        try {
          const json = JSON.parse(text);
          errorDetail = json.detail || json.message || text;
        } catch {
          errorDetail = text.length < 300 ? text : `${defaultMsg} (${res.status} ${res.statusText})`;
        }
      } else {
        errorDetail = `${defaultMsg} (Server returned status ${res.status})`;
      }
    } catch {
      errorDetail = `${defaultMsg} (${res.status})`;
    }
    throw new Error(errorDetail);
  }
  return res.json();
};

export const api = {
  // Authentication & Google Account
  getGoogleConfig: async () => {
    const res = await authFetch(`${API_BASE}/auth/google/config`);
    return handleResponse(res, 'Failed to get Google config');
  },

  getGoogleStatus: async () => {
    let res = await authFetch(`${API_BASE}/auth/google/status`);
    if (res.status === 401) {
      localStorage.removeItem('formmind_token');
      res = await fetch(`${API_BASE}/auth/google/status`);
    }
    return handleResponse(res, 'Failed to get Google account status');
  },

  connectGoogleEmail: async (email, name = null) => {
    let res = await authFetch(`${API_BASE}/auth/google/connect-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, name }),
    });
    if (res.status === 401) {
      localStorage.removeItem('formmind_token');
      res = await fetch(`${API_BASE}/auth/google/connect-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name }),
      });
    }
    const data = await handleResponse(res, 'Failed to connect email');
    if (data.access_token) {
      localStorage.setItem('formmind_token', data.access_token);
    }
    return data;
  },

  updateGoogleConfig: async (clientId, clientSecret, redirectUri) => {
    const res = await authFetch(`${API_BASE}/auth/google/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        client_id: clientId,
        client_secret: clientSecret,
        redirect_uri: redirectUri
      }),
    });
    return handleResponse(res, 'Failed to update Google config');
  },

  setGoogleDirectToken: async (accessToken) => {
    const res = await authFetch(`${API_BASE}/auth/google/direct-token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ access_token: accessToken }),
    });
    const data = await handleResponse(res, 'Failed to set Google access token');
    if (data.access_token) {
      localStorage.setItem('formmind_token', data.access_token);
    }
    return data;
  },

  getGoogleAuthUrl: async () => {
    const res = await authFetch(`${API_BASE}/auth/google/url`);
    return handleResponse(res, 'Failed to get Google OAuth URL');
  },

  googleOAuthCallback: async (code) => {
    const res = await authFetch(`${API_BASE}/auth/google/callback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    });
    const data = await handleResponse(res, 'Failed to authenticate with Google');
    if (data.access_token) {
      localStorage.setItem('formmind_token', data.access_token);
    }
    return data;
  },

  disconnectGoogle: async () => {
    const res = await authFetch(`${API_BASE}/auth/google/disconnect`, {
      method: 'POST',
    });
    return handleResponse(res, 'Failed to disconnect Google');
  },

  getGoogleDriveForms: async () => {
    const res = await authFetch(`${API_BASE}/forms/google/drive-forms`);
    return handleResponse(res, 'Failed to list Google Forms from Drive');
  },

  getCurrentUser: async () => {
    const res = await authFetch(`${API_BASE}/auth/me`);
    return handleResponse(res, 'Failed to get current user');
  },

  // Synchronization & Data Status
  getFormDataStatus: async (formId) => {
    const res = await authFetch(`${API_BASE}/forms/${formId}/data-status`);
    return handleResponse(res, 'Failed to get form data status');
  },

  syncFormResponses: async (formId) => {
    const res = await authFetch(`${API_BASE}/forms/${formId}/sync`, {
      method: 'POST',
    });
    return handleResponse(res, 'Failed to sync latest responses');
  },

  attachFormSheet: async (formId, sheetUrl) => {
    const res = await authFetch(`${API_BASE}/forms/${formId}/attach-sheet`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sheet_url: sheetUrl }),
    });
    return handleResponse(res, 'Failed to attach responses spreadsheet');
  },

  uploadFormResponses: async (formId, fileOrFormData) => {
    let body = fileOrFormData;
    if (fileOrFormData instanceof File) {
      body = new FormData();
      body.append('file', fileOrFormData);
    }
    const res = await authFetch(`${API_BASE}/forms/${formId}/upload-responses`, {
      method: 'POST',
      body: body,
    });
    return handleResponse(res, 'Failed to upload response file');
  },


  getFormAttachments: async (formId) => {
    const res = await authFetch(`${API_BASE}/forms/${formId}/attachments`);
    return handleResponse(res, 'Failed to get form attachments');
  },

  // Forms & Ingestion
  analyzeForm: async (data) => {
    const res = await authFetch(`${API_BASE}/forms/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(res, 'Failed to analyze form');
  },

  uploadFormFile: async (formData) => {
    const res = await authFetch(`${API_BASE}/forms/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(res, 'Failed to upload form file');
  },

  getForms: async () => {
    const res = await authFetch(`${API_BASE}/forms`);
    return handleResponse(res, 'Failed to fetch forms');
  },

  getFormDetail: async (formId) => {
    const res = await authFetch(`${API_BASE}/forms/${formId}`);
    return handleResponse(res, 'Failed to fetch form detail');
  },

  deleteForm: async (formId) => {
    const res = await authFetch(`${API_BASE}/forms/${formId}`, {
      method: 'DELETE',
    });
    return handleResponse(res, 'Failed to delete form');
  },

  getQuestions: async (formId) => {
    const res = await authFetch(`${API_BASE}/forms/${formId}/questions`);
    return handleResponse(res, 'Failed to fetch questions');
  },

  getAnalysis: async (formId) => {
    const res = await authFetch(`${API_BASE}/forms/${formId}/analysis`);
    return handleResponse(res, 'Failed to fetch analysis');
  },

  getResponses: async (formId, page = 1, pageSize = 25, search = '', sortBy = '', sortDesc = false) => {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
      ...(search ? { search } : {}),
      ...(sortBy ? { sort_by: sortBy, sort_desc: sortDesc.toString() } : {})
    });
    const res = await authFetch(`${API_BASE}/forms/${formId}/responses?${params.toString()}`);
    return handleResponse(res, 'Failed to fetch responses');
  },

  // AI Chat
  sendChatMessage: async (formId, content) => {
    const res = await authFetch(`${API_BASE}/forms/${formId}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });
    return handleResponse(res, 'Failed to send chat message');
  },

  getChatHistory: async (formId) => {
    const res = await authFetch(`${API_BASE}/forms/${formId}/chat/history`);
    return handleResponse(res, 'Failed to fetch chat history');
  },

  clearChatHistory: async (formId) => {
    const res = await authFetch(`${API_BASE}/forms/${formId}/chat/history`, {
      method: 'DELETE',
    });
    return handleResponse(res, 'Failed to clear chat history');
  },

  // Reports & Exports
  generateCustomReport: async (formId, reportType = 'full', customInstructions = '', title = '') => {
    const res = await authFetch(`${API_BASE}/forms/${formId}/report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ report_type: reportType, custom_instructions: customInstructions, title }),
    });
    return handleResponse(res, 'Failed to generate report');
  },

  getExportPdfUrl: (formId) => `${API_BASE}/forms/${formId}/export/pdf`,
  getExportDocxUrl: (formId) => `${API_BASE}/forms/${formId}/export/docx`,
  getExportXlsxUrl: (formId) => `${API_BASE}/forms/${formId}/export/xlsx`,
  getExportCsvUrl: (formId) => `${API_BASE}/forms/${formId}/export/csv`,
  getExportImageUrl: (formId, format = 'png') => `${API_BASE}/forms/${formId}/image?format=${format}`,

  downloadFile: async (url, defaultFilename = 'document') => {
    const res = await authFetch(url);
    if (!res.ok) {
      throw new Error(`Download failed (${res.status} ${res.statusText})`);
    }
    const blob = await res.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = defaultFilename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);
  }
};
