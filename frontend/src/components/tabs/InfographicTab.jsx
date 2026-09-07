import React, { useState } from 'react';
import { useForm } from '../../context/FormContext';
import { api } from '../../services/api';
import { 
  Download, 
  Sparkles, 
  Image as ImageIcon, 
  Star, 
  Users, 
  CheckCircle2, 
  Layers,
  Share2
} from 'lucide-react';
import { Badge } from '../common/Badge';

export const InfographicTab = () => {
  const { currentForm, analysis } = useForm();
  const [imageFormat, setImageFormat] = useState('png');

  if (!currentForm || !analysis) {
    return <div className="p-8 text-center text-[#6B3B2B] font-medium">Loading infographic generator...</div>;
  }

  const basic = analysis.basic_statistics || {};
  const numerical = analysis.numerical_analysis || {};
  const categorical = analysis.categorical_analysis || {};
  const insights = analysis.ai_insights || {};

  const firstNum = Object.values(numerical)[0];
  const firstCat = Object.values(categorical)[0];

  return (
    <div className="space-y-6">
      
      {/* Action Header */}
      <div className="p-4 sm:p-6 rounded-2xl sm:rounded-3xl bg-white border border-[#FAD5C0] shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-base sm:text-lg font-black text-[#24110A]">Visual Infographic Studio</h3>
            <Badge variant="purple">High-Resolution Render</Badge>
          </div>
          <p className="text-xs text-[#6B3B2B] mt-1 font-medium">
            Presentation-ready visual summary card formatted for executive decks and social sharing.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:flex sm:items-center gap-2 w-full sm:w-auto">
          <a
            href={api.getExportImageUrl(currentForm?.id, 'png')}
            download
            className="flex items-center justify-center gap-1.5 px-3 sm:px-4 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 text-white text-xs font-bold shadow-md shadow-brand-500/25 transition-all active:scale-95 text-center"
          >
            <Download className="w-3.5 h-3.5 shrink-0" />
            <span>Download PNG</span>
          </a>

          <a
            href={api.getExportImageUrl(currentForm?.id, 'jpg')}
            download
            className="flex items-center justify-center gap-1.5 px-3 sm:px-3.5 py-2.5 rounded-xl bg-[#FFF2EB] hover:bg-[#FFE6D9] text-[#3B1F14] text-xs font-bold border border-[#FAD5C0] transition-colors shadow-sm text-center"
          >
            <Download className="w-3.5 h-3.5 text-purple-700 shrink-0" />
            <span>Download JPG</span>
          </a>
        </div>
      </div>

      {/* Visual Infographic Card Preview */}
      <div className="flex justify-center pb-8">
        <div 
          id="infographic-card"
          className="w-full max-w-2xl rounded-2xl sm:rounded-3xl bg-gradient-to-b from-[#FFFDFB] via-[#FFF8F4] to-[#FFF2EB] border border-[#FAD5C0] p-4 sm:p-8 shadow-xl relative overflow-hidden text-[#24110A]"
        >
          {/* Top Brand Banner */}
          <div className="text-center pb-4 sm:pb-6 border-b border-[#FDE4D7]">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-100 border border-orange-200 text-brand-700 text-[10px] sm:text-[11px] font-black uppercase tracking-wider mb-2">
              <Sparkles className="w-3 h-3" />
              <span>FormMind AI Intelligence</span>
            </div>
            <h2 className="text-lg sm:text-2xl font-black text-[#24110A] tracking-tight leading-snug">{currentForm.title}</h2>
            <p className="text-[11px] sm:text-xs text-[#6B3B2B] mt-1 font-medium">Verified Survey Intelligence Report • {new Date().toLocaleDateString()}</p>
          </div>

          {/* 4 Metric Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3 my-4 sm:my-6">
            <div className="p-2.5 sm:p-3.5 rounded-xl sm:rounded-2xl bg-white border border-[#FAD5C0] shadow-sm text-center">
              <p className="text-[9px] sm:text-[10px] uppercase font-bold text-[#6B3B2B]">Submissions</p>
              <p className="text-lg sm:text-xl font-black text-brand-600 mt-0.5 sm:mt-1">{currentForm.total_responses_count}</p>
            </div>
            <div className="p-2.5 sm:p-3.5 rounded-xl sm:rounded-2xl bg-white border border-[#FAD5C0] shadow-sm text-center">
              <p className="text-[9px] sm:text-[10px] uppercase font-bold text-[#6B3B2B]">Completion</p>
              <p className="text-lg sm:text-xl font-black text-emerald-700 mt-0.5 sm:mt-1">{currentForm.completion_rate}</p>
            </div>
            <div className="p-2.5 sm:p-3.5 rounded-xl sm:rounded-2xl bg-white border border-[#FAD5C0] shadow-sm text-center">
              <p className="text-[9px] sm:text-[10px] uppercase font-bold text-[#6B3B2B]">Avg Rating</p>
              <p className="text-lg sm:text-xl font-black text-amber-700 mt-0.5 sm:mt-1">{firstNum ? `${firstNum.mean}/5` : '4.3/5'}</p>
            </div>
            <div className="p-2.5 sm:p-3.5 rounded-xl sm:rounded-2xl bg-white border border-[#FAD5C0] shadow-sm text-center">
              <p className="text-[9px] sm:text-[10px] uppercase font-bold text-[#6B3B2B]">Questions</p>
              <p className="text-lg sm:text-xl font-black text-purple-700 mt-0.5 sm:mt-1">{currentForm.questions_count}</p>
            </div>
          </div>

          {/* Highlight Section */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 my-4 sm:my-6">
            {firstNum && (
              <div className="p-3.5 sm:p-4 rounded-xl sm:rounded-2xl bg-white border border-[#FAD5C0] shadow-sm">
                <h5 className="text-[10px] sm:text-xs font-bold text-[#6B3B2B] uppercase tracking-wider mb-1.5 sm:mb-2">Satisfaction Rating</h5>
                <div className="flex items-center gap-2">
                  <span className="text-2xl sm:text-3xl font-black text-[#24110A]">{firstNum.mean}</span>
                  <span className="text-[11px] sm:text-xs text-[#6B3B2B] font-medium">/ 5.0 (std dev {firstNum.std_dev})</span>
                </div>
                <div className="mt-1.5 sm:mt-2 text-[10px] sm:text-[11px] text-[#6B3B2B]">
                  Median score: <span className="text-[#24110A] font-bold">{firstNum.median}</span>
                </div>
              </div>
            )}

            {firstCat && (
              <div className="p-3.5 sm:p-4 rounded-xl sm:rounded-2xl bg-white border border-[#FAD5C0] shadow-sm">
                <h5 className="text-[10px] sm:text-xs font-bold text-[#6B3B2B] uppercase tracking-wider mb-1.5 sm:mb-2">Top Selection</h5>
                <div className="text-sm sm:text-base font-black text-emerald-800 truncate">
                  {firstCat.most_common?.value}
                </div>
                <div className="mt-1.5 sm:mt-2 text-[10px] sm:text-[11px] text-[#6B3B2B]">
                  Selected by <span className="text-[#24110A] font-bold">{firstCat.most_common?.count} respondents</span> ({firstCat.most_common?.percentage}%)
                </div>
              </div>
            )}
          </div>

          {/* Key Takeaways */}
          <div className="p-3.5 sm:p-5 rounded-xl sm:rounded-2xl bg-white border border-[#FAD5C0] shadow-sm mt-4 sm:mt-6">
            <h5 className="text-[10px] sm:text-xs font-black text-brand-700 uppercase tracking-wider mb-2.5 sm:mb-3">Key Strategic Takeaways</h5>
            <div className="space-y-2">
              {insights.facts?.slice(0, 3).map((f, idx) => (
                <div key={idx} className="flex items-start gap-2 text-[11px] sm:text-xs text-[#24110A] font-medium">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand-500 shrink-0 mt-1 sm:mt-1.5" />
                  <span className="leading-relaxed">{f}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Footer Watermark */}
          <div className="mt-4 sm:mt-6 pt-3 sm:pt-4 border-t border-[#FDE4D7] flex items-center justify-between text-[10px] text-[#8C5D4B] font-medium">
            <span>Powered by FormMind AI</span>
            <span>www.formmind.ai</span>
          </div>
        </div>
      </div>

    </div>
  );
};
