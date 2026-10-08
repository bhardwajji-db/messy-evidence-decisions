import React, { useState } from 'react';
import {
  GitCommit,
  GitMerge,
  ArrowDown,
  ArrowRight,
  AlertOctagon,
  CheckCircle,
  FileText,
  FileImage,
  Mic,
  MessageSquare,
  ExternalLink,
  Layers,
  ChevronRight,
  X
} from 'lucide-react';
import { Evidence, Claim, Relationship, Extraction } from '../types';
import { api } from '../api/client';

interface EvidenceTraceGraphProps {
  evidenceList: Evidence[];
  claims: Claim[];
  relationships: Relationship[];
  extractions: Extraction[];
}

export const EvidenceTraceGraph: React.FC<EvidenceTraceGraphProps> = ({
  evidenceList,
  claims,
  relationships,
  extractions,
}) => {
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);

  const selectedEvidence = evidenceList.find((e) => e.id === selectedEvidenceId);
  const selectedClaims = claims.filter((c) => c.evidence_id === selectedEvidenceId);
  const selectedExtractions = extractions.filter((x) => x.evidence_id === selectedEvidenceId);
  const relatedEdges = relationships.filter(
    (r) => r.source_evidence_id === selectedEvidenceId || r.target_evidence_id === selectedEvidenceId
  );

  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'IMAGE':
        return <FileImage className="w-4 h-4 text-emerald-400" />;
      case 'PDF':
      case 'DOCUMENT':
        return <FileText className="w-4 h-4 text-rose-400" />;
      case 'AUDIO':
        return <Mic className="w-4 h-4 text-violet-400" />;
      case 'TEXT':
        return <MessageSquare className="w-4 h-4 text-amber-400" />;
      default:
        return <FileText className="w-4 h-4 text-slate-400" />;
    }
  };

  const getNodeTypeInfo = (type: string) => {
    switch (type) {
      case 'IMAGE':
        return { label: '📸 IMAGE', badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' };
      case 'PDF':
      case 'DOCUMENT':
        return { label: '📄 PDF', badge: 'bg-rose-500/10 text-rose-400 border-rose-500/30' };
      case 'AUDIO':
        return { label: '🎙️ AUDIO', badge: 'bg-violet-500/10 text-violet-400 border-violet-500/30' };
      case 'TEXT':
        return { label: '📝 TEXT', badge: 'bg-amber-500/10 text-amber-400 border-amber-500/30' };
      default:
        return { label: '📄 TEXT', badge: 'bg-slate-500/10 text-slate-400 border-slate-500/30' };
    }
  };

  const getRelationshipBadge = (type: string) => {
    switch (type) {
      case 'CONTRADICTS':
        return 'bg-red-500/20 text-red-400 border-red-500/40 font-bold';
      case 'CORROBORATES':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/40 font-bold';
      case 'SUPPORTS':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40 font-bold';
      default:
        return 'bg-slate-500/20 text-slate-300 border-slate-500/40';
    }
  };

  return (
    <div className="space-y-6">
      {/* Visual Pipeline Trace Graph */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
          <div>
            <h3 className="font-semibold text-white text-sm flex items-center space-x-2">
              <GitMerge className="w-4 h-4 text-sky-400" />
              <span>Evidence Trace & Fusion Graph</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Click any evidence node to inspect original file, extracted claims, and decision causality.
            </p>
          </div>
          <span className="text-xs font-mono text-slate-500">
            {relationships.length} Relationship Edges
          </span>
        </div>

        {/* Trace Flowchart */}
        <div className="flex flex-col items-center space-y-4 py-2">
          {/* Level 1: Input Evidence Nodes */}
          <div className="w-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {evidenceList.map((ev) => {
              const evClaims = claims.filter((c) => c.evidence_id === ev.id);
              const isSelected = selectedEvidenceId === ev.id;
              const typeInfo = getNodeTypeInfo(ev.source_type);
              return (
                <div
                  key={ev.id}
                  onClick={() => setSelectedEvidenceId(isSelected ? null : ev.id)}
                  className={`p-3 rounded-xl border cursor-pointer transition flex flex-col justify-between ${
                    isSelected
                      ? 'bg-sky-950/40 border-sky-500 shadow-md shadow-sky-500/10'
                      : 'bg-slate-950/80 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="flex items-center space-x-1.5 font-mono text-xs font-bold text-slate-200">
                      {getSourceIcon(ev.source_type)}
                      <span>{ev.id}</span>
                    </span>
                    <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-bold border ${typeInfo.badge}`}>
                      {typeInfo.label}
                    </span>
                  </div>

                  <div className="text-[11px] text-slate-300 font-medium truncate mb-2">
                    {ev.file_name}
                  </div>

                  <div className="space-y-1 border-t border-slate-800/80 pt-2">
                    {evClaims.length > 0 ? (
                      evClaims.slice(0, 2).map((c) => (
                        <div key={c.id} className="text-[10px] font-mono text-sky-300 truncate">
                          • {c.attribute}: <span className="font-bold">{c.value}</span>
                        </div>
                      ))
                    ) : (
                      <span className="text-[10px] text-slate-500 font-mono">No claims extracted</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Level 1.5: Visual Relationship Graph Connectors (GAP 5) */}
          {relationships.length > 0 && (
            <div className="w-full bg-slate-950/90 border border-slate-800 rounded-xl p-4 my-2">
              <div className="flex items-center justify-between mb-3 border-b border-slate-800/80 pb-2">
                <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
                  <GitCommit className="w-4 h-4 text-sky-400" />
                  <span>Relationship Graph & Cross-Verification Vectors</span>
                </span>
                <span className="text-[11px] font-mono text-slate-400">
                  {relationships.length} active vectors
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                {relationships.map((rel, idx) => {
                  const srcEv = evidenceList.find(e => e.id === rel.source_evidence_id);
                  const tgtEv = evidenceList.find(e => e.id === rel.target_evidence_id);
                  const srcType = srcEv ? getNodeTypeInfo(srcEv.source_type).label : 'NODE';
                  const tgtType = tgtEv ? getNodeTypeInfo(tgtEv.source_type).label : 'NODE';
                  const isContradiction = rel.relationship_type === 'CONTRADICTS';
                  const isCorroboration = rel.relationship_type === 'CORROBORATES';
                  const isSupport = rel.relationship_type === 'SUPPORTS';

                  return (
                    <div
                      key={idx}
                      className={`p-3 rounded-lg border flex flex-col justify-between space-y-1.5 ${
                        isContradiction
                          ? 'bg-red-950/20 border-red-500/40'
                          : isCorroboration
                          ? 'bg-blue-950/20 border-blue-500/40'
                          : isSupport
                          ? 'bg-emerald-950/20 border-emerald-500/40'
                          : 'bg-slate-900 border-slate-800'
                      }`}
                    >
                      <div className="flex items-center justify-between text-xs font-mono flex-wrap gap-1">
                        <span className="font-bold text-slate-200">
                          {srcType} <span className="text-sky-300">{rel.source_evidence_id}</span>
                        </span>
                        {/* Colored arrow and label */}
                        <div className="flex items-center space-x-1 px-1.5 py-0.5 rounded font-black text-[11px] uppercase tracking-wider">
                          <span
                            className={
                              isContradiction
                                ? 'text-red-400 font-bold'
                                : isCorroboration
                                ? 'text-blue-400 font-bold'
                                : isSupport
                                ? 'text-emerald-400 font-bold'
                                : 'text-slate-400 font-bold'
                            }
                          >
                            ─── {rel.relationship_type} ───▶
                          </span>
                        </div>
                        <span className="font-bold text-slate-200">
                          {tgtType} <span className="text-sky-300">{rel.target_evidence_id}</span>
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 font-sans">
                        {rel.description}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Fusion Arrow */}
          <div className="flex flex-col items-center">
            <ArrowDown className="w-5 h-5 text-sky-400 animate-bounce" />
            <span className="text-[10px] font-mono tracking-widest uppercase text-sky-400 px-3 py-0.5 rounded-full bg-sky-950 border border-sky-800">
              Multimodal Evidence Fusion & Cross-Correlation
            </span>
          </div>

          {/* Level 2: Fusion Decision Outcome */}
          <div className="w-full max-w-xl p-4 rounded-xl border border-red-500/40 bg-red-950/20 text-center space-y-1">
            <div className="flex items-center justify-center space-x-2 text-red-400 font-bold text-sm">
              <AlertOctagon className="w-4 h-4" />
              <span>EVIDENCE CONFLICT DETECTED</span>
            </div>
            <p className="text-xs text-slate-300">
              Official completion records contradict physical ground photo & citizen voice reports.
            </p>
            <div className="pt-2 flex items-center justify-center space-x-3 text-xs font-mono">
              <span className="px-2 py-0.5 rounded bg-orange-500/20 border border-orange-500/30 text-orange-300 font-bold">
                SEVERITY: HIGH
              </span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
              <span className="px-2 py-0.5 rounded bg-sky-500/20 border border-sky-500/30 text-sky-300 font-bold">
                PHYSICAL INSPECTION REQUIRED
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Selected Evidence Deep-Dive Drawer / Card */}
      {selectedEvidence && (
        <div className="bg-slate-900 border border-sky-500/50 rounded-xl p-5 space-y-4 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2">
              <span className="p-1.5 rounded bg-slate-800 border border-slate-700">
                {getSourceIcon(selectedEvidence.source_type)}
              </span>
              <div>
                <h4 className="font-semibold text-white text-sm">
                  Inspection Deep-Dive: {selectedEvidence.id} ({selectedEvidence.file_name})
                </h4>
                <p className="text-xs text-slate-400 font-mono">
                  SHA-256: {selectedEvidence.file_hash}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <a
                href={api.getEvidenceFileUrl(selectedEvidence.id)}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700"
              >
                <ExternalLink className="w-3 h-3 text-sky-400" />
                <span>Open File</span>
              </a>
              <button
                onClick={() => setSelectedEvidenceId(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Rich Media Deep-Dive Preview */}
          {selectedEvidence.source_type === 'IMAGE' && (
            <div className="mb-4 rounded-xl overflow-hidden bg-slate-950 border border-slate-800 flex flex-col items-center justify-center p-2">
              <img
                src={api.getEvidenceFileUrl(selectedEvidence.id)}
                alt={selectedEvidence.file_name}
                className="max-h-64 object-contain rounded-lg shadow-lg"
                onError={(e) => {
                  const parent = (e.currentTarget.parentElement as HTMLElement);
                  if (parent) parent.style.display = 'none';
                }}
              />
            </div>
          )}

          {selectedEvidence.source_type === 'AUDIO' && (
            <div className="mb-4 p-3 rounded-xl bg-violet-950/30 border border-violet-800/40 space-y-2">
              <div className="flex items-center space-x-2 text-xs text-violet-300 font-mono font-semibold">
                <Mic className="w-4 h-4 text-violet-400 animate-pulse" />
                <span>Audio Player — Citizen Voice Recording</span>
              </div>
              <audio
                controls
                className="w-full"
                src={api.getEvidenceFileUrl(selectedEvidence.id)}
              />
              {selectedEvidence.raw_text && (
                <div className="p-2.5 rounded bg-slate-950 border border-slate-800 text-xs text-slate-300 font-mono">
                  <span className="text-[10px] text-violet-400 font-bold uppercase block mb-1">
                    faster-whisper Transcription:
                  </span>
                  "{selectedEvidence.raw_text}"
                </div>
              )}
            </div>
          )}

          {selectedEvidence.source_type === 'TEXT' && selectedEvidence.raw_text && (
            <div className="mb-4 p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[10px] text-amber-400 font-mono font-bold uppercase block mb-1">
                Citizen Grievance Text:
              </span>
              <p className="text-xs text-slate-300 font-mono whitespace-pre-wrap">
                {selectedEvidence.raw_text}
              </p>
            </div>
          )}

          {(selectedEvidence.source_type === 'PDF' || selectedEvidence.source_type === 'DOCUMENT') && (
            <div className="mb-4 p-3 rounded-xl bg-rose-950/20 border border-rose-800/30 flex items-center justify-between">
              <div className="flex items-center space-x-2.5 text-xs text-rose-300 font-mono">
                <FileText className="w-5 h-5 text-rose-400" />
                <div>
                  <div className="font-bold">Official Municipal Work Order Document</div>
                  <div className="text-[11px] text-slate-400">{selectedEvidence.file_name}</div>
                </div>
              </div>
              <a
                href={api.getEvidenceFileUrl(selectedEvidence.id)}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-mono font-semibold"
              >
                Inspect PDF Document
              </a>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Extracted Claims */}
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2">
              <span className="text-xs font-mono font-semibold text-sky-400 uppercase tracking-wider">
                Extracted Claims ({selectedClaims.length})
              </span>
              <div className="space-y-1.5">
                {selectedClaims.map((c) => (
                  <div
                    key={c.id}
                    className="p-2 rounded bg-slate-900/80 border border-slate-800 text-xs font-mono space-y-1"
                  >
                    <div className="flex justify-between text-slate-200 font-bold">
                      <span>{c.attribute}</span>
                      <span className="text-sky-300">"{c.value}"</span>
                    </div>
                    <div className="flex justify-between text-[11px] text-slate-400">
                      <span>Entity: {c.entity}</span>
                      <span>Confidence: {Math.round(c.confidence * 100)}%</span>
                    </div>
                    {c.location && (
                      <div className="text-[10px] text-slate-400">Location: {c.location}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Cross-Evidence Relationships */}
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2">
              <span className="text-xs font-mono font-semibold text-sky-400 uppercase tracking-wider">
                Active Relationship Edges ({relatedEdges.length})
              </span>
              <div className="space-y-1.5">
                {relatedEdges.map((rel, idx) => (
                  <div
                    key={idx}
                    className="p-2 rounded bg-slate-900/80 border border-slate-800 text-xs font-mono space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-slate-300">
                        {rel.source_evidence_id} → {rel.target_evidence_id}
                      </span>
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-bold border ${getRelationshipBadge(
                          rel.relationship_type
                        )}`}
                      >
                        {rel.relationship_type}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 font-sans">{rel.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Extracted Claims Master Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/40">
          <div>
            <h3 className="font-semibold text-white text-sm">Normalized Claims Schema</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Structured representations preserving original evidence ID provenance.
            </p>
          </div>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
            {claims.length} Claims
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-3">Claim ID</th>
                <th className="p-3">Source ID</th>
                <th className="p-3">Entity</th>
                <th className="p-3">Attribute</th>
                <th className="p-3">Value</th>
                <th className="p-3">Location</th>
                <th className="p-3">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {claims.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-4 text-center text-slate-500 font-sans">
                    No claims extracted yet. Run case analysis.
                  </td>
                </tr>
              ) : (
                claims.map((cl) => (
                  <tr key={cl.id} className="hover:bg-slate-800/40 transition">
                    <td className="p-3 font-bold text-sky-400">{cl.id}</td>
                    <td className="p-3 text-slate-200">{cl.evidence_id}</td>
                    <td className="p-3">{cl.entity}</td>
                    <td className="p-3 font-semibold text-white">{cl.attribute}</td>
                    <td className="p-3">
                      <span
                        className={`px-1.5 py-0.5 rounded font-bold ${
                          cl.value === 'completed'
                            ? 'bg-emerald-500/10 text-emerald-400'
                            : cl.value === 'true'
                            ? 'bg-red-500/10 text-red-400'
                            : 'bg-slate-800 text-slate-300'
                        }`}
                      >
                        {cl.value}
                      </span>
                    </td>
                    <td className="p-3 text-slate-400">{cl.location || '-'}</td>
                    <td className="p-3 text-slate-400">{Math.round(cl.confidence * 100)}%</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
