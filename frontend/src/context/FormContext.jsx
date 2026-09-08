import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const FormContext = createContext();

export const FormProvider = ({ children }) => {
  const [forms, setForms] = useState([]);
  const [currentForm, setCurrentForm] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [isAnalyzeModalOpen, setIsAnalyzeModalOpen] = useState(false);
  const [isMyFormsModalOpen, setIsMyFormsModalOpen] = useState(false);
  const [isGoogleModalOpen, setIsGoogleModalOpen] = useState(false);
  const [isAttachModalOpen, setIsAttachModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const [loadingStep, setLoadingStep] = useState('');
  const [error, setError] = useState(null);
  const defaultRedirectUri = typeof window !== 'undefined' ? `${window.location.origin}/auth/callback` : 'http://localhost:5173/auth/callback';
  const [googleConfig, setGoogleConfig] = useState({ is_configured: false, client_id: null, redirect_uri: defaultRedirectUri });
  const [googleStatus, setGoogleStatus] = useState({ is_connected: false, email: null, name: null });

  // Load existing forms, Google config, and check for OAuth callback code on startup
  useEffect(() => {
    loadForms();
    refreshGoogleStatus();
    api.getGoogleConfig().then(setGoogleConfig).catch(() => {});

    // Detect Google OAuth callback code in URL
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    if (code) {
      handleOAuthCallback(code);
    }
  }, []);

  const handleOAuthCallback = async (code) => {
    setIsLoading(true);
    setLoadingStep('Authenticating with Google OAuth...');
    try {
      await api.googleOAuthCallback(code);
      // Clean query param from URL without reloading
      const cleanUrl = window.location.pathname;
      window.history.replaceState({}, document.title, cleanUrl);
      await refreshGoogleStatus();
      await loadForms();
      setIsLoading(false);
      setLoadingStep('');
    } catch (err) {
      setIsLoading(false);
      setError(err.message || 'Google OAuth authentication failed.');
    }
  };

  const refreshGoogleStatus = async () => {
    try {
      const status = await api.getGoogleStatus();
      setGoogleStatus(status);
      return status;
    } catch (err) {
      console.error('Failed to get Google status:', err);
    }
  };

  const connectGoogle = async () => {
    try {
      const res = await api.getGoogleAuthUrl();
      if (res.auth_url) {
        window.location.href = res.auth_url;
      }
    } catch (err) {
      console.error('Failed to get Google Auth URL:', err);
      throw err;
    }
  };

  const disconnectGoogle = async () => {
    try {
      await api.disconnectGoogle();
      setCurrentForm(null);
      setAnalysis(null);
      setQuestions([]);
      await refreshGoogleStatus();
    } catch (err) {
      console.error('Failed to disconnect Google:', err);
      throw err;
    }
  };

  const connectEmail = async (email, name = null) => {
    try {
      // Clear active form state from any previous session
      setCurrentForm(null);
      setAnalysis(null);
      setQuestions([]);

      const res = await api.connectGoogleEmail(email, name);
      await refreshGoogleStatus();
      await loadForms();
      return res;
    } catch (err) {
      console.error('Failed to connect email:', err);
      throw err;
    }
  };

  const connectDirectToken = async (token) => {
    try {
      setCurrentForm(null);
      setAnalysis(null);
      setQuestions([]);

      const res = await api.setGoogleDirectToken(token);
      await refreshGoogleStatus();
      await loadForms();
      return res;
    } catch (err) {
      console.error('Failed to set direct token:', err);
      throw err;
    }
  };

  const updateGoogleConfig = async (clientId, clientSecret, redirectUri) => {
    try {
      const res = await api.updateGoogleConfig(clientId, clientSecret, redirectUri);
      setGoogleConfig({
        is_configured: res.is_configured,
        client_id: res.client_id,
        redirect_uri: res.redirect_uri
      });
      return res;
    } catch (err) {
      console.error('Failed to update Google config:', err);
      throw err;
    }
  };

  const loadForms = async () => {
    try {
      const data = await api.getForms();
      setForms(data);
      return data;
    } catch (err) {
      console.error('Failed to load forms:', err);
      return [];
    }
  };

  const selectForm = async (formId) => {
    try {
      setIsLoading(true);
      setError(null);
      const detail = await api.getFormDetail(formId);
      setCurrentForm(detail);
      setQuestions(detail.questions || []);
      const analysisData = await api.getAnalysis(formId);
      setAnalysis(analysisData);
      setIsLoading(false);
    } catch (err) {
      console.error('Error selecting form:', err);
      setError('Failed to load form details');
      setIsLoading(false);
    }
  };

  const runAnalysisAnimation = async (asyncTask) => {
    setIsLoading(true);
    setError(null);
    const steps = [
      "Connecting to Google Form...",
      "Resolving Form ID with connected Gmail...",
      "Retrieving respondent submissions...",
      "Processing questions & schema...",
      "Cleaning data & standardizing types...",
      "Calculating deterministic statistics...",
      "Generating AI insights & narratives...",
      "Preparing intelligence dashboard..."
    ];

    let stepIdx = 0;
    setLoadingStep(steps[0]);
    const interval = setInterval(() => {
      stepIdx++;
      if (stepIdx < steps.length) {
        setLoadingStep(steps[stepIdx]);
      }
    }, 450);

    try {
      const newForm = await asyncTask();
      clearInterval(interval);
      setLoadingStep("Analysis complete!");
      setTimeout(async () => {
        await loadForms();
        await selectForm(newForm.id);
        setIsLoading(false);
        setIsAnalyzeModalOpen(false);
        setActiveTab('overview');
      }, 500);
      return newForm;
    } catch (err) {
      clearInterval(interval);
      setIsLoading(false);
      setError(err.message || 'Analysis failed. Please check form link or permissions.');
      throw err;
    }
  };

  const analyzeUrl = async (url, title = null) => {
    return runAnalysisAnimation(() => api.analyzeForm({ url, title }));
  };

  const analyzeDemo = async (demoType = 'workshop_feedback', title = null) => {
    return runAnalysisAnimation(() => api.analyzeForm({ demo_type: demoType, title }));
  };

  const uploadFile = async (file, title = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    return runAnalysisAnimation(() => api.uploadFormFile(formData));
  };

  const deleteCurrentForm = async (formId) => {
    try {
      await api.deleteForm(formId);
      const updated = forms.filter(f => f.id !== formId);
      setForms(updated);
      if (currentForm?.id === formId) {
        if (updated.length > 0) {
          selectForm(updated[0].id);
        } else {
          setCurrentForm(null);
          setAnalysis(null);
          setQuestions([]);
        }
      }
    } catch (err) {
      console.error('Delete form error:', err);
      throw err;
    }
  };

  const syncCurrentForm = async () => {
    if (!currentForm) return;
    try {
      setIsLoading(true);
      setLoadingStep('Syncing latest responses from Google...');
      await api.syncFormResponses(currentForm.id);
      await selectForm(currentForm.id);
      setIsLoading(false);
    } catch (err) {
      setIsLoading(false);
      setError(err.message || 'Failed to sync responses.');
      throw err;
    }
  };

  const attachSheetToCurrentForm = async (sheetUrl) => {
    if (!currentForm) return;
    return await runAnalysisAnimation(async () => {
      const updated = await api.attachFormSheet(currentForm.id, sheetUrl);
      await loadForms();
      return updated;
    });
  };

  const uploadResponsesToCurrentForm = async (file) => {
    if (!currentForm) return;
    return await runAnalysisAnimation(async () => {
      const updated = await api.uploadFormResponses(currentForm.id, file);
      await loadForms();
      return updated;
    });
  };

  const resetToHome = () => {
    setCurrentForm(null);
    setAnalysis(null);
    setQuestions([]);
    setActiveTab('overview');
    setError(null);
  };

  return (
    <FormContext.Provider
      value={{
        forms,
        currentForm,
        questions,
        analysis,
        activeTab,
        setActiveTab,
        isAnalyzeModalOpen,
        setIsAnalyzeModalOpen,
        isMyFormsModalOpen,
        setIsMyFormsModalOpen,
        isGoogleModalOpen,
        setIsGoogleModalOpen,
        isAttachModalOpen,
        setIsAttachModalOpen,
        isLoading,
        loadingStep,
        error,
        setError,
        googleConfig,
        googleStatus,
        refreshGoogleStatus,
        connectEmail,
        connectGoogle,
        disconnectGoogle,
        connectDirectToken,
        updateGoogleConfig,
        loadForms,
        selectForm,
        resetToHome,
        analyzeUrl,
        analyzeDemo,
        uploadFile,
        deleteCurrentForm,
        syncCurrentForm,
        attachSheetToCurrentForm,
        uploadResponsesToCurrentForm
      }}
    >
      {children}
    </FormContext.Provider>
  );

};

export const useForm = () => useContext(FormContext);
