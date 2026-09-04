import React, { useState } from 'react';
import { 
  X, 
  FileSpreadsheet, 
  UploadCloud, 
  Link2, 
  HelpCircle, 
  CheckCircle2, 
  AlertCircle, 
  ArrowRight,
  ExternalLink,
  Sparkles
} from 'lucide-react';
import { useForm } from '../context/FormContext';

export const AttachResponsesModal = ({ isOpen, onClose }) => {
  const { currentForm, attachSheetToCurrentForm, uploadResponsesToCurrentForm } = useForm();
  const [activeTab, setActiveTab] = useState('sheet'); // 'sheet' | 'file'
  const [sheetUrl, setSheetUrl] = useState('');
  const [file, setFile] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [localError, setLocalError] = useState(null);

  if (!isOpen || !currentForm) return null;

  const handleAttachSheet = async (e) => {
    e.preventDefault();
    if (!sheetUrl.trim()) {
      setLocalError("Please enter your Google Sheet link.");
      return;
    }
    setLocalError(null);
    setIsSubmitting(true);
    try {
      await attachSheetToCurrentForm(sheetUrl.trim());
      setIsSubmitting(false);
      onClose();
    } catch (err) {
      setIsSubmitting(false);
      setLocalError(err.message || "Failed to attach spreadsheet responses.");
    }
  };

  const handleUploadFile = async (e) => {
    e.preventDefault();
    if (!file) {
      setLocalError("Please select a CSV or Excel responses file.");
      return;
    }
    setLocalError(null);
    setIsSubmitting(true);
    try {
      await uploadResponsesToCurrentForm(file);
      setIsSubmitting(false);
      onClose();
    } catch (err) {
      setIsSubmitting(false);
      setLocalError(err.message || "Failed to import response file.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="w-full max-w-xl rounded-3xl bg-white border border-[#FAD5C0] shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="p-6 border-b border-[#FDE4D7] flex items-center justify-between bg-[#FFF7F2]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-orange-100 border border-orange-200 flex items-center justify-center text-brand-700">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-black text-[#24110A] flex items-center gap-2">
                Attach Form Responses
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-orange-100 text-brand-800 border border-orange-200 font-bold">
                  {currentForm.title}
                </span>
              </h3>
              <p className="text-xs text-[#6B3B2B] font-medium">
                Provide respondent data via Google Sheets link or downloaded CSV
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="w-8 h-8 rounded-full flex items-center justify-center text-[#6B3B2B] hover:text-[#24110A] hover:bg-[#FFF2EB] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Tab Selector */}
          <div className="grid grid-cols-2 p-1 rounded-2xl bg-[#FFF2EB] border border-[#FAD5C0]">
            <button
              onClick={() => { setActiveTab('sheet'); setLocalError(null); }}
              className={`flex items-center justify-center gap-2 py-2.5 rounded-xl text-xs font-bold transition-all ${
                activeTab === 'sheet'
                  ? 'bg-gradient-to-r from-brand-600 to-brand-500 text-white shadow-md shadow-brand-500/25'
                  : 'text-[#6B3B2B] hover:text-[#24110A]'
              }`}
            >
              <Link2 className="w-3.5 h-3.5" />
              <span>Google Sheet Link</span>
            </button>
            <button
              onClick={() => { setActiveTab('file'); setLocalError(null); }}
              className={`flex items-center justify-center gap-2 py-2.5 rounded-xl text-xs font-bold transition-all ${
                activeTab === 'file'
                  ? 'bg-gradient-to-r from-brand-600 to-brand-500 text-white shadow-md shadow-brand-500/25'
                  : 'text-[#6B3B2B] hover:text-[#24110A]'
              }`}
            >
              <UploadCloud className="w-3.5 h-3.5" />
              <span>Upload CSV / Excel</span>
            </button>
          </div>

          {/* Error Message */}
          {localError && (
            <div className="p-3.5 rounded-2xl bg-rose-50 border border-rose-300 text-rose-800 text-xs flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
              <div className="flex-1 leading-relaxed font-semibold">{localError}</div>
            </div>
          )}

          {activeTab === 'sheet' ? (
            <form onSubmit={handleAttachSheet} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#24110A] mb-2">
                  Linked Google Sheet Responses URL
                </label>
                <div className="relative">
                  <input
                    type="url"
                    value={sheetUrl}
                    onChange={(e) => setSheetUrl(e.target.value)}
                    placeholder="https://docs.google.com/spreadsheets/d/.../edit"
                    className="w-full px-4 py-3 rounded-2xl bg-white border border-[#FAD5C0] text-[#24110A] placeholder-[#8C5D4B] text-xs font-medium focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 shadow-sm"
                  />
                  <FileSpreadsheet className="w-4 h-4 text-brand-600 absolute right-3.5 top-3.5" />
                </div>
              </div>

              {/* Step-by-Step Instructions */}
              <div className="p-4 rounded-2xl bg-[#FFF8F4] border border-[#FDE4D7] space-y-2.5 text-xs">
                <div className="font-black text-[#24110A] flex items-center gap-1.5">
                  <HelpCircle className="w-3.5 h-3.5 text-brand-600" />
                  <span>How to get your Google Form response sheet link:</span>
                </div>
                <ol className="space-y-1.5 text-[#4A281A] list-decimal list-inside pl-1 font-medium">
                  <li>Open your form in <strong className="text-[#24110A]">Google Forms</strong></li>
                  <li>Click on the <strong className="text-[#24110A]">Responses</strong> tab</li>
                  <li>Click the green <strong className="text-emerald-700">Link to Sheets</strong> icon (creates/opens a spreadsheet)</li>
                  <li>Copy that spreadsheet URL from your browser address bar and paste it above</li>
                </ol>
                <div className="text-[11px] text-amber-800 font-semibold pt-1 flex items-start gap-1">
                  <span>💡</span>
                  <span>Tip: In your Google Sheet, ensure sharing is set to "Anyone with the link can view" or publish to web via File → Share → Publish to web.</span>
                </div>
              </div>

              <div className="flex justify-end gap-2.5 pt-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2.5 rounded-xl border border-[#FAD5C0] hover:bg-[#FFF2EB] text-[#3B1F14] text-xs font-bold transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !sheetUrl.trim()}
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 text-white text-xs font-bold shadow-md shadow-brand-500/25 transition-all active:scale-95 disabled:opacity-50 flex items-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Syncing Responses...</span>
                    </>
                  ) : (
                    <>
                      <span>Attach & Analyze</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </>
                  )}
                </button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleUploadFile} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#24110A] mb-2">
                  Upload Exported Responses (.csv or .xlsx)
                </label>
                <label className="border-2 border-dashed border-[#FAD5C0] hover:border-brand-500 rounded-2xl p-6 flex flex-col items-center justify-center gap-2.5 bg-[#FFF8F4] cursor-pointer transition-colors group">
                  <div className="w-12 h-12 rounded-2xl bg-orange-100 flex items-center justify-center text-brand-700 group-hover:scale-110 transition-transform">
                    <UploadCloud className="w-6 h-6" />
                  </div>
                  <div className="text-center">
                    <p className="text-xs font-bold text-[#24110A]">
                      {file ? file.name : "Click to select response file"}
                    </p>
                    <p className="text-[11px] text-[#6B3B2B] mt-0.5 font-medium">
                      {file ? `${(file.size / 1024).toFixed(1)} KB` : "Supports Google Forms exported .csv or .xlsx"}
                    </p>
                  </div>
                  <input
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    onChange={(e) => setFile(e.target.files[0] || null)}
                    className="hidden"
                  />
                </label>
              </div>

              {/* Step-by-Step Instructions */}
              <div className="p-4 rounded-2xl bg-[#FFF8F4] border border-[#FDE4D7] space-y-2.5 text-xs">
                <div className="font-black text-[#24110A] flex items-center gap-1.5">
                  <HelpCircle className="w-3.5 h-3.5 text-brand-600" />
                  <span>How to export responses CSV from Google Forms:</span>
                </div>
                <ol className="space-y-1.5 text-[#4A281A] list-decimal list-inside pl-1 font-medium">
                  <li>Open your form in <strong className="text-[#24110A]">Google Forms</strong></li>
                  <li>Click on the <strong className="text-[#24110A]">Responses</strong> tab</li>
                  <li>Click the <strong className="text-[#24110A]">three vertical dots (⋮)</strong> next to the Sheets icon</li>
                  <li>Click <strong className="text-brand-700">Download responses (.csv)</strong></li>
                </ol>
              </div>

              <div className="flex justify-end gap-2.5 pt-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2.5 rounded-xl border border-[#FAD5C0] hover:bg-[#FFF2EB] text-[#3B1F14] text-xs font-bold transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !file}
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 text-white text-xs font-bold shadow-md shadow-brand-500/25 transition-all active:scale-95 disabled:opacity-50 flex items-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Importing Responses...</span>
                    </>
                  ) : (
                    <>
                      <span>Upload & Analyze</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </>
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
