import React, { useState, useRef, useEffect } from 'react';
import { 
  Plus, 
  ArrowRight, 
  FileSpreadsheet, 
  FileText, 
  Link as LinkIcon, 
  X, 
  Sparkles, 
  Clock, 
  BarChart3, 
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Layers
} from 'lucide-react';
import { useForm } from '../context/FormContext';

export const AnalysisHome = () => {
  const { 
    authUser, 
    forms, 
    selectForm, 
    uploadFile, 
    analyzeUrl, 
    analyzeDemo,
    setIsAnalyzeModalOpen 
  } = useForm();

  // Input states
  const [promptText, setPromptText] = useState('');
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [attachedFile, setAttachedFile] = useState(null);
  const [attachedUrl, setAttachedUrl] = useState('');
  const [isUrlInputMode, setIsUrlInputMode] = useState(false);
  const [tempUrl, setTempUrl] = useState('');
  const [inputError, setInputError] = useState('');

  // Refs
  const menuRef = useRef(null);
  const fileInputRef = useRef(null);
  const excelInputRef = useRef(null);
  const textInputRef = useRef(null);

  // Time-based greeting
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const userName = authUser?.name || authUser?.email?.split('@')[0] || 'there';

  // Close plus menu on outside click or Escape
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setIsMenuOpen(false);
      }
    };
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setIsMenuOpen(false);
        setIsUrlInputMode(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const ext = file.name.split('.').pop().toLowerCase();
      if (!['csv', 'xlsx', 'xls'].includes(ext)) {
        setInputError("This file format isn't supported. Please upload CSV, XLS, or XLSX.");
        return;
      }
      setAttachedFile(file);
      setAttachedUrl('');
      setIsUrlInputMode(false);
      setInputError('');
      setIsMenuOpen(false);
    }
  };

  const handleUrlAttach = () => {
    if (!tempUrl.trim()) return;
    setAttachedUrl(tempUrl.trim());
    setAttachedFile(null);
    setIsUrlInputMode(false);
    setTempUrl('');
    setInputError('');
    setIsMenuOpen(false);
  };

  const removeAttachment = () => {
    setAttachedFile(null);
    setAttachedUrl('');
    setIsUrlInputMode(false);
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    setInputError('');

    // Case 1: File attached
    if (attachedFile) {
      try {
        await uploadFile(attachedFile, promptText.trim() || null);
      } catch (err) {
        setInputError(err.message || "We couldn't analyze this dataset. Please check the file and try again.");
      }
      return;
    }

    // Case 2: URL attached
    if (attachedUrl) {
      try {
        await analyzeUrl(attachedUrl, promptText.trim() || null);
      } catch (err) {
        setInputError(err.message || "We couldn't analyze this form link. Please check the URL.");
      }
      return;
    }

    // Case 3: Prompt only without attachment
    if (promptText.trim()) {
      // If user typed a URL directly into the prompt
      if (promptText.includes('forms.gle') || promptText.includes('docs.google.com/forms') || promptText.includes('forms.office.com')) {
        try {
          await analyzeUrl(promptText.trim());
        } catch (err) {
          setInputError(err.message || "We couldn't analyze this form link.");
        }
        return;
      }

      setInputError('Please attach a survey dataset (.xlsx, .csv) or form link using the (+) button to begin.');
    } else {
      setInputError('Click the (+) button to attach a CSV, Excel, or Form URL to analyze.');
    }
  };

  const handleQuickPrompt = (prompt) => {
    setPromptText(prompt);
    if (!attachedFile && !attachedUrl) {
      // If no file attached, open demo to give instant results or open attachment menu
      analyzeDemo('workshop_feedback', prompt);
    } else {
      handleSubmit();
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10 sm:py-16 space-y-12">
      
      {/* Personalized Welcome Header */}
      <div className="text-center space-y-3">
        <h1 className="text-3xl sm:text-4xl font-black text-[#24110A] tracking-tight">
          {getGreeting()}, <span className="bg-gradient-to-r from-[#E64825] to-[#FF7A50] bg-clip-text text-transparent">{userName}</span> 👋
        </h1>
        <p className="text-base sm:text-lg text-[#6B3B2B] font-medium">
          What would you like to analyze today?
        </p>
      </div>

      {/* Hidden File Inputs */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        accept=".csv"
        className="hidden"
      />
      <input
        type="file"
        ref={excelInputRef}
        onChange={handleFileSelect}
        accept=".xlsx, .xls"
        className="hidden"
      />

      {/* Main Interactive "+ Ask anything" Input Container */}
      <div className="space-y-4">
        <form 
          onSubmit={handleSubmit}
          className="relative bg-white rounded-3xl border-2 border-[#FAD5C0] hover:border-brand-400 focus-within:border-brand-500 focus-within:ring-4 focus-within:ring-orange-500/10 shadow-lg shadow-orange-950/5 transition-all p-3 sm:p-4"
        >
          {/* Attachment Chips (Inside input container) */}
          {(attachedFile || attachedUrl) && (
            <div className="flex flex-wrap items-center gap-2 pb-3 mb-2 border-b border-[#F5E6DC]">
              {attachedFile && (
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-orange-50 border border-orange-200 text-xs font-bold text-[#24110A]">
                  <FileSpreadsheet className="w-4 h-4 text-brand-600" />
                  <span className="truncate max-w-[220px]">{attachedFile.name}</span>
                  <span className="text-[10px] text-[#7A4533] font-normal">
                    ({(attachedFile.size / 1024).toFixed(0)} KB)
                  </span>
                  <button
                    type="button"
                    onClick={removeAttachment}
                    className="p-0.5 rounded-full hover:bg-orange-200/70 text-[#7A4533] hover:text-[#24110A] transition-colors"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}

              {attachedUrl && (
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-orange-50 border border-orange-200 text-xs font-bold text-[#24110A]">
                  <LinkIcon className="w-4 h-4 text-brand-600" />
                  <span className="truncate max-w-[220px]">{attachedUrl}</span>
                  <button
                    type="button"
                    onClick={removeAttachment}
                    className="p-0.5 rounded-full hover:bg-orange-200/70 text-[#7A4533] hover:text-[#24110A] transition-colors"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Inline URL Input Mode */}
          {isUrlInputMode && !attachedUrl && (
            <div className="flex items-center gap-2 pb-3 mb-2 border-b border-[#F5E6DC] animate-in fade-in duration-150">
              <LinkIcon className="w-4 h-4 text-brand-600 shrink-0 ml-1" />
              <input
                type="url"
                value={tempUrl}
                onChange={(e) => setTempUrl(e.target.value)}
                placeholder="Paste Google Form or data source URL..."
                className="flex-1 text-xs font-medium text-[#24110A] placeholder-[#9E6554] focus:outline-none bg-transparent"
                autoFocus
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleUrlAttach())}
              />
              <button
                type="button"
                onClick={handleUrlAttach}
                className="px-3 py-1 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-2xs"
              >
                Attach
              </button>
              <button
                type="button"
                onClick={() => setIsUrlInputMode(false)}
                className="p-1 rounded-md text-[#7A4533] hover:bg-orange-100"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* Main Input Row */}
          <div className="flex items-center gap-3">
            
            {/* Integrated Plus (+) Button & Popover Menu */}
            <div className="relative" ref={menuRef}>
              <button
                type="button"
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className={`w-10 h-10 rounded-2xl flex items-center justify-center transition-all cursor-pointer ${
                  isMenuOpen 
                    ? 'bg-brand-600 text-white shadow-md shadow-orange-500/20 rotate-45' 
                    : 'bg-orange-50 hover:bg-orange-100 text-[#24110A] border border-orange-200/80 hover:border-brand-500 shadow-2xs active:scale-95'
                }`}
                title="Add file or data source"
                aria-label="Add file or data source"
              >
                <Plus className="w-5 h-5 transition-transform" />
              </button>

              {/* Compact Attachment Menu */}
              {isMenuOpen && (
                <div className="absolute left-0 top-12 z-30 w-56 bg-white rounded-2xl border border-[#FAD5C0] shadow-xl p-2 space-y-1 animate-in zoom-in-95 duration-150">
                  <div className="px-3 py-1.5 text-[11px] font-black uppercase tracking-wider text-[#7A4533]">
                    Add to analysis
                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      excelInputRef.current?.click();
                    }}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-bold text-[#24110A] hover:bg-orange-50/80 hover:text-brand-600 transition-colors text-left cursor-pointer"
                  >
                    <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
                    <span>Upload Excel (.xlsx, .xls)</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      fileInputRef.current?.click();
                    }}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-bold text-[#24110A] hover:bg-orange-50/80 hover:text-brand-600 transition-colors text-left cursor-pointer"
                  >
                    <FileText className="w-4 h-4 text-blue-600" />
                    <span>Upload CSV (.csv)</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setIsMenuOpen(false);
                      setIsUrlInputMode(true);
                    }}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-bold text-[#24110A] hover:bg-orange-50/80 hover:text-brand-600 transition-colors text-left cursor-pointer"
                  >
                    <LinkIcon className="w-4 h-4 text-purple-600" />
                    <span>Google Form / URL</span>
                  </button>
                </div>
              )}
            </div>

            {/* Prompt Input */}
            <input
              ref={textInputRef}
              type="text"
              value={promptText}
              onChange={(e) => setPromptText(e.target.value)}
              placeholder={
                attachedFile 
                  ? `Ask anything about ${attachedFile.name}...`
                  : attachedUrl
                  ? "Ask anything about this form..."
                  : "Ask anything about your survey data..."
              }
              className="flex-1 text-sm sm:text-base font-medium text-[#24110A] placeholder-[#9E6554] focus:outline-none bg-transparent"
            />

            {/* Submit Action Button */}
            <button
              type="submit"
              className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-[#E64825] to-[#FF7A50] hover:from-[#CF3C1B] hover:to-[#E64825] text-white flex items-center justify-center shadow-md shadow-orange-500/20 active:scale-95 transition-all cursor-pointer shrink-0"
              title="Analyze"
              aria-label="Submit analysis"
            >
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </form>

        {/* Error Notification */}
        {inputError && (
          <div className="flex items-center gap-2 p-3 text-xs font-semibold text-red-700 bg-red-50 border border-red-200 rounded-2xl animate-in fade-in">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
            <span>{inputError}</span>
          </div>
        )}

        {/* Prompt Suggestions */}
        <div className="space-y-2">
          <div className="text-xs font-bold text-[#7A4533] flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-brand-600" />
            <span>Try asking:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {[
              "Analyze my customer feedback",
              "Find the biggest problems",
              "Summarize this survey",
              "Calculate satisfaction & NPS"
            ].map((prompt, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleQuickPrompt(prompt)}
                className="px-3.5 py-1.5 rounded-full bg-white hover:bg-orange-50 border border-[#FAD5C0] hover:border-brand-500 text-xs font-semibold text-[#24110A] shadow-2xs hover:shadow-xs transition-all cursor-pointer active:scale-98"
              >
                "{prompt}"
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Analyses Section (Uses existing backend forms list) */}
      <div className="space-y-4 pt-4 border-t border-[#F5E6DC]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-brand-600" />
            <h3 className="text-base font-black text-[#24110A] tracking-tight">
              Recent Analyses
            </h3>
          </div>
          {forms.length > 0 && (
            <span className="text-xs text-[#7A4533] font-semibold">
              {forms.length} {forms.length === 1 ? 'survey' : 'surveys'} analyzed
            </span>
          )}
        </div>

        {forms.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {forms.map((form) => (
              <div
                key={form.id}
                onClick={() => selectForm(form.id)}
                className="group bg-white rounded-2xl p-5 border border-[#FAD5C0] hover:border-brand-500 hover:shadow-md transition-all cursor-pointer flex flex-col justify-between space-y-4"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between gap-2">
                    <span className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-orange-50 text-brand-600 border border-orange-200/60">
                      {form.source_type || 'Survey'}
                    </span>
                    <span className="text-[11px] text-[#9E6554] font-medium">
                      {form.updated_at ? new Date(form.updated_at).toLocaleDateString() : 'Recent'}
                    </span>
                  </div>
                  <h4 className="font-bold text-sm text-[#24110A] group-hover:text-brand-600 transition-colors line-clamp-2">
                    {form.title}
                  </h4>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-[#F5E6DC] text-xs">
                  <span className="text-[#6B3B2B] font-semibold">
                    {form.total_responses_count ?? 0} responses
                  </span>
                  <span className="text-brand-600 font-bold group-hover:translate-x-1 transition-transform inline-flex items-center gap-0.5">
                    Open →
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white/80 rounded-2xl p-8 border border-dashed border-[#FAD5C0] text-center space-y-3">
            <div className="w-10 h-10 rounded-xl bg-orange-50 text-brand-600 flex items-center justify-center mx-auto border border-orange-200/60">
              <Layers className="w-5 h-5" />
            </div>
            <div className="space-y-1">
              <h4 className="text-sm font-bold text-[#24110A]">No previous analyses yet</h4>
              <p className="text-xs text-[#7A4533] max-w-sm mx-auto">
                Attach an Excel/CSV file or Form URL in the box above, or explore a sample demo dataset.
              </p>
            </div>
            <button
              onClick={() => analyzeDemo('workshop_feedback')}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-orange-50 hover:bg-orange-100 text-xs font-bold text-brand-600 border border-orange-200 transition-all cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5" />
              Load Sample Dataset
            </button>
          </div>
        )}
      </div>

    </div>
  );
};
