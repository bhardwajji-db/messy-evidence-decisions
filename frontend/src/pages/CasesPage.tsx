import React, { useState } from 'react';
import {
  FolderOpen,
  Search,
  PlusCircle,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  ShieldAlert,
  ArrowRight,
  Filter
} from 'lucide-react';
import { Case } from '../types';

interface CasesPageProps {
  cases: Case[];
  onSelectCase: (caseId: string) => void;
  onNavigateCreate: () => void;
}

export const CasesPage: React.FC<CasesPageProps> = ({
  cases,
  onSelectCase,
  onNavigateCreate,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<string>('ALL');

  const getStatusBadge = (decisionOrStatus?: string) => {
    switch (decisionOrStatus) {
      case 'CONFLICT':
        return {
          bg: 'bg-red-500/10 border-red-500/30 text-red-400',
          icon: AlertTriangle,
          text: 'CONFLICT',
        };
      case 'VERIFIED':
        return {
          bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
          icon: CheckCircle2,
          text: 'VERIFIED',
        };
      case 'PARTIALLY VERIFIED':
        return {
          bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
          icon: ShieldAlert,
          text: 'PARTIALLY VERIFIED',
        };
      case 'INSUFFICIENT EVIDENCE':
        return {
          bg: 'bg-slate-500/10 border-slate-500/30 text-slate-400',
          icon: HelpCircle,
          text: 'INSUFFICIENT EVIDENCE',
        };
      default:
        return {
          bg: 'bg-sky-500/10 border-sky-500/30 text-sky-400',
          icon: FolderOpen,
          text: decisionOrStatus || 'NEW',
        };
    }
  };

  const getRiskBadge = (severity?: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'text-red-400 border-red-500/40 bg-red-500/10';
      case 'HIGH':
        return 'text-orange-400 border-orange-500/40 bg-orange-500/10';
      case 'MEDIUM':
        return 'text-amber-400 border-amber-500/40 bg-amber-500/10';
      case 'LOW':
        return 'text-emerald-400 border-emerald-500/40 bg-emerald-500/10';
      default:
        return 'text-slate-400 border-slate-700 bg-slate-800';
    }
  };

  const filterOptions = [
    'ALL',
    'CONFLICT',
    'VERIFIED',
    'PARTIALLY VERIFIED',
    'INSUFFICIENT EVIDENCE',
  ];

  const filteredCases = cases.filter((c) => {
    const dec = c.decision || c.status;
    const matchesFilter = selectedFilter === 'ALL' || dec === selectedFilter;
    const query = searchQuery.toLowerCase().trim();
    const matchesSearch =
      !query ||
      c.id.toLowerCase().includes(query) ||
      c.title.toLowerCase().includes(query) ||
      (c.location && c.location.toLowerCase().includes(query));
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">
            Municipal Inspection Cases
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Complete registry of civil infrastructure dossiers, verification determinations, and risk ratings.
          </p>
        </div>

        <button
          onClick={onNavigateCreate}
          className="flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white shadow-lg shadow-sky-600/20 transition"
        >
          <PlusCircle className="w-4 h-4" />
          <span>New Case Dossier</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-3">
        {/* Search */}
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by Case ID, title, or location..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
        </div>

        {/* Filter Buttons */}
        <div className="flex items-center space-x-1.5 overflow-x-auto">
          {filterOptions.map((filter) => (
            <button
              key={filter}
              onClick={() => setSelectedFilter(filter)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition whitespace-nowrap ${
                selectedFilter === filter
                  ? 'bg-sky-600 text-white shadow-sm'
                  : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {filter}
            </button>
          ))}
        </div>
      </div>

      {/* Cases Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        {filteredCases.length === 0 ? (
          <div className="py-20 text-center space-y-3">
            <FolderOpen className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-sm text-slate-400">No cases match the selected filter.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="p-3.5">Case ID</th>
                  <th className="p-3.5">Title</th>
                  <th className="p-3.5">Location</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5">Risk</th>
                  <th className="p-3.5">Evidence Count</th>
                  <th className="p-3.5">Created At</th>
                  <th className="p-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {filteredCases.map((c) => {
                  const statusInfo = getStatusBadge(c.decision || c.status);
                  const StatusIcon = statusInfo.icon;
                  return (
                    <tr
                      key={c.id}
                      onClick={() => onSelectCase(c.id)}
                      className="hover:bg-slate-800/50 cursor-pointer transition group"
                    >
                      <td className="p-3.5 font-bold text-sky-400">
                        {c.id}
                      </td>
                      <td className="p-3.5 font-sans font-medium text-white max-w-[220px] truncate">
                        {c.title}
                      </td>
                      <td className="p-3.5 text-slate-400 font-sans">
                        {c.location || '—'}
                      </td>
                      <td className="p-3.5">
                        <span className={`inline-flex items-center space-x-1.5 px-2 py-0.5 rounded text-[10px] font-bold border ${statusInfo.bg}`}>
                          <StatusIcon className="w-3 h-3" />
                          <span>{statusInfo.text}</span>
                        </span>
                      </td>
                      <td className="p-3.5">
                        {c.severity ? (
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getRiskBadge(c.severity)}`}>
                            {c.severity}
                          </span>
                        ) : (
                          <span className="text-slate-500">—</span>
                        )}
                      </td>
                      <td className="p-3.5 text-slate-300 font-semibold">
                        {c.evidence_count ?? 0} Items
                      </td>
                      <td className="p-3.5 text-slate-400 text-[11px]">
                        {c.created_at ? c.created_at.slice(0, 10) : '—'}
                      </td>
                      <td className="p-3.5 text-right font-sans">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectCase(c.id);
                          }}
                          className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-sky-500/10 text-sky-400 hover:bg-sky-500/20 border border-sky-500/30 transition group-hover:border-sky-400"
                        >
                          <span>Open</span>
                          <ArrowRight className="w-3 h-3" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
