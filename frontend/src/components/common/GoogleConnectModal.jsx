import React, { useState } from 'react';
import { useForm } from '../../context/FormContext';
import { 
  X, 
  CheckCircle2, 
  AlertCircle, 
  Mail, 
  KeyRound, 
  ExternalLink, 
  ShieldCheck, 
  Unlink, 
  Settings, 
  ChevronDown, 
  ChevronUp,
  Sparkles,
  ArrowRight
} from 'lucide-react';

export const GoogleConnectModal = () => {
  const {
    isGoogleModalOpen,
    setIsGoogleModalOpen,
    googleStatus,
    connectEmail,
    connectGoogle,
    disconnectGoogle,
    connectDirectToken,
    updateGoogleConfig,
    googleConfig
  } = useForm();

  const [emailInput, setEmailInput] = useState(googleStatus?.email || '');
  const [emailLoading, setEmailLoading] = useState(false);
  const [directToken, setDirectToken] = useState('');
  const [tokenLoading, setTokenLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Advanced settings accordion
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [clientId, setClientId] = useState(googleConfig?.client_id || '');
  const [clientSecret, setClientSecret] = useState('');
  const [redirectUri, setRedirectUri] = useState(googleConfig?.redirect_uri || 'http://localhost:5173/auth/callback');
  const [configSaving, setConfigSaving] = useState(false);

  if (!isGoogleModalOpen) return null;

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    const cleanEmail = emailInput.trim();
    if (!cleanEmail || !cleanEmail.includes('@')) {
      setErrorMsg('Please enter a valid Gmail address (e.g., yourname@gmail.com)');
      return;
    }
    setErrorMsg('');
    setEmailLoading(true);
    try {
      await connectEmail(cleanEmail);
      setSuccessMsg(`Successfully connected as ${cleanEmail}!`);
      setTimeout(() => {
        setIsGoogleModalOpen(false);
        setSuccessMsg('');
      }, 1200);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to connect Gmail address.');
    } finally {
      setEmailLoading(false);
    }
  };

  const handleOAuthLogin = async () => {
    setErrorMsg('');
    try {
      await connectGoogle();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to initiate Google OAuth.');
    }
  };

  const handleDirectTokenSubmit = async (e) => {
    e.preventDefault();
    if (!directToken.trim()) {
      setErrorMsg('Please enter a valid Google OAuth Access Token.');
      return;
    }
    setErrorMsg('');
    setTokenLoading(true);
    try {
      await connectDirectToken(directToken.trim());
      setSuccessMsg('Google Account connected successfully!');
      setDirectToken('');
      setTimeout(() => {
        setIsGoogleModalOpen(false);
        setSuccessMsg('');
      }, 1200);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to authenticate token with Google.');
    } finally {
      setTokenLoading(false);
    }
  };

  const handleConfigSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setConfigSaving(true);
    try {
      await updateGoogleConfig(clientId.trim(), clientSecret.trim(), redirectUri.trim());
      setSuccessMsg('Google OAuth settings updated.');
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to update Google OAuth settings.');
    } finally {
      setConfigSaving(false);
    }
  };

  const handleDisconnect = async () => {
    setErrorMsg('');
    try {
      await disconnectGoogle();
      setEmailInput('');
      setSuccessMsg('Google account disconnected.');
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to disconnect account.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white border border-[#FAD5C0] rounded-3xl max-w-lg w-full p-6 shadow-2xl relative overflow-hidden animate-in fade-in duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#FDE4D7]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-[#FFF8F4] border border-[#FDE4D7] flex items-center justify-center shadow-sm p-2">
              <svg className="w-6 h-6" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
                <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"/>
                <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
                <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-black text-[#24110A]">Connect Google / Gmail ID</h3>
              <p className="text-xs text-[#6B3B2B] font-medium">Unlock form response analysis & multi-format reports</p>
            </div>
          </div>

          <button
            onClick={() => {
              setIsGoogleModalOpen(false);
              setErrorMsg('');
              setSuccessMsg('');
            }}
            className="p-1.5 rounded-lg text-[#6B3B2B] hover:text-[#24110A] hover:bg-[#FFF2EB] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="mt-5 space-y-4">
          
          {/* Status Section if Connected */}
          {googleStatus?.is_connected ? (
            <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-300 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                  <div>
                    <h4 className="text-sm font-black text-emerald-950">
                      Connected: <span className="text-emerald-700">{googleStatus.email}</span>
                    </h4>
                    <p className="text-xs text-emerald-800 font-medium">
                      FormMind AI is linked with your Gmail ID. Provide your Google Form link to generate full reports!
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleDisconnect}
                  className="px-3 py-1.5 rounded-xl bg-white hover:bg-rose-50 border border-[#FAD5C0] hover:border-rose-400 text-[#3B1F14] hover:text-rose-700 text-xs font-bold transition-colors flex items-center gap-1.5 shadow-sm"
                >
                  <Unlink className="w-3.5 h-3.5" />
                  <span>Disconnect</span>
                </button>
              </div>

              {/* Ready badges */}
              <div className="pt-2 border-t border-emerald-200 grid grid-cols-2 gap-2 text-[11px] text-emerald-900 font-semibold">
                <div className="flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Google Form Ingestion</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Automatic Response Analysis</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                  <span>PDF / Word DOCX Exports</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Excel XLSX / CSV Reports</span>
                </div>
              </div>
            </div>
          ) : (
            /* Direct Email Connection Form (PRIMARY & EASY) */
            <div className="p-4 rounded-2xl bg-[#FFF8F4] border border-[#FDE4D7] space-y-3">
              <div>
                <h4 className="text-sm font-black text-[#24110A] flex items-center gap-2">
                  <Mail className="w-4 h-4 text-brand-600" />
                  <span>Connect with Your Gmail Address</span>
                </h4>
                <p className="text-xs text-[#6B3B2B] mt-1 leading-relaxed font-medium">
                  Simply enter the Gmail ID where your Google Form was created. No tokens, no Google Cloud setup required!
                </p>
              </div>

              <form onSubmit={handleEmailSubmit} className="space-y-3 pt-1">
                <div>
                  <label className="block text-[11px] font-bold text-[#24110A] mb-1">
                    Your Gmail ID / Email Address
                  </label>
                  <div className="relative">
                    <input
                      type="email"
                      required
                      value={emailInput}
                      onChange={(e) => setEmailInput(e.target.value)}
                      placeholder="e.g., yourname@gmail.com"
                      className="w-full bg-white border border-[#FAD5C0] rounded-xl px-3.5 py-2.5 text-sm text-[#24110A] placeholder-[#8C5D4B] font-medium focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 shadow-sm"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={emailLoading || !emailInput.trim()}
                  className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 disabled:opacity-50 text-white text-xs font-bold shadow-md shadow-brand-500/20 transition-all flex items-center justify-center gap-2 active:scale-[0.99]"
                >
                  {emailLoading ? 'Connecting...' : (
                    <>
                      <span>Connect Gmail Account (1-Click)</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </>
                  )}
                </button>
              </form>
            </div>
          )}

          {/* Advanced / Optional OAuth Accordion */}
          <div className="rounded-2xl border border-[#FAD5C0] bg-[#FFF8F4] overflow-hidden">
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="w-full p-3 text-left text-xs font-bold text-[#3B1F14] hover:text-[#24110A] flex items-center justify-between transition-colors"
            >
              <div className="flex items-center gap-2">
                <Settings className="w-3.5 h-3.5 text-brand-600" />
                <span>Advanced: Google Cloud OAuth & Access Tokens (Optional)</span>
              </div>
              {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4 text-[#8C5D4B]" />}
            </button>

            {showAdvanced && (
              <div className="p-4 pt-2 space-y-4 border-t border-[#FDE4D7] bg-white">
                <div className="space-y-2">
                  <button
                    onClick={handleOAuthLogin}
                    className="w-full py-2 px-3 rounded-xl bg-[#FFF2EB] hover:bg-[#FFE6D9] text-[#24110A] border border-[#FAD5C0] text-xs font-bold transition-all flex items-center justify-center gap-2 shadow-sm"
                  >
                    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24">
                      <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
                      <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"/>
                      <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
                      <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
                    </svg>
                    <span>Sign in with Google Cloud OAuth</span>
                  </button>
                </div>

                <form onSubmit={handleDirectTokenSubmit} className="space-y-2 pt-2 border-t border-[#FDE4D7]">
                  <div className="flex items-center justify-between text-[11px] text-[#6B3B2B] font-medium">
                    <span>Or enter OAuth Access Token:</span>
                    <a
                      href="https://developers.google.com/oauthplayground"
                      target="_blank"
                      rel="noreferrer"
                      className="text-brand-700 hover:text-brand-800 text-[10px] font-bold flex items-center gap-1"
                    >
                      <span>OAuth Playground</span>
                      <ExternalLink className="w-2.5 h-2.5" />
                    </a>
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="password"
                      value={directToken}
                      onChange={(e) => setDirectToken(e.target.value)}
                      placeholder="Paste ya29... token"
                      className="flex-1 bg-white border border-[#FAD5C0] rounded-xl px-3 py-1.5 text-xs text-[#24110A] placeholder-[#8C5D4B] font-medium focus:outline-none focus:border-brand-500 shadow-sm"
                    />
                    <button
                      type="submit"
                      disabled={tokenLoading || !directToken.trim()}
                      className="px-3 py-1.5 rounded-xl bg-[#FFF2EB] hover:bg-[#FFE6D9] text-[#24110A] border border-[#FAD5C0] text-xs font-bold transition-colors shrink-0 shadow-sm"
                    >
                      {tokenLoading ? 'Verifying...' : 'Connect'}
                    </button>
                  </div>
                </form>

                <form onSubmit={handleConfigSubmit} className="space-y-2 pt-2 border-t border-[#FDE4D7]">
                  <span className="text-[11px] font-bold text-[#24110A] block">OAuth 2.0 Client Credentials:</span>
                  <input
                    type="text"
                    value={clientId}
                    onChange={(e) => setClientId(e.target.value)}
                    placeholder="Client ID (xxxx.apps.googleusercontent.com)"
                    className="w-full bg-white border border-[#FAD5C0] rounded-xl px-3 py-1.5 text-xs text-[#24110A] placeholder-[#8C5D4B] font-medium focus:outline-none focus:border-brand-500 shadow-sm"
                  />
                  <input
                    type="password"
                    value={clientSecret}
                    onChange={(e) => setClientSecret(e.target.value)}
                    placeholder="Client Secret (GOCSPX-...)"
                    className="w-full bg-white border border-[#FAD5C0] rounded-xl px-3 py-1.5 text-xs text-[#24110A] placeholder-[#8C5D4B] font-medium focus:outline-none focus:border-brand-500 shadow-sm"
                  />
                  <button
                    type="submit"
                    disabled={configSaving}
                    className="w-full py-1.5 rounded-xl bg-[#FFF2EB] hover:bg-[#FFE6D9] text-[#24110A] border border-[#FAD5C0] text-xs font-bold transition-colors shadow-sm"
                  >
                    {configSaving ? 'Saving...' : 'Save OAuth Config'}
                  </button>
                </form>
              </div>
            )}
          </div>

          {/* Feedback Messages */}
          {errorMsg && (
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-300 text-xs text-rose-800 flex items-start gap-2 font-semibold">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-300 text-xs text-emerald-800 flex items-center gap-2 font-semibold">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

        </div>

      </div>
    </div>
  );
};
