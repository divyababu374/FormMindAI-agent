import React, { useState, useEffect } from 'react';
import { useForm } from '../context/FormContext';
import { api } from '../services/api';
import { 
  X, 
  Link as LinkIcon, 
  UploadCloud, 
  Sparkles, 
  FileSpreadsheet, 
  HelpCircle, 
  AlertCircle, 
  ShieldCheck, 
  Play, 
  CheckCircle2, 
  FolderOpen, 
  ChevronRight, 
  ExternalLink, 
  Mail 
} from 'lucide-react';

export const AnalyzeModal = () => {
  const {
    isAnalyzeModalOpen,
    setIsAnalyzeModalOpen,
    analyzeUrl,
    analyzeDemo,
    uploadFile,
    error,
    setError,
    googleStatus,
    setIsGoogleModalOpen,
    connectEmail
  } = useForm();

  const [activeTab, setActiveTab] = useState('url'); // 'url', 'upload', 'demo'
  const [urlInput, setUrlInput] = useState('');
  const [titleInput, setTitleInput] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [formError, setFormError] = useState('');
  const [quickEmail, setQuickEmail] = useState('');
  const [quickEmailLoading, setQuickEmailLoading] = useState(false);

  // Google Drive Forms state
  const [driveForms, setDriveForms] = useState([]);
  const [loadingDriveForms, setLoadingDriveForms] = useState(false);
  const [showDriveForms, setShowDriveForms] = useState(false);

  const handleQuickConnect = async () => {
    if (!quickEmail.trim() || !quickEmail.includes('@')) {
      setFormError('Please enter a valid Gmail / email address.');
      return;
    }
    setQuickEmailLoading(true);
    setFormError('');
    try {
      await connectEmail(quickEmail.trim());
      setQuickEmail('');
    } catch (err) {
      setFormError(err.message || 'Failed to connect Gmail address.');
    } finally {
      setQuickEmailLoading(false);
    }
  };

  useEffect(() => {
    if (isAnalyzeModalOpen && googleStatus?.is_connected && activeTab === 'url') {
      fetchDriveForms();
    }
  }, [isAnalyzeModalOpen, googleStatus?.is_connected, activeTab]);

  const fetchDriveForms = async () => {
    setLoadingDriveForms(true);
    try {
      const forms = await api.getGoogleDriveForms();
      setDriveForms(forms || []);
    } catch (err) {
      console.error('Failed to load drive forms:', err);
    } finally {
      setLoadingDriveForms(false);
    }
  };

  if (!isAnalyzeModalOpen) return null;

  const handleSelectDriveForm = (form) => {
    setUrlInput(form.edit_url || form.view_url);
    setTitleInput(form.name || '');
    setShowDriveForms(false);
  };

  const handleUrlSubmit = async (e) => {
    e.preventDefault();
    if (!urlInput.trim()) {
      setFormError('Please enter a valid Google Forms or Microsoft Forms link.');
      return;
    }
    setFormError('');
    try {
      await analyzeUrl(urlInput.trim(), titleInput.trim() || null);
    } catch (err) {
      setFormError(err.message || 'Failed to analyze form URL.');
    }
  };

  const handleFileSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setFormError('Please select a CSV or Excel file to upload.');
      return;
    }
    setFormError('');
    try {
      await uploadFile(selectedFile, titleInput.trim() || null);
    } catch (err) {
      setFormError(err.message || 'Failed to parse file.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-2.5 sm:p-4">
      <div className="bg-white border border-[#FAD5C0] rounded-2xl sm:rounded-3xl max-w-xl w-full p-4 sm:p-6 shadow-2xl relative overflow-hidden animate-in fade-in duration-200 max-h-[92dvh] flex flex-col">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-3 sm:pb-4 border-b border-[#FDE4D7] shrink-0">
          <div className="flex items-center gap-2 sm:gap-2.5 min-w-0">
            <div className="p-1.5 sm:p-2 rounded-xl bg-orange-100 text-brand-700 border border-orange-200 shrink-0">
              <Sparkles className="w-4 h-4 sm:w-5 sm:h-5" />
            </div>
            <div className="min-w-0">
              <h3 className="text-base sm:text-lg font-black text-[#24110A] truncate">Import & Analyze Form</h3>
              <p className="text-[11px] sm:text-xs text-[#6B3B2B] font-medium truncate">Ingest responses from Google Forms, Microsoft Forms, or files</p>
            </div>
          </div>
          <button
            onClick={() => {
              setIsAnalyzeModalOpen(false);
              setFormError('');
              setShowDriveForms(false);
            }}
            className="p-1.5 rounded-lg text-[#6B3B2B] hover:text-[#24110A] hover:bg-[#FFF2EB] transition-colors shrink-0 ml-2"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-1 sm:gap-2 p-1 bg-[#FFF2EB] rounded-xl mt-3 sm:mt-4 border border-[#FAD5C0] shrink-0">
          <button
            onClick={() => { setActiveTab('url'); setFormError(''); }}
            className={`flex-1 flex items-center justify-center gap-1 sm:gap-1.5 py-1.5 sm:py-2 px-1 rounded-lg text-[11px] sm:text-xs font-bold transition-all truncate ${
              activeTab === 'url' ? 'bg-gradient-to-r from-brand-600 to-brand-500 text-white shadow-sm' : 'text-[#6B3B2B] hover:text-[#24110A]'
            }`}
          >
            <LinkIcon className="w-3.5 h-3.5 shrink-0" />
            <span className="truncate">Google / MS</span>
          </button>
          <button
            onClick={() => { setActiveTab('upload'); setFormError(''); }}
            className={`flex-1 flex items-center justify-center gap-1 sm:gap-1.5 py-1.5 sm:py-2 px-1 rounded-lg text-[11px] sm:text-xs font-bold transition-all truncate ${
              activeTab === 'upload' ? 'bg-gradient-to-r from-brand-600 to-brand-500 text-white shadow-sm' : 'text-[#6B3B2B] hover:text-[#24110A]'
            }`}
          >
            <UploadCloud className="w-3.5 h-3.5 shrink-0" />
            <span className="truncate">CSV / Excel</span>
          </button>
          <button
            onClick={() => { setActiveTab('demo'); setFormError(''); }}
            className={`flex-1 flex items-center justify-center gap-1 sm:gap-1.5 py-1.5 sm:py-2 px-1 rounded-lg text-[11px] sm:text-xs font-bold transition-all truncate ${
              activeTab === 'demo' ? 'bg-gradient-to-r from-brand-600 to-brand-500 text-white shadow-sm' : 'text-[#6B3B2B] hover:text-[#24110A]'
            }`}
          >
            <Play className="w-3.5 h-3.5 shrink-0" />
            <span className="truncate">Samples</span>
          </button>
        </div>

        {/* Scrollable Form Content */}
        <div className="overflow-y-auto pr-1 mt-4 flex-1">
          
          {/* Tab 1: URL Input */}
          {activeTab === 'url' && (
            <form onSubmit={handleUrlSubmit} className="space-y-4">
              
              {/* Google Account Connection Status Banner */}
              {googleStatus?.is_connected ? (
                <div className="p-3 rounded-2xl bg-emerald-50 border border-emerald-300 flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 text-xs">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    <div>
                      <span className="text-emerald-950 font-bold">Gmail Connected:</span>{' '}
                      <span className="text-emerald-800 font-semibold">{googleStatus.email}</span>
                      <p className="text-[11px] text-emerald-700 font-medium">
                        Submissions from this form link will be retrieved automatically.
                      </p>
                    </div>
                  </div>
                  {driveForms.length > 0 && (
                    <button
                      type="button"
                      onClick={() => setShowDriveForms(!showDriveForms)}
                      className="px-2.5 py-1.5 rounded-lg bg-white hover:bg-emerald-100 text-emerald-900 text-[11px] font-bold border border-emerald-300 transition-colors whitespace-nowrap shrink-0 flex items-center gap-1 shadow-sm"
                    >
                      <FolderOpen className="w-3 h-3" />
                      <span>{showDriveForms ? 'Hide Forms' : `Pick Form (${driveForms.length})`}</span>
                    </button>
                  )}
                </div>
              ) : (
                <div className="p-3.5 rounded-2xl bg-[#FFF8F4] border border-[#FDE4D7] space-y-2.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs">
                      <Mail className="w-4 h-4 text-brand-600 shrink-0" />
                      <div>
                        <span className="font-black text-[#24110A]">Connect with Creator Gmail ID</span>
                        <p className="text-[11px] text-[#6B3B2B] font-medium">
                          Enter your Gmail ID to link form responses & export reports. No tokens needed!
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <input
                      type="email"
                      value={quickEmail}
                      onChange={(e) => setQuickEmail(e.target.value)}
                      placeholder="Enter your Gmail ID (e.g. yourname@gmail.com)"
                      className="flex-1 bg-white border border-[#FAD5C0] rounded-xl px-3 py-1.5 text-xs text-[#24110A] placeholder-[#8C5D4B] font-medium focus:outline-none focus:border-brand-500 shadow-sm"
                    />
                    <button
                      type="button"
                      onClick={handleQuickConnect}
                      disabled={quickEmailLoading || !quickEmail.trim()}
                      className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 disabled:opacity-50 text-white text-xs font-bold shrink-0 transition-all shadow-sm"
                    >
                      {quickEmailLoading ? 'Connecting...' : 'Connect'}
                    </button>
                  </div>
                </div>
              )}

              {/* Drive Forms Quick Select Dropdown */}
              {showDriveForms && driveForms.length > 0 && (
                <div className="p-3 rounded-2xl bg-[#FFF8F4] border border-[#FDE4D7] space-y-2 max-h-44 overflow-y-auto animate-in fade-in duration-150">
                  <span className="text-[11px] font-black text-[#8C2C08] uppercase tracking-wider block">
                    Your Google Forms:
                  </span>
                  {driveForms.map((f) => (
                    <div
                      key={f.id}
                      onClick={() => handleSelectDriveForm(f)}
                      className="p-2 rounded-xl bg-white hover:bg-[#FFF2EB] border border-[#FAD5C0] hover:border-brand-500 cursor-pointer flex items-center justify-between text-xs transition-colors shadow-sm"
                    >
                      <div className="truncate pr-2">
                        <span className="font-bold text-[#24110A] block truncate">{f.name}</span>
                        <span className="text-[10px] text-[#8C5D4B]">ID: {f.id.slice(0, 16)}...</span>
                      </div>
                      <ChevronRight className="w-4 h-4 text-brand-600 shrink-0" />
                    </div>
                  ))}
                </div>
              )}

              <div>
                <label className="block text-xs font-bold text-[#24110A] mb-1.5">
                  Google Form or Microsoft Forms Link <span className="text-rose-500">*</span>
                </label>
                <input
                  type="url"
                  required
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  placeholder="https://forms.office.com/r/... or https://docs.google.com/forms/d/..."
                  className="w-full bg-white border border-[#FAD5C0] rounded-xl px-4 py-2.5 text-sm text-[#24110A] placeholder-[#8C5D4B] font-medium focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 shadow-sm"
                />
                <p className="text-[11px] text-[#6B3B2B] mt-1 flex items-center gap-1 font-medium">
                  <HelpCircle className="w-3 h-3 text-brand-600 shrink-0" />
                  <span>Supports Google Forms (forms.gle, docs.google.com) and Microsoft Forms (forms.office.com, forms.microsoft.com).</span>
                </p>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#24110A] mb-1.5">
                  Custom Title (Optional)
                </label>
                <input
                  type="text"
                  value={titleInput}
                  onChange={(e) => setTitleInput(e.target.value)}
                  placeholder="e.g., Q3 Customer Feedback"
                  className="w-full bg-white border border-[#FAD5C0] rounded-xl px-4 py-2 text-sm text-[#24110A] placeholder-[#8C5D4B] font-medium focus:outline-none focus:border-brand-500 shadow-sm"
                />
              </div>

              <button
                type="submit"
                className="w-full py-3 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 text-white text-sm font-bold shadow-md shadow-brand-500/25 transition-all active:scale-[0.99] flex items-center justify-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                <span>Start AI Analysis</span>
              </button>
            </form>
          )}

          {/* Tab 2: File Upload */}
          {activeTab === 'upload' && (
            <form onSubmit={handleFileSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#24110A] mb-1.5">
                  Upload Exported Form Data (.CSV or .XLSX)
                </label>
                <div className="border-2 border-dashed border-[#FAD5C0] hover:border-brand-500 rounded-2xl p-6 text-center bg-[#FFF8F4] cursor-pointer transition-colors relative">
                  <input
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    onChange={(e) => setSelectedFile(e.target.files[0] || null)}
                    className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                  />
                  <UploadCloud className="w-10 h-10 text-brand-600 mx-auto mb-2" />
                  <p className="text-sm font-bold text-[#24110A]">
                    {selectedFile ? selectedFile.name : 'Click to browse or drag and drop file'}
                  </p>
                  <p className="text-xs text-[#6B3B2B] mt-1 font-medium">Supports Google Forms & Microsoft Forms Excel/CSV responses</p>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#24110A] mb-1.5">
                  Survey Title (Optional)
                </label>
                <input
                  type="text"
                  value={titleInput}
                  onChange={(e) => setTitleInput(e.target.value)}
                  placeholder="e.g., Employee Satisfaction Survey"
                  className="w-full bg-white border border-[#FAD5C0] rounded-xl px-4 py-2 text-sm text-[#24110A] placeholder-[#8C5D4B] font-medium focus:outline-none focus:border-brand-500 shadow-sm"
                />
              </div>

              <button
                type="submit"
                disabled={!selectedFile}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 disabled:opacity-50 text-white text-sm font-bold shadow-md shadow-brand-500/25 transition-all flex items-center justify-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                <span>Upload & Analyze Dataset</span>
              </button>
            </form>
          )}

          {/* Tab 3: Demo Datasets */}
          {activeTab === 'demo' && (
            <div className="space-y-3">
              <p className="text-xs text-[#6B3B2B] font-medium mb-2">
                Select one of our rich preloaded datasets to immediately experience the full analytics suite:
              </p>

              <button
                onClick={() => analyzeDemo('ms_employee_feedback', 'Microsoft 365 Workplace Engagement & Collaboration Survey')}
                className="w-full text-left p-4 rounded-2xl bg-white border border-[#FAD5C0] hover:border-brand-500 hover:bg-orange-50/60 transition-all flex items-center justify-between group shadow-sm"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-sky-100 text-sky-800 border border-sky-200">
                      Microsoft Forms
                    </span>
                    <h4 className="text-sm font-black text-[#24110A] group-hover:text-brand-700 transition-colors">
                      Workplace Engagement & Collaboration
                    </h4>
                  </div>
                  <p className="text-xs text-[#6B3B2B] font-medium mt-1">
                    25 responses • Ratings, Work Arrangements, Teams Apps, Departments & Feedback
                  </p>
                </div>
                <Play className="w-4 h-4 text-brand-600 group-hover:translate-x-0.5 transition-transform" />
              </button>

              <button
                onClick={() => analyzeDemo('workshop_feedback', 'Full-Stack AI Workshop Feedback')}
                className="w-full text-left p-4 rounded-2xl bg-white border border-[#FAD5C0] hover:border-brand-500 hover:bg-orange-50/60 transition-all flex items-center justify-between group shadow-sm"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-orange-100 text-brand-800 border border-orange-200">
                      Google Form
                    </span>
                    <h4 className="text-sm font-black text-[#24110A] group-hover:text-brand-700 transition-colors">
                      Student Workshop Feedback
                    </h4>
                  </div>
                  <p className="text-xs text-[#6B3B2B] font-medium mt-1">
                    248 responses • Ratings, Departments, Favorite Topics, Multi-select Skills, Feedback
                  </p>
                </div>
                <Play className="w-4 h-4 text-brand-600 group-hover:translate-x-0.5 transition-transform" />
              </button>

              <button
                onClick={() => analyzeDemo('customer_nps', 'Enterprise SaaS Customer Satisfaction & Feature Survey')}
                className="w-full text-left p-4 rounded-2xl bg-white border border-[#FAD5C0] hover:border-brand-500 hover:bg-orange-50/60 transition-all flex items-center justify-between group shadow-sm"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200">
                      Google Form
                    </span>
                    <h4 className="text-sm font-black text-[#24110A] group-hover:text-purple-700 transition-colors">
                      Customer Satisfaction & NPS Survey
                    </h4>
                  </div>
                  <p className="text-xs text-[#6B3B2B] font-medium mt-1">
                    185 responses • Net Promoter Scores, Pricing Tiers, Support Rating, Feature Requests
                  </p>
                </div>
                <Play className="w-4 h-4 text-brand-600 group-hover:translate-x-0.5 transition-transform" />
              </button>
            </div>
          )}

          {/* Error Notice */}
          {formError && (
            <div className="mt-4 p-3 rounded-xl bg-rose-50 border border-rose-300 text-xs text-rose-800 flex items-start gap-2 font-semibold">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <span>{formError}</span>
            </div>
          )}

        </div>

      </div>
    </div>
  );
};
