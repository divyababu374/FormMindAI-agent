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
  CheckCircle2,
  FileSpreadsheet,
  Image as ImageIcon,
  Play,
  Mail,
  Lock,
  ExternalLink,
  AlertCircle,
  FolderKanban,
  Unlink
} from 'lucide-react';
import { Badge } from './common/Badge';
import confetti from 'canvas-confetti';

export const LandingPage = () => {
  const { 
    googleStatus, 
    connectEmail, 
    disconnectGoogle,
    analyzeUrl, 
    analyzeDemo, 
    forms,
    currentForm,
    selectForm
  } = useForm();

  // 1-Click Email connect state
  const [emailInput, setEmailInput] = useState('');
  const [emailLoading, setEmailLoading] = useState(false);
  const [connectError, setConnectError] = useState('');
  const [connectSuccess, setConnectSuccess] = useState('');

  // Form URL analyzer state (when connected)
  const [inputUrl, setInputUrl] = useState('');
  const [inputError, setInputError] = useState('');

  const isConnected = Boolean(googleStatus?.is_connected);

  const handleEmailConnect = async (e) => {
    e.preventDefault();
    const clean = emailInput.trim();
    if (!clean || !clean.includes('@')) {
      setConnectError('Please enter a valid Gmail or work email address.');
      return;
    }
    setConnectError('');
    setEmailLoading(true);
    try {
      await connectEmail(clean);
      setConnectSuccess(`Connected successfully as ${clean}!`);
      try {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 }
        });
      } catch {
        // confetti fallback
      }
    } catch (err) {
      setConnectError(err.message || 'Failed to connect email account.');
    } finally {
      setEmailLoading(false);
    }
  };

  const handleQuickAnalyze = async (e) => {
    e.preventDefault();
    if (!inputUrl.trim()) {
      setInputError('Please enter a valid Google Forms or Microsoft Forms URL.');
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
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-[600px] bg-gradient-to-b from-brand-500/15 via-orange-300/10 to-transparent blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-1/3 -left-40 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-1/2 -right-40 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl pointer-events-none -z-10" />

      {/* Hero Section */}
      <section className="max-w-5xl mx-auto pt-8 sm:pt-16 px-4 text-center">
        
        {/* Top Announcement Pill */}
        <div className="inline-flex items-center gap-1.5 sm:gap-2 px-3.5 py-1.5 rounded-full bg-orange-100/90 border border-orange-300 text-orange-950 text-[11px] sm:text-xs font-bold mb-4 sm:mb-6 shadow-sm max-w-full">
          <Sparkles className="w-3.5 h-3.5 text-brand-600 shrink-0" />
          <span className="truncate">Next-Gen Survey Intelligence & Grounded Chat</span>
        </div>

        {/* Hero Title */}
        <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black text-[#24110A] tracking-tight leading-[1.15] sm:leading-[1.1]">
          Turn your Google & Microsoft Forms <br className="hidden sm:block" />
          <span className="gradient-text">into intelligent insights</span>.
        </h1>

        {/* Subtitle */}
        <p className="mt-3.5 sm:mt-5 text-sm sm:text-base text-[#522A1A] font-medium max-w-3xl mx-auto leading-relaxed">
          {isConnected ? (
            <span>Analyze your survey responses with verified statistical models, chat with your data in natural language, and generate executive reports in seconds.</span>
          ) : (
            <span>Connect your Gmail account in 1-click to unlock full mathematical analysis, conversational AI chat, and multi-format report exports with zero hallucinations.</span>
          )}
        </p>

        {/* ========================================================= */}
        {/* HERO CARD: GATED BY CONNECTION STATE                      */}
        {/* ========================================================= */}
        <div className="mt-8 sm:mt-10 max-w-2xl mx-auto">
          
          {!isConnected ? (
            /* 1-CLICK GMAIL CONNECT / SIGN-UP CARD */
            <div className="p-6 sm:p-8 rounded-3xl bg-white/95 backdrop-blur-md border-2 border-[#FAD5C0] shadow-2xl relative overflow-hidden text-left transition-all">
              
              {/* Card Header */}
              <div className="flex items-center gap-3 pb-5 border-b border-[#FDE4D7]">
                <div className="p-2.5 rounded-2xl bg-orange-100 text-brand-600 border border-orange-200 shrink-0">
                  <Mail className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-base sm:text-lg font-black text-[#24110A] tracking-tight">
                    Sign In & Connect with Gmail
                  </h3>
                  <p className="text-xs text-[#6B3B2B] font-medium mt-0.5">
                    1-Click access to survey intelligence. No password required.
                  </p>
                </div>
              </div>

              {/* Form Input */}
              <form onSubmit={handleEmailConnect} className="mt-5 space-y-3">
                <div>
                  <label className="block text-xs font-bold text-[#3B1F14] mb-1.5">
                    Your Gmail / Email Address
                  </label>
                  <div className="relative">
                    <input
                      type="email"
                      required
                      value={emailInput}
                      onChange={(e) => {
                        setEmailInput(e.target.value);
                        if (connectError) setConnectError('');
                      }}
                      placeholder="e.g., yourname@gmail.com"
                      className="w-full px-4 py-3 rounded-xl bg-[#FFF9F5] border border-[#FAD5C0] text-sm text-[#24110A] placeholder-[#946452] font-medium focus:outline-none focus:ring-2 focus:ring-brand-500/30 focus:border-brand-500 transition-all"
                    />
                  </div>
                </div>

                {connectError && (
                  <div className="p-3 rounded-xl bg-rose-50 border border-rose-300 flex items-center gap-2 text-xs font-bold text-rose-800">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>{connectError}</span>
                  </div>
                )}

                {connectSuccess && (
                  <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-300 flex items-center gap-2 text-xs font-bold text-emerald-800">
                    <CheckCircle2 className="w-4 h-4 shrink-0" />
                    <span>{connectSuccess}</span>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={emailLoading}
                  className="w-full py-3.5 px-6 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 text-white text-sm font-black shadow-lg shadow-brand-500/25 transition-all flex items-center justify-center gap-2 active:scale-98 disabled:opacity-60"
                >
                  {emailLoading ? (
                    <span className="inline-flex items-center gap-2">
                      <svg className="animate-spin w-4 h-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                      </svg>
                      <span>Connecting...</span>
                    </span>
                  ) : (
                    <>
                      <span>Connect Gmail Account (1-Click)</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>

              {/* Trust Indicators */}
              <div className="mt-5 grid grid-cols-1 sm:grid-cols-3 gap-2 text-center text-[11px] font-bold text-[#6B3B2B] pt-2">
                <div className="flex items-center justify-center gap-1.5">
                  <Zap className="w-3.5 h-3.5 text-brand-600 shrink-0" />
                  <span>Instant Access</span>
                </div>
                <div className="flex items-center justify-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span>100% Private Database</span>
                </div>
                <div className="flex items-center justify-center gap-1.5">
                  <CheckCircle className="w-3.5 h-3.5 text-sky-600 shrink-0" />
                  <span>Zero Password Needed</span>
                </div>
              </div>

            </div>
          ) : (
            /* UNLOCKED WORKSPACE: URL ANALYZER & DEMO SURVEYS */
            <div className="space-y-4">
              {/* Connected Banner */}
              <div className="p-3.5 sm:p-4 rounded-2xl bg-emerald-50 border border-emerald-300 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-left shadow-sm">
                <div className="flex items-center gap-2.5 min-w-0 flex-1">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-black text-emerald-950 truncate">
                      Connected as <span className="underline decoration-emerald-400 font-extrabold">{googleStatus?.email}</span>
                    </p>
                    <p className="text-[11px] text-emerald-800 font-medium">
                      All survey analysis features are unlocked for your account.
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0 self-stretch sm:self-auto justify-end flex-wrap">
                  {forms.length > 0 && (
                    <button
                      onClick={() => selectForm(forms[0].id)}
                      className="px-3 py-1.5 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold transition-colors shrink-0 shadow-sm flex items-center gap-1 cursor-pointer"
                    >
                      <FolderKanban className="w-3.5 h-3.5" />
                      <span>Open Form</span>
                    </button>
                  )}
                  <button
                    onClick={disconnectGoogle}
                    className="px-3 py-1.5 rounded-xl bg-white hover:bg-rose-50 border border-rose-200 hover:border-rose-400 text-rose-700 hover:text-rose-800 text-xs font-bold transition-all shadow-sm flex items-center gap-1 cursor-pointer shrink-0 active:scale-95"
                    title="Disconnect this account"
                  >
                    <Unlink className="w-3.5 h-3.5 text-rose-600 shrink-0" />
                    <span>Disconnect</span>
                  </button>
                </div>
              </div>

              {/* Form URL Input */}
              <form onSubmit={handleQuickAnalyze} className="relative group">
                <div className="flex flex-col sm:flex-row items-stretch gap-2 p-1.5 sm:p-2 rounded-2xl bg-white border-2 border-[#FAD5C0] shadow-xl hover:border-brand-500 transition-all">
                  <input
                    type="url"
                    value={inputUrl}
                    onChange={(e) => {
                      setInputUrl(e.target.value);
                      if (inputError) setInputError('');
                    }}
                    placeholder="Paste your Google Form or Microsoft Forms link..."
                    className="flex-1 bg-transparent px-3 sm:px-4 py-2.5 sm:py-3 text-xs sm:text-sm text-[#24110A] placeholder-[#8D5A46] focus:outline-none font-medium min-w-0"
                  />
                  <button
                    type="submit"
                    className="flex items-center justify-center gap-2 px-5 sm:px-6 py-2.5 sm:py-3 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 text-white text-xs sm:text-sm font-bold shadow-lg shadow-brand-500/25 transition-all active:scale-95 whitespace-nowrap"
                  >
                    <span>Analyze Form</span>
                    <ArrowRight className="w-4 h-4 shrink-0" />
                  </button>
                </div>
                {inputError && (
                  <p className="text-xs text-rose-600 font-bold mt-2.5 text-left pl-2">
                    {inputError}
                  </p>
                )}
              </form>

              {/* Instant Demo Surveys */}
              <div className="mt-4 flex flex-col sm:flex-row flex-wrap items-center justify-center gap-2 sm:gap-2.5">
                <span className="text-xs text-[#522A1A] font-bold">Instant demo surveys:</span>
                <div className="flex flex-col sm:flex-row flex-wrap items-center justify-center gap-2 w-full sm:w-auto">
                  <button
                    onClick={() => analyzeDemo('ms_employee_feedback', 'Microsoft 365 Workplace Engagement Survey')}
                    className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-50 hover:bg-sky-100 border border-sky-300 text-xs font-bold text-sky-900 transition-colors shadow-sm w-full sm:w-auto text-center"
                    title="Try verified Microsoft Forms demo"
                  >
                    <Play className="w-3 h-3 text-sky-600 fill-sky-600 shrink-0" />
                    <span>Microsoft Forms Demo (25 responses)</span>
                  </button>
                  <button
                    onClick={() => analyzeDemo('workshop_feedback', 'Full-Stack AI Workshop Feedback')}
                    className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#FFF2EB] hover:bg-[#FFE6D9] border border-[#FAD5C0] text-xs font-bold text-[#3B1F14] transition-colors shadow-sm w-full sm:w-auto text-center"
                  >
                    <Play className="w-3 h-3 text-brand-600 fill-brand-600 shrink-0" />
                    <span>Google Form: Workshop (248 responses)</span>
                  </button>
                  <button
                    onClick={() => analyzeDemo('customer_nps', 'Enterprise SaaS Customer NPS')}
                    className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#FFF2EB] hover:bg-[#FFE6D9] border border-[#FAD5C0] text-xs font-bold text-[#3B1F14] transition-colors shadow-sm w-full sm:w-auto text-center"
                  >
                    <Play className="w-3 h-3 text-brand-600 fill-brand-600 shrink-0" />
                    <span>Customer NPS (185 responses)</span>
                  </button>
                </div>
              </div>
            </div>
          )}

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
            { step: '01', title: 'Connect Your Gmail', desc: '1-click connect with zero passwords to establish your secure analytical workspace.' },
            { step: '02', title: 'Paste Form Link', desc: 'Provide your Google Form URL, Microsoft Form link, or attach your responses file.' },
            { step: '03', title: 'Mathematical Stats', desc: 'Automatic statistical calculation, completion score, and verified distribution charts.' },
            { step: '04', title: 'Chat & Boardroom Reports', desc: 'Ask analytical questions in natural language and export PDF, DOCX, or Excel in seconds.' },
          ].map((item, i) => (
            <div key={i} className="p-6 rounded-2xl bg-white border border-[#FAD5C0] hover:border-brand-400 shadow-sm transition-all relative group">
              <span className="text-3xl font-black text-brand-600">{item.step}</span>
              <h4 className="text-base font-extrabold text-[#24110A] mt-3">{item.title}</h4>
              <p className="text-xs text-[#6B3B2B] mt-2 font-medium leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Feature Grid with Gating Indicators */}
      <section className="max-w-6xl mx-auto mt-24 px-4">
        <div className="text-center mb-12">
          <h2 className="text-xs font-bold text-brand-600 uppercase tracking-widest">Complete Feature Suite</h2>
          <h3 className="text-2xl sm:text-3xl font-extrabold text-[#24110A] mt-2">Engineered for researchers, leaders & teams</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => {
            const Icon = f.icon;
            return (
              <div 
                key={i} 
                className={`p-6 rounded-2xl bg-white border border-[#FAD5C0] transition-all shadow-sm relative overflow-hidden ${
                  isConnected ? 'hover:border-brand-400 hover:shadow-md' : 'opacity-90'
                }`}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-orange-50 border border-orange-200 flex items-center justify-center text-brand-600">
                    <Icon className="w-5 h-5" />
                  </div>
                  {!isConnected ? (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-50 border border-amber-200 text-[10px] font-bold text-amber-800">
                      <Lock className="w-3 h-3 text-amber-600" />
                      <span>Unlocks after connect</span>
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-[10px] font-bold text-emerald-800">
                      <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                      <span>Ready to use</span>
                    </span>
                  )}
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
