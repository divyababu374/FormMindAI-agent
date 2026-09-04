import React from 'react';
import { useForm } from '../../context/FormContext';
import { Badge } from '../common/Badge';
import { 
  CheckCircle2, 
  Lightbulb, 
  TrendingUp, 
  Layers, 
  ArrowUpRight,
  Target
} from 'lucide-react';

export const InsightsTab = () => {
  const { analysis } = useForm();

  if (!analysis) {
    return <div className="p-8 text-center text-[#6B3B2B]">Loading AI insights...</div>;
  }

  const insights = analysis.ai_insights || {};
  const comparisons = analysis.comparative_analysis || [];

  return (
    <div className="space-y-8">
      
      <div className="pb-3 border-b border-[#FDE4D7]">
        <h3 className="text-lg font-black text-[#24110A]">Grounded AI Insights & Intelligence</h3>
        <p className="text-xs text-[#6B3B2B] font-medium mt-0.5">
          Strictly segregated mathematical facts, strategic trend interpretations, and prioritized recommendations
        </p>
      </div>

      {/* Section 1: Grounded Factual Claims */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <div className="p-1.5 rounded-lg bg-sky-100 text-sky-800 border border-sky-300">
            <CheckCircle2 className="w-4 h-4" />
          </div>
          <h4 className="text-sm font-black text-[#24110A] uppercase tracking-wider">
            1. Verified Data Facts (Exact Mathematical Findings)
          </h4>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {insights.facts?.map((fact, idx) => (
            <div
              key={idx}
              className="p-4 rounded-2xl bg-white border border-[#FAD5C0] hover:border-brand-400 shadow-sm flex items-start gap-3 transition-all"
            >
              <span className="w-6 h-6 rounded-full bg-sky-100 text-sky-900 text-xs font-black flex items-center justify-center shrink-0 mt-0.5">
                {idx + 1}
              </span>
              <p className="text-xs text-[#24110A] leading-relaxed font-semibold">
                {fact}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Section 2: Strategic Interpretations */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <div className="p-1.5 rounded-lg bg-purple-100 text-purple-800 border border-purple-300">
            <TrendingUp className="w-4 h-4" />
          </div>
          <h4 className="text-sm font-black text-[#24110A] uppercase tracking-wider">
            2. Strategic Interpretations (Trend & Driver Analysis)
          </h4>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {insights.interpretations?.map((item, idx) => (
            <div
              key={idx}
              className="p-4 rounded-2xl bg-white border border-[#FAD5C0] hover:border-brand-400 shadow-sm flex items-start gap-3 transition-all"
            >
              <span className="w-6 h-6 rounded-full bg-purple-100 text-purple-900 text-xs font-black flex items-center justify-center shrink-0 mt-0.5">
                {idx + 1}
              </span>
              <p className="text-xs text-[#24110A] leading-relaxed font-semibold">
                {item}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Section 3: Comparative Segment Insights */}
      {comparisons.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <div className="p-1.5 rounded-lg bg-emerald-100 text-emerald-800 border border-emerald-300">
              <Layers className="w-4 h-4" />
            </div>
            <h4 className="text-sm font-black text-[#24110A] uppercase tracking-wider">
              3. Cross-Segment Comparative Analysis
            </h4>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {comparisons.map((comp, idx) => (
              <div key={idx} className="p-5 rounded-2xl bg-white border border-[#FAD5C0] shadow-sm">
                <h5 className="text-sm font-black text-[#24110A]">{comp.title}</h5>
                <p className="text-xs text-[#6B3B2B] italic mt-1 font-medium">{comp.key_insight}</p>

                <div className="mt-4 space-y-2">
                  {comp.segments?.map((seg, sIdx) => (
                    <div key={sIdx} className="flex items-center justify-between p-2.5 rounded-xl bg-[#FFF8F4] border border-[#FDE4D7] text-xs">
                      <span className="font-bold text-[#24110A]">{seg.group}</span>
                      <div className="flex items-center gap-3">
                        <span className="text-[#6B3B2B] font-medium">{seg.count} respondents</span>
                        <span className="text-brand-700 font-black">{seg.mean} avg</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Section 4: Actionable Recommendations */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <div className="p-1.5 rounded-lg bg-amber-100 text-amber-800 border border-amber-300">
            <Target className="w-4 h-4" />
          </div>
          <h4 className="text-sm font-black text-[#24110A] uppercase tracking-wider">
            4. Prescriptive Action Items & Next Steps
          </h4>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {insights.recommendations?.map((rec, idx) => (
            <div
              key={idx}
              className="p-4 rounded-2xl bg-white border border-[#FAD5C0] hover:border-amber-400 shadow-sm flex items-start gap-3 transition-all"
            >
              <div className="p-1.5 rounded-lg bg-amber-100 text-amber-800 shrink-0 mt-0.5">
                <Lightbulb className="w-4 h-4" />
              </div>
              <p className="text-xs text-[#24110A] leading-relaxed font-semibold">
                {rec}
              </p>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
