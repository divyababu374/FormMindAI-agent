import React from 'react';
import { useForm } from './context/FormContext';
import { Navbar } from './components/Navbar';
import { LandingPage } from './components/LandingPage';
import { Dashboard } from './components/Dashboard';
import { AnalyzeModal } from './components/AnalyzeModal';
import { MyFormsModal } from './components/MyFormsModal';
import { GoogleConnectModal } from './components/common/GoogleConnectModal';
import { LoadingOverlay } from './components/common/LoadingOverlay';

export const App = () => {
  const { currentForm, isLoading, loadingStep } = useForm();

  return (
    <div className="min-h-screen bg-[#FFF9F6] text-[#24110A] flex flex-col font-sans selection:bg-brand-500 selection:text-white">
      {/* Navigation Header */}
      <Navbar />

      {/* Main Content Area */}
      <main className="flex-1">
        {currentForm ? <Dashboard /> : <LandingPage />}
      </main>

      {/* Modals & Loading Animations */}
      <AnalyzeModal />
      <MyFormsModal />
      <GoogleConnectModal />
      {isLoading && <LoadingOverlay step={loadingStep} />}

      {/* Footer */}
      <footer className="border-t border-[#FAD5C0] py-6 text-center text-xs text-[#6B3B2B] bg-white">
        <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex flex-col sm:flex-row items-center gap-2 text-center sm:text-left">
            <span className="font-black text-[#24110A]">FormMind AI</span>
            <span className="hidden sm:inline text-[#D4A390]">—</span>
            <span>AI-Powered Google & MS Form Intelligence Platform</span>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-3">
            <span className="text-[#6B3B2B] font-medium hidden lg:inline">
              Deterministic Math Models • Zero-Hallucination Grounded Chat
            </span>
            <span className="hidden lg:inline text-[#D4A390]">•</span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-50 border border-orange-200 text-xs font-semibold text-[#24110A] shadow-2xs">
              <span>Developed and maintained by</span>
              <span className="font-black text-brand-600 tracking-tight">Alzo Tech</span>
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
