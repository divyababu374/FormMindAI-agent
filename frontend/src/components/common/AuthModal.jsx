import React, { useState } from 'react';
import { X, Sparkles, Shield, Zap, Lock, AlertCircle, Loader2 } from 'lucide-react';
import { useForm } from '../../context/FormContext';

export const AuthModal = () => {
  const { isAuthModalOpen, setIsAuthModalOpen, loginWithGoogle } = useForm();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isAuthModalOpen) return null;

  const handleGoogleLogin = async () => {
    setError('');
    setLoading(true);
    try {
      await loginWithGoogle();
      setIsAuthModalOpen(false);
    } catch (err) {
      setError(err.message || 'Unable to sign in with Google. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200"
      onClick={() => !loading && setIsAuthModalOpen(false)}
    >
      <div 
        className="relative w-full max-w-md bg-white rounded-3xl p-8 sm:p-10 border border-[#FAD5C0] shadow-2xl text-center space-y-7 animate-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={() => !loading && setIsAuthModalOpen(false)}
          className="absolute top-5 right-5 p-2 rounded-full text-[#7A4533] hover:text-[#24110A] hover:bg-orange-50 transition-colors cursor-pointer"
          aria-label="Close modal"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Brand Logo & Header */}
        <div className="flex flex-col items-center space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-[#E64825] to-[#FF7A50] flex items-center justify-center text-white shadow-lg shadow-orange-500/25">
            <Sparkles className="w-7 h-7" />
          </div>
          <div>
            <h2 className="text-2xl font-black tracking-tight text-[#24110A]">
              Welcome to FormMind
            </h2>
            <p className="text-sm font-medium text-[#7A4533] mt-1">
              Analyze smarter. Understand faster.
            </p>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="flex items-center gap-2 p-3 text-xs font-semibold text-red-700 bg-red-50 border border-red-200 rounded-xl text-left">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
            <span>{error}</span>
          </div>
        )}

        {/* Primary Action: Google Login Button */}
        <div className="space-y-3">
          <button
            onClick={handleGoogleLogin}
            disabled={loading}
            className="w-full flex items-center justify-center gap-3 px-6 py-4 rounded-2xl bg-white hover:bg-orange-50/70 border-2 border-[#FAD5C0] hover:border-brand-500 text-[#24110A] font-bold text-base shadow-sm hover:shadow-md transition-all active:scale-[0.99] cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed group"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin text-brand-600" />
            ) : (
              /* Official Google G SVG Icon */
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                />
              </svg>
            )}
            <span>{loading ? 'Connecting with Google...' : 'Continue with Google'}</span>
          </button>
        </div>

        {/* Security & Privacy Badges */}
        <div className="pt-2 border-t border-[#F5E6DC] flex items-center justify-center gap-3 text-xs text-[#7A4533] font-medium">
          <span className="flex items-center gap-1">
            <Lock className="w-3.5 h-3.5 text-brand-600" />
            Secure
          </span>
          <span className="text-[#D4A390]">•</span>
          <span className="flex items-center gap-1">
            <Zap className="w-3.5 h-3.5 text-amber-600" />
            Fast
          </span>
          <span className="text-[#D4A390]">•</span>
          <span className="flex items-center gap-1">
            <Shield className="w-3.5 h-3.5 text-emerald-600" />
            Private
          </span>
        </div>
      </div>
    </div>
  );
};
