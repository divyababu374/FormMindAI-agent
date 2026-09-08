import React from 'react';
import { 
  Sparkles, 
  ShieldCheck, 
  Zap, 
  BarChart3, 
  FileSpreadsheet, 
  FileText, 
  CheckCircle2, 
  ExternalLink,
  Lock,
  Cpu,
  Terminal,
  Heart
} from 'lucide-react';
import { useForm } from '../context/FormContext';

export const Footer = () => {
  const { setIsAnalyzeModalOpen, setIsMyFormsModalOpen, setIsGoogleModalOpen, analyzeDemo } = useForm();

  return (
    <footer className="border-t border-[#FAD5C0]/80 bg-white text-[#24110A] font-sans">
      {/* Top Banner / Value Proposition Ribbon */}
      <div className="border-b border-[#F5E6DC] bg-gradient-to-r from-orange-50/70 via-white to-amber-50/50 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <span className="flex h-2.5 w-2.5 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <span className="text-xs font-semibold text-[#6B3B2B]">
              FormMind Core Engine: <span className="text-emerald-700 font-bold">Operational (v1.0.0 Production)</span>
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-xs text-[#6B3B2B]">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-white border border-orange-200/80 font-medium shadow-2xs">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              100% Grounded Numbers
            </span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-white border border-orange-200/80 font-medium shadow-2xs">
              <Lock className="w-3.5 h-3.5 text-brand-600" />
              Zero Training on Survey Data
            </span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-white border border-orange-200/80 font-medium shadow-2xs">
              <Zap className="w-3.5 h-3.5 text-amber-600" />
              Vercel Edge Ready
            </span>
          </div>
        </div>
      </div>

      {/* Main 4-Column Footer Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-10">
          
          {/* Brand & Mission Column (Spans 2 on large screens) */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#E64825] to-[#FF8C66] flex items-center justify-center text-white shadow-md shadow-orange-500/20">
                <Sparkles className="w-5 h-5" />
              </div>
              <span className="text-xl font-black tracking-tight text-[#24110A]">
                FormMind <span className="text-[#E64825]">AI</span>
              </span>
            </div>

            <p className="text-sm text-[#6B3B2B] leading-relaxed max-w-sm">
              Full-stack survey intelligence platform that bridges raw response collection and strategic decisions with deterministic math and grounded AI synthesis.
            </p>

            <div className="flex flex-wrap gap-2 pt-2">
              <button
                onClick={() => analyzeDemo('workshop_feedback')}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-orange-50 hover:bg-orange-100/80 border border-orange-200 text-xs font-bold text-[#24110A] transition-all"
              >
                <Zap className="w-3.5 h-3.5 text-brand-600" />
                Try Interactive Demo
              </button>
              <button
                onClick={() => setIsAnalyzeModalOpen(true)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#E64825] hover:bg-[#CF3C1B] text-white text-xs font-bold shadow-sm transition-all"
              >
                Analyze Your Form
              </button>
            </div>
          </div>

          {/* Column 2: Ingestion & Processing */}
          <div className="space-y-3">
            <h4 className="text-xs font-black uppercase tracking-wider text-[#24110A]">
              Ingestion & Data
            </h4>
            <ul className="space-y-2 text-xs text-[#6B3B2B]">
              <li>
                <button 
                  onClick={() => setIsGoogleModalOpen(true)} 
                  className="hover:text-[#E64825] transition-colors text-left"
                >
                  Google Forms & Drive Sync
                </button>
              </li>
              <li>
                <button 
                  onClick={() => setIsAnalyzeModalOpen(true)} 
                  className="hover:text-[#E64825] transition-colors text-left"
                >
                  Microsoft Forms Parser
                </button>
              </li>
              <li>
                <button 
                  onClick={() => setIsAnalyzeModalOpen(true)} 
                  className="hover:text-[#E64825] transition-colors text-left"
                >
                  CSV & Excel Uploads (.xlsx)
                </button>
              </li>
              <li>
                <button 
                  onClick={() => setIsAnalyzeModalOpen(true)} 
                  className="hover:text-[#E64825] transition-colors text-left"
                >
                  Automated Data Cleaner
                </button>
              </li>
              <li>
                <button 
                  onClick={() => setIsMyFormsModalOpen(true)} 
                  className="hover:text-[#E64825] transition-colors text-left"
                >
                  Saved Workspace Forms
                </button>
              </li>
            </ul>
          </div>

          {/* Column 3: Analytical Capabilities */}
          <div className="space-y-3">
            <h4 className="text-xs font-black uppercase tracking-wider text-[#24110A]">
              Analytics & Exports
            </h4>
            <ul className="space-y-2 text-xs text-[#6B3B2B]">
              <li>
                <span className="hover:text-[#E64825] cursor-default transition-colors">
                  Statistical Engine (Mean, IQR, SD)
                </span>
              </li>
              <li>
                <span className="hover:text-[#E64825] cursor-default transition-colors">
                  Zero-Hallucination Grounded Chat
                </span>
              </li>
              <li>
                <span className="hover:text-[#E64825] cursor-default transition-colors">
                  Executive PDF Reports (ReportLab)
                </span>
              </li>
              <li>
                <span className="hover:text-[#E64825] cursor-default transition-colors">
                  Editable Word Documents (.docx)
                </span>
              </li>
              <li>
                <span className="hover:text-[#E64825] cursor-default transition-colors">
                  Multi-Tab Excel Workbooks (.xlsx)
                </span>
              </li>
              <li>
                <span className="hover:text-[#E64825] cursor-default transition-colors">
                  Social & Board Infographics (.png)
                </span>
              </li>
            </ul>
          </div>

          {/* Column 4: Platform & Developer */}
          <div className="space-y-3">
            <h4 className="text-xs font-black uppercase tracking-wider text-[#24110A]">
              Engines & APIs
            </h4>
            <ul className="space-y-2 text-xs text-[#6B3B2B]">
              <li className="flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-brand-600" />
                <span>Deterministic Reasoner</span>
              </li>
              <li>
                <span>Google Gemini 1.5 / 2.0</span>
              </li>
              <li>
                <span>OpenAI GPT-4o Integration</span>
              </li>
              <li>
                <span>Groq Cloud & Local Ollama</span>
              </li>
              <li className="pt-1">
                <a
                  href="/docs"
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-[#E64825] hover:underline font-bold"
                >
                  <Terminal className="w-3.5 h-3.5" />
                  FastAPI OpenAPI Docs
                  <ExternalLink className="w-3 h-3" />
                </a>
              </li>
            </ul>
          </div>

        </div>
      </div>

      {/* Bottom Copyright & Credits Bar */}
      <div className="border-t border-[#F5E6DC] bg-[#FFF9F5] py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#6B3B2B]">
          <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2">
            <span>© {new Date().getFullYear()} <strong className="text-[#24110A]">FormMind AI</strong>.</span>
            <span>All rights reserved.</span>
            <span className="hidden sm:inline text-[#D4A390]">•</span>
            <span>MIT License</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white border border-orange-200/90 text-xs font-semibold text-[#24110A] shadow-2xs">
              <span>Developed & maintained with</span>
              <Heart className="w-3.5 h-3.5 text-red-500 fill-red-500" />
              <span>by</span>
              <span className="font-black text-[#E64825] tracking-tight">Alzo Tech</span>
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};
