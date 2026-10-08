import React from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  FileQuestion,
  ShieldAlert,
  ArrowRight,
  Sparkles,
  FileText,
  UserCheck,
  Scale,
  Camera,
  Mic,
  FileCheck2,
  MessageSquare,
  GitCommit,
  Check,
  HelpCircle,
  ExternalLink
} from 'lucide-react';
import type { Decision, Case, Evidence, Relationship, Claim } from '../types';
import { api } from '../api/client';

interface AnalysisViewProps {
  currentCase: Case;
  decision?: Decision;
  evidenceList: Evidence[];
  relationships: Relationship[];
  claims?: Claim[];
  isAnalyzing: boolean;
  onRunAnalysis: () => void;
  onOpenReview: () => void;
  onOpenReport: () => void;
}

export const AnalysisView: React.FC<AnalysisViewProps> = ({
  currentCase,
  decision,
  evidenceList,
  relationships,
  claims = [],
  isAnalyzing,
  onRunAnalysis,
  onOpenReview,
  onOpenReport,
}) => {
  const getDecisionBadge = (state: string) => {
    switch (state) {
      case 'CONFLICT':
        return {
          bg: 'bg-red-500/10 border-red-500/30 text-red-400',
          badgeText: '⚠ EVIDENCE CONFLICT',
          icon: AlertTriangle,
        };
      case 'VERIFIED':
        return {
          bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
          badgeText: '✓ REPAIR VERIFIED',
          icon: CheckCircle2,
        };
      case 'PARTIALLY VERIFIED':
        return {
          bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
          badgeText: 'PARTIALLY VERIFIED',
          icon: ShieldAlert,
        };
      case 'INSUFFICIENT EVIDENCE':
      default:
        return {
          bg: 'bg-slate-500/10 border-slate-500/30 text-slate-400',
          badgeText: '? INSUFFICIENT EVIDENCE',
          icon: FileQuestion,
        };
    }
  };

  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'IMAGE':
        return <Camera className="w-4 h-4 text-emerald-400" />;
      case 'PDF':
      case 'DOCUMENT':
        return <FileCheck2 className="w-4 h-4 text-rose-400" />;
      case 'AUDIO':
        return <Mic className="w-4 h-4 text-violet-400" />;
      case 'TEXT':
        return <MessageSquare className="w-4 h-4 text-amber-400" />;
      default:
        return <FileText className="w-4 h-4 text-slate-400" />;
    }
  };

  const badge = decision ? getDecisionBadge(decision.decision) : null;
  const BadgeIcon = badge?.icon;

  return (
    <div className="space-y-6">
      {/* Top Controls Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-0.5">
          <div className="flex items-center space-x-2">
            <Scale className="w-5 h-5 text-sky-400" />
            <h3 className="font-semibold text-white text-sm">
              Multimodal Verification Dashboard
            </h3>
          </div>
          <p className="text-xs text-slate-400">
            Fuses images, official documents, voice complaints, and road markers into an explainable audit decision.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={onOpenReport}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-semibold bg-slate-800 text-slate-200 hover:bg-slate-700 border border-slate-700 transition"
          >
            <FileText className="w-3.5 h-3.5 text-sky-400" />
            <span>Generate Report</span>
          </button>

          <button
            onClick={onOpenReview}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-semibold bg-sky-500/10 text-sky-300 hover:bg-sky-500/20 border border-sky-500/30 transition"
          >
            <UserCheck className="w-3.5 h-3.5" />
            <span>Human Review</span>
          </button>

          <button
            onClick={onRunAnalysis}
            disabled={isAnalyzing}
            className="flex items-center space-x-1.5 px-4 py-2 rounded-lg text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white shadow-lg shadow-sky-600/20 transition disabled:opacity-50"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{isAnalyzing ? 'Analyzing Multimodal Inputs...' : 'Analyze & Correlate'}</span>
          </button>
        </div>
      </div>

      {decision ? (
        <div className="space-y-6">
          {/* SECTION A: Primary Decision & Severity Hero Box */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Decision Card */}
            <div className="md:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden">
              <span className="text-[10px] font-mono uppercase tracking-widest text-slate-400 font-bold block mb-2">
                EXECUTIVE DETERMINATION
              </span>
              <div className="flex items-center space-x-3">
                {BadgeIcon && (
                  <div className={`p-2.5 rounded-xl border ${badge?.bg}`}>
                    <BadgeIcon className="w-7 h-7" />
                  </div>
                )}
                <div>
                  <h2 className="text-2xl font-black text-white tracking-wide font-mono">
                    {badge?.badgeText}
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">
                    Contradiction detected between administrative repair order and field evidence.
                  </p>
                </div>
              </div>

              <div className="mt-5 p-3 rounded-xl bg-slate-950 border border-slate-800/80 text-xs text-slate-300 font-mono">
                {decision.rationale}
              </div>
            </div>

            {/* Severity & Confidence Assessment Card (GAP 2) */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between space-y-4">
              {/* Row 1: EXTRACTION CONFIDENCE */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-mono uppercase tracking-widest text-slate-400 font-bold block">
                    EXTRACTION CONFIDENCE
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-950/80 border border-sky-800/80 text-sky-300 font-semibold">
                    AI Scored
                  </span>
                </div>
                <div className="flex items-baseline space-x-2">
                  <span className="text-3xl font-black font-mono text-sky-400">
                    {Math.round(decision.score * 100)}%
                  </span>
                </div>
                <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden mt-2 border border-slate-800">
                  <div
                    className="bg-sky-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${Math.round(decision.score * 100)}%` }}
                  ></div>
                </div>
              </div>

              {/* Row 2: RISK LEVEL */}
              <div className="pt-4 border-t border-slate-800/80">
                <span className="text-[10px] font-mono uppercase tracking-widest text-slate-400 font-bold block mb-1.5">
                  RISK LEVEL
                </span>
                <div className="flex items-baseline space-x-2">
                  <span
                    className={`text-2xl font-black font-mono px-3 py-1 rounded-xl border ${
                      decision.severity === 'CRITICAL'
                        ? 'text-red-400 border-red-500/40 bg-red-500/10'
                        : decision.severity === 'HIGH'
                        ? 'text-orange-400 border-orange-500/40 bg-orange-500/10'
                        : decision.severity === 'MEDIUM'
                        ? 'text-amber-400 border-amber-500/40 bg-amber-500/10'
                        : 'text-emerald-400 border-emerald-500/40 bg-emerald-500/10'
                    }`}
                  >
                    {decision.severity}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* SECTION B: Ingested Evidence Dossier */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-semibold text-white text-sm flex items-center space-x-2">
                <Camera className="w-4 h-4 text-sky-400" />
                <span>EVIDENCE DOSSIER</span>
              </h3>
              <span className="text-xs font-mono text-slate-400">{evidenceList.length} Items</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {evidenceList.map((ev) => {
                const evClaims = claims.filter((c) => c.evidence_id === ev.id);
                return (
                  <div
                    key={ev.id}
                    className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="flex items-center space-x-1.5 font-mono text-xs font-bold text-slate-200">
                        {getSourceIcon(ev.source_type)}
                        <span>{ev.id}</span>
                      </span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded font-mono bg-slate-800 text-slate-400">
                        {ev.source_type}
                      </span>
                    </div>

                    <div className="text-xs font-medium text-white truncate mb-1.5" title={ev.file_name}>
                      {ev.file_name}
                    </div>

                    {/* Rich Multimodal Media Preview */}
                    {ev.source_type === 'IMAGE' && (
                      <div className="h-28 w-full rounded-lg overflow-hidden mb-2 bg-slate-900 border border-slate-800 relative group/thumb">
                        <img
                          src={api.getEvidenceFileUrl(ev.id)}
                          alt={ev.file_name}
                          className="w-full h-full object-cover group-hover/thumb:scale-105 transition duration-300"
                          onError={(e) => {
                            const parent = (e.currentTarget.parentElement as HTMLElement);
                            if (parent) parent.style.display = 'none';
                          }}
                        />
                      </div>
                    )}

                    {ev.source_type === 'AUDIO' && (
                      <div className="mb-2 p-1.5 rounded-lg bg-violet-950/30 border border-violet-800/40">
                        <div className="flex items-center space-x-1 text-[10px] text-violet-300 font-mono mb-1">
                          <Mic className="w-3 h-3 text-violet-400 shrink-0 animate-pulse" />
                          <span>Voice Complaint Audio</span>
                        </div>
                        <audio
                          controls
                          preload="none"
                          className="w-full h-6 rounded"
                          src={api.getEvidenceFileUrl(ev.id)}
                        />
                      </div>
                    )}

                    {(ev.source_type === 'PDF' || ev.source_type === 'DOCUMENT') && (
                      <div className="mb-2 p-2 rounded-lg bg-rose-950/20 border border-rose-800/30 flex items-center space-x-2 text-[10px] text-rose-300 font-mono">
                        <FileCheck2 className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                        <span className="truncate">Official Completion Order PDF</span>
                      </div>
                    )}

                    {/* GAP 3: Dynamic Real Claims from Findings */}
                    <div className="space-y-1 mb-2 bg-slate-900/60 p-2 rounded-lg border border-slate-800/80 min-h-[46px] flex flex-col justify-center">
                      {evClaims.length > 0 ? (
                        evClaims.slice(0, 2).map((c) => (
                          <div key={c.id} className="text-[11px] font-mono text-slate-300 truncate">
                            <span className="text-slate-400">{c.attribute}:</span>{' '}
                            <span className="font-semibold text-sky-300">{c.value}</span>
                          </div>
                        ))
                      ) : (
                        <div className="text-[11px] text-slate-500 font-mono italic">
                          Extraction pending
                        </div>
                      )}
                    </div>

                    <div className="mt-2 pt-2 border-t border-slate-800/80 flex items-center justify-between">
                      <span className="text-[10px] text-emerald-400 font-mono font-semibold">
                        ✓ Ingested
                      </span>
                      <a
                        href={api.getEvidenceFileUrl(ev.id)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[10px] text-sky-400 hover:underline flex items-center space-x-1"
                      >
                        <span>View</span>
                        <ExternalLink className="w-2.5 h-2.5" />
                      </a>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* SECTION C: Evidence Relationships Visual Mapping */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="font-semibold text-white text-sm flex items-center space-x-2">
                  <GitCommit className="w-4 h-4 text-sky-400" />
                  <span>EVIDENCE RELATIONSHIPS & VERIFICATION MAPPING</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Cross-evidence verification vectors establishing consistency and contradiction edges.
                </p>
              </div>
              <span className="text-xs font-mono text-slate-400">
                {relationships.length} Active Edges
              </span>
            </div>

            <div className="space-y-2">
              {relationships.length === 0 ? (
                <div className="p-4 text-center text-xs text-slate-500 font-mono">
                  No relationship edges formed yet.
                </div>
              ) : (
                relationships.map((rel, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono"
                  >
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-white bg-slate-900 px-2 py-0.5 rounded border border-slate-700">
                        {rel.source_evidence_id}
                      </span>
                      <span className="text-slate-500 font-sans">──</span>
                      <span
                        className={`px-2 py-0.5 rounded font-bold border ${
                          rel.relationship_type === 'CONTRADICTS'
                            ? 'bg-red-500/20 text-red-300 border-red-500/40'
                            : rel.relationship_type === 'CORROBORATES'
                            ? 'bg-blue-500/20 text-blue-300 border-blue-500/40'
                            : rel.relationship_type === 'SUPPORTS'
                            ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                            : 'bg-slate-800 text-slate-300 border-slate-700'
                        }`}
                      >
                        {rel.relationship_type}
                      </span>
                      <span className="text-slate-500 font-sans">──→</span>
                      <span className="font-bold text-white bg-slate-900 px-2 py-0.5 rounded border border-slate-700">
                        {rel.target_evidence_id}
                      </span>
                    </div>

                    <span className="text-slate-400 font-sans text-xs flex-1 sm:text-right">
                      {rel.description}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* SECTION D: Recommended Action & Human Review Controls */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5">
            <div className="p-4 rounded-xl bg-sky-950/30 border-l-4 border-l-sky-500 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-widest text-sky-400 font-bold">
                  RECOMMENDED ACTION
                </span>
                <h4 className="text-lg font-bold text-white mt-0.5">
                  {decision.recommended_action}
                </h4>
                <p className="text-xs text-slate-400 mt-1">
                  Due to critical conflict between official sign-off and ground reality, dispatch an independent inspection crew.
                </p>
              </div>

              <div className="shrink-0 flex items-center space-x-2">
                <button
                  onClick={onOpenReview}
                  className="px-4 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition shadow-md shadow-emerald-600/20"
                >
                  Approve Finding
                </button>
                <button
                  onClick={onOpenReview}
                  className="px-4 py-2 rounded-xl text-xs font-bold bg-amber-600 hover:bg-amber-500 text-white transition shadow-md shadow-amber-600/20"
                >
                  Override Decision
                </button>
                <button
                  onClick={onOpenReview}
                  className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
                >
                  Request Evidence
                </button>
              </div>
            </div>

            {/* Why severity was assigned */}
            <div>
              <h4 className="text-xs font-bold text-slate-300 font-mono uppercase tracking-wider mb-2">
                Explainable Severity Rationale:
              </h4>
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-slate-300 font-mono">
                {decision.severity_reasons && decision.severity_reasons.length > 0 ? (
                  decision.severity_reasons.map((r, i) => (
                    <li key={i} className="flex items-start space-x-2 p-2 rounded bg-slate-950 border border-slate-800">
                      <span className="text-sky-400 font-bold">✓</span>
                      <span>{r}</span>
                    </li>
                  ))
                ) : (
                  <li className="flex items-start space-x-2 p-2 rounded bg-slate-950 border border-slate-800">
                    <span className="text-sky-400 font-bold">✓</span>
                    <span>Verified by deterministic correlation and contradiction matrix.</span>
                  </li>
                )}
              </ul>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center">
          <Scale className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h4 className="text-base font-semibold text-white">Verification Ready</h4>
          <p className="text-xs text-slate-400 max-w-md mx-auto mt-1">
            Click "Analyze & Correlate" above to execute multimodal evidence extraction and contradiction detection.
          </p>
        </div>
      )}
    </div>
  );
};
