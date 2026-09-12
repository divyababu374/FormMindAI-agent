import React from 'react';
import { useForm } from './context/FormContext';
import { Navbar } from './components/Navbar';
import { LandingPage } from './components/LandingPage';
import { AnalysisHome } from './components/AnalysisHome';
import { Dashboard } from './components/Dashboard';
import { AnalyzeModal } from './components/AnalyzeModal';
import { MyFormsModal } from './components/MyFormsModal';
import { AuthModal } from './components/common/AuthModal';
import { LoadingOverlay } from './components/common/LoadingOverlay';
import { Footer } from './components/Footer';
import { Sparkles, ArrowRight } from 'lucide-react';
import { trackPageView } from './services/analytics';

export const App = () => {
  const { 
    authUser, 
    isAuthLoading, 
    currentForm, 
    isLoading, 
    loadingStep, 
    isDemoMode,
    setIsAuthModalOpen 
  } = useForm();

  // Track SPA view navigation in GA4
  React.useEffect(() => {
    let viewTitle = 'FormMind AI — Turn Google Forms into Intelligent Insights';
    let viewPath = '/';

    if (currentForm) {
      if (isDemoMode) {
        viewPath = '/demo';
        viewTitle = 'Demo Form Dashboard | FormMind AI';
      } else {
        viewPath = `/forms/${currentForm.id || 'active'}`;
        viewTitle = `${currentForm.title || 'Form'} | FormMind AI`;
      }
    } else if (authUser) {
      viewPath = '/home';
      viewTitle = 'My Forms | FormMind AI';
    } else {
      viewPath = '/';
      viewTitle = 'FormMind AI — Turn Google Forms into Intelligent Insights';
    }

    trackPageView(viewPath, viewTitle);
  }, [currentForm, isDemoMode, authUser]);

  // Determine active view
  const renderMainContent = () => {
    // 1. If viewing an active form (either real user dataset or demo dataset)
    if (currentForm) {
      return (
        <div className="space-y-4">
          {/* Demo Banner */}
          {isDemoMode && !authUser && (
            <div className="bg-gradient-to-r from-amber-500/10 via-orange-500/10 to-amber-500/10 border-b border-orange-200/80 py-2.5 px-4">
              <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-2 text-[#7A4533] font-semibold">
                  <Sparkles className="w-4 h-4 text-brand-600" />
                  <span>Viewing Sample Demo Dataset. All numbers, charts, and grounded facts reflect live simulated survey responses.</span>
                </div>
                <button
                  onClick={() => setIsAuthModalOpen(true)}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-[#E64825] hover:bg-[#CF3C1B] text-white font-bold shadow-2xs transition-all active:scale-95 cursor-pointer"
                >
                  <span>Analyze Your Own Data</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
          <Dashboard />
        </div>
      );
    }

    // 2. If authenticated and on home screen
    if (authUser) {
      return <AnalysisHome />;
    }

    // 3. Default: Public Landing Page
    return <LandingPage />;
  };

  return (
    <div className="min-h-screen bg-[#FFF9F6] text-[#24110A] flex flex-col font-sans selection:bg-brand-500 selection:text-white">
      {/* Navigation Header */}
      <Navbar />

      {/* Main Content Area */}
      <main className="flex-1">
        {isAuthLoading ? (
          <div className="min-h-[60vh] flex items-center justify-center">
            <div className="w-8 h-8 rounded-full border-2 border-brand-500 border-t-transparent animate-spin" />
          </div>
        ) : (
          renderMainContent()
        )}
      </main>

      {/* Modals & Loading Animations */}
      <AuthModal />
      <AnalyzeModal />
      <MyFormsModal />
      {isLoading && <LoadingOverlay step={loadingStep} />}

      {/* Structured Footer */}
      <Footer />
    </div>
  );
};

export default App;
