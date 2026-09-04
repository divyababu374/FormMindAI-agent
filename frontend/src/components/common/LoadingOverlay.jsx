import React from 'react';
import { Loader2, Sparkles, CheckCircle2 } from 'lucide-react';

export const LoadingOverlay = ({ step = 'Processing analysis...' }) => {
  const isComplete = step.includes('complete');

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white border border-[#FAD5C0] rounded-3xl p-8 max-w-md w-full text-center shadow-2xl relative overflow-hidden">
        {/* Glow ambient circle */}
        <div className="absolute -top-20 -left-20 w-40 h-40 bg-orange-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-20 -right-20 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl" />

        <div className="relative z-10 flex flex-col items-center">
          <div className="relative mb-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600 to-brand-500 flex items-center justify-center shadow-lg shadow-brand-500/30">
              {isComplete ? (
                <CheckCircle2 className="w-8 h-8 text-white animate-bounce" />
              ) : (
                <Sparkles className="w-8 h-8 text-white animate-pulse" />
              )}
            </div>
            {!isComplete && (
              <div className="absolute -bottom-1 -right-1 p-1 bg-white rounded-full shadow-sm border border-[#FAD5C0]">
                <Loader2 className="w-5 h-5 text-brand-600 animate-spin" />
              </div>
            )}
          </div>

          <h3 className="text-xl font-black text-[#24110A] mb-2 tracking-tight">
            {isComplete ? 'FormMind Intelligence Ready!' : 'FormMind AI Analyzing Form'}
          </h3>
          
          <div className="flex items-center gap-2 justify-center text-sm font-bold text-brand-800 mt-2 bg-orange-100 border border-orange-200 px-4 py-2 rounded-full">
            <span className="w-2 h-2 rounded-full bg-brand-600 animate-ping" />
            <span>{step}</span>
          </div>

          <p className="text-xs text-[#6B3B2B] mt-4 leading-relaxed font-medium">
            Extracting questions, standardizing response matrices, and computing verified zero-hallucination statistical models.
          </p>
        </div>
      </div>
    </div>
  );
};
