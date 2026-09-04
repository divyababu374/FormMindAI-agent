import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useForm } from '../../context/FormContext';
import { api } from '../../services/api';
import { ChartRenderer } from '../common/ChartRenderer';
import { Badge } from '../common/Badge';
import { 
  Send, 
  Sparkles, 
  User, 
  Trash2, 
  Bot, 
  CheckCircle2, 
  BarChart3, 
  FileText,
  ImageIcon,
  RotateCcw,
  Download,
  FileSpreadsheet,
  FileCheck,
  Loader2
} from 'lucide-react';

export const AIChatTab = () => {
  const { currentForm, setActiveTab } = useForm();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [downloadingUrl, setDownloadingUrl] = useState(null);
  const messagesEndRef = useRef(null);

  const handleDownload = async (url, filename) => {
    try {
      setDownloadingUrl(url);
      await api.downloadFile(url, filename);
    } catch (err) {
      console.error('Download error, opening directly in new tab:', err);
      window.open(url, '_blank');
    } finally {
      setDownloadingUrl(null);
    }
  };

  const getFileTheme = (type) => {
    switch ((type || '').toLowerCase()) {
      case 'docx':
        return {
          cardBg: 'bg-gradient-to-br from-blue-50 to-indigo-50/60 border-blue-200',
          badgeBg: 'bg-blue-600 text-white shadow-blue-500/20',
          btnBg: 'bg-blue-600 hover:bg-blue-700 text-white shadow-md shadow-blue-500/25',
          label: 'Word (.docx)',
          icon: FileText
        };
      case 'pdf':
        return {
          cardBg: 'bg-gradient-to-br from-rose-50 to-red-50/60 border-rose-200',
          badgeBg: 'bg-rose-600 text-white shadow-rose-500/20',
          btnBg: 'bg-rose-600 hover:bg-rose-700 text-white shadow-md shadow-rose-500/25',
          label: 'PDF Document',
          icon: FileText
        };
      case 'xlsx':
        return {
          cardBg: 'bg-gradient-to-br from-emerald-50 to-teal-50/60 border-emerald-200',
          badgeBg: 'bg-emerald-600 text-white shadow-emerald-500/20',
          btnBg: 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-md shadow-emerald-500/25',
          label: 'Excel (.xlsx)',
          icon: FileSpreadsheet
        };
      case 'csv':
        return {
          cardBg: 'bg-gradient-to-br from-purple-50 to-violet-50/60 border-purple-200',
          badgeBg: 'bg-purple-600 text-white shadow-purple-500/20',
          btnBg: 'bg-purple-600 hover:bg-purple-700 text-white shadow-md shadow-purple-500/25',
          label: 'Raw CSV',
          icon: FileCheck
        };
      default:
        return {
          cardBg: 'bg-gradient-to-br from-orange-50 to-amber-50/60 border-orange-200',
          badgeBg: 'bg-brand-600 text-white shadow-brand-500/20',
          btnBg: 'bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 text-white shadow-md shadow-brand-500/25',
          label: 'Document',
          icon: Download
        };
    }
  };

  const loadHistory = async () => {
    if (!currentForm) return;
    try {
      const history = await api.getChatHistory(currentForm.id);
      setMessages(history.messages || []);
    } catch (err) {
      console.error('Failed to load chat history:', err);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [currentForm?.id]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  const handleSendMessage = async (textToSend) => {
    const text = textToSend || inputValue;
    if (!text.trim() || isSending || !currentForm) return;

    const userMsg = {
      id: 'temp-' + Date.now(),
      role: 'user',
      content: text,
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsSending(true);

    try {
      const responseMsg = await api.sendChatMessage(currentForm.id, text);
      setMessages(prev => [...prev, responseMsg]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: 'err-' + Date.now(),
          role: 'assistant',
          content: 'Sorry, an error occurred while processing your query. Please try again.',
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const handleClearHistory = async () => {
    if (!window.confirm('Clear all conversation history for this form?')) return;
    await api.clearChatHistory(currentForm.id);
    setMessages([]);
  };

  // Generate dynamic contextual prompts based on actual form questions
  const dynamicPrompts = useMemo(() => {
    const prompts = [];
    const questions = currentForm?.questions || [];

    if (questions.length > 0) {
      prompts.push("What are the answers to question 1?");
    }
    if (questions.length > 1) {
      prompts.push("What are the answers to question 2?");
    }

    const ratingQ = questions.find(q => 
      q.question_type === 'rating' || 
      q.inferred_data_type === 'numeric' || 
      /rating|satisfied|satisfaction|score/i.test(q.question_text)
    );
    if (ratingQ) {
      prompts.push("What is the average rating score?");
    }

    prompts.push("Generate downloadable Word report (.docx)");
    prompts.push("Export all responses to Excel (.xlsx)");
    prompts.push("What was the most popular topic or choice?");
    prompts.push("Show negative feedback and critiques");
    prompts.push("Summarize all responses into key insights");

    return prompts.slice(0, 8);
  }, [currentForm]);

  // Formatter for markdown content (tables, headers, bold, bullet points)
  const renderFormattedMarkdown = (text) => {
    if (!text) return null;

    const lines = text.split('\n');
    const elements = [];
    let tableRows = [];
    let inTable = false;

    const flushTable = (key) => {
      if (tableRows.length === 0) return;
      const headerRow = tableRows[0];
      const dataRows = tableRows.slice(1).filter(r => !r.every(c => /^:?-+:?$/.test(c.trim())));
      elements.push(
        <div key={`table-${key}`} className="my-3 overflow-x-auto rounded-xl border border-[#FAD5C0] shadow-sm bg-white">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-[#FFF2EB] border-b border-[#FAD5C0]">
                {headerRow.map((col, ci) => (
                  <th key={ci} className="p-2.5 font-bold text-[#8C2C08]">{formatInline(col)}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#FDE4D7]">
              {dataRows.map((row, ri) => (
                <tr key={ri} className={ri % 2 === 0 ? "bg-[#FFFAF7]" : "bg-white"}>
                  {row.map((col, ci) => (
                    <td key={ci} className="p-2 text-[#24110A] font-medium">{formatInline(col)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      tableRows = [];
      inTable = false;
    };

    const formatInline = (str) => {
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

    lines.forEach((line, i) => {
      const trimmed = line.trim();
      if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
        inTable = true;
        const cells = trimmed.split('|').slice(1, -1).map(c => c.trim());
        tableRows.push(cells);
      } else {
        if (inTable) {
          flushTable(i);
        }
        if (trimmed.startsWith('### ')) {
          elements.push(<h4 key={i} className="text-sm font-black text-[#24110A] mt-3 mb-1.5">{formatInline(trimmed.replace(/^###\s+/, ''))}</h4>);
        } else if (trimmed.startsWith('## ')) {
          elements.push(<h3 key={i} className="text-base font-black text-[#24110A] mt-3 mb-2">{formatInline(trimmed.replace(/^##\s+/, ''))}</h3>);
        } else if (trimmed.startsWith('• ') || trimmed.startsWith('- ')) {
          elements.push(
            <div key={i} className="flex items-start gap-2 my-1 text-[#24110A] font-medium">
              <span className="text-brand-600 font-bold mt-0.5">•</span>
              <span className="flex-1">{formatInline(trimmed.substring(2))}</span>
            </div>
          );
        } else if (/^\d+\.\s/.test(trimmed)) {
          const numMatch = trimmed.match(/^(\d+)\.\s(.*)/);
          elements.push(
            <div key={i} className="flex items-start gap-2 my-1 text-[#24110A] font-medium">
              <span className="text-brand-600 font-mono text-xs font-bold">{numMatch[1]}.</span>
              <span className="flex-1">{formatInline(numMatch[2])}</span>
            </div>
          );
        } else if (trimmed === '') {
          elements.push(<div key={i} className="h-1.5" />);
        } else {
          elements.push(<p key={i} className="my-1 text-[#24110A] leading-relaxed font-medium">{formatInline(line)}</p>);
        }
      }
    });

    if (inTable) {
      flushTable(lines.length);
    }

    return elements;
  };

  return (
    <div className="flex flex-col h-[720px] rounded-3xl bg-white border border-[#FAD5C0] overflow-hidden shadow-md">
      
      {/* Chat Header */}
      <div className="p-4 border-b border-[#FDE4D7] flex items-center justify-between bg-[#FFF7F2]">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-brand-600 to-brand-500 text-white shadow-md shadow-brand-500/20">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-black text-[#24110A]">FormMind AI Intelligence Chat</h3>
              <Badge variant="peach">Zero Hallucinations</Badge>
            </div>
            <p className="text-[11px] text-[#6B3B2B] font-medium">100% grounded in your exact survey answers & participant submissions</p>
          </div>
        </div>

        <button
          onClick={handleClearHistory}
          className="p-2 rounded-xl bg-white hover:bg-[#FFF2EB] text-[#6B3B2B] hover:text-[#24110A] border border-[#FAD5C0] transition-colors shadow-sm"
          title="Reset conversation"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 bg-[#FFFAF7]">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto">
            <div className="p-4 rounded-3xl bg-orange-100 text-brand-700 border border-orange-200 mb-4 shadow-sm">
              <Sparkles className="w-8 h-8" />
            </div>
            <h4 className="text-base font-black text-[#24110A]">Ask Anything About This Form</h4>
            <p className="text-xs text-[#6B3B2B] mt-1.5 leading-relaxed font-medium">
              FormMind is directly hooked into the raw submissions database. You can query specific respondent answers, ask for sentiment summaries, or filter by demographics.
            </p>

            <div className="mt-6 grid grid-cols-1 gap-2 w-full text-left">
              {dynamicPrompts.slice(0, 4).map((prompt, pIdx) => (
                <button
                  key={pIdx}
                  onClick={() => handleSendMessage(prompt)}
                  className="p-3 rounded-xl bg-white hover:bg-orange-50 border border-[#FAD5C0] text-xs text-[#24110A] font-bold text-left transition-all shadow-sm flex items-center justify-between group"
                >
                  <span className="group-hover:text-brand-700 transition-colors">"{prompt}"</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => {
            const isUser = msg.role === 'user';
            return (
              <div
                key={msg.id || idx}
                className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
              >
                {/* Avatar */}
                <div
                  className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                    isUser
                      ? 'bg-brand-600 text-white shadow-md shadow-brand-500/20'
                      : 'bg-orange-100 border border-orange-200 text-brand-700'
                  }`}
                >
                  {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>

                {/* Message Bubble */}
                <div
                  className={`p-4 rounded-2xl max-w-xl text-xs sm:text-sm leading-relaxed ${
                    isUser
                      ? 'bg-gradient-to-r from-brand-600 to-brand-500 text-white shadow-md shadow-brand-500/10 whitespace-pre-wrap font-medium'
                      : 'bg-white border border-[#FAD5C0] text-[#24110A] shadow-sm font-medium'
                  }`}
                >
                  {isUser ? (
                    <div>{msg.content}</div>
                  ) : (
                    <div>{renderFormattedMarkdown(msg.content)}</div>
                  )}

                  {/* Inline Chart Attachment */}
                  {msg.chart_data && (
                    <div className="mt-4 p-3 rounded-xl bg-[#FFF8F4] border border-[#FDE4D7]">
                      <ChartRenderer
                        type={msg.chart_data.type || 'bar'}
                        labels={msg.chart_data.labels || []}
                        data={msg.chart_data.datasets?.[0]?.data || []}
                        title={msg.chart_data.title}
                        height={180}
                      />
                    </div>
                  )}

                  {/* Downloadable Document Attachment Card */}
                  {msg.file_attachment && (
                    <div className={`mt-3.5 p-4 rounded-2xl border shadow-sm ${getFileTheme(msg.file_attachment.file_type).cardBg}`}>
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                        <div className="flex items-start gap-3">
                          <div className={`p-2.5 rounded-xl shrink-0 shadow-sm ${getFileTheme(msg.file_attachment.file_type).badgeBg}`}>
                            {React.createElement(getFileTheme(msg.file_attachment.file_type).icon, { className: "w-5 h-5" })}
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <h4 className="text-xs sm:text-sm font-black text-[#24110A]">
                                {msg.file_attachment.title || 'Downloadable Document'}
                              </h4>
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center gap-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse" />
                                Ready
                              </span>
                            </div>
                            <p className="text-[11px] font-mono text-[#6B3B2B] mt-0.5">
                              {msg.file_attachment.filename}
                            </p>
                          </div>
                        </div>

                        {/* Primary Download Action Button */}
                        <button
                          onClick={() => handleDownload(msg.file_attachment.download_url, msg.file_attachment.filename)}
                          disabled={downloadingUrl === msg.file_attachment.download_url}
                          className={`flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all active:scale-95 shrink-0 ${getFileTheme(msg.file_attachment.file_type).btnBg}`}
                        >
                          {downloadingUrl === msg.file_attachment.download_url ? (
                            <>
                              <Loader2 className="w-4 h-4 animate-spin" />
                              <span>Downloading...</span>
                            </>
                          ) : (
                            <>
                              <Download className="w-4 h-4" />
                              <span>Download {getFileTheme(msg.file_attachment.file_type).label}</span>
                            </>
                          )}
                        </button>
                      </div>

                      {/* Other Export Formats Available */}
                      {msg.file_attachment.other_formats && msg.file_attachment.other_formats.length > 0 && (
                        <div className="mt-3 pt-2.5 border-t border-black/10 flex flex-wrap items-center gap-2">
                          <span className="text-[11px] font-bold text-[#6B3B2B]">Other formats:</span>
                          {msg.file_attachment.other_formats.map((fmt, fIdx) => (
                            <button
                              key={fIdx}
                              onClick={() => handleDownload(fmt.url, `FormMind_Export_${fmt.type}.${fmt.type}`)}
                              disabled={downloadingUrl === fmt.url}
                              className="px-2.5 py-1 rounded-lg bg-white hover:bg-orange-50 text-[#3B1F14] border border-[#FAD5C0] text-[11px] font-semibold transition-colors flex items-center gap-1.5 shadow-xs"
                            >
                              <Download className="w-3 h-3 text-brand-600" />
                              <span>{fmt.label}</span>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Action Shortcuts if Intent Detected */}
                  {(msg.intent_detected === 'report_generation' || msg.intent_detected === 'document_generation') && (
                    <button
                      onClick={() => setActiveTab('reports')}
                      className="mt-3 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-orange-100 text-brand-800 border border-orange-200 text-xs font-bold hover:bg-orange-200 transition-colors"
                    >
                      <FileText className="w-3.5 h-3.5" />
                      <span>Open Reports Studio</span>
                    </button>
                  )}

                  {msg.intent_detected === 'image_generation' && (
                    <button
                      onClick={() => setActiveTab('infographic')}
                      className="mt-3 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-100 text-purple-900 border border-purple-200 text-xs font-bold hover:bg-purple-200 transition-colors"
                    >
                      <ImageIcon className="w-3.5 h-3.5" />
                      <span>View & Download Infographic</span>
                    </button>
                  )}
                </div>
              </div>
            );
          })
        )}

        {isSending && (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-orange-100 border border-orange-200 text-brand-700 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4" />
            </div>
            <div className="p-3.5 rounded-2xl bg-white border border-[#FAD5C0] flex items-center gap-2 shadow-sm">
              <div className="w-2 h-2 rounded-full bg-brand-500 animate-bounce" />
              <div className="w-2 h-2 rounded-full bg-brand-500 animate-bounce [animation-delay:0.2s]" />
              <div className="w-2 h-2 rounded-full bg-brand-500 animate-bounce [animation-delay:0.4s]" />
              <span className="text-xs text-[#6B3B2B] ml-2 font-semibold">Reading form data...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Follow-Up Chips */}
      {dynamicPrompts.length > 0 && messages.length > 0 && (
        <div className="px-4 py-2 border-t border-[#FDE4D7] bg-[#FFF7F2] flex items-center gap-2 overflow-x-auto text-xs">
          <span className="text-[11px] text-[#6B3B2B] font-bold shrink-0">Suggestions:</span>
          {dynamicPrompts.slice(0, 4).map((chip, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(chip)}
              className="px-2.5 py-1 rounded-lg bg-white hover:bg-[#FFF2EB] text-[#3B1F14] hover:text-[#24110A] border border-[#FAD5C0] whitespace-nowrap transition-colors font-semibold shadow-sm"
            >
              {chip}
            </button>
          ))}
        </div>
      )}

      {/* Input Area */}
      <div className="p-4 border-t border-[#FDE4D7] bg-[#FFF7F2]">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask anything (e.g., 'What are the answers to question 2?', 'Show Suresh's response')..."
            className="flex-1 bg-white border border-[#FAD5C0] rounded-2xl px-4 py-3 text-xs sm:text-sm text-[#24110A] placeholder-[#8C5D4B] focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 shadow-inner"
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isSending}
            className="p-3 rounded-2xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 disabled:opacity-40 text-white shadow-md shadow-brand-500/20 transition-all active:scale-95"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>

    </div>
  );
};
