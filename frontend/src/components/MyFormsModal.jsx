import React, { useState } from 'react';
import { useForm } from '../context/FormContext';
import { 
  X, 
  Trash2, 
  ArrowRight, 
  FileText, 
  Calendar, 
  Users, 
  AlertTriangle,
  Sparkles
} from 'lucide-react';
import { Badge } from './common/Badge';

export const MyFormsModal = () => {
  const {
    forms,
    currentForm,
    selectForm,
    deleteCurrentForm,
    isMyFormsModalOpen,
    setIsMyFormsModalOpen,
    setIsAnalyzeModalOpen
  } = useForm();

  const [deletingId, setDeletingId] = useState(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);

  if (!isMyFormsModalOpen) return null;

  const handleDelete = async (formId) => {
    setDeletingId(formId);
    try {
      await deleteCurrentForm(formId);
      setConfirmDeleteId(null);
      setDeletingId(null);
    } catch (err) {
      alert('Failed to delete form: ' + err.message);
      setDeletingId(null);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white border border-[#FAD5C0] rounded-3xl max-w-2xl w-full p-6 shadow-2xl relative overflow-hidden flex flex-col max-h-[85vh]">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#FDE4D7]">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-orange-100 text-brand-700 border border-orange-200">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-black text-[#24110A]">My Analyzed Forms</h3>
              <p className="text-xs text-[#6B3B2B] font-medium">Switch datasets, manage survey sessions, or delete records</p>
            </div>
          </div>
          <button
            onClick={() => setIsMyFormsModalOpen(false)}
            className="p-1.5 rounded-lg text-[#6B3B2B] hover:text-[#24110A] hover:bg-[#FFF2EB] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Forms List */}
        <div className="flex-1 overflow-y-auto py-4 space-y-3 pr-1">
          {forms.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-sm text-[#6B3B2B] font-medium">No forms analyzed yet.</p>
              <button
                onClick={() => {
                  setIsMyFormsModalOpen(false);
                  setIsAnalyzeModalOpen(true);
                }}
                className="mt-4 px-4 py-2 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-600 text-white text-xs font-bold transition-all shadow-md shadow-brand-500/25"
              >
                Analyze Your First Form
              </button>
            </div>
          ) : (
            forms.map((f) => {
              const isActive = currentForm?.id === f.id;
              const isConfirming = confirmDeleteId === f.id;

              return (
                <div
                  key={f.id}
                  className={`p-4 rounded-2xl border transition-all ${
                    isActive
                      ? 'bg-orange-50/90 border-brand-500 shadow-md ring-2 ring-brand-500/30'
                      : 'bg-white border-[#FAD5C0] hover:border-brand-400 hover:bg-[#FFFAF7] shadow-sm'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-black text-[#24110A] truncate">{f.title}</h4>
                        {isActive && <Badge variant="peach">Active Form</Badge>}
                      </div>
                      <div className="flex flex-wrap items-center gap-3 text-xs text-[#6B3B2B] font-medium mt-2">
                        <span className="flex items-center gap-1">
                          <Users className="w-3.5 h-3.5 text-[#6B3B2B]" />
                          <span>{f.total_responses_count} responses</span>
                        </span>
                        <span>•</span>
                        <span>{f.questions_count} questions</span>
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3.5 h-3.5 text-[#6B3B2B]" />
                          <span>{new Date(f.created_at).toLocaleDateString()}</span>
                        </span>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 shrink-0">
                      {!isActive && (
                        <button
                          onClick={() => {
                            selectForm(f.id);
                            setIsMyFormsModalOpen(false);
                          }}
                          className="px-3 py-1.5 rounded-lg bg-[#FFF2EB] hover:bg-[#FFE6D9] text-xs font-bold text-[#3B1F14] border border-[#FAD5C0] transition-colors flex items-center gap-1.5 shadow-sm"
                        >
                          <span>Open</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      )}

                      {isConfirming ? (
                        <div className="flex items-center gap-1.5 bg-rose-50 p-1 rounded-lg border border-rose-300">
                          <button
                            disabled={deletingId === f.id}
                            onClick={() => handleDelete(f.id)}
                            className="px-2 py-1 bg-rose-600 hover:bg-rose-500 text-[11px] font-bold text-white rounded transition-colors"
                          >
                            Confirm Delete
                          </button>
                          <button
                            onClick={() => setConfirmDeleteId(null)}
                            className="px-2 py-1 bg-white hover:bg-[#FFF2EB] text-[11px] font-bold text-[#3B1F14] border border-[#FAD5C0] rounded transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setConfirmDeleteId(f.id)}
                          className="p-1.5 rounded-lg text-[#8C5D4B] hover:text-rose-600 hover:bg-rose-50 transition-colors"
                          title="Delete form and data"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-[#FDE4D7] flex items-center justify-between">
          <button
            onClick={() => {
              setIsMyFormsModalOpen(false);
              setIsAnalyzeModalOpen(true);
            }}
            className="flex items-center gap-1.5 text-xs font-bold text-brand-700 hover:text-brand-800 transition-colors"
          >
            <Sparkles className="w-4 h-4" />
            <span>Analyze Another Form</span>
          </button>
          <button
            onClick={() => setIsMyFormsModalOpen(false)}
            className="px-4 py-2 rounded-xl bg-[#FFF2EB] hover:bg-[#FFE6D9] text-xs font-bold text-[#3B1F14] border border-[#FAD5C0] transition-colors shadow-sm"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
};
