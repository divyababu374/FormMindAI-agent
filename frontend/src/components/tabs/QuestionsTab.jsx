import React from 'react';
import { useForm } from '../../context/FormContext';
import { ChartRenderer } from '../common/ChartRenderer';
import { Badge } from '../common/Badge';
import { HelpCircle, BarChart2, MessageSquare, CheckSquare, Star } from 'lucide-react';

export const QuestionsTab = () => {
  const { questions, analysis } = useForm();

  if (!questions || questions.length === 0) {
    return <div className="p-8 text-center text-slate-400">No questions found in this form.</div>;
  }

  const numerical = analysis?.numerical_analysis || {};
  const categorical = analysis?.categorical_analysis || {};
  const multiselect = analysis?.multiselect || {};
  const textAnalysis = analysis?.text_analysis || {};

  return (
    <div className="space-y-6">
      
      <div className="flex items-center justify-between pb-3 border-b border-[#FDE4D7]">
        <div>
          <h3 className="text-lg font-black text-[#24110A]">Question-by-Question Analysis</h3>
          <p className="text-xs text-[#6B3B2B] font-medium">Detailed statistical breakdown and distribution charts for all {questions.length} questions</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:gap-6">
        {questions.map((q, idx) => {
          const k = q.question_key;
          const numData = numerical[k];
          const catData = categorical[k];
          const multiData = multiselect[k];
          const txtData = textAnalysis[k];

          return (
            <div
              key={q.id || idx}
              className="p-4 sm:p-6 rounded-2xl sm:rounded-3xl bg-white border border-[#FAD5C0] hover:border-brand-400 transition-all shadow-sm"
            >
              {/* Question Card Header */}
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 pb-4 border-b border-[#FDE4D7]">
                <div className="flex items-start gap-3">
                  <span className="px-2.5 py-1 rounded-xl bg-orange-100 border border-orange-200 text-brand-700 text-xs font-bold shrink-0">
                    {q.question_key}
                  </span>
                  <div>
                    <h4 className="text-base font-black text-[#24110A] tracking-tight leading-snug">
                      {q.question_text}
                    </h4>
                    <div className="flex flex-wrap items-center gap-2 mt-2">
                      <Badge variant={q.inferred_data_type === 'numeric' ? 'amber' : q.inferred_data_type === 'categorical' ? 'purple' : 'blue'}>
                        {q.question_type.replace('_', ' ').toUpperCase()}
                      </Badge>
                      {q.is_required && <Badge variant="rose">Required</Badge>}
                    </div>
                  </div>
                </div>
              </div>

              {/* Numerical Question Content */}
              {numData && (
                <div className="mt-5 grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3.5 rounded-2xl bg-[#FFF8F4] border border-[#FDE4D7]">
                      <p className="text-[11px] font-bold text-[#6B3B2B]">Average / Mean</p>
                      <p className="text-xl font-black text-brand-600 mt-1">{numData.mean}</p>
                    </div>
                    <div className="p-3.5 rounded-2xl bg-[#FFF8F4] border border-[#FDE4D7]">
                      <p className="text-[11px] font-bold text-[#6B3B2B]">Median Score</p>
                      <p className="text-xl font-black text-emerald-700 mt-1">{numData.median}</p>
                    </div>
                    <div className="p-3.5 rounded-2xl bg-[#FFF8F4] border border-[#FDE4D7]">
                      <p className="text-[11px] font-bold text-[#6B3B2B]">Std Deviation</p>
                      <p className="text-xl font-black text-purple-700 mt-1">{numData.std_dev}</p>
                    </div>
                    <div className="p-3.5 rounded-2xl bg-[#FFF8F4] border border-[#FDE4D7]">
                      <p className="text-[11px] font-bold text-[#6B3B2B]">Responses</p>
                      <p className="text-xl font-black text-[#24110A] mt-1">{numData.count}</p>
                    </div>
                  </div>

                  {/* Chart */}
                  <div className="lg:col-span-2">
                    <ChartRenderer
                      type="bar"
                      labels={numData.distribution?.map(d => d.label) || []}
                      data={numData.distribution?.map(d => d.count) || []}
                      height={200}
                    />
                  </div>
                </div>
              )}

              {/* Categorical Question Content */}
              {catData && (
                <div className="mt-5 grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
                  {/* Top Stats */}
                  <div className="space-y-3">
                    <div className="p-3.5 rounded-2xl bg-[#FFF8F4] border border-[#FDE4D7]">
                      <p className="text-[11px] font-bold text-[#6B3B2B]">Most Popular Answer</p>
                      <p className="text-sm font-black text-emerald-800 mt-1">
                        {catData.most_common?.value}
                      </p>
                      <p className="text-xs text-[#6B3B2B] mt-0.5 font-medium">
                        {catData.most_common?.count} votes ({catData.most_common?.percentage}%)
                      </p>
                    </div>
                    <div className="p-3.5 rounded-2xl bg-[#FFF8F4] border border-[#FDE4D7]">
                      <p className="text-[11px] font-bold text-[#6B3B2B]">Total Unique Options</p>
                      <p className="text-lg font-black text-[#24110A] mt-1">{catData.unique_count}</p>
                    </div>
                  </div>

                  {/* Chart */}
                  <div className="lg:col-span-2">
                    <ChartRenderer
                      type="doughnut"
                      labels={catData.distribution?.map(d => d.label) || []}
                      data={catData.distribution?.map(d => d.count) || []}
                      height={200}
                    />
                  </div>
                </div>
              )}

              {/* Multi-Select Checkboxes Content */}
              {multiData && (
                <div className="mt-5">
                  <ChartRenderer
                    type="bar"
                    horizontal={true}
                    labels={multiData.distribution?.map(d => d.label) || []}
                    data={multiData.distribution?.map(d => d.count) || []}
                    height={220}
                  />
                </div>
              )}

              {/* Text / Open-Ended Content */}
              {txtData && (
                <div className="mt-5 space-y-4">
                  {/* Sentiment Bar */}
                  <div className="p-4 rounded-2xl bg-[#FFF8F4] border border-[#FDE4D7]">
                    <div className="flex items-center justify-between text-xs font-bold mb-2">
                      <span className="text-[#24110A]">Sentiment Distribution</span>
                      <span className="text-emerald-800 font-black">{txtData.sentiment?.positive_percentage}% Positive</span>
                    </div>
                    <div className="w-full h-2.5 rounded-full bg-slate-200 overflow-hidden flex">
                      <div style={{ width: `${txtData.sentiment?.positive_percentage}%` }} className="bg-emerald-500" />
                      <div style={{ width: `${txtData.sentiment?.neutral_percentage}%` }} className="bg-slate-400" />
                      <div style={{ width: `${txtData.sentiment?.negative_percentage}%` }} className="bg-rose-500" />
                    </div>
                  </div>

                  {/* Snippets */}
                  {txtData.positive_feedback?.length > 0 && (
                    <div>
                      <h5 className="text-xs font-bold text-emerald-800 uppercase tracking-wider mb-2">Sample Positive Mentions</h5>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {txtData.positive_feedback.slice(0, 4).map((pos, pIdx) => (
                          <div key={pIdx} className="p-3 rounded-xl bg-[#FFF8F4] border border-[#FDE4D7] text-xs text-[#3B1F14] italic font-medium">
                            "{pos}"
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {txtData.negative_feedback?.length > 0 && (
                    <div>
                      <h5 className="text-xs font-bold text-rose-800 uppercase tracking-wider mb-2">Critiques / Improvement Areas</h5>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {txtData.negative_feedback.slice(0, 4).map((neg, nIdx) => (
                          <div key={nIdx} className="p-3 rounded-xl bg-[#FFF8F4] border border-[#FDE4D7] text-xs text-[#3B1F14] italic font-medium">
                            "{neg}"
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

            </div>
          );
        })}
      </div>

    </div>
  );
};
