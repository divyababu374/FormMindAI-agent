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
  Mail,
  FileText
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
      setFormError('Please enter a valid Google Form or survey URL.');
      return;
    }
    setFormError('');
    try {
      await analyzeUrl(urlInput.trim(), titleInput.trim() || null);
    } catch (err) {
      setFormError(err.message || 'Failed to analyze this form URL.');
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setFormError('Please choose a file to upload (.xlsx, .xls, .csv).');
      return;
    }
    setFormError('');
    try {
      await uploadFile(selectedFile, titleInput.trim() || null);
    } catch (err) {
      setFormError(err.message || 'Failed to analyze uploaded file.');
    }
  };

  const handleDemoSelect = async (demoType) => {
    setFormError('');
    try {
      await analyzeDemo(demoType);
    } catch (err) {
      setFormError(err.message || 'Failed to load demo dataset.');
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-200 overflow-y-auto"
      onClick={() => setIsAnalyzeModalOpen(false)}
    >
      <div 
        className="relative w-full max-w-lg bg-white rounded-3xl p-5 sm:p-7 border border-[#FAD5C0] shadow-2xl space-y-4 my-auto animate-in zoom-in-95 duration-200 flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[#F5E6DC] shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-orange-50 text-brand-600 flex items-center justify-center border border-orange-200">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-black text-[#24110A] tracking-tight">
                Analyze Survey Dataset
              </h3>
              <p className="text-xs text-[#7A4533] font-medium">
                Import from URL, upload spreadsheets, or explore samples
              </p>
            </div>
          </div>
          <button
            onClick={() => setIsAnalyzeModalOpen(false)}
            className="p-1.5 rounded-full text-[#7A4533] hover:text-[#24110A] hover:bg-orange-50 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex rounded-xl bg-orange-50/70 p-1 border border-orange-200/80 gap-1 shrink-0">
          <button
            onClick={() => { setActiveTab('url'); setFormError(''); }}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-2 rounded-lg text-xs font-bold transition-all ${
              activeTab === 'url' ? 'bg-[#E64825] text-white shadow-xs' : 'text-[#6B3B2B] hover:text-[#24110A]'
            }`}
          >
            <LinkIcon className="w-3.5 h-3.5 shrink-0" />
            <span>Google Form / URL</span>
          </button>
          <button
            onClick={() => { setActiveTab('upload'); setFormError(''); }}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-2 rounded-lg text-xs font-bold transition-all ${
              activeTab === 'upload' ? 'bg-[#E64825] text-white shadow-xs' : 'text-[#6B3B2B] hover:text-[#24110A]'
            }`}
          >
            <UploadCloud className="w-3.5 h-3.5 shrink-0" />
            <span>Upload Excel / CSV</span>
          </button>
          <button
            onClick={() => { setActiveTab('demo'); setFormError(''); }}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-2 rounded-lg text-xs font-bold transition-all ${
              activeTab === 'demo' ? 'bg-[#E64825] text-white shadow-xs' : 'text-[#6B3B2B] hover:text-[#24110A]'
            }`}
          >
            <Play className="w-3.5 h-3.5 shrink-0" />
            <span>Sample Datasets</span>
          </button>
        </div>

        {/* Error Alert */}
        {(formError || error) && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-xl flex items-center gap-2 text-xs font-semibold text-red-700">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
            <span>{formError || error}</span>
          </div>
        )}

        {/* Scrollable Form Content */}
        <div className="overflow-y-auto pr-1 flex-1 space-y-4">
          
          {/* Tab 1: Form / URL */}
          {activeTab === 'url' && (
            <form onSubmit={handleUrlSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-black text-[#24110A] uppercase tracking-wider">
                  Google Form / Survey Link
                </label>
                <input
                  type="url"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  placeholder="https://docs.google.com/forms/d/e/.../viewform"
                  className="w-full bg-[#FFF9F6] border border-[#FAD5C0] rounded-xl px-3.5 py-2.5 text-xs text-[#24110A] placeholder-[#9E6554] font-medium focus:outline-none focus:border-brand-500 focus:bg-white"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-black text-[#24110A] uppercase tracking-wider">
                  Custom Title <span className="text-normal text-[#7A4533] font-normal">(Optional)</span>
                </label>
                <input
                  type="text"
                  value={titleInput}
                  onChange={(e) => setTitleInput(e.target.value)}
                  placeholder="e.g. Q3 Customer NPS Survey"
                  className="w-full bg-[#FFF9F6] border border-[#FAD5C0] rounded-xl px-3.5 py-2.5 text-xs text-[#24110A] placeholder-[#9E6554] font-medium focus:outline-none focus:border-brand-500 focus:bg-white"
                />
              </div>

              <button
                type="submit"
                className="w-full py-3 rounded-xl bg-[#E64825] hover:bg-[#CF3C1B] text-white font-extrabold text-xs shadow-md transition-all active:scale-[0.98] cursor-pointer"
              >
                Analyze Form
              </button>
            </form>
          )}

          {/* Tab 2: Upload Excel / CSV */}
          {activeTab === 'upload' && (
            <form onSubmit={handleFileUpload} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-black text-[#24110A] uppercase tracking-wider">
                  Survey File (.xlsx, .xls, .csv)
                </label>
                <div 
                  onClick={() => document.getElementById('modal-file-input').click()}
                  className="border-2 border-dashed border-[#FAD5C0] hover:border-brand-500 bg-[#FFF9F6] rounded-2xl p-6 text-center cursor-pointer transition-all hover:bg-orange-50/50 space-y-2"
                >
                  <input
                    id="modal-file-input"
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                    className="hidden"
                  />
                  <div className="w-10 h-10 rounded-xl bg-orange-100 text-brand-600 flex items-center justify-center mx-auto">
                    <FileSpreadsheet className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-[#24110A] block">
                      {selectedFile ? selectedFile.name : 'Click to browse survey file'}
                    </span>
                    <span className="text-[11px] text-[#7A4533]">
                      {selectedFile ? `${(selectedFile.size / 1024).toFixed(0)} KB` : 'Supports Excel (.xlsx, .xls) and CSV (.csv)'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-black text-[#24110A] uppercase tracking-wider">
                  Survey Title <span className="text-[#7A4533] font-normal">(Optional)</span>
                </label>
                <input
                  type="text"
                  value={titleInput}
                  onChange={(e) => setTitleInput(e.target.value)}
                  placeholder="e.g. Employee Pulse 2026"
                  className="w-full bg-[#FFF9F6] border border-[#FAD5C0] rounded-xl px-3.5 py-2.5 text-xs text-[#24110A] placeholder-[#9E6554] font-medium focus:outline-none focus:border-brand-500 focus:bg-white"
                />
              </div>

              <button
                type="submit"
                disabled={!selectedFile}
                className="w-full py-3 rounded-xl bg-[#E64825] hover:bg-[#CF3C1B] disabled:opacity-50 text-white font-extrabold text-xs shadow-md transition-all active:scale-[0.98] cursor-pointer"
              >
                Upload & Analyze
              </button>
            </form>
          )}

          {/* Tab 3: Sample Datasets */}
          {activeTab === 'demo' && (
            <div className="space-y-3">
              <span className="text-xs text-[#7A4533] font-medium block">
                Select a ready-to-analyze sample dataset to test the intelligence engine:
              </span>

              <div className="space-y-2">
                {[
                  {
                    id: 'workshop_feedback',
                    title: 'AI Product Workshop Feedback',
                    desc: '248 responses • Likert ratings, text critiques, segment correlations',
                    icon: Sparkles
                  },
                  {
                    id: 'customer_nps',
                    title: 'Customer Satisfaction & NPS 2026',
                    desc: '180 responses • Net Promoter Score, feature rankings, open feedback',
                    icon: ShieldCheck
                  }
                ].map((demo) => (
                  <button
                    key={demo.id}
                    onClick={() => handleDemoSelect(demo.id)}
                    className="w-full p-3.5 rounded-2xl bg-[#FFF9F6] hover:bg-orange-50 border border-[#FAD5C0] hover:border-brand-500 text-left transition-all flex items-center justify-between group cursor-pointer"
                  >
                    <div className="space-y-1">
                      <div className="font-bold text-xs text-[#24110A] group-hover:text-brand-600 transition-colors">
                        {demo.title}
                      </div>
                      <div className="text-[11px] text-[#7A4533]">
                        {demo.desc}
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-brand-600 group-hover:translate-x-0.5 transition-transform shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
};
