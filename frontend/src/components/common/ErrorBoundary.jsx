import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Unhandled React error caught by ErrorBoundary:', error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReload = () => {
    window.location.reload();
  };

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#FFF9F6] text-[#24110A] flex items-center justify-center p-4 font-sans">
          <div className="max-w-lg w-full bg-white rounded-3xl p-8 border border-orange-200 shadow-xl text-center space-y-6">
            <div className="w-16 h-16 bg-red-50 text-red-600 rounded-2xl flex items-center justify-center mx-auto border border-red-200 shadow-inner">
              <AlertTriangle className="w-8 h-8" />
            </div>

            <div className="space-y-2">
              <h2 className="text-2xl font-black text-[#24110A] tracking-tight">Something Went Wrong</h2>
              <p className="text-sm text-[#6B3B2B] leading-relaxed">
                An unexpected UI rendering error occurred. Your data is safe. Try reloading the application or return home.
              </p>
            </div>

            {this.state.error && (
              <div className="text-left bg-orange-50/70 border border-orange-200/80 rounded-xl p-3.5 text-xs text-[#8A3A1B] font-mono overflow-auto max-h-32">
                {this.state.error.toString()}
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <button
                onClick={this.handleReload}
                className="flex-1 inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-[#E64825] hover:bg-[#CF3C1B] text-white font-bold text-sm shadow-md transition-all active:scale-[0.98]"
              >
                <RefreshCw className="w-4 h-4" />
                Reload Application
              </button>
              <button
                onClick={this.handleReset}
                className="flex-1 inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-orange-100/70 hover:bg-orange-200/80 text-[#24110A] font-bold text-sm border border-orange-200 transition-all active:scale-[0.98]"
              >
                <Home className="w-4 h-4" />
                Return Home
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
