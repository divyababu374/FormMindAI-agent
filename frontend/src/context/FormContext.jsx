import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';
import { authService } from '../services/supabase';

const FormContext = createContext();

export const FormProvider = ({ children }) => {
  // Auth state (Supabase Google Auth)
  const [authUser, setAuthUser] = useState(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isDemoMode, setIsDemoMode] = useState(false);

  // Forms and active analysis state
  const [forms, setForms] = useState([]);
  const [currentForm, setCurrentForm] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [activeTab, setActiveTabState] = useState('overview');
  const [tabHistory, setTabHistory] = useState(['overview']);

  // Modals and loading state
  const [isAnalyzeModalOpen, setIsAnalyzeModalOpen] = useState(false);
  const [isMyFormsModalOpen, setIsMyFormsModalOpen] = useState(false);
  const [isAttachModalOpen, setIsAttachModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('');
  const [error, setError] = useState(null);

  // Google status & config from backend
  const defaultRedirectUri = typeof window !== 'undefined' ? `${window.location.origin}/auth/callback` : 'http://localhost:5173/auth/callback';
  const [googleConfig, setGoogleConfig] = useState({ is_configured: false, client_id: null, redirect_uri: defaultRedirectUri });
  const [googleStatus, setGoogleStatus] = useState({ is_connected: false, email: null, name: null });

  // 1. Initialize Supabase Auth & Session on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        const session = await authService.getSession();
        if (session?.user) {
          const userObj = {
            id: session.user.id,
            name: session.user.user_metadata?.full_name || session.user.email?.split('@')[0] || 'Analyst',
            email: session.user.email,
            avatar_url: session.user.user_metadata?.avatar_url || null,
          };
          setAuthUser(userObj);
          
          // Sync with backend session
          try {
            await api.connectGoogleEmail(userObj.email, userObj.name);
          } catch {
            // backend connection fallback
          }
          await loadForms();
        }
      } catch (err) {
        console.error('Error initializing auth:', err);
      } finally {
        setIsAuthLoading(false);
      }
    };

    initAuth();

    // Subscribe to auth state changes
    const { data: authListener } = authService.onAuthStateChange(async (event, session) => {
      if (session?.user) {
        const userObj = {
          id: session.user.id,
          name: session.user.user_metadata?.full_name || session.user.email?.split('@')[0] || 'Analyst',
          email: session.user.email,
          avatar_url: session.user.user_metadata?.avatar_url || null,
        };
        setAuthUser(userObj);
        await authService.upsertProfile(session.user);
        try {
          await api.connectGoogleEmail(userObj.email, userObj.name);
        } catch {}
        await loadForms();
      } else if (event === 'SIGNED_OUT') {
        setAuthUser(null);
        setForms([]);
        setCurrentForm(null);
        setAnalysis(null);
        setQuestions([]);
      }
    });

    api.getGoogleConfig().then(setGoogleConfig).catch(() => {});

    return () => {
      authListener?.subscription?.unsubscribe();
    };
  }, []);

  // Auth Handlers
  const loginWithGoogle = async () => {
    try {
      const result = await authService.signInWithGoogle();
      if (result?.user) {
        const userObj = {
          id: result.user.id,
          name: result.user.user_metadata?.full_name || result.user.email?.split('@')[0] || 'Analyst',
          email: result.user.email,
          avatar_url: result.user.user_metadata?.avatar_url || null,
        };
        setAuthUser(userObj);
        try {
          await api.connectGoogleEmail(userObj.email, userObj.name);
        } catch {}
        await loadForms();
      }
      setIsAuthModalOpen(false);
      setIsDemoMode(false);
      return result;
    } catch (err) {
      console.error('Login error:', err);
      throw err;
    }
  };

  const logout = async () => {
    try {
      await authService.signOut();
      setAuthUser(null);
      setForms([]);
      setCurrentForm(null);
      setAnalysis(null);
      setQuestions([]);
      setIsDemoMode(false);
      setActiveTabState('overview');
      setTabHistory(['overview']);
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  // Demo Mode Handlers
  const startDemoMode = async () => {
    setIsDemoMode(true);
    try {
      await analyzeDemo('workshop_feedback');
    } catch (err) {
      console.error('Error starting demo:', err);
    }
  };

  const exitDemoMode = () => {
    setIsDemoMode(false);
    setCurrentForm(null);
    setAnalysis(null);
    setQuestions([]);
    setActiveTabState('overview');
    setTabHistory(['overview']);
  };

  // Tab Navigation
  const setActiveTab = (tabOrFn) => {
    setActiveTabState((prev) => {
      const nextTab = typeof tabOrFn === 'function' ? tabOrFn(prev) : tabOrFn;
      if (nextTab !== prev) {
        setTabHistory((h) => [...h, nextTab]);
      }
      return nextTab;
    });
  };

  const goBack = () => {
    if (tabHistory.length > 1) {
      setTabHistory((prev) => {
        const next = [...prev];
        next.pop();
        const target = next[next.length - 1] || 'overview';
        setActiveTabState(target);
        return next;
      });
    } else if (activeTab !== 'overview') {
      setActiveTabState('overview');
      setTabHistory(['overview']);
    } else {
      resetToHome();
    }
  };

  const resetToHome = () => {
    setCurrentForm(null);
    setAnalysis(null);
    setQuestions([]);
    setActiveTabState('overview');
    setTabHistory(['overview']);
    setError(null);
    if (isDemoMode) {
      setIsDemoMode(false);
    }
  };

  // Forms & Analysis API calls
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
      setActiveTabState('overview');
      setTabHistory(['overview']);
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
      "Reading survey responses...",
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
      }, 400);
      return newForm;
    } catch (err) {
      clearInterval(interval);
      setIsLoading(false);
      setError(err.message || 'Analysis failed. Please check form link or file format.');
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
      setLoadingStep('Syncing latest responses...');
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

  return (
    <FormContext.Provider
      value={{
        authUser,
        isAuthLoading,
        isAuthModalOpen,
        setIsAuthModalOpen,
        isDemoMode,
        startDemoMode,
        exitDemoMode,
        loginWithGoogle,
        logout,
        forms,
        currentForm,
        questions,
        analysis,
        activeTab,
        setActiveTab,
        goBack,
        tabHistory,
        isAnalyzeModalOpen,
        setIsAnalyzeModalOpen,
        isMyFormsModalOpen,
        setIsMyFormsModalOpen,
        isAttachModalOpen,
        setIsAttachModalOpen,
        isLoading,
        loadingStep,
        error,
        setError,
        googleConfig,
        googleStatus,
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
