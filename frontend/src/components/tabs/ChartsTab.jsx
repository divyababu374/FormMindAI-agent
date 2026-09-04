import React, { useState } from 'react';
import { useForm } from '../../context/FormContext';
import { ChartRenderer } from '../common/ChartRenderer';
import { Badge } from '../common/Badge';
import { BarChart3, PieChart, LineChart } from 'lucide-react';

export const ChartsTab = () => {
  const { currentForm, analysis, questions } = useForm();
  const [chartTypeOverrides, setChartTypeOverrides] = useState({});

  if (!analysis) {
    return <div className="p-8 text-center text-slate-400">Loading chart studio...</div>;
  }

  const numerical = analysis.numerical_analysis || {};
  const categorical = analysis.categorical_analysis || {};
  const multiselect = analysis.multiselect || {};

  const toggleChartType = (key, type) => {
    setChartTypeOverrides(prev => ({ ...prev, [key]: type }));
  };

  const chartableQuestions = questions.filter(
    q => numerical[q.question_key] || categorical[q.question_key] || multiselect[q.question_key]
  );

  return (
    <div className="space-y-6">
      
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div>
          <h3 className="text-lg font-bold text-white">Interactive Chart Gallery</h3>
          <p className="text-xs text-slate-400">Explore distribution visualizations with dynamic chart switchers</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {chartableQuestions.map((q) => {
          const k = q.question_key;
          const num = numerical[k];
          const cat = categorical[k];
          const multi = multiselect[k];

          const activeData = num || cat || multi;
          const dist = activeData?.distribution || [];
          const labels = dist.map(d => d.label);
          const data = dist.map(d => d.count);

          const defaultType = num ? 'bar' : cat ? 'doughnut' : 'bar';
          const currentType = chartTypeOverrides[k] || defaultType;

          return (
            <div
              key={k}
              className="p-6 rounded-3xl bg-white border border-[#FAD5C0] shadow-sm flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-4">
                  <div>
                    <h4 className="text-sm font-extrabold text-[#24110A] truncate max-w-xs">{q.question_text}</h4>
                    <p className="text-xs text-[#6B3B2B] mt-0.5 font-medium">{dist.length} categories / buckets</p>
                  </div>

                  {/* Chart Type Selector Pills */}
                  <div className="flex items-center gap-1 bg-[#FFF2EB] p-1 rounded-xl border border-[#FAD5C0]">
                    <button
                      onClick={() => toggleChartType(k, 'bar')}
                      className={`p-1.5 rounded-lg text-xs transition-colors ${currentType === 'bar' ? 'bg-brand-600 text-white shadow-sm' : 'text-[#6B3B2B] hover:text-[#24110A]'}`}
                      title="Bar Chart"
                    >
                      <BarChart3 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => toggleChartType(k, 'doughnut')}
                      className={`p-1.5 rounded-lg text-xs transition-colors ${currentType === 'doughnut' ? 'bg-brand-600 text-white shadow-sm' : 'text-[#6B3B2B] hover:text-[#24110A]'}`}
                      title="Donut Chart"
                    >
                      <PieChart className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => toggleChartType(k, 'line')}
                      className={`p-1.5 rounded-lg text-xs transition-colors ${currentType === 'line' ? 'bg-brand-600 text-white shadow-sm' : 'text-[#6B3B2B] hover:text-[#24110A]'}`}
                      title="Line Chart"
                    >
                      <LineChart className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <div className="mt-2">
                  <ChartRenderer
                    type={currentType}
                    labels={labels}
                    data={data}
                    height={240}
                  />
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                <span>Total Samples: {activeData.count || currentForm?.total_responses_count}</span>
                <span className="text-brand-400 font-medium">Verified Visualization</span>
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
};
