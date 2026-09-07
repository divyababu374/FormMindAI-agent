import React, { useState } from 'react';
import { useForm } from '../context/FormContext';
import { 
  Sparkles, 
  PlusCircle, 
  FolderKanban, 
  ChevronDown, 
  Menu,
  X,
  CheckCircle2,
  Layers
} from 'lucide-react';

export const Navbar = () => {
  const {
    forms,
    currentForm,
    selectForm,
    resetToHome,
    setIsAnalyzeModalOpen,
    setIsMyFormsModalOpen,
    googleStatus,
    setIsGoogleModalOpen
  } = useForm();

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#FAD5C0] bg-white/95 backdrop-blur-lg shadow-sm">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Left: Brand Logo & Desktop Form Switcher */}
        <div className="flex items-center gap-3 sm:gap-6 min-w-0">
          <div 
            onClick={() => {
              setMobileMenuOpen(false);
              resetToHome();
            }} 
            className="flex items-center gap-2 sm:gap-2.5 cursor-pointer group shrink-0"
            title="Return to Home"
          >
            <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-brand-500 flex items-center justify-center shadow-md shadow-brand-500/20 group-hover:scale-105 transition-transform shrink-0">
              <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            </div>
            <div className="flex flex-col">
              <span className="font-black text-base sm:text-lg tracking-tight bg-gradient-to-r from-[#24110A] via-brand-600 to-brand-500 bg-clip-text text-transparent">
                FormMind<span className="text-brand-600 font-black ml-0.5">AI</span>
              </span>
              <span className="text-[9px] sm:text-[10px] text-[#7A4533] font-bold tracking-wider -mt-1 uppercase hidden xs:inline-block">
                Survey Intelligence
              </span>
            </div>
          </div>

          {/* Desktop Form Switcher Dropdown */}
          {forms.length > 0 && currentForm && (
            <div className="hidden lg:flex items-center gap-2 pl-4 border-l border-[#FAD5C0]">
              <span className="text-xs text-[#6B3B2B] font-bold shrink-0">Active Form:</span>
              <div className="relative group">
                <select
                  value={currentForm.id}
                  onChange={(e) => selectForm(e.target.value)}
                  className="appearance-none bg-[#FFF8F4] border border-[#FAD5C0] rounded-xl py-1.5 pl-3 pr-8 text-xs font-bold text-[#24110A] hover:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 cursor-pointer max-w-[200px] truncate shadow-sm"
                >
                  {forms.map((f) => (
                    <option key={f.id} value={f.id}>
                      {f.title}
                    </option>
                  ))}
                </select>
                <ChevronDown className="w-3.5 h-3.5 text-brand-600 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>
            </div>
          )}
        </div>

        {/* Right Desktop Actions (md and up) */}
        <div className="hidden md:flex items-center gap-2.5 lg:gap-3">
          {/* Google Account Connection Button */}
          <button
            onClick={() => setIsGoogleModalOpen(true)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-bold transition-all shadow-sm ${
              googleStatus?.is_connected
                ? 'bg-emerald-50 border-emerald-300 text-emerald-900 hover:bg-emerald-100'
                : 'bg-white border-[#FAD5C0] text-[#24110A] hover:border-brand-500 hover:bg-[#FFF2EB]'
            }`}
            title={googleStatus?.is_connected ? `Connected as ${googleStatus.email}` : "Connect Gmail ID to access private responses"}
          >
            <svg className="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
              <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"/>
              <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
              <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
            </svg>
            <span className="truncate max-w-[120px] lg:max-w-[170px]">
              {googleStatus?.is_connected ? (googleStatus.email || "Google Connected") : "Connect Gmail ID"}
            </span>
            <span className={`w-2 h-2 rounded-full shrink-0 ${googleStatus?.is_connected ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
          </button>

          {/* My Forms Button */}
          {forms.length > 0 && (
            <button
              onClick={() => setIsMyFormsModalOpen(true)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white border border-[#FAD5C0] hover:bg-[#FFF2EB] text-[#24110A] text-xs font-bold transition-colors shadow-sm"
            >
              <FolderKanban className="w-4 h-4 text-brand-600 shrink-0" />
              <span className="truncate">My Forms ({forms.length})</span>
            </button>
          )}

          {/* Analyze New Form Button */}
          <button
            onClick={() => setIsAnalyzeModalOpen(true)}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 text-white text-xs font-bold shadow-md shadow-brand-500/25 transition-all active:scale-95 shrink-0"
          >
            <PlusCircle className="w-4 h-4 shrink-0" />
            <span>Analyze Form</span>
          </button>
        </div>

        {/* Right Mobile Actions (Phones / Small Tablets < md) */}
        <div className="flex md:hidden items-center gap-2">
          {/* Quick primary action: Analyze */}
          <button
            onClick={() => setIsAnalyzeModalOpen(true)}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 text-white text-xs font-bold shadow-sm shadow-brand-500/20 active:scale-95"
            title="Analyze Form"
          >
            <PlusCircle className="w-3.5 h-3.5 shrink-0" />
            <span>Analyze</span>
          </button>

          {/* Mobile Menu Hamburger Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-xl border border-[#FAD5C0] bg-[#FFF8F4] text-[#24110A] hover:bg-[#FFF1E8] active:scale-95 transition-colors relative"
            aria-label="Toggle Navigation Menu"
          >
            {mobileMenuOpen ? (
              <X className="w-4 h-4 text-brand-600" />
            ) : (
              <Menu className="w-4 h-4 text-[#24110A]" />
            )}
            {/* Status indicator dot if connected or forms present */}
            {googleStatus?.is_connected && (
              <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-emerald-500 ring-2 ring-white" />
            )}
          </button>
        </div>

      </div>

      {/* Mobile Drawer Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-[#FAD5C0] bg-white/98 backdrop-blur-xl px-4 py-4 shadow-xl animate-fadeIn space-y-3">
          
          {/* Mobile Active Form Switcher */}
          {forms.length > 0 && currentForm && (
            <div className="p-2.5 rounded-xl bg-[#FFF8F4] border border-[#FAD5C0] space-y-1.5">
              <div className="flex items-center justify-between text-[11px] font-bold text-[#7A4533]">
                <span className="flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-brand-600" />
                  Active Form:
                </span>
                <span className="text-[10px] text-brand-700 bg-[#FFEFE5] px-2 py-0.5 rounded-md font-extrabold">
                  {forms.length} loaded
                </span>
              </div>
              <div className="relative">
                <select
                  value={currentForm.id}
                  onChange={(e) => {
                    selectForm(e.target.value);
                    setMobileMenuOpen(false);
                  }}
                  className="w-full appearance-none bg-white border border-[#FAD5C0] rounded-lg py-2 pl-3 pr-8 text-xs font-bold text-[#24110A] focus:outline-none focus:ring-1 focus:ring-brand-500"
                >
                  {forms.map((f) => (
                    <option key={f.id} value={f.id}>
                      {f.title}
                    </option>
                  ))}
                </select>
                <ChevronDown className="w-4 h-4 text-brand-600 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>
            </div>
          )}

          {/* Quick Action Grid */}
          <div className="grid grid-cols-2 gap-2">
            {/* My Forms Button */}
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                setIsMyFormsModalOpen(true);
              }}
              className="flex items-center justify-center gap-2 p-2.5 rounded-xl bg-white border border-[#FAD5C0] text-[#24110A] text-xs font-bold hover:bg-[#FFF2EB] active:scale-98 transition-colors shadow-sm"
            >
              <FolderKanban className="w-4 h-4 text-brand-600 shrink-0" />
              <span>My Forms ({forms.length})</span>
            </button>

            {/* Google Connection Status */}
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                setIsGoogleModalOpen(true);
              }}
              className={`flex items-center justify-center gap-1.5 p-2.5 rounded-xl border text-xs font-bold transition-all shadow-sm ${
                googleStatus?.is_connected
                  ? 'bg-emerald-50 border-emerald-300 text-emerald-900'
                  : 'bg-white border-[#FAD5C0] text-[#24110A] hover:bg-[#FFF2EB]'
              }`}
            >
              <svg className="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
                <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"/>
                <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
                <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
              </svg>
              <span className="truncate max-w-[100px]">
                {googleStatus?.is_connected ? "Gmail Connected" : "Connect Gmail"}
              </span>
            </button>
          </div>

        </div>
      )}
    </header>
  );
};

