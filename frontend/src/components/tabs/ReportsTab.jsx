import React, { useState, useEffect, useMemo } from 'react';
import { useForm } from '../../context/FormContext';
import { api } from '../../services/api';
import { 
  FileText, 
  Download, 
  FileSpreadsheet, 
  FileCheck, 
  Sparkles, 
  Printer,
  CheckCircle,
  Copy,
  Check,
  Eye,
  Code2,
  TrendingUp,
  Award,
  Users,
  CheckCircle2,
  Quote,
  Layers,
  AlertCircle,
  Briefcase
} from 'lucide-react';
import { Badge } from '../common/Badge';

export const ReportsTab = () => {
  const { currentForm } = useForm();
  const [reportType, setReportType] = useState('full');
  const [reportContent, setReportContent] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [viewMode, setViewMode] = useState('formatted'); // 'formatted' | 'raw'

  const fetchReport = async (type = 'full', instructions = '') => {
    if (!currentForm) return;
    setIsGenerating(true);
    try {
      const res = await api.generateCustomReport(currentForm.id, type, instructions);
      setReportContent(res.content_markdown || '');
    } catch (err) {
      console.error('Failed to generate report:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  useEffect(() => {
    fetchReport('full');
  }, [currentForm?.id]);

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(reportContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    window.print();
  };

  const reportPresets = [
    { 
      id: 'full', 
      label: 'Full 10-Section Analysis', 
      badge: '10 Sections',
      desc: 'Complete breakdown with executive overview, question distributions, comparative matrices, and recommendations.',
      icon: FileText,
      color: 'text-brand-600'
    },
    { 
      id: 'executive_summary', 
      label: 'Executive Brief (1-Page)', 
      badge: '1-Page Brief',
      desc: 'High-level synthesis designed for quick leadership review.',
      icon: Award,
      color: 'text-purple-600'
    },
    { 
      id: 'negative_feedback', 
      label: 'Critiques & Friction Points', 
      badge: 'Friction & Issues',
      desc: 'Focuses entirely on constructive responses, complaints, and improvement requests.',
      icon: AlertCircle,
      color: 'text-amber-700'
    },
    { 
      id: 'leadership', 
      label: 'Executive Presentation', 
      badge: 'Boardroom Strategic',
      desc: 'Formal strategic summary with key performance indicators and recommendations.',
      icon: Briefcase,
      color: 'text-emerald-700'
    }
  ];

  // Inline formatting helper for bold text and clean labels
  const renderInline = (str) => {
    if (!str) return str;
    const parts = [];
    const boldRegex = /\*\*(.*?)\*\*/g;
    let lastIndex = 0;
    let match;
    let idx = 0;
    while ((match = boldRegex.exec(str)) !== null) {
      if (match.index > lastIndex) {
        parts.push(str.substring(lastIndex, match.index));
      }
      parts.push(<strong key={idx++} className="font-black text-[#24110A]">{match[1]}</strong>);
      lastIndex = match.index + match[0].length;
    }
    if (lastIndex < str.length) {
      parts.push(str.substring(lastIndex));
    }
    return parts.length > 0 ? parts : str;
  };

  // Parser that converts markdown text into structured, clean UI components with real tables and bullet points
  const renderedSections = useMemo(() => {
    if (!reportContent) return null;

    const lines = reportContent.split('\n');
    const nodes = [];
    let currentTable = [];
    let inTable = false;

    const flushTable = (key) => {
      if (currentTable.length === 0) return;
      const headerRow = currentTable[0];
      const dataRows = currentTable.slice(1).filter(r => !r.every(c => /^:?-+:?$/.test(c.trim())));

      nodes.push(
        <div key={`table-${key}`} className="my-4 overflow-x-auto touch-scroll rounded-2xl border border-[#FAD5C0] bg-white shadow-sm -mx-2 sm:mx-0">
          <table className="w-full min-w-[500px] text-left border-collapse text-xs sm:text-sm">
            <thead>
              <tr className="bg-[#FFF2EB] border-b border-[#FAD5C0]">
                {headerRow.map((col, ci) => (
                  <th key={ci} className="py-2.5 sm:py-3 px-3 sm:px-4 font-bold text-[#8C2C08] uppercase tracking-wider text-[10px] sm:text-[11px]">
                    {renderInline(col)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#FDE4D7]">
              {dataRows.map((row, ri) => (
                <tr key={ri} className={ri % 2 === 0 ? "bg-[#FFFAF7]" : "bg-white"}>
                  {row.map((col, ci) => (
                    <td key={ci} className="py-2 sm:py-2.5 px-3 sm:px-4 text-[#24110A] font-medium leading-relaxed">
                      {renderInline(col)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );

      currentTable = [];
      inTable = false;
    };

    lines.forEach((line, i) => {
      const trimmed = line.trim();

      // Table line detection
      if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
        inTable = true;
        const cells = trimmed.split('|').slice(1, -1).map(c => c.trim());
        currentTable.push(cells);
      } else {
        if (inTable) {
          flushTable(i);
        }

        if (trimmed.startsWith('# ')) {
          nodes.push(
            <div key={i} className="pb-4 mb-6 border-b border-[#FDE4D7]">
              <h1 className="text-xl sm:text-2xl font-black text-[#24110A] tracking-tight">
                {trimmed.replace(/^#\s+/, '')}
              </h1>
            </div>
          );
        } else if (trimmed.startsWith('## ')) {
          const title = trimmed.replace(/^##\s+/, '');
          nodes.push(
            <div key={i} className="mt-8 mb-4 flex items-center gap-2.5 pb-2 border-b border-[#FDE4D7]">
              <div className="w-2 h-5 rounded-full bg-brand-500" />
              <h2 className="text-base sm:text-lg font-black text-[#24110A] tracking-wide">
                {title}
              </h2>
            </div>
          );
        } else if (trimmed.startsWith('### ')) {
          const title = trimmed.replace(/^###\s+/, '');
          nodes.push(
            <div key={i} className="mt-6 mb-2.5">
              <h3 className="text-sm sm:text-base font-black text-brand-800 flex items-center gap-2">
                <span>{title}</span>
              </h3>
            </div>
          );
        } else if (trimmed.startsWith('• ') || trimmed.startsWith('- ')) {
          const content = trimmed.replace(/^[•\-]\s+/, '');
          // Check if it's a quote
          const isQuote = content.startsWith('"') || content.startsWith('&quot;');
          nodes.push(
            <div key={i} className={`flex items-start gap-2.5 my-2 ${isQuote ? 'pl-4 py-2 border-l-4 border-brand-500 bg-[#FFF8F4] rounded-r-xl' : 'text-[#24110A]'}`}>
              {!isQuote && <span className="text-brand-600 font-bold mt-0.5">•</span>}
              <div className="flex-1 text-xs sm:text-sm text-[#24110A] font-medium leading-relaxed">
                {renderInline(content)}
              </div>
            </div>
          );
        } else if (/^\d+\.\s/.test(trimmed)) {
          const numMatch = trimmed.match(/^(\d+)\.\s(.*)/);
          nodes.push(
            <div key={i} className="flex items-start gap-3 my-3 p-3.5 rounded-xl bg-[#FFF8F4] border border-[#FDE4D7]">
              <span className="w-6 h-6 rounded-lg bg-orange-100 text-brand-700 font-bold flex items-center justify-center text-xs shrink-0 mt-0.5">
                {numMatch[1]}
              </span>
              <div className="flex-1 text-xs sm:text-sm text-[#24110A] font-medium leading-relaxed">
                {renderInline(numMatch[2])}
              </div>
            </div>
          );
        } else if (trimmed === '') {
          // Spacer
        } else {
          nodes.push(
            <p key={i} className="my-2.5 text-xs sm:text-sm text-[#4A281A] font-medium leading-relaxed">
              {renderInline(line)}
            </p>
          );
        }
      }
    });

    if (inTable) {
      flushTable(lines.length);
    }

    return nodes;
  }, [reportContent]);

  return (
    <div className="space-y-6">
      
      {/* Header & Export Download Toolbar */}
      <div className="p-4 sm:p-6 rounded-2xl sm:rounded-3xl bg-white border border-[#FAD5C0] flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 sm:gap-5 shadow-sm">
        <div className="w-full lg:w-auto">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-gradient-to-tr from-brand-600 to-brand-500 text-white shadow-md shadow-brand-500/20 shrink-0">
              <FileCheck className="w-4 h-4 sm:w-5 sm:h-5" />
            </div>
            <div>
              <h3 className="text-base sm:text-lg font-black text-[#24110A]">Reports & Multi-Format Exports</h3>
              <p className="text-xs text-[#6B3B2B] font-medium mt-0.5">
                Verified analytical documents formatted with tabular columns and executive summaries.
              </p>
            </div>
          </div>
        </div>

        {/* Clean Export Download Actions (2 cols on mobile, flex on tablet/desktop) */}
        <div className="grid grid-cols-2 sm:flex sm:flex-wrap items-center gap-2 sm:gap-2.5 w-full lg:w-auto">
          <a
            href={api.getExportPdfUrl(currentForm?.id)}
            download
            className="flex items-center justify-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 text-white text-xs font-bold shadow-md shadow-brand-500/20 transition-all active:scale-95 text-center"
            title="Download PDF Analytical Document"
          >
            <Download className="w-3.5 h-3.5 sm:w-4 sm:h-4 shrink-0" />
            <span className="truncate">PDF Document</span>
          </a>

          <a
            href={api.getExportDocxUrl(currentForm?.id)}
            download
            className="flex items-center justify-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-2.5 rounded-xl bg-[#FFF2EB] hover:bg-[#FFE6D9] text-[#3B1F14] text-xs font-bold border border-[#FAD5C0] transition-colors shadow-sm text-center"
            title="Download Microsoft Word .DOCX Document"
          >
            <Download className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-blue-700 shrink-0" />
            <span className="truncate">Word (.docx)</span>
          </a>

          <a
            href={api.getExportXlsxUrl(currentForm?.id)}
            download
            className="flex items-center justify-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-2.5 rounded-xl bg-[#FFF2EB] hover:bg-[#FFE6D9] text-[#3B1F14] text-xs font-bold border border-[#FAD5C0] transition-colors shadow-sm text-center"
            title="Download 5-Sheet Excel Workbook"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-emerald-700 shrink-0" />
            <span className="truncate">Excel (.xlsx)</span>
          </a>

          <a
            href={api.getExportCsvUrl(currentForm?.id)}
            download
            className="flex items-center justify-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-2.5 rounded-xl bg-[#FFF2EB] hover:bg-[#FFE6D9] text-[#3B1F14] text-xs font-bold border border-[#FAD5C0] transition-colors shadow-sm text-center"
            title="Download Raw CSV Data"
          >
            <Download className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-purple-700 shrink-0" />
            <span className="truncate">Raw CSV</span>
          </a>
        </div>
      </div>

      {/* Preset Selector Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {reportPresets.map((preset) => {
          const isSelected = reportType === preset.id;
          const IconComponent = preset.icon;
          return (
            <button
              key={preset.id}
              onClick={() => {
                setReportType(preset.id);
                fetchReport(preset.id);
              }}
              className={`p-3.5 sm:p-4 rounded-2xl text-left border transition-all flex flex-col justify-between active:scale-[0.99] ${
                isSelected
                  ? 'bg-orange-50/90 border-brand-500 shadow-md ring-2 ring-brand-500/30'
                  : 'bg-white border-[#FAD5C0] hover:border-brand-400 hover:bg-[#FFFAF7] shadow-sm'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-1.5">
                    <IconComponent className={`w-4 h-4 ${preset.color}`} />
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-[#FFF2EB] text-[#3B1F14] border border-[#FAD5C0]">
                      {preset.badge}
                    </span>
                  </div>
                  {isSelected && <CheckCircle className="w-4 h-4 text-brand-600 shrink-0" />}
                </div>
                <h4 className="text-xs font-black text-[#24110A] leading-snug">
                  {preset.label}
                </h4>
                <p className="text-[11px] text-[#6B3B2B] mt-1.5 font-medium leading-relaxed">{preset.desc}</p>
              </div>
            </button>
          );
        })}
      </div>

      {/* Report Document Box */}
      <div className="p-4 sm:p-8 rounded-2xl sm:rounded-3xl bg-white border border-[#FAD5C0] relative shadow-md">
        
        {/* Controls Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 sm:pb-5 mb-5 sm:mb-6 border-b border-[#FDE4D7]">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-300 shrink-0">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-sm font-black text-[#24110A]">Live Verified Report</h4>
              <p className="text-[11px] text-[#6B3B2B] font-medium">Structured tables and bulleted highlights</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* View Mode Toggle */}
            <div className="flex items-center p-1 rounded-xl bg-[#FFF2EB] border border-[#FAD5C0] text-xs">
              <button
                onClick={() => setViewMode('formatted')}
                className={`flex items-center gap-1 px-2.5 sm:px-3 py-1.5 rounded-lg font-bold transition-all text-xs ${
                  viewMode === 'formatted'
                    ? 'bg-gradient-to-r from-brand-600 to-brand-500 text-white shadow-sm'
                    : 'text-[#6B3B2B] hover:text-[#24110A]'
                }`}
              >
                <Eye className="w-3.5 h-3.5 shrink-0" />
                <span>Document View</span>
              </button>
              <button
                onClick={() => setViewMode('raw')}
                className={`flex items-center gap-1 px-2.5 sm:px-3 py-1.5 rounded-lg font-bold transition-all text-xs ${
                  viewMode === 'raw'
                    ? 'bg-gradient-to-r from-brand-600 to-brand-500 text-white shadow-sm'
                    : 'text-[#6B3B2B] hover:text-[#24110A]'
                }`}
              >
                <Code2 className="w-3.5 h-3.5 shrink-0" />
                <span>Raw Markdown</span>
              </button>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleCopyMarkdown}
                className="flex items-center gap-1.5 px-3 py-1.5 sm:py-2 rounded-xl bg-[#FFF2EB] hover:bg-[#FFE6D9] text-xs text-[#3B1F14] font-bold transition-colors border border-[#FAD5C0] shadow-sm"
                title="Copy markdown text"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>

              <button
                onClick={handlePrint}
                className="flex items-center gap-1.5 px-3 py-1.5 sm:py-2 rounded-xl bg-[#FFF2EB] hover:bg-[#FFE6D9] text-xs text-[#3B1F14] font-bold transition-colors border border-[#FAD5C0] shadow-sm"
                title="Print document"
              >
                <Printer className="w-3.5 h-3.5 text-[#3B1F14]" />
                <span>Print</span>
              </button>
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        {isGenerating ? (
          <div className="py-16 sm:py-24 text-center text-[#6B3B2B] flex flex-col items-center justify-center gap-3">
            <Sparkles className="w-8 h-8 text-brand-600 animate-spin" />
            <span className="text-xs sm:text-sm font-bold text-[#24110A]">Generating report document with verified survey calculations...</span>
          </div>
        ) : viewMode === 'formatted' ? (
          <div className="bg-[#FFFAF7] p-4 sm:p-10 rounded-2xl border border-[#FDE4D7] shadow-inner max-h-[750px] overflow-y-auto overflow-x-hidden">
            {renderedSections}
          </div>
        ) : (
          <div className="bg-[#FFF8F4] p-4 sm:p-6 rounded-2xl border border-[#FDE4D7] max-h-[750px] overflow-y-auto overflow-x-auto text-xs font-mono text-[#24110A] whitespace-pre-wrap leading-relaxed">
            {reportContent}
          </div>
        )}

      </div>

    </div>
  );
};
