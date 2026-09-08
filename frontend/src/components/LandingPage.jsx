import React from 'react';
import { 
  Sparkles, 
  ArrowRight, 
  BarChart3, 
  MessageSquareText, 
  FileSpreadsheet, 
  Layers, 
  Zap, 
  ShieldCheck, 
  CheckCircle2, 
  Lock,
  Play,
  Plus
} from 'lucide-react';
import { useForm } from '../context/FormContext';

export const LandingPage = () => {
  const { setIsAuthModalOpen, startDemoMode } = useForm();

  const coreFeatures = [
    {
      icon: BarChart3,
      title: 'Analyze Data',
      desc: 'Turn raw form responses into clean statistical distributions, quartiles, and completion metrics with zero math errors.',
      badge: 'Deterministic Math'
    },
    {
      icon: Sparkles,
      title: 'AI Insights',
      desc: 'Automatically identify critical sentiment trends, friction points, and executive takeaways from respondents.',
      badge: 'Automated Synthesis'
    },
    {
      icon: MessageSquareText,
      title: 'Ask Your Data',
      desc: 'Query your survey in plain English with 100% verified mathematical grounding against actual submission counts.',
      badge: 'Zero Hallucinations'
    },
    {
      icon: FileSpreadsheet,
      title: 'Multiple Data Sources',
      desc: 'Seamless support for Google Forms, CSV datasets, and multi-tab Excel workbooks (.xlsx, .xls).',
      badge: 'Universal Ingestion'
    }
  ];

  return (
    <div className="relative overflow-hidden">
      
      {/* Subtle Background Glows */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-[520px] bg-gradient-to-b from-brand-500/10 via-orange-200/10 to-transparent blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-1/3 -left-32 w-80 h-80 bg-brand-500/5 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-1/2 -right-32 w-80 h-80 bg-amber-500/5 rounded-full blur-3xl pointer-events-none -z-10" />

      {/* 1. Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 sm:pt-20 pb-16 text-center space-y-8">
        
        {/* Top Feature Pill */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-orange-50 border border-orange-200/90 text-xs font-bold text-brand-600 shadow-2xs animate-in fade-in slide-in-from-top-2 duration-300">
          <Sparkles className="w-3.5 h-3.5 text-brand-600" />
          <span>Next-Gen Survey Intelligence & Grounded Chat</span>
        </div>

        {/* Main Headline */}
        <div className="max-w-4xl mx-auto space-y-4">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-[#24110A] tracking-tight leading-[1.12]">
            Turn Your Form & Survey Data Into{' '}
            <span className="bg-gradient-to-r from-[#E64825] via-[#FF7A50] to-[#E64825] bg-clip-text text-transparent">
              Intelligent Insights
            </span>
          </h1>
          <p className="text-base sm:text-lg lg:text-xl text-[#6B3B2B] font-medium max-w-2xl mx-auto leading-relaxed">
            Upload your response data, discover trends, understand patterns, and ask AI questions about your data with 100% mathematical grounding.
          </p>
        </div>

        {/* Hero Action CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
          <button
            onClick={() => setIsAuthModalOpen(true)}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-8 py-4 rounded-2xl bg-gradient-to-tr from-[#E64825] to-[#FF7A50] hover:from-[#CF3C1B] hover:to-[#E64825] text-white font-extrabold text-base shadow-lg shadow-orange-500/25 hover:shadow-xl hover:shadow-orange-500/30 transition-all active:scale-[0.98] cursor-pointer"
          >
            <span>Get Started</span>
            <ArrowRight className="w-5 h-5" />
          </button>

          <button
            onClick={startDemoMode}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-4 rounded-2xl bg-white hover:bg-orange-50/80 border-2 border-[#FAD5C0] hover:border-brand-500 text-[#24110A] font-bold text-base shadow-sm transition-all active:scale-[0.98] cursor-pointer"
          >
            <Play className="w-4 h-4 text-brand-600 fill-brand-600" />
            <span>Explore Demo</span>
          </button>
        </div>

        {/* Trust Badges */}
        <div className="pt-4 flex flex-wrap items-center justify-center gap-6 text-xs text-[#7A4533] font-semibold">
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            100% Grounded Numbers
          </span>
          <span className="text-[#D4A390] hidden sm:inline">•</span>
          <span className="flex items-center gap-1.5">
            <Lock className="w-4 h-4 text-brand-600" />
            Zero Training on Survey Data
          </span>
          <span className="text-[#D4A390] hidden sm:inline">•</span>
          <span className="flex items-center gap-1.5">
            <Zap className="w-4 h-4 text-amber-600" />
            Free Instant Demo
          </span>
        </div>

        {/* 2. Interactive "+ Ask anything" Mockup Preview */}
        <div className="pt-6 max-w-4xl mx-auto">
          <div className="bg-white rounded-3xl border border-[#FAD5C0] shadow-2xl p-4 sm:p-6 text-left space-y-4">
            
            {/* Mock Header */}
            <div className="flex items-center justify-between border-b border-[#F5E6DC] pb-3 text-xs">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-red-400" />
                <span className="w-3 h-3 rounded-full bg-amber-400" />
                <span className="w-3 h-3 rounded-full bg-emerald-400" />
                <span className="ml-2 font-bold text-[#7A4533]">FormMind AI Interactive Workspace</span>
              </div>
              <span className="text-emerald-700 font-bold bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-md">
                Live Engine
              </span>
            </div>

            {/* Mock "+ Ask anything" Bar */}
            <div 
              onClick={() => setIsAuthModalOpen(true)}
              className="bg-orange-50/50 rounded-2xl border-2 border-[#FAD5C0] hover:border-brand-500 p-3 flex items-center justify-between gap-3 cursor-pointer group transition-all"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-xl bg-orange-100/90 text-brand-600 flex items-center justify-center font-bold border border-orange-200">
                  <Plus className="w-4 h-4" />
                </div>
                <span className="text-sm font-semibold text-[#7A4533] group-hover:text-[#24110A] transition-colors">
                  Ask anything about your customer feedback dataset...
                </span>
              </div>
              <span className="w-8 h-8 rounded-xl bg-brand-600 text-white flex items-center justify-center shadow-sm">
                <ArrowRight className="w-4 h-4" />
              </span>
            </div>

            {/* Mock KPI Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
              <div className="bg-[#FFF9F6] p-3 rounded-xl border border-orange-200/60">
                <div className="text-[10px] font-bold uppercase text-[#7A4533]">Responses</div>
                <div className="text-lg font-black text-[#24110A]">248</div>
              </div>
              <div className="bg-[#FFF9F6] p-3 rounded-xl border border-orange-200/60">
                <div className="text-[10px] font-bold uppercase text-[#7A4533]">Completion Rate</div>
                <div className="text-lg font-black text-emerald-600">98.4%</div>
              </div>
              <div className="bg-[#FFF9F6] p-3 rounded-xl border border-orange-200/60">
                <div className="text-[10px] font-bold uppercase text-[#7A4533]">Satisfaction Index</div>
                <div className="text-lg font-black text-brand-600">4.7 / 5.0</div>
              </div>
              <div className="bg-[#FFF9F6] p-3 rounded-xl border border-orange-200/60">
                <div className="text-[10px] font-bold uppercase text-[#7A4533]">Grounded Facts</div>
                <div className="text-lg font-black text-purple-600">12 Verified</div>
              </div>
            </div>

          </div>
        </div>

      </section>

      {/* 3. Core Capabilities Section (4 Focused Cards) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-[#FAD5C0]/80">
        <div className="text-center space-y-3 mb-12">
          <h2 className="text-2xl sm:text-3xl font-black text-[#24110A] tracking-tight">
            Designed for Instant Clarity & Mathematical Accuracy
          </h2>
          <p className="text-sm sm:text-base text-[#6B3B2B] max-w-xl mx-auto font-medium">
            Everything you need to transform raw spreadsheets and form submissions into presentation-ready intelligence.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {coreFeatures.map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <div
                key={idx}
                className="bg-white rounded-2xl p-6 border border-[#FAD5C0] hover:border-brand-500 hover:shadow-lg transition-all space-y-4 flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="w-12 h-12 rounded-2xl bg-orange-50 text-brand-600 flex items-center justify-center border border-orange-200 shadow-2xs">
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-black text-[#24110A] tracking-tight">
                    {feat.title}
                  </h3>
                  <p className="text-xs text-[#6B3B2B] leading-relaxed">
                    {feat.desc}
                  </p>
                </div>

                <div className="pt-2 border-t border-[#F5E6DC]">
                  <span className="inline-flex items-center gap-1 text-[11px] font-bold text-brand-600">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    {feat.badge}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 4. Bottom CTA Strip */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        <div className="bg-gradient-to-tr from-[#24110A] to-[#3B1F14] rounded-3xl p-8 sm:p-12 text-center text-white space-y-6 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-brand-500/20 rounded-full blur-3xl pointer-events-none" />
          
          <div className="space-y-2 max-w-xl mx-auto">
            <h2 className="text-2xl sm:text-3xl font-black tracking-tight">
              Ready to analyze your survey data?
            </h2>
            <p className="text-xs sm:text-sm text-[#FAD5C0]/90">
              Sign in with Google to upload files, connect Google Forms, and ask questions to your data in seconds.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <button
              onClick={() => setIsAuthModalOpen(true)}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-2xl bg-[#E64825] hover:bg-[#CF3C1B] text-white font-extrabold text-sm shadow-md transition-all active:scale-[0.98] cursor-pointer"
            >
              <span>Get Started with Google</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={startDemoMode}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm border border-white/20 transition-all active:scale-[0.98] cursor-pointer"
            >
              <span>Try Demo First</span>
            </button>
          </div>
        </div>
      </section>

    </div>
  );
};
