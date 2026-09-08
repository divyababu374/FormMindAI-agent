import React, { useState, useRef, useEffect } from 'react';
import { useForm } from '../context/FormContext';
import { 
  Sparkles, 
  Plus, 
  ChevronDown, 
  Menu, 
  X, 
  ArrowLeft,
  LogOut,
  User,
  LayoutDashboard,
  Home,
  Play,
  Layers
} from 'lucide-react';

export const Navbar = () => {
  const {
    authUser,
    currentForm,
    resetToHome,
    goBack,
    setIsAuthModalOpen,
    setIsAnalyzeModalOpen,
    setIsMyFormsModalOpen,
    startDemoMode,
    logout,
    isDemoMode,
    exitDemoMode
  } = useForm();

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const userDropdownRef = useRef(null);

  // Close user dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (userDropdownRef.current && !userDropdownRef.current.contains(e.target)) {
        setUserDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const isAuthenticated = Boolean(authUser);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#FAD5C0] bg-white/95 backdrop-blur-lg shadow-sm font-sans">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Left: Brand Logo & Navigation Back Button */}
        <div className="flex items-center gap-3">
          {currentForm && (
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                goBack();
              }}
              className="p-2 rounded-xl bg-white hover:bg-orange-50 border border-[#FAD5C0] hover:border-brand-500 text-[#3B1F14] hover:text-[#24110A] transition-all shadow-2xs cursor-pointer active:scale-95 group shrink-0"
              title="Go back"
              aria-label="Back"
            >
              <ArrowLeft className="w-4 h-4 text-brand-600 group-hover:-translate-x-0.5 transition-transform" />
            </button>
          )}

          <div 
            onClick={() => {
              setMobileMenuOpen(false);
              resetToHome();
            }} 
            className="flex items-center gap-2.5 cursor-pointer group shrink-0"
            title="Return to Home"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#E64825] to-[#FF7A50] flex items-center justify-center shadow-md shadow-orange-500/20 group-hover:scale-105 transition-transform shrink-0">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div className="flex flex-col">
              <span className="font-black text-lg tracking-tight text-[#24110A]">
                FormMind<span className="text-[#E64825] font-black ml-0.5">AI</span>
              </span>
              <span className="text-[10px] text-[#7A4533] font-bold tracking-wider -mt-1 uppercase hidden xs:inline-block">
                Survey Intelligence
              </span>
            </div>
          </div>
        </div>

        {/* Center / Right: Desktop Navigation */}
        <div className="hidden md:flex items-center gap-3">
          
          {/* Unauthenticated Navigation */}
          {!isAuthenticated && !isDemoMode && (
            <div className="flex items-center gap-3">
              <button
                onClick={startDemoMode}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white hover:bg-orange-50/80 border border-[#FAD5C0] hover:border-brand-500 text-xs font-bold text-[#24110A] transition-all cursor-pointer"
              >
                <Play className="w-3.5 h-3.5 text-brand-600 fill-brand-600" />
                <span>Explore Demo</span>
              </button>

              <button
                onClick={() => setIsAuthModalOpen(true)}
                className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-gradient-to-tr from-[#E64825] to-[#FF7A50] hover:from-[#CF3C1B] hover:to-[#E64825] text-white font-extrabold text-xs shadow-md shadow-orange-500/20 active:scale-[0.98] transition-all cursor-pointer"
              >
                <span>Get Started</span>
              </button>
            </div>
          )}

          {/* Demo Mode Navigation */}
          {isDemoMode && !isAuthenticated && (
            <div className="flex items-center gap-3">
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-50 border border-amber-200 text-xs font-bold text-amber-800">
                Sample Dataset Active
              </span>
              <button
                onClick={() => setIsAuthModalOpen(true)}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#E64825] hover:bg-[#CF3C1B] text-white text-xs font-bold shadow-sm transition-all cursor-pointer"
              >
                <span>Sign in to Analyze Your Data</span>
              </button>
            </div>
          )}

          {/* Authenticated Navigation */}
          {isAuthenticated && (
            <div className="flex items-center gap-3">
              
              {/* Home & Dashboard Switcher */}
              <button
                onClick={resetToHome}
                className={`inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  !currentForm
                    ? 'bg-orange-50 text-brand-600 border border-orange-200'
                    : 'text-[#6B3B2B] hover:text-[#24110A] hover:bg-orange-50/60'
                }`}
              >
                <Home className="w-4 h-4" />
                <span>Home</span>
              </button>

              {currentForm && (
                <div className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-orange-50 text-brand-600 border border-orange-200 text-xs font-bold">
                  <LayoutDashboard className="w-4 h-4" />
                  <span className="truncate max-w-[160px]">{currentForm.title}</span>
                </div>
              )}

              <button
                onClick={() => setIsAnalyzeModalOpen(true)}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-white hover:bg-orange-50/80 border border-[#FAD5C0] hover:border-brand-500 text-xs font-bold text-[#24110A] shadow-2xs transition-all cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5 text-brand-600" />
                <span>New Analysis</span>
              </button>

              {/* User Profile Avatar & Dropdown */}
              <div className="relative pl-2 border-l border-[#FAD5C0]" ref={userDropdownRef}>
                <button
                  onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                  className="flex items-center gap-2 p-1.5 rounded-xl hover:bg-orange-50/80 border border-transparent hover:border-[#FAD5C0] transition-all cursor-pointer"
                  aria-label="User menu"
                >
                  {authUser.avatar_url ? (
                    <img 
                      src={authUser.avatar_url} 
                      alt={authUser.name} 
                      className="w-8 h-8 rounded-full border border-orange-200 object-cover" 
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#E64825] to-[#FF7A50] text-white font-black text-xs flex items-center justify-center shadow-2xs">
                      {authUser.name?.charAt(0).toUpperCase() || 'U'}
                    </div>
                  )}
                  <span className="text-xs font-bold text-[#24110A] hidden lg:inline-block max-w-[120px] truncate">
                    {authUser.name}
                  </span>
                  <ChevronDown className="w-3.5 h-3.5 text-[#7A4533]" />
                </button>

                {/* Dropdown Menu */}
                {userDropdownOpen && (
                  <div className="absolute right-0 top-12 z-50 w-60 bg-white rounded-2xl border border-[#FAD5C0] shadow-xl p-2 space-y-1 animate-in zoom-in-95 duration-150">
                    <div className="px-3 py-2 border-b border-[#F5E6DC]">
                      <div className="font-bold text-xs text-[#24110A] truncate">{authUser.name}</div>
                      <div className="text-[11px] text-[#7A4533] truncate">{authUser.email}</div>
                    </div>

                    <button
                      onClick={() => {
                        setUserDropdownOpen(false);
                        resetToHome();
                      }}
                      className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-bold text-[#24110A] hover:bg-orange-50 hover:text-brand-600 transition-colors text-left cursor-pointer"
                    >
                      <Home className="w-4 h-4 text-brand-600" />
                      <span>Analysis Home</span>
                    </button>

                    <button
                      onClick={() => {
                        setUserDropdownOpen(false);
                        setIsAnalyzeModalOpen(true);
                      }}
                      className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-bold text-[#24110A] hover:bg-orange-50 hover:text-brand-600 transition-colors text-left cursor-pointer"
                    >
                      <Plus className="w-4 h-4 text-brand-600" />
                      <span>New Analysis</span>
                    </button>

                    <button
                      onClick={() => {
                        setUserDropdownOpen(false);
                        startDemoMode();
                      }}
                      className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-bold text-[#24110A] hover:bg-orange-50 hover:text-brand-600 transition-colors text-left cursor-pointer"
                    >
                      <Play className="w-4 h-4 text-amber-600" />
                      <span>Explore Demo Dataset</span>
                    </button>

                    <div className="pt-1 border-t border-[#F5E6DC]">
                      <button
                        onClick={() => {
                          setUserDropdownOpen(false);
                          logout();
                        }}
                        className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-bold text-red-600 hover:bg-red-50 transition-colors text-left cursor-pointer"
                      >
                        <LogOut className="w-4 h-4" />
                        <span>Log Out</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>

            </div>
          )}

        </div>

        {/* Mobile Hamburger Toggle */}
        <div className="md:hidden flex items-center gap-2">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-xl bg-orange-50 hover:bg-orange-100 text-[#24110A] border border-[#FAD5C0] cursor-pointer"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-[#FAD5C0] bg-white p-4 space-y-3 animate-in slide-in-from-top-2 duration-150">
          {!isAuthenticated ? (
            <div className="space-y-2">
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  startDemoMode();
                }}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-orange-50 border border-orange-200 text-xs font-bold text-[#24110A]"
              >
                <Play className="w-4 h-4 text-brand-600" />
                <span>Explore Demo</span>
              </button>

              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  setIsAuthModalOpen(true);
                }}
                className="w-full py-3 rounded-xl bg-[#E64825] text-white text-xs font-bold shadow-sm"
              >
                <span>Get Started with Google</span>
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="p-3 bg-orange-50 rounded-xl border border-orange-200">
                <div className="font-bold text-xs text-[#24110A]">{authUser.name}</div>
                <div className="text-[11px] text-[#7A4533]">{authUser.email}</div>
              </div>

              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  resetToHome();
                }}
                className="w-full flex items-center gap-2 py-2.5 px-3 rounded-xl text-xs font-bold text-[#24110A] hover:bg-orange-50"
              >
                <Home className="w-4 h-4 text-brand-600" />
                <span>Analysis Home</span>
              </button>

              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  setIsAnalyzeModalOpen(true);
                }}
                className="w-full flex items-center gap-2 py-2.5 px-3 rounded-xl text-xs font-bold text-[#24110A] hover:bg-orange-50"
              >
                <Plus className="w-4 h-4 text-brand-600" />
                <span>New Analysis</span>
              </button>

              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  logout();
                }}
                className="w-full flex items-center gap-2 py-2.5 px-3 rounded-xl text-xs font-bold text-red-600 hover:bg-red-50"
              >
                <LogOut className="w-4 h-4" />
                <span>Log Out</span>
              </button>
            </div>
          )}
        </div>
      )}

    </header>
  );
};
