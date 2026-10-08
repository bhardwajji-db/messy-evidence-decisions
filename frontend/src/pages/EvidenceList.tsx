import React, { useState, useEffect } from 'react';
import {
  FileText,
  Camera,
  Mic,
  MessageSquare,
  FileCheck2,
  Search,
  ExternalLink,
  RefreshCw,
  FolderOpen,
  ArrowRight,
  X,
  Hash,
  MapPin,
  User,
  Eye
} from 'lucide-react';
import { Evidence } from '../types';
import { api } from '../api/client';

interface EvidenceListProps {
  onSelectCase: (caseId: string) => void;
}

export const EvidenceList: React.FC<EvidenceListProps> = ({ onSelectCase }) => {
  const [evidenceList, setEvidenceList] = useState<Evidence[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [inspectingEvidence, setInspectingEvidence] = useState<Evidence | null>(null);

  const fetchEvidence = async () => {
    setIsLoading(true);
    try {
      const data = await api.getAllEvidence();
      setEvidenceList(data);
    } catch (err) {
      console.error('Failed fetching all evidence:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEvidence();
  }, []);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'IMAGE':
        return <Camera className="w-3.5 h-3.5 text-emerald-400" />;
      case 'PDF':
      case 'DOCUMENT':
        return <FileCheck2 className="w-3.5 h-3.5 text-rose-400" />;
      case 'AUDIO':
        return <Mic className="w-3.5 h-3.5 text-violet-400" />;
      case 'TEXT':
        return <MessageSquare className="w-3.5 h-3.5 text-amber-400" />;
      default:
        return <FileText className="w-3.5 h-3.5 text-slate-400" />;
    }
  };

  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'IMAGE':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'PDF':
      case 'DOCUMENT':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'AUDIO':
        return 'bg-violet-500/10 text-violet-400 border-violet-500/30';
      case 'TEXT':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  const filteredItems = evidenceList.filter((ev) => {
    const matchesType = selectedType === 'ALL' || ev.source_type === selectedType;
    const query = searchQuery.toLowerCase().trim();
    const matchesSearch =
      !query ||
      ev.id.toLowerCase().includes(query) ||
      ev.case_id.toLowerCase().includes(query) ||
      ev.file_name.toLowerCase().includes(query) ||
      (ev.location && ev.location.toLowerCase().includes(query));
    return matchesType && matchesSearch;
  });

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">
            Master Evidence Repository
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Browse and inspect all multimodal evidence files ingested across municipal verification cases.
          </p>
        </div>

        <button
          onClick={fetchEvidence}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition"
        >
          <RefreshCw className="w-3.5 h-3.5 text-sky-400" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-3">
        {/* Search */}
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by Evidence ID, Case ID, filename, or location..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
        </div>

        {/* Type Filter Buttons */}
        <div className="flex items-center space-x-1.5 overflow-x-auto">
          {['ALL', 'IMAGE', 'PDF', 'AUDIO', 'TEXT'].map((type) => (
            <button
              key={type}
              onClick={() => setSelectedType(type)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition ${
                selectedType === type
                  ? 'bg-sky-600 text-white'
                  : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {type === 'IMAGE' ? '📸 IMAGE' : type === 'PDF' ? '📄 PDF' : type === 'AUDIO' ? '🎙️ AUDIO' : type === 'TEXT' ? '📝 TEXT' : 'ALL'}
            </button>
          ))}
        </div>
      </div>

      {/* Evidence Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        {isLoading ? (
          <div className="py-20 text-center">
            <RefreshCw className="w-6 h-6 text-sky-400 animate-spin mx-auto mb-2" />
            <p className="text-xs text-slate-400 font-mono">Loading evidence items...</p>
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="py-20 text-center space-y-2">
            <FileText className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-sm text-slate-400">No evidence items match your filters.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="p-3.5">Evidence ID</th>
                  <th className="p-3.5">Case ID</th>
                  <th className="p-3.5">Type</th>
                  <th className="p-3.5">File Name</th>
                  <th className="p-3.5">Location</th>
                  <th className="p-3.5">Upload Date</th>
                  <th className="p-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {filteredItems.map((ev) => (
                  <tr
                    key={ev.id}
                    onClick={() => setInspectingEvidence(ev)}
                    className="hover:bg-slate-800/50 cursor-pointer transition group"
                  >
                    <td className="p-3.5 font-bold text-sky-400 flex items-center space-x-1.5">
                      <span>{ev.id}</span>
                    </td>
                    <td className="p-3.5 text-slate-300 font-semibold">
                      <span className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700/80 text-sky-300">
                        {ev.case_id}
                      </span>
                    </td>
                    <td className="p-3.5">
                      <span className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-bold border ${getTypeBadge(ev.source_type)}`}>
                        {getTypeIcon(ev.source_type)}
                        <span>{ev.source_type}</span>
                      </span>
                    </td>
                    <td className="p-3.5 text-slate-200 max-w-[200px] truncate font-sans">
                      {ev.file_name}
                    </td>
                    <td className="p-3.5 text-slate-400 font-sans">
                      {ev.location || '—'}
                    </td>
                    <td className="p-3.5 text-slate-400 text-[11px]">
                      {ev.timestamp ? ev.timestamp.slice(0, 10) : '—'}
                    </td>
                    <td className="p-3.5 text-right font-sans">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setInspectingEvidence(ev);
                          }}
                          className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
                          title="Inspect Evidence Media & Metadata"
                        >
                          <Eye className="w-3 h-3 text-sky-400" />
                          <span>Inspect</span>
                        </button>

                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectCase(ev.case_id);
                          }}
                          className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-sky-500/10 text-sky-400 hover:bg-sky-500/20 border border-sky-500/30 transition group-hover:border-sky-400"
                        >
                          <span>View Case</span>
                          <ArrowRight className="w-3 h-3" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Quick Evidence Inspection Modal */}
      {inspectingEvidence && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
              <div className="flex items-center space-x-2">
                <span className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded text-xs font-bold border ${getTypeBadge(inspectingEvidence.source_type)}`}>
                  {getTypeIcon(inspectingEvidence.source_type)}
                  <span>{inspectingEvidence.source_type}</span>
                </span>
                <span className="text-sm font-bold text-white font-mono">{inspectingEvidence.id}</span>
              </div>

              <div className="flex items-center space-x-2">
                <a
                  href={api.getEvidenceFileUrl(inspectingEvidence.id)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-1.5 rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:text-white text-xs flex items-center space-x-1"
                  title="Open Raw File"
                >
                  <ExternalLink className="w-3.5 h-3.5 text-sky-400" />
                  <span className="text-xs">Raw File</span>
                </a>
                <button
                  onClick={() => setInspectingEvidence(null)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="p-5 overflow-y-auto space-y-4">
              <div>
                <h3 className="text-base font-bold text-white mb-1">{inspectingEvidence.file_name}</h3>
                <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400 font-mono">
                  <span className="flex items-center space-x-1">
                    <Hash className="w-3.5 h-3.5 text-slate-500" />
                    <span>{inspectingEvidence.file_hash}</span>
                  </span>
                  {inspectingEvidence.location && (
                    <span className="flex items-center space-x-1 text-slate-300">
                      <MapPin className="w-3.5 h-3.5 text-slate-500" />
                      <span>{inspectingEvidence.location}</span>
                    </span>
                  )}
                  {inspectingEvidence.uploader && (
                    <span className="flex items-center space-x-1">
                      <User className="w-3.5 h-3.5 text-slate-500" />
                      <span>{inspectingEvidence.uploader}</span>
                    </span>
                  )}
                </div>
              </div>

              {/* Media Preview Section */}
              {inspectingEvidence.source_type === 'IMAGE' && (
                <div className="rounded-xl overflow-hidden bg-slate-950 border border-slate-800 p-2 flex items-center justify-center">
                  <img
                    src={api.getEvidenceFileUrl(inspectingEvidence.id)}
                    alt={inspectingEvidence.file_name}
                    className="max-h-72 object-contain rounded-lg"
                  />
                </div>
              )}

              {inspectingEvidence.source_type === 'AUDIO' && (
                <div className="p-4 rounded-xl bg-violet-950/30 border border-violet-800/40 space-y-3">
                  <div className="flex items-center space-x-2 text-xs text-violet-300 font-mono font-semibold">
                    <Mic className="w-4 h-4 text-violet-400 animate-pulse" />
                    <span>Citizen Audio Recording</span>
                  </div>
                  <audio
                    controls
                    className="w-full"
                    src={api.getEvidenceFileUrl(inspectingEvidence.id)}
                  />
                  {inspectingEvidence.raw_text && (
                    <div className="p-3 rounded bg-slate-950 border border-slate-800 text-xs text-slate-300 font-mono">
                      <span className="text-[10px] text-violet-400 font-bold uppercase block mb-1">
                        Speech-To-Text Transcription:
                      </span>
                      "{inspectingEvidence.raw_text}"
                    </div>
                  )}
                </div>
              )}

              {(inspectingEvidence.source_type === 'PDF' || inspectingEvidence.source_type === 'DOCUMENT') && (
                <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-800/30 space-y-3">
                  <div className="flex items-center space-x-2 text-xs text-rose-300 font-mono font-bold">
                    <FileCheck2 className="w-4 h-4 text-rose-400" />
                    <span>Official Administrative Order PDF</span>
                  </div>
                  {inspectingEvidence.raw_text && (
                    <div className="p-3 rounded bg-slate-950 border border-slate-800 text-xs text-slate-300 font-mono whitespace-pre-wrap">
                      <span className="text-[10px] text-rose-400 font-bold uppercase block mb-1">
                        Parsed Text & Fields:
                      </span>
                      {inspectingEvidence.raw_text}
                    </div>
                  )}
                </div>
              )}

              {inspectingEvidence.source_type === 'TEXT' && inspectingEvidence.raw_text && (
                <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-800/30 space-y-2">
                  <div className="flex items-center space-x-2 text-xs text-amber-300 font-mono font-bold">
                    <MessageSquare className="w-4 h-4 text-amber-400" />
                    <span>Citizen Grievance Log</span>
                  </div>
                  <div className="p-3 rounded bg-slate-950 border border-slate-800 text-xs text-slate-300 font-mono whitespace-pre-wrap">
                    {inspectingEvidence.raw_text}
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 border-t border-slate-800 bg-slate-950 flex items-center justify-between">
              <span className="text-xs font-mono text-slate-500">
                Case: <strong className="text-sky-400">{inspectingEvidence.case_id}</strong>
              </span>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setInspectingEvidence(null)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:text-white"
                >
                  Close
                </button>
                <button
                  onClick={() => {
                    const cid = inspectingEvidence.case_id;
                    setInspectingEvidence(null);
                    onSelectCase(cid);
                  }}
                  className="flex items-center space-x-1.5 px-4 py-2 rounded-lg text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white shadow-md shadow-sky-600/20"
                >
                  <span>Go to Case Analysis</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

