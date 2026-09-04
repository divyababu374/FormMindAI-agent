import React, { useState } from 'react';
import { useForm } from '../context/FormContext';
import { 
  Sparkles, 
  ArrowRight, 
  FileText, 
  BarChart3, 
  MessageSquareText, 
  Download, 
  Layers, 
  Zap, 
  ShieldCheck, 
  CheckCircle,
  FileSpreadsheet,
  Image as ImageIcon,
  Play
} from 'lucide-react';
import { Badge } from './common/Badge';

export const LandingPage = () => {
  const { analyzeUrl, analyzeDemo, setIsAnalyzeModalOpen, error } = useForm();
  const [inputUrl, setInputUrl] = useState('');
  const [inputError, setInputError] = useState('');

  const handleQuickAnalyze = async (e) => {
    e.preventDefault();
    if (!inputUrl.trim()) {
      setInputError('Please enter a valid Google Forms or Google Sheets URL.');
      return;
    }
    setInputError('');
    try {
      await analyzeUrl(inputUrl.trim());
    } catch (err) {
      setInputError(err.message || 'Could not analyze this form link.');
    }
  };

  const features = [
    {
      icon: BarChart3,
      title: 'Deterministic Analytics',
      desc: 'Accurate calculations for mean, median, mode, percentiles, and category distributions with zero math hallucinations.',
      color: 'blue'
    },
    {
      icon: MessageSquareText,
      title: 'ChatGPT for Google Forms',
      desc: 'Ask complex analytical questions in natural language. Filters and aggregations are computed on the real dataset.',
      color: 'purple'
    },
    {
      icon: Sparkles,
      title: 'Automatic AI Insights',
      desc: 'Instantly segregates hard data FACTS from strategic INTERPRETATIONS and actionable RECOMMENDATIONS.',
      color: 'emerald'
    },
    {
      icon: FileText,
      title: 'Executive PDF & DOCX Reports',
      desc: 'Generate presentation-ready, multi-page professional reports with KPI tables, question breakdowns, and takeaways.',
      color: 'amber'
    },
    {
      icon: FileSpreadsheet,
      title: '5-Sheet Excel Workbooks',
      desc: 'Exports Summary, Raw Data, Cleaned Data, Statistics, and AI Insights with formatted headers.',
      color: 'blue'
    },
    {
      icon: ImageIcon,
      title: 'High-Res Infographics',
      desc: '1-click export of visual infographic cards in PNG/JPG formatted for social sharing and slide decks.',
      color: 'purple'
    }
  ];

  return (
    <div className="relative overflow-hidden pb-20">
      
      {/* Background Ambient Glows */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-[600px] bg-gradient-to-b from-brand-600/15 via-purple-600/10 to-transparent blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-1/3 -left-40 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-1/2 -right-40 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl pointer-events-none -z-10" />

      {/* Hero Section */}
      <section className="max-w-5xl mx-auto pt-16 sm:pt-24 px-4 text-center">
        
        {/* Top Announcement Pill */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-orange-100/90 border border-orange-300 text-orange-950 text-xs font-bold mb-6 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-brand-600" />
          <span>Next-Gen Survey Intelligence & Grounded Chat</span>
        </div>

        {/* Hero Title */}
        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black text-[#24110A] tracking-tight leading-[1.1]">
          Turn your Google & Microsoft Forms <br className="hidden sm:block" />
          <span className="gradient-text">into intelligent insights</span>.
        </h1>

        {/* Subtitle */}
        <p className="mt-6 text-base sm:text-lg text-[#522A1A] font-medium max-w-3xl mx-auto leading-relaxed">
          Connect any Google Form or Microsoft Forms link, analyze every response with verified statistical models, 
          chat with your survey data in natural language, and generate executive reports in seconds.
        </p>

        {/* Hero Form URL Input Bar */}
        <div className="mt-10 max-w-2xl mx-auto">
          <form onSubmit={handleQuickAnalyze} className="relative group">
            <div className="flex flex-col sm:flex-row items-stretch gap-2 p-2 rounded-2xl bg-white border-2 border-[#FAD5C0] shadow-xl hover:border-brand-500 transition-all">
              <input
                type="url"
                value={inputUrl}
                onChange={(e) => {
                  setInputUrl(e.target.value);
                  if (inputError) setInputError('');
                }}
                placeholder="Paste your Google Form or Microsoft Forms link (e.g. forms.office.com/r/...)"
                className="flex-1 bg-transparent px-4 py-3 text-sm text-[#24110A] placeholder-[#8D5A46] focus:outline-none font-medium"
              />
              <button
                type="submit"
                className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 text-white text-sm font-bold shadow-lg shadow-brand-500/25 transition-all active:scale-95 whitespace-nowrap"
              >
                <span>Analyze Form</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
            {inputError && (
              <p className="text-xs text-rose-600 font-bold mt-2.5 text-left pl-2">
                {inputError}
              </p>
            )}
          </form>

          {/* Quick Demo Dataset Launchers */}
          <div className="mt-6 flex flex-wrap items-center justify-center gap-2.5">
            <span className="text-xs text-[#522A1A] font-bold">Instant demo surveys:</span>
            <button
              onClick={() => analyzeDemo('ms_employee_feedback', 'Microsoft 365 Workplace Engagement Survey')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-50 hover:bg-sky-100 border border-sky-300 text-xs font-bold text-sky-900 transition-colors shadow-sm"
              title="Try verified Microsoft Forms demo"
            >
              <Play className="w-3 h-3 text-sky-600 fill-sky-600" />
              <span>Microsoft Forms Demo (25 responses)</span>
            </button>
            <button
              onClick={() => analyzeDemo('workshop_feedback', 'Full-Stack AI Workshop Feedback')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#FFF2EB] hover:bg-[#FFE6D9] border border-[#FAD5C0] text-xs font-bold text-[#3B1F14] transition-colors shadow-sm"
            >
              <Play className="w-3 h-3 text-brand-600 fill-brand-600" />
              <span>Google Form: Workshop (248 responses)</span>
            </button>
            <button
              onClick={() => analyzeDemo('customer_nps', 'Enterprise SaaS Customer NPS')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#FFF2EB] hover:bg-[#FFE6D9] border border-[#FAD5C0] text-xs font-bold text-[#3B1F14] transition-colors shadow-sm"
            >
              <Play className="w-3 h-3 text-brand-600 fill-brand-600" />
              <span>Customer NPS (185 responses)</span>
            </button>
          </div>
        </div>

      </section>

      {/* How it Works / 4-Step Process */}
      <section className="max-w-6xl mx-auto mt-20 px-4">
        <div className="text-center mb-10">
          <h2 className="text-xs font-bold text-brand-600 uppercase tracking-widest">Simple & Instant Workflow</h2>
          <h3 className="text-2xl sm:text-3xl font-extrabold text-[#24110A] mt-2">From raw responses to boardroom reports</h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { step: '01', title: 'Paste Form Link', desc: 'Provide your Google Form URL or connect an associated Google Spreadsheet.' },
            { step: '02', title: 'Data Cleaning & Stats', desc: 'Automatic type inference, duplicate detection, and high-precision math computations.' },
            { step: '03', title: 'Ask Anything & Chat', desc: 'Ask analytical questions in natural language with guaranteed zero-hallucination answers.' },
            { step: '04', title: 'Export in Multi-Format', desc: 'Download PDF executive reports, editable DOCX, 5-sheet Excel workbooks, or Infographics.' },
          ].map((item, i) => (
            <div key={i} className="p-6 rounded-2xl bg-white border border-[#FAD5C0] hover:border-brand-400 shadow-sm transition-all relative group">
              <span className="text-3xl font-black text-brand-600">{item.step}</span>
              <h4 className="text-base font-extrabold text-[#24110A] mt-3">{item.title}</h4>
              <p className="text-xs text-[#6B3B2B] mt-2 font-medium leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Feature Grid */}
      <section className="max-w-6xl mx-auto mt-24 px-4">
        <div className="text-center mb-12">
          <h2 className="text-xs font-bold text-brand-600 uppercase tracking-widest">Complete Feature Suite</h2>
          <h3 className="text-2xl sm:text-3xl font-extrabold text-[#24110A] mt-2">Engineered for researchers, leaders & teams</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => {
            const Icon = f.icon;
            return (
              <div key={i} className="p-6 rounded-2xl bg-white border border-[#FAD5C0] hover:border-brand-400 shadow-sm hover:shadow-md transition-all">
                <div className="w-10 h-10 rounded-xl bg-orange-50 border border-orange-200 flex items-center justify-center text-brand-600 mb-4">
                  <Icon className="w-5 h-5" />
                </div>
                <h4 className="text-base font-extrabold text-[#24110A]">{f.title}</h4>
                <p className="text-xs text-[#6B3B2B] mt-2 font-medium leading-relaxed">{f.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

    </div>
  );
};
