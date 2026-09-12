import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
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
  Loader2,
  ArrowLeft,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  Volume2,
  VolumeX,
  Mic,
  MicOff,
  Square,
  ArrowDown,
  Edit3,
  X,
  Share2,
  FileDown,
  PlusCircle,
  HelpCircle,
  Code2
} from 'lucide-react';

export const AIChatTab = () => {
  const { currentForm, setActiveTab, goBack } = useForm();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingMessageId, setStreamingMessageId] = useState(null);
  const [displayedStreamingText, setDisplayedStreamingText] = useState('');
  const [downloadingUrl, setDownloadingUrl] = useState(null);
  
  // Feedback states per message id: { [msgId]: 'liked' | 'disliked' }
  const [feedbackState, setFeedbackState] = useState({});
  // Copy state per message id: { [msgId]: boolean }
  const [copiedStates, setCopiedStates] = useState({});
  // Speech synthesis state: currently speaking message id or null
  const [speakingMessageId, setSpeakingMessageId] = useState(null);
  // Voice input recognition state
  const [isListening, setIsListening] = useState(false);
  // User prompt editing state: messageId being edited, or null
  const [editingMessageId, setEditingMessageId] = useState(null);
  const [editingText, setEditingText] = useState('');
  // Scroll to bottom floating button visibility
  const [showScrollBottom, setShowScrollBottom] = useState(false);

  const messagesEndRef = useRef(null);
  const chatScrollContainerRef = useRef(null);
  const textareaRef = useRef(null);
  const streamIntervalRef = useRef(null);
  const recognitionRef = useRef(null);

  // -------------------------------------------------------------
  // Speech Recognition (Voice to Text) Setup
  // -------------------------------------------------------------
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        setInputValue(prev => (prev ? prev + ' ' + transcript : transcript));
      };

      recognition.onerror = (err) => {
        console.warn('Speech recognition error:', err);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }
  }, []);

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      alert('Speech Recognition is not supported by your current browser. Please use Chrome, Edge, or Safari.');
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (e) {
        console.error('Failed to start speech recognition:', e);
      }
    }
  };

  // -------------------------------------------------------------
  // Text-to-Speech (Read Aloud)
  // -------------------------------------------------------------
  const toggleSpeak = (msgId, text) => {
    if (!('speechSynthesis' in window)) {
      alert('Text-to-speech is not supported in this browser.');
      return;
    }

    if (speakingMessageId === msgId) {
      window.speechSynthesis.cancel();
      setSpeakingMessageId(null);
      return;
    }

    window.speechSynthesis.cancel();
    // Strip markdown formatting for cleaner speech
    const cleanText = text
      .replace(/[*_#`~[\]]/g, '')
      .replace(/\|/g, ' ')
      .replace(/\n+/g, '. ');

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.05;
    utterance.pitch = 1.0;
    utterance.onend = () => setSpeakingMessageId(null);
    utterance.onerror = () => setSpeakingMessageId(null);

    setSpeakingMessageId(msgId);
    window.speechSynthesis.speak(utterance);
  };

  useEffect(() => {
    return () => {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
      if (streamIntervalRef.current) {
        clearInterval(streamIntervalRef.current);
      }
    };
  }, []);

  // -------------------------------------------------------------
  // Auto-resize Textarea
  // -------------------------------------------------------------
  const handleInputChange = (e) => {
    setInputValue(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  };

  // -------------------------------------------------------------
  // Scroll Detection for Floating "Scroll to Bottom" Button
  // -------------------------------------------------------------
  const handleScroll = () => {
    if (!chatScrollContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = chatScrollContainerRef.current;
    const isFarFromBottom = scrollHeight - scrollTop - clientHeight > 180;
    setShowScrollBottom(isFarFromBottom);
  };

  const scrollToBottom = (behavior = 'smooth') => {
    messagesEndRef.current?.scrollIntoView({ behavior });
  };

  // -------------------------------------------------------------
  // Download Handler for Export Documents
  // -------------------------------------------------------------
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
          cardBg: 'bg-gradient-to-br from-blue-50/80 to-indigo-50/50 border-blue-200/80',
          badgeBg: 'bg-blue-600 text-white shadow-blue-500/20',
          btnBg: 'bg-blue-600 hover:bg-blue-700 text-white shadow-md shadow-blue-500/25',
          label: 'Word (.docx)',
          icon: FileText
        };
      case 'pdf':
        return {
          cardBg: 'bg-gradient-to-br from-rose-50/80 to-red-50/50 border-rose-200/80',
          badgeBg: 'bg-rose-600 text-white shadow-rose-500/20',
          btnBg: 'bg-rose-600 hover:bg-rose-700 text-white shadow-md shadow-rose-500/25',
          label: 'PDF Document',
          icon: FileText
        };
      case 'xlsx':
        return {
          cardBg: 'bg-gradient-to-br from-emerald-50/80 to-teal-50/50 border-emerald-200/80',
          badgeBg: 'bg-emerald-600 text-white shadow-emerald-500/20',
          btnBg: 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-md shadow-emerald-500/25',
          label: 'Excel (.xlsx)',
          icon: FileSpreadsheet
        };
      case 'csv':
        return {
          cardBg: 'bg-gradient-to-br from-purple-50/80 to-violet-50/50 border-purple-200/80',
          badgeBg: 'bg-purple-600 text-white shadow-purple-500/20',
          btnBg: 'bg-purple-600 hover:bg-purple-700 text-white shadow-md shadow-purple-500/25',
          label: 'Raw CSV',
          icon: FileCheck
        };
      default:
        return {
          cardBg: 'bg-gradient-to-br from-orange-50/80 to-amber-50/50 border-orange-200/80',
          badgeBg: 'bg-brand-600 text-white shadow-brand-500/20',
          btnBg: 'bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 text-white shadow-md shadow-brand-500/25',
          label: 'Document',
          icon: Download
        };
    }
  };

  // -------------------------------------------------------------
  // Load History
  // -------------------------------------------------------------
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
    if (!showScrollBottom) {
      scrollToBottom('smooth');
    }
  }, [messages, displayedStreamingText, isSending]);

  // -------------------------------------------------------------
  // Typewriter Streaming Emulation
  // -------------------------------------------------------------
  const streamAssistantResponse = useCallback((fullMessage) => {
    const fullText = fullMessage.content || '';
    if (!fullText) {
      setMessages(prev => [...prev, fullMessage]);
      setIsStreaming(false);
      return;
    }

    const words = fullText.split(' ');
    let currentIdx = 0;
    setDisplayedStreamingText('');
    setStreamingMessageId(fullMessage.id);
    setIsStreaming(true);

    // Initial message shell added so attachments and roles render
    setMessages(prev => [...prev, { ...fullMessage, content: '' }]);

    if (streamIntervalRef.current) clearInterval(streamIntervalRef.current);

    streamIntervalRef.current = setInterval(() => {
      currentIdx += Math.floor(Math.random() * 2) + 1; // 1-2 words per tick for realistic rhythm
      if (currentIdx >= words.length) {
        clearInterval(streamIntervalRef.current);
        streamIntervalRef.current = null;
        setDisplayedStreamingText('');
        setIsStreaming(false);
        setStreamingMessageId(null);
        // Replace with complete content
        setMessages(prev => prev.map(m => m.id === fullMessage.id ? fullMessage : m));
      } else {
        const partial = words.slice(0, currentIdx).join(' ');
        setDisplayedStreamingText(partial);
        setMessages(prev => prev.map(m => m.id === fullMessage.id ? { ...m, content: partial } : m));
      }
    }, 28);
  }, []);

  const stopGenerating = () => {
    if (streamIntervalRef.current) {
      clearInterval(streamIntervalRef.current);
      streamIntervalRef.current = null;
    }
    setIsStreaming(false);
    setIsSending(false);
    setStreamingMessageId(null);
    setDisplayedStreamingText('');
  };

  // -------------------------------------------------------------
  // Send Message / Regenerate / Edit Prompt
  // -------------------------------------------------------------
  const handleSendMessage = async (textToSend) => {
    const text = textToSend || inputValue;
    if (!text.trim() || isSending || !currentForm) return;

    if (isStreaming) {
      stopGenerating();
    }

    const userMsg = {
      id: 'usr-' + Date.now(),
      role: 'user',
      content: text.trim(),
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    setIsSending(true);

    try {
      const responseMsg = await api.sendChatMessage(currentForm.id, text.trim());
      setIsSending(false);
      streamAssistantResponse(responseMsg);
    } catch (err) {
      setIsSending(false);
      setMessages(prev => [
        ...prev,
        {
          id: 'err-' + Date.now(),
          role: 'assistant',
          content: 'I apologize, an issue occurred while analyzing the submissions. Please verify your connection or try again.',
          created_at: new Date().toISOString()
        }
      ]);
    }
  };

  // Re-run the last prompt (ChatGPT Regenerate)
  const handleRegenerate = () => {
    if (isSending || isStreaming || messages.length === 0) return;
    // Find the last user message
    const lastUserMsg = [...messages].reverse().find(m => m.role === 'user');
    if (lastUserMsg) {
      handleSendMessage(lastUserMsg.content);
    }
  };

  // Edit user prompt in place
  const handleStartEdit = (msg) => {
    setEditingMessageId(msg.id);
    setEditingText(msg.content);
  };

  const handleCancelEdit = () => {
    setEditingMessageId(null);
    setEditingText('');
  };

  const handleSaveAndSubmitEdit = (originalMsgId) => {
    if (!editingText.trim()) return;
    // Remove messages from this user message onward
    const idx = messages.findIndex(m => m.id === originalMsgId);
    if (idx !== -1) {
      setMessages(messages.slice(0, idx));
    }
    const newPrompt = editingText.trim();
    setEditingMessageId(null);
    setEditingText('');
    handleSendMessage(newPrompt);
  };

  // Copy message text
  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedStates(prev => ({ ...prev, [id]: true }));
    setTimeout(() => {
      setCopiedStates(prev => ({ ...prev, [id]: false }));
    }, 2000);
  };

  // Copy individual code block
  const handleCopyCode = (codeKey, codeContent) => {
    navigator.clipboard.writeText(codeContent);
    setCopiedStates(prev => ({ ...prev, [codeKey]: true }));
    setTimeout(() => {
      setCopiedStates(prev => ({ ...prev, [codeKey]: false }));
    }, 2000);
  };

  // Feedback thumb rating
  const handleFeedback = (msgId, type) => {
    setFeedbackState(prev => ({
      ...prev,
      [msgId]: prev[msgId] === type ? null : type
    }));
  };

  // Clear / Reset Conversation
  const handleClearHistory = async () => {
    if (!window.confirm('Reset conversation? This will clear all messages in this session.')) return;
    if (speakingMessageId) {
      window.speechSynthesis.cancel();
      setSpeakingMessageId(null);
    }
    stopGenerating();
    await api.clearChatHistory(currentForm.id);
    setMessages([]);
  };

  // Export full chat transcript as Markdown (.md)
  const handleExportChat = () => {
    if (messages.length === 0) return;
    const title = currentForm?.title || 'FormMind Chat';
    let md = `# FormMind AI Conversation: ${title}\n`;
    md += `*Exported on ${new Date().toLocaleString()}*\n\n---\n\n`;

    messages.forEach(m => {
      const sender = m.role === 'user' ? '👤 **You**' : '🤖 **FormMind AI**';
      md += `${sender}:\n\n${m.content}\n\n---\n\n`;
    });

    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${title.replace(/\s+/g, '_')}_Chat_Transcript.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Dynamic contextual suggestions based on actual form questions
  const dynamicPrompts = useMemo(() => {
    const prompts = [];
    const questions = currentForm?.questions || [];

    if (questions.length > 0) {
      prompts.push(`What are the most frequent answers to "${questions[0].question_text.slice(0, 32)}..."?`);
    }
    if (questions.length > 1) {
      prompts.push(`Compare breakdown for Question 2 with overall results`);
    }

    const ratingQ = questions.find(q =>
      q.question_type === 'rating' ||
      q.inferred_data_type === 'numeric' ||
      /rating|satisfied|satisfaction|score/i.test(q.question_text)
    );
    if (ratingQ) {
      prompts.push("What is the average rating score and satisfaction trend?");
    }

    prompts.push("Summarize all responses into key executive insights");
    prompts.push("Generate downloadable Word report (.docx)");
    prompts.push("Show negative feedback and critical pain points");
    prompts.push("Export all clean responses to Excel (.xlsx)");

    return prompts;
  }, [currentForm]);

  // -------------------------------------------------------------
  // Markdown & Code Block Formatter
  // -------------------------------------------------------------
  const renderFormattedMarkdown = (text, messageId) => {
    if (!text) return null;

    // Check for fenced code blocks: ```lang ... ```
    const codeBlockRegex = /```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g;
    const blocks = [];
    let lastIdx = 0;
    let match;

    while ((match = codeBlockRegex.exec(text)) !== null) {
      if (match.index > lastIdx) {
        blocks.push({ type: 'markdown', content: text.substring(lastIdx, match.index) });
      }
      blocks.push({
        type: 'code',
        language: match[1] || 'text',
        code: match[2].trimEnd()
      });
      lastIdx = match.index + match[0].length;
    }

    if (lastIdx < text.length) {
      blocks.push({ type: 'markdown', content: text.substring(lastIdx) });
    }

    return (
      <div className="space-y-3">
        {blocks.map((block, bIdx) => {
          if (block.type === 'code') {
            const codeKey = `${messageId}-code-${bIdx}`;
            const isCopied = copiedStates[codeKey];
            return (
              <div key={bIdx} className="my-3 rounded-xl overflow-hidden border border-neutral-800 bg-[#1e1e1e] text-neutral-100 shadow-md chat-code-block">
                <div className="flex items-center justify-between px-4 py-2 bg-[#2d2d2d] border-b border-neutral-700/60 text-xs font-mono chat-code-header">
                  <span className="text-neutral-300 font-semibold lowercase flex items-center gap-1.5">
                    <Code2 className="w-3.5 h-3.5 text-neutral-300" />
                    {block.language || 'code'}
                  </span>
                  <button
                    onClick={() => handleCopyCode(codeKey, block.code)}
                    className="flex items-center gap-1 px-2.5 py-1 rounded bg-neutral-700 hover:bg-neutral-600 text-neutral-200 hover:text-white transition-colors text-[11px] font-sans"
                    title="Copy code to clipboard"
                  >
                    {isCopied ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-emerald-400 font-medium">Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        <span>Copy code</span>
                      </>
                    )}
                  </button>
                </div>
                <pre className="p-4 text-xs font-mono overflow-x-auto text-neutral-200 leading-relaxed whitespace-pre">
                  <code>{block.code}</code>
                </pre>
              </div>
            );
          }

          // Markdown regular lines & tables
          return (
            <div key={bIdx} className="space-y-1.5">
              {renderMarkdownText(block.content, `${messageId}-${bIdx}`)}
            </div>
          );
        })}
      </div>
    );
  };

  const renderMarkdownText = (text, keyPrefix) => {
    const lines = text.split('\n');
    const elements = [];
    let tableRows = [];
    let inTable = false;

    const flushTable = (k) => {
      if (tableRows.length === 0) return;
      const headerRow = tableRows[0];
      const dataRows = tableRows.slice(1).filter(r => !r.every(c => /^:?-+:?$/.test(c.trim())));
      elements.push(
        <div key={`table-${k}`} className="my-3 overflow-x-auto rounded-xl border border-[#FAD5C0] shadow-xs bg-white">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-[#FFF2EB] border-b border-[#FAD5C0]">
                {headerRow.map((col, ci) => (
                  <th key={ci} className="p-2.5 font-bold text-[#8C2C08] whitespace-nowrap">
                    {formatInline(col)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#FDE4D7]">
              {dataRows.map((row, ri) => (
                <tr key={ri} className={ri % 2 === 0 ? "bg-[#FFFAF7]" : "bg-white"}>
                  {row.map((col, ci) => (
                    <td key={ci} className="p-2.5 text-[#24110A] font-medium leading-normal">
                      {formatInline(col)}
                    </td>
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
        parts.push(<strong key={idx++} className="font-bold text-[#24110A]">{match[1]}</strong>);
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
          elements.push(
            <h4 key={i} className="text-sm font-bold text-[#24110A] mt-3.5 mb-1.5 flex items-center gap-1.5">
              {formatInline(trimmed.replace(/^###\s+/, ''))}
            </h4>
          );
        } else if (trimmed.startsWith('## ')) {
          elements.push(
            <h3 key={i} className="text-base font-extrabold text-[#24110A] mt-4 mb-2">
              {formatInline(trimmed.replace(/^##\s+/, ''))}
            </h3>
          );
        } else if (trimmed.startsWith('• ') || trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
          elements.push(
            <div key={i} className="flex items-start gap-2.5 my-1 text-[#24110A] font-medium pl-1">
              <span className="text-brand-600 font-bold mt-0.5 select-none">•</span>
              <span className="flex-1 leading-relaxed">{formatInline(trimmed.substring(2))}</span>
            </div>
          );
        } else if (/^\d+\.\s/.test(trimmed)) {
          const numMatch = trimmed.match(/^(\d+)\.\s(.*)/);
          elements.push(
            <div key={i} className="flex items-start gap-2.5 my-1 text-[#24110A] font-medium pl-1">
              <span className="text-brand-600 font-mono text-xs font-bold mt-0.5 select-none">{numMatch[1]}.</span>
              <span className="flex-1 leading-relaxed">{formatInline(numMatch[2])}</span>
            </div>
          );
        } else if (trimmed.startsWith('> ')) {
          elements.push(
            <div key={i} className="my-2 pl-3 py-1.5 border-l-3 border-brand-500 bg-[#FFF5F0] rounded-r-lg text-xs italic text-[#4A2618]">
              {formatInline(trimmed.replace(/^>\s+/, ''))}
            </div>
          );
        } else if (trimmed === '') {
          elements.push(<div key={i} className="h-1.5" />);
        } else {
          elements.push(
            <p key={i} className="my-1 text-[#24110A] leading-relaxed font-medium text-xs sm:text-sm">
              {formatInline(line)}
            </p>
          );
        }
      }
    });

    if (inTable) {
      flushTable(lines.length);
    }

    return elements;
  };

  return (
    <div className="relative flex flex-col h-[calc(100dvh-170px)] sm:h-[760px] min-h-[520px] max-h-[860px] rounded-2xl sm:rounded-3xl bg-white border border-[#FAD5C0] overflow-hidden shadow-lg">
      
      {/* -------------------------------------------------------------
          Header Bar (ChatGPT Style with Model Selector & Actions)
          ------------------------------------------------------------- */}
      <div className="px-3 sm:px-5 py-3 border-b border-[#FDE4D7] flex items-center justify-between bg-[#FFF7F2] z-10 shrink-0">
        <div className="flex items-center gap-2 sm:gap-3 min-w-0">
          {/* Back Arrow */}
          <button
            onClick={goBack}
            className="p-1.5 sm:p-2 rounded-xl bg-white hover:bg-[#FFEFE5] text-[#3B1F14] hover:text-[#24110A] border border-[#FAD5C0] hover:border-brand-500 transition-all shadow-xs flex items-center gap-1 text-xs font-bold shrink-0 cursor-pointer active:scale-95 group"
            title="Go back to previous page"
            aria-label="Back"
          >
            <ArrowLeft className="w-4 h-4 text-brand-600 group-hover:-translate-x-0.5 transition-transform" />
            <span className="hidden md:inline">Back</span>
          </button>

          {/* Model Badge / Selector */}
          <div className="flex items-center gap-2 bg-white px-2.5 sm:px-3 py-1.5 rounded-xl border border-[#FAD5C0] shadow-2xs">
            <div className="w-5 h-5 rounded-lg bg-gradient-to-tr from-brand-600 to-brand-500 text-white flex items-center justify-center shadow-xs shrink-0">
              <Bot className="w-3.5 h-3.5" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-extrabold text-[#24110A] tracking-tight">FormMind Intelligence</span>
                <span className="hidden sm:inline-block px-1.5 py-0.2 rounded text-[9px] font-bold bg-orange-100 text-brand-800 border border-orange-200">
                  GPT-4o Grounded
                </span>
              </div>
              <p className="text-[10px] text-[#6B3B2B] font-medium truncate hidden sm:block">
                Zero Hallucinations • {currentForm?.responses?.length || 0} Submissions Linked
              </p>
            </div>
          </div>
        </div>

        {/* Top Right Controls: New Chat, Export Transcript, Reset */}
        <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
          {/* New Chat Button */}
          <button
            onClick={handleClearHistory}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-white hover:bg-orange-50 text-[#3B1F14] hover:text-brand-700 border border-[#FAD5C0] text-xs font-bold transition-all shadow-xs active:scale-95"
            title="Start New Chat session"
          >
            <PlusCircle className="w-3.5 h-3.5 text-brand-600" />
            <span className="hidden sm:inline">New Chat</span>
          </button>

          {/* Export Transcript Button */}
          {messages.length > 0 && (
            <button
              onClick={handleExportChat}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-white hover:bg-orange-50 text-[#3B1F14] hover:text-brand-700 border border-[#FAD5C0] text-xs font-bold transition-all shadow-xs active:scale-95"
              title="Download conversation transcript (.md)"
            >
              <FileDown className="w-3.5 h-3.5 text-brand-600" />
              <span className="hidden md:inline">Export</span>
            </button>
          )}

          {/* Clear History Button */}
          <button
            onClick={handleClearHistory}
            className="p-1.5 sm:p-2 rounded-xl bg-white hover:bg-rose-50 text-[#6B3B2B] hover:text-rose-700 border border-[#FAD5C0] hover:border-rose-200 transition-colors shadow-xs"
            title="Clear conversation"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* -------------------------------------------------------------
          Chat Messages Flow
          ------------------------------------------------------------- */}
      <div
        ref={chatScrollContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto px-3 sm:px-6 py-4 sm:py-6 space-y-6 bg-[#FFFAF7] relative scroll-smooth"
      >
        {messages.length === 0 ? (
          /* Empty State - ChatGPT Style Welcome Screen */
          <div className="h-full flex flex-col items-center justify-center text-center max-w-xl mx-auto py-8">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-600 to-brand-500 text-white flex items-center justify-center mb-4 shadow-lg shadow-brand-500/20">
              <Sparkles className="w-7 h-7" />
            </div>
            <h3 className="text-lg sm:text-xl font-black text-[#24110A] tracking-tight">
              What would you like to know about {currentForm?.title || 'this form'}?
            </h3>
            <p className="text-xs sm:text-sm text-[#6B3B2B] mt-2 max-w-md font-medium leading-relaxed">
              FormMind is directly synchronized with verified respondent data. Ask specific questions, generate custom documents, or analyze demographic correlations with zero hallucinations.
            </p>

            {/* Suggested Prompt Cards (2-column on tablet/desktop) */}
            <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full text-left">
              {dynamicPrompts.slice(0, 4).map((prompt, pIdx) => (
                <button
                  key={pIdx}
                  onClick={() => handleSendMessage(prompt)}
                  className="p-3.5 rounded-2xl bg-white hover:bg-[#FFF5F0] border border-[#FAD5C0] hover:border-brand-400 text-xs text-[#24110A] font-semibold text-left transition-all shadow-xs hover:shadow-sm flex items-center justify-between group active:scale-[0.99]"
                >
                  <span className="line-clamp-2 group-hover:text-brand-700 transition-colors">
                    "{prompt}"
                  </span>
                  <Send className="w-3.5 h-3.5 text-[#C48C75] group-hover:text-brand-600 shrink-0 ml-2 group-hover:translate-x-0.5 transition-transform" />
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Render Message Thread */
          messages.map((msg, idx) => {
            const isUser = msg.role === 'user';
            const isLastMessage = idx === messages.length - 1;
            const isCurrentlyStreaming = isStreaming && streamingMessageId === msg.id;

            return (
              <div
                key={msg.id || idx}
                className={`group flex items-start gap-2.5 sm:gap-3.5 max-w-3xl mx-auto ${
                  isUser ? 'flex-row-reverse' : 'flex-row'
                }`}
              >
                {/* Avatar */}
                <div
                  className={`w-7 h-7 sm:w-8 sm:h-8 rounded-xl flex items-center justify-center shrink-0 shadow-2xs ${
                    isUser
                      ? 'bg-brand-600 text-white'
                      : 'bg-gradient-to-tr from-brand-600 to-brand-500 text-white'
                  }`}
                >
                  {isUser ? <User className="w-3.5 h-3.5 sm:w-4 sm:h-4" /> : <Bot className="w-3.5 h-3.5 sm:w-4 sm:h-4" />}
                </div>

                {/* Message Body */}
                <div className={`flex flex-col min-w-0 max-w-[86%] sm:max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
                  
                  {/* If user is currently editing this prompt */}
                  {isUser && editingMessageId === msg.id ? (
                    <div className="w-full bg-white border border-brand-500 rounded-2xl p-3 shadow-md space-y-2">
                      <textarea
                        value={editingText}
                        onChange={(e) => setEditingText(e.target.value)}
                        className="w-full text-xs sm:text-sm text-[#24110A] focus:outline-none resize-none min-h-[60px]"
                        rows={3}
                        autoFocus
                      />
                      <div className="flex items-center justify-end gap-2 pt-1 border-t border-neutral-100">
                        <button
                          onClick={handleCancelEdit}
                          className="px-3 py-1 rounded-lg bg-neutral-100 hover:bg-neutral-200 text-neutral-700 text-xs font-semibold transition-colors"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={() => handleSaveAndSubmitEdit(msg.id)}
                          className="px-3 py-1 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold transition-colors"
                        >
                          Send
                        </button>
                      </div>
                    </div>
                  ) : (
                    /* Normal Message Bubble */
                    <div
                      className={`p-3.5 sm:p-4 rounded-2xl text-xs sm:text-sm leading-relaxed break-words relative ${
                        isUser
                          ? 'bg-gradient-to-r from-brand-600 to-brand-500 text-white shadow-md shadow-brand-500/10 font-medium rounded-tr-sm'
                          : 'bg-white border border-[#FAD5C0] text-[#24110A] shadow-xs font-normal rounded-tl-sm w-full'
                      }`}
                    >
                      {isUser ? (
                        <div className="whitespace-pre-wrap">{msg.content}</div>
                      ) : (
                        <div>
                          {renderFormattedMarkdown(msg.content, msg.id || idx)}
                          
                          {/* Blinking cursor while streaming this message */}
                          {isCurrentlyStreaming && (
                            <span className="inline-block w-2 h-4 bg-brand-600 ml-1 animate-pulse align-middle" />
                          )}
                        </div>
                      )}

                      {/* Inline Chart Attachment */}
                      {msg.chart_data && (
                        <div className="mt-4 p-3 rounded-xl bg-[#FFF8F4] border border-[#FDE4D7]">
                          <ChartRenderer
                            type={msg.chart_data.type || 'bar'}
                            labels={msg.chart_data.labels || []}
                            data={msg.chart_data.datasets?.[0]?.data || []}
                            title={msg.chart_data.title}
                            height={190}
                          />
                        </div>
                      )}

                      {/* Downloadable Document Attachment Card */}
                      {msg.file_attachment && (
                        <div className={`mt-3.5 p-3.5 sm:p-4 rounded-2xl border shadow-xs ${getFileTheme(msg.file_attachment.file_type).cardBg}`}>
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                            <div className="flex items-start gap-3">
                              <div className={`p-2.5 rounded-xl shrink-0 shadow-xs ${getFileTheme(msg.file_attachment.file_type).badgeBg}`}>
                                {React.createElement(getFileTheme(msg.file_attachment.file_type).icon, { className: "w-5 h-5" })}
                              </div>
                              <div>
                                <div className="flex items-center gap-2">
                                  <h4 className="text-xs sm:text-sm font-bold text-[#24110A]">
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

                            {/* Download Action Button */}
                            <button
                              onClick={() => handleDownload(msg.file_attachment.download_url, msg.file_attachment.filename)}
                              disabled={downloadingUrl === msg.file_attachment.download_url}
                              className={`flex items-center justify-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all active:scale-95 shrink-0 ${getFileTheme(msg.file_attachment.file_type).btnBg}`}
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

                          {/* Secondary format chips */}
                          {msg.file_attachment.other_formats && msg.file_attachment.other_formats.length > 0 && (
                            <div className="mt-3 pt-2.5 border-t border-black/10 flex flex-wrap items-center gap-2">
                              <span className="text-[11px] font-bold text-[#6B3B2B]">Other formats:</span>
                              {msg.file_attachment.other_formats.map((fmt, fIdx) => (
                                <button
                                  key={fIdx}
                                  onClick={() => handleDownload(fmt.url, `FormMind_Export_${fmt.type}.${fmt.type}`)}
                                  disabled={downloadingUrl === fmt.url}
                                  className="px-2.5 py-1 rounded-lg bg-white hover:bg-orange-50 text-[#3B1F14] border border-[#FAD5C0] text-[11px] font-semibold transition-colors flex items-center gap-1.5 shadow-2xs"
                                >
                                  <Download className="w-3 h-3 text-brand-600" />
                                  <span>{fmt.label}</span>
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Intent Direct Action Shortcuts */}
                      {(msg.intent_detected === 'report_generation' || msg.intent_detected === 'document_generation') && (
                        <button
                          onClick={() => setActiveTab('reports')}
                          className="mt-3 flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-orange-100 text-brand-800 border border-orange-200 text-xs font-bold hover:bg-orange-200 transition-colors"
                        >
                          <FileText className="w-3.5 h-3.5" />
                          <span>Open Reports Studio</span>
                        </button>
                      )}

                      {msg.intent_detected === 'image_generation' && (
                        <button
                          onClick={() => setActiveTab('infographic')}
                          className="mt-3 flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-purple-100 text-purple-900 border border-purple-200 text-xs font-bold hover:bg-purple-200 transition-colors"
                        >
                          <ImageIcon className="w-3.5 h-3.5" />
                          <span>View & Download Infographic</span>
                        </button>
                      )}
                    </div>
                  )}

                  {/* -------------------------------------------------------------
                      ChatGPT Message Action Toolbar
                      ------------------------------------------------------------- */}
                  <div className="flex items-center gap-1 mt-1.5 px-1 text-neutral-500">
                    {isUser ? (
                      /* User Actions: Edit Prompt, Copy */
                      <div className="flex items-center gap-1 opacity-80 hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => handleStartEdit(msg)}
                          className="p-1 rounded hover:bg-black/5 text-[#8C5D4B] hover:text-[#24110A] transition-colors"
                          title="Edit prompt"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleCopy(msg.id, msg.content)}
                          className="p-1 rounded hover:bg-black/5 text-[#8C5D4B] hover:text-[#24110A] transition-colors"
                          title="Copy prompt"
                        >
                          {copiedStates[msg.id] ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                        </button>
                      </div>
                    ) : (
                      /* Assistant Actions: Copy, Read Aloud, Regenerate, Thumbs Up/Down */
                      <div className="flex items-center gap-1.5 text-xs text-[#8C5D4B]">
                        {/* Copy button */}
                        <button
                          onClick={() => handleCopy(msg.id, msg.content)}
                          className="p-1 rounded hover:bg-black/5 hover:text-[#24110A] transition-colors flex items-center gap-1"
                          title="Copy response"
                        >
                          {copiedStates[msg.id] ? (
                            <>
                              <Check className="w-3.5 h-3.5 text-emerald-600" />
                              <span className="text-[10px] text-emerald-600 font-semibold">Copied</span>
                            </>
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                        </button>

                        {/* Read Aloud (Text to Speech) */}
                        <button
                          onClick={() => toggleSpeak(msg.id, msg.content)}
                          className={`p-1 rounded hover:bg-black/5 transition-colors flex items-center gap-1 ${
                            speakingMessageId === msg.id ? 'text-brand-600 font-bold bg-orange-100' : 'hover:text-[#24110A]'
                          }`}
                          title={speakingMessageId === msg.id ? "Stop speaking" : "Read aloud"}
                        >
                          {speakingMessageId === msg.id ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
                          {speakingMessageId === msg.id && <span className="text-[10px]">Listening</span>}
                        </button>

                        {/* Regenerate (if last message) */}
                        {isLastMessage && (
                          <button
                            onClick={handleRegenerate}
                            disabled={isSending || isStreaming}
                            className="p-1 rounded hover:bg-black/5 hover:text-[#24110A] transition-colors flex items-center gap-1"
                            title="Regenerate response"
                          >
                            <RotateCcw className="w-3.5 h-3.5" />
                          </button>
                        )}

                        {/* Thumbs Up */}
                        <button
                          onClick={() => handleFeedback(msg.id, 'liked')}
                          className={`p-1 rounded hover:bg-black/5 transition-colors ${
                            feedbackState[msg.id] === 'liked' ? 'text-emerald-600 bg-emerald-50' : 'hover:text-[#24110A]'
                          }`}
                          title="Good response"
                        >
                          <ThumbsUp className="w-3.5 h-3.5" />
                        </button>

                        {/* Thumbs Down */}
                        <button
                          onClick={() => handleFeedback(msg.id, 'disliked')}
                          className={`p-1 rounded hover:bg-black/5 transition-colors ${
                            feedbackState[msg.id] === 'disliked' ? 'text-rose-600 bg-rose-50' : 'hover:text-[#24110A]'
                          }`}
                          title="Bad response"
                        >
                          <ThumbsDown className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}

        {/* Loading Spinner Indicator (Before first token arrives) */}
        {isSending && !isStreaming && (
          <div className="flex items-center gap-3 max-w-3xl mx-auto">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-brand-600 to-brand-500 text-white flex items-center justify-center shrink-0 shadow-2xs">
              <Bot className="w-4 h-4" />
            </div>
            <div className="p-3.5 rounded-2xl bg-white border border-[#FAD5C0] flex items-center gap-2 shadow-xs">
              <div className="w-2 h-2 rounded-full bg-brand-500 animate-bounce" />
              <div className="w-2 h-2 rounded-full bg-brand-500 animate-bounce [animation-delay:0.2s]" />
              <div className="w-2 h-2 rounded-full bg-brand-500 animate-bounce [animation-delay:0.4s]" />
              <span className="text-xs text-[#6B3B2B] ml-2 font-semibold">Analyzing form records...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* -------------------------------------------------------------
          Floating "Scroll to Bottom" Button
          ------------------------------------------------------------- */}
      {showScrollBottom && (
        <button
          onClick={() => scrollToBottom('smooth')}
          className="absolute bottom-28 right-6 z-20 p-2.5 rounded-full bg-white hover:bg-orange-50 text-[#24110A] border border-[#FAD5C0] shadow-md transition-all animate-in fade-in zoom-in-90 hover:scale-105"
          title="Scroll to latest message"
        >
          <ArrowDown className="w-4 h-4 text-brand-600" />
        </button>
      )}

      {/* -------------------------------------------------------------
          Stop Generating Floating Banner (During streaming)
          ------------------------------------------------------------- */}
      {isStreaming && (
        <div className="absolute bottom-24 left-1/2 -translate-x-1/2 z-20">
          <button
            onClick={stopGenerating}
            className="flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-neutral-300 text-neutral-800 text-xs font-bold shadow-md hover:bg-neutral-50 transition-all active:scale-95"
          >
            <Square className="w-3.5 h-3.5 fill-current text-rose-600" />
            <span>Stop generating</span>
          </button>
        </div>
      )}

      {/* -------------------------------------------------------------
          Suggested Quick Chips (Above input)
          ------------------------------------------------------------- */}
      {dynamicPrompts.length > 0 && messages.length > 0 && (
        <div className="px-3 sm:px-5 py-2 border-t border-[#FDE4D7] bg-[#FFF7F2] flex items-center gap-1.5 sm:gap-2 overflow-x-auto no-scrollbar touch-scroll text-xs shrink-0">
          <span className="text-[10px] sm:text-[11px] text-[#6B3B2B] font-bold shrink-0">Suggested:</span>
          {dynamicPrompts.slice(0, 5).map((chip, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(chip)}
              disabled={isSending || isStreaming}
              className="px-2.5 py-1 rounded-lg bg-white hover:bg-[#FFF2EB] text-[#3B1F14] hover:text-[#24110A] border border-[#FAD5C0] whitespace-nowrap transition-colors font-semibold shadow-2xs shrink-0 text-xs disabled:opacity-50"
            >
              {chip}
            </button>
          ))}
        </div>
      )}

      {/* -------------------------------------------------------------
          ChatGPT Multiline Input Card & Voice Dictation
          ------------------------------------------------------------- */}
      <div className="p-3 sm:p-4 border-t border-[#FDE4D7] bg-[#FFF7F2] shrink-0">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="max-w-3xl mx-auto"
        >
          <div className="relative flex items-end bg-white border border-[#FAD5C0] focus-within:border-brand-500 focus-within:ring-2 focus-within:ring-brand-500/20 rounded-2xl sm:rounded-3xl shadow-sm transition-all p-1.5 sm:p-2">
            
            {/* Microphone Voice Dictation Button */}
            <button
              type="button"
              onClick={toggleVoiceInput}
              className={`p-2 rounded-xl transition-all shrink-0 ${
                isListening
                  ? 'bg-rose-600 text-white animate-pulse shadow-md shadow-rose-500/30'
                  : 'text-[#8C5D4B] hover:text-[#24110A] hover:bg-orange-50'
              }`}
              title={isListening ? "Listening... click to stop" : "Voice input (Speech to text)"}
            >
              {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>

            {/* Multiline Expandable Textarea */}
            <textarea
              ref={textareaRef}
              rows={1}
              value={inputValue}
              onChange={handleInputChange}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder={isListening ? "Listening... speak now" : "Ask anything about this form (Shift + Enter for new line)..."}
              className="flex-1 min-w-0 bg-transparent px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm text-[#24110A] placeholder-[#8C5D4B] focus:outline-none resize-none max-h-[160px] leading-relaxed"
            />

            {/* Stop or Send Action Button */}
            {isStreaming ? (
              <button
                type="button"
                onClick={stopGenerating}
                className="p-2 sm:p-2.5 rounded-xl bg-neutral-900 hover:bg-neutral-800 text-white shadow-sm transition-all active:scale-95 shrink-0"
                title="Stop generating"
              >
                <Square className="w-4 h-4 fill-current text-white" />
              </button>
            ) : (
              <button
                type="submit"
                disabled={!inputValue.trim() || isSending}
                className="p-2 sm:p-2.5 rounded-xl sm:rounded-2xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 disabled:opacity-30 disabled:hover:from-brand-600 disabled:hover:to-brand-500 text-white shadow-md shadow-brand-500/20 transition-all active:scale-95 shrink-0 cursor-pointer disabled:cursor-not-allowed"
                aria-label="Send prompt"
              >
                {isSending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </button>
            )}
          </div>

          {/* Bottom Disclaimer Footer (like ChatGPT) */}
          <div className="mt-1.5 text-center">
            <p className="text-[10px] text-[#8C5D4B] font-medium">
              FormMind AI can make mistakes. All responses are verified against raw respondent submissions.
            </p>
          </div>
        </form>
      </div>

    </div>
  );
};
