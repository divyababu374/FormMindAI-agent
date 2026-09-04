import React from 'react';
import { useForm } from '../context/FormContext';
import { 
  LayoutDashboard, 
  HelpCircle, 
  BarChart3, 
  Sparkles, 
  Table as TableIcon, 
  MessageSquareText, 
  FileText, 
  Image as ImageIcon,
  CheckCircle,
  ExternalLink,
  Calendar,
  Layers,
  FileSpreadsheet
} from 'lucide-react';
import { Badge } from './common/Badge';
import { AttachResponsesModal } from './AttachResponsesModal';
import { OverviewTab } from './tabs/OverviewTab';
import { QuestionsTab } from './tabs/QuestionsTab';
import { ChartsTab } from './tabs/ChartsTab';
import { InsightsTab } from './tabs/InsightsTab';
import { ResponsesTab } from './tabs/ResponsesTab';
import { AIChatTab } from './tabs/AIChatTab';
import { ReportsTab } from './tabs/ReportsTab';
import { InfographicTab } from './tabs/InfographicTab';

export const Dashboard = () => {
  const { 
    currentForm, 
    activeTab, 
    setActiveTab, 
    syncCurrentForm, 
    googleStatus, 
    setIsGoogleModalOpen,
    isAttachModalOpen,
    setIsAttachModalOpen 
  } = useForm();
  const [isSyncing, setIsSyncing] = React.useState(false);


  if (!currentForm) return null;

  const handleSync = async () => {
    try {
      setIsSyncing(true);
      await syncCurrentForm();
    } catch (e) {
      console.error(e);
    } finally {
      setIsSyncing(false);
    }
  };

  const isZeroResponses = currentForm.total_responses_count === 0;
  const isUnauthorized = currentForm.response_access_status === 'unauthorized';

  const tabs = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'questions', label: 'Questions', icon: HelpCircle, badge: currentForm.questions_count },
    { id: 'charts', label: 'Charts Gallery', icon: BarChart3 },
    { id: 'insights', label: 'AI Insights', icon: Sparkles },
    { id: 'responses', label: 'Data Grid', icon: TableIcon, badge: currentForm.total_responses_count },
    { id: 'chat', label: 'AI Chat', icon: MessageSquareText, highlight: true },
    { id: 'reports', label: 'Reports & Exports', icon: FileText },
    { id: 'infographic', label: 'Infographic', icon: ImageIcon },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      {/* Form Top Banner */}
      <div className="p-6 rounded-3xl bg-white border border-[#FAD5C0] shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-xl sm:text-2xl font-black text-[#24110A] tracking-tight">
              {currentForm.title}
            </h1>
            <Badge variant={isUnauthorized ? "yellow" : "blue"}>
              {isUnauthorized ? "Structure Only" : "Verified Ingestion"}
            </Badge>
            <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${
              currentForm.source_type === 'microsoft_form'
                ? 'bg-sky-50 text-sky-900 border-sky-300'
                : 'bg-[#FFF2EB] text-[#4A2416] border-[#FAD5C0]'
            }`}>
              Source: {
                currentForm.source_type === 'microsoft_form'
                  ? 'Microsoft Form'
                  : currentForm.source_type === 'google_form'
                  ? 'Google Form'
                  : currentForm.source_type === 'google_sheet'
                  ? 'Google Sheet'
                  : currentForm.source_type
              }
            </span>
          </div>
          {currentForm.description && (
            <p className="text-xs text-[#522A1A] font-medium mt-1 max-w-2xl line-clamp-2">
              {currentForm.description}
            </p>
          )}

          <div className="flex flex-wrap items-center gap-4 text-xs text-[#6B3B2B] mt-3 font-medium">
            <span className="flex items-center gap-1.5 font-bold text-[#24110A]">
              <span className={`w-2 h-2 rounded-full ${isZeroResponses ? 'bg-amber-500' : 'bg-emerald-500'}`} />
              <span>{currentForm.total_responses_count} Verified Submissions</span>
            </span>
            <span>•</span>
            <span>{currentForm.questions_count} Questions</span>
            <span>•</span>
            <span>Completion: <strong className="text-[#24110A] font-bold">{currentForm.completion_rate}</strong></span>
            {currentForm.last_synced_at && (
              <>
                <span>•</span>
                <span>Synced: {new Date(currentForm.last_synced_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
              </>
            )}
            {currentForm.source_url && (
              <>
                <span>•</span>
                <a
                  href={currentForm.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-brand-700 hover:text-brand-800 font-bold flex items-center gap-1 transition-colors"
                >
                  <span>View Source Form</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </>
            )}
          </div>
        </div>

        {/* Action Controls: Sync, Attach & Chat */}
        <div className="flex items-center gap-2.5 shrink-0 flex-wrap sm:flex-nowrap">
          <button
            onClick={() => setIsAttachModalOpen(true)}
            className="flex items-center gap-2 px-3.5 py-2.5 rounded-2xl bg-emerald-50 hover:bg-emerald-100 border border-emerald-300 text-emerald-900 text-xs font-bold shadow-sm transition-all active:scale-95"
            title="Attach linked Google Sheet or upload responses CSV"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-700" />
            <span>Attach Responses / Sheet</span>
          </button>

          {currentForm.source_url && (
            <button
              onClick={handleSync}
              disabled={isSyncing}
              className="flex items-center gap-2 px-3.5 py-2.5 rounded-2xl bg-[#FFF2EB] hover:bg-[#FFE6D9] border border-[#FAD5C0] text-[#3B1F14] text-xs font-bold shadow-sm transition-all active:scale-95 disabled:opacity-50"
              title="Fetch newly submitted responses from Google"
            >
              <Layers className={`w-3.5 h-3.5 ${isSyncing ? 'animate-spin text-brand-600' : 'text-brand-700'}`} />
              <span>{isSyncing ? 'Syncing...' : 'Sync Latest Responses'}</span>
            </button>
          )}

          {activeTab !== 'chat' && (
            <button
              onClick={() => setActiveTab('chat')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 text-white text-xs font-bold shadow-md shadow-brand-500/25 transition-all active:scale-95"
            >
              <MessageSquareText className="w-4 h-4" />
              <span>Chat with this Form</span>
            </button>
          )}
        </div>
      </div>

      {/* Truthful Zero-Response or Unauthorized Banner */}
      {isZeroResponses && (
        <div className={`p-4 rounded-2xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3.5 ${
          isUnauthorized 
            ? 'bg-amber-50 border-amber-300 text-amber-950 font-medium' 
            : 'bg-orange-50 border-orange-300 text-orange-950 font-medium'
        }`}>
          <div className="flex items-start gap-3.5">
            <CheckCircle className={`w-5 h-5 shrink-0 mt-0.5 ${isUnauthorized ? 'text-amber-600' : 'text-brand-600'}`} />
            <div>
              <h4 className="text-sm font-bold">
                {isUnauthorized ? "Private / Restricted Survey Link" : "Form Structure Ready"}
              </h4>
              <p className="text-xs mt-0.5">
                {isUnauthorized 
                  ? "We parsed the form questions, but response data is restricted. Attach your responses sheet to unlock full analytics."
                  : "We have mapped all form questions. Attach a Google Sheet or upload responses to generate full analysis."}
              </p>
            </div>
          </div>
          <button
            onClick={() => setIsAttachModalOpen(true)}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 text-white text-xs font-bold shadow-md shrink-0 transition-all"
          >
            Attach Responses Sheet
          </button>
        </div>
      )}

      {/* Modern Horizontal Navigation Tabs */}
      <div className="flex items-center gap-1.5 p-1.5 rounded-2xl bg-white border border-[#FAD5C0] shadow-sm overflow-x-auto">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all duration-200 ${
                isActive
                  ? 'bg-gradient-to-r from-brand-600 to-brand-500 text-white shadow-sm shadow-brand-500/20'
                  : tab.highlight
                  ? 'text-brand-800 bg-orange-100/70 hover:bg-orange-100 border border-orange-200'
                  : 'text-[#6B3B2B] hover:text-[#24110A] hover:bg-[#FFF2EB]'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {tab.badge !== undefined && (
                <span className={`px-1.5 py-0.5 rounded-md text-[10px] font-bold ${
                  isActive ? 'bg-brand-700 text-white' : 'bg-[#FFF2EB] text-[#522A1A]'
                }`}>
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab Views */}
      <div className="animate-in fade-in duration-200">
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'questions' && <QuestionsTab />}
        {activeTab === 'charts' && <ChartsTab />}
        {activeTab === 'insights' && <InsightsTab />}
        {activeTab === 'responses' && <ResponsesTab />}
        {activeTab === 'chat' && <AIChatTab />}
        {activeTab === 'reports' && <ReportsTab />}
        {activeTab === 'infographic' && <InfographicTab />}
      </div>

      {/* Modal for Attaching Google Sheet or Uploading CSV Responses */}
      <AttachResponsesModal 
        isOpen={isAttachModalOpen} 
        onClose={() => setIsAttachModalOpen(false)} 
      />

    </div>
  );
};

