import React, { useState, useEffect } from 'react';
import { useForm } from '../../context/FormContext';
import { api } from '../../services/api';
import { 
  Search, 
  ChevronLeft, 
  ChevronRight, 
  Download, 
  SlidersHorizontal,
  Table as TableIcon,
  CheckCircle,
  Clock
} from 'lucide-react';
import { Badge } from '../common/Badge';

export const ResponsesTab = () => {
  const { currentForm } = useForm();
  const [data, setData] = useState({ items: [], columns: [], total: 0, total_pages: 1 });
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('');
  const [sortDesc, setSortDesc] = useState(false);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState('cleaned'); // 'cleaned' or 'raw'

  const fetchResponses = async () => {
    if (!currentForm) return;
    setLoading(true);
    try {
      const res = await api.getResponses(currentForm.id, page, pageSize, search, sortBy, sortDesc);
      setData(res);
    } catch (err) {
      console.error('Failed to load responses:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResponses();
  }, [currentForm?.id, page, pageSize, sortBy, sortDesc]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchResponses();
  };

  const handleSort = (key) => {
    if (sortBy === key) {
      setSortDesc(!sortDesc);
    } else {
      setSortBy(key);
      setSortDesc(false);
    }
    setPage(1);
  };

  return (
    <div className="space-y-4">
      
      {/* Search & Actions Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 p-4 rounded-2xl bg-white border border-[#FAD5C0] shadow-sm">
        
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-[#8C5D4B] absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search response answers..."
            className="w-full bg-white border border-[#FAD5C0] rounded-xl pl-9 pr-4 py-2 text-xs text-[#24110A] placeholder-[#8C5D4B] focus:outline-none focus:border-brand-500 shadow-inner"
          />
        </form>

        {/* View Mode & CSV Download */}
        <div className="flex items-center gap-2.5">
          <div className="flex items-center p-1 bg-[#FFF2EB] rounded-xl border border-[#FAD5C0] text-xs">
            <button
              onClick={() => setViewMode('cleaned')}
              className={`px-3 py-1 rounded-lg font-bold transition-colors ${
                viewMode === 'cleaned' ? 'bg-brand-600 text-white shadow-sm' : 'text-[#6B3B2B] hover:text-[#24110A]'
              }`}
            >
              Cleaned Data
            </button>
            <button
              onClick={() => setViewMode('raw')}
              className={`px-3 py-1 rounded-lg font-bold transition-colors ${
                viewMode === 'raw' ? 'bg-brand-600 text-white shadow-sm' : 'text-[#6B3B2B] hover:text-[#24110A]'
              }`}
            >
              Raw Original
            </button>
          </div>

          <a
            href={api.getExportCsvUrl(currentForm?.id)}
            download
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#FFF2EB] hover:bg-[#FFE6D9] text-[#3B1F14] text-xs font-bold border border-[#FAD5C0] transition-colors shadow-sm"
          >
            <Download className="w-3.5 h-3.5 text-brand-600" />
            <span>Export CSV</span>
          </a>
        </div>
      </div>

      {/* Data Table */}
      <div className="rounded-2xl border border-[#FAD5C0] bg-white overflow-hidden shadow-sm">
        <div className="overflow-x-auto max-h-[550px]">
          <table className="w-full text-left text-xs text-[#24110A]">
            <thead className="sticky top-0 z-10 bg-[#FFF2EB] border-b border-[#FAD5C0] text-[#8C2C08] uppercase font-bold">
              <tr>
                {data.columns?.map((col) => (
                  <th
                    key={col.key}
                    onClick={() => handleSort(col.key)}
                    className="px-4 py-3 cursor-pointer hover:text-brand-800 transition-colors whitespace-nowrap"
                  >
                    <div className="flex items-center gap-1.5">
                      <span>{col.label}</span>
                      {sortBy === col.key && (
                        <span className="text-brand-600 font-black">{sortDesc ? '▼' : '▲'}</span>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#FDE4D7]">
              {loading ? (
                <tr>
                  <td colSpan={data.columns?.length || 5} className="py-12 text-center text-[#6B3B2B] font-medium">
                    Loading records...
                  </td>
                </tr>
              ) : data.items?.length === 0 ? (
                <tr>
                  <td colSpan={data.columns?.length || 5} className="py-12 text-center text-[#6B3B2B] font-medium">
                    No responses matching query.
                  </td>
                </tr>
              ) : (
                data.items?.map((row) => {
                  const displayRow = viewMode === 'cleaned' ? row.cleaned_data : row.raw_data;
                  return (
                    <tr key={row.id} className="hover:bg-[#FFF8F4] transition-colors">
                      <td className="px-4 py-3 font-black text-[#24110A]">
                        #{row.response_number}
                      </td>
                      <td className="px-4 py-3 text-[#6B3B2B] font-medium whitespace-nowrap">
                        {row.submission_timestamp
                          ? new Date(row.submission_timestamp).toLocaleString()
                          : 'N/A'}
                      </td>
                      {data.columns?.slice(2).map((col) => {
                        const val = viewMode === 'cleaned' ? displayRow?.[col.key] : displayRow?.[col.label];
                        return (
                          <td key={col.key} className="px-4 py-3 max-w-xs truncate text-[#24110A] font-medium">
                            {Array.isArray(val) ? (
                              <div className="flex flex-wrap gap-1">
                                {val.map((item, idx) => (
                                  <Badge key={idx} variant="blue" className="text-[10px]">
                                    {item}
                                  </Badge>
                                ))}
                              </div>
                            ) : val !== null && val !== undefined ? (
                              String(val)
                            ) : (
                              <span className="text-[#8C5D4B] italic">null</span>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="p-4 border-t border-[#FDE4D7] bg-[#FFF7F2] flex items-center justify-between text-xs text-[#6B3B2B] font-medium">
          <div>
            Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, data.total)} of {data.total} responses
          </div>

          <div className="flex items-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(p => Math.max(1, p - 1))}
              className="p-1.5 rounded-lg bg-white hover:bg-[#FFF2EB] border border-[#FAD5C0] disabled:opacity-30 disabled:pointer-events-none text-[#24110A] transition-colors shadow-sm"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-bold text-[#24110A]">
              Page {page} of {data.total_pages}
            </span>
            <button
              disabled={page >= data.total_pages}
              onClick={() => setPage(p => Math.min(data.total_pages, p + 1))}
              className="p-1.5 rounded-lg bg-white hover:bg-[#FFF2EB] border border-[#FAD5C0] disabled:opacity-30 disabled:pointer-events-none text-[#24110A] transition-colors shadow-sm"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

    </div>
  );
};
