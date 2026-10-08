import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  MapPin,
  User,
  Calendar,
  Layers,
  Sparkles,
  GitMerge,
  History,
  FileText,
  UserCheck,
  RefreshCw,
  AlertTriangle
} from 'lucide-react';
import { Case, FindingsResponse } from '../types';
import { api } from '../api/client';
import { AnalysisView } from '../components/AnalysisView';
import { EvidenceWorkspace } from '../components/EvidenceWorkspace';
import { EvidenceTraceGraph } from '../components/EvidenceTraceGraph';
import { AuditTrailList } from '../components/AuditTrailList';
import { HumanReviewModal } from '../components/HumanReviewModal';
import { ReportModal } from '../components/ReportModal';

interface CaseDetailProps {
  caseId: string;
  onBack: () => void;
}

export const CaseDetail: React.FC<CaseDetailProps> = ({ caseId, onBack }) => {
  const [findings, setFindings] = useState<FindingsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState<'analysis' | 'evidence' | 'trace' | 'audit'>('analysis');
  const [isReviewOpen, setIsReviewOpen] = useState(false);
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchFindings = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const data = await api.getCaseFindings(caseId);
      setFindings(data);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed loading case findings');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchFindings();
  }, [caseId]);

  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      await api.analyzeCase(caseId);
      await fetchFindings();
      setActiveTab('analysis');
    } catch (err: any) {
      alert(`Analysis failed: ${err.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="py-24 text-center">
        <RefreshCw className="w-8 h-8 text-sky-400 animate-spin mx-auto mb-3" />
        <p className="text-xs text-slate-400 font-mono">Loading case verification packet...</p>
      </div>
    );
  }

  if (!findings) {
    return (
      <div className="py-24 text-center space-y-3">
        <AlertTriangle className="w-8 h-8 text-red-400 mx-auto" />
        <p className="text-sm text-slate-300">Case record could not be loaded.</p>
        <button onClick={onBack} className="text-xs text-sky-400 hover:underline">
          Return to Dashboard
        </button>
      </div>
    );
  }

  const { case: currentCase, evidence, extractions, claims, relationships, decision, reviews, audit_events } = findings;

  return (
    <div className="space-y-6 pb-16">
      {/* Top Breadcrumb & Action Row */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <button
          onClick={onBack}
          className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to All Cases</span>
        </button>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsReportOpen(true)}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-200 hover:bg-slate-700 border border-slate-700 transition"
          >
            <FileText className="w-3.5 h-3.5 text-sky-400" />
            <span>Official Report</span>
          </button>
          <button
            onClick={() => setIsReviewOpen(true)}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-sky-500/10 text-sky-300 hover:bg-sky-500/20 border border-sky-500/30 transition"
          >
            <UserCheck className="w-3.5 h-3.5" />
            <span>Human Review</span>
          </button>
        </div>
      </div>

      {/* Case Header Details Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30">
                {currentCase.id}
              </span>
              <span className="text-xs text-slate-400">{currentCase.category}</span>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-white mt-1">
              {currentCase.title}
            </h1>
          </div>

          <div>
            <span
              className={`px-3 py-1 rounded-full text-xs font-mono font-bold ${
                currentCase.status === 'ANALYZED'
                  ? 'bg-red-500/10 text-red-400 border border-red-500/30'
                  : currentCase.status === 'REVIEWED'
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                  : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
              }`}
            >
              STATUS: {currentCase.status}
            </span>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-slate-400 font-mono pt-2 border-t border-slate-800/80">
          <div className="flex items-center space-x-1.5">
            <MapPin className="w-3.5 h-3.5 text-slate-500" />
            <span className="text-slate-300">{currentCase.location || 'Not Specified'}</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <User className="w-3.5 h-3.5 text-slate-500" />
            <span>Reporter: {currentCase.reporter || 'Anonymous'}</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <Calendar className="w-3.5 h-3.5 text-slate-500" />
            <span>Created: {currentCase.created_at.substring(0, 10)}</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <Layers className="w-3.5 h-3.5 text-slate-500" />
            <span>{evidence.length} Evidence Items</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab('analysis')}
          className={`flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-semibold transition ${
            activeTab === 'analysis'
              ? 'bg-sky-600 text-white shadow-md shadow-sky-600/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Decision & Findings</span>
        </button>

        <button
          onClick={() => setActiveTab('evidence')}
          className={`flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-semibold transition ${
            activeTab === 'evidence'
              ? 'bg-sky-600 text-white shadow-md shadow-sky-600/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Evidence Workspace ({evidence.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('trace')}
          className={`flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-semibold transition ${
            activeTab === 'trace'
              ? 'bg-sky-600 text-white shadow-md shadow-sky-600/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <GitMerge className="w-3.5 h-3.5" />
          <span>Evidence Trace ({relationships.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('audit')}
          className={`flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-semibold transition ${
            activeTab === 'audit'
              ? 'bg-sky-600 text-white shadow-md shadow-sky-600/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <History className="w-3.5 h-3.5" />
          <span>Chain of Custody ({audit_events.length})</span>
        </button>
      </div>

      {/* Tab Panels */}
      {activeTab === 'analysis' && (
        <AnalysisView
          currentCase={currentCase}
          decision={decision}
          evidenceList={evidence}
          relationships={relationships}
          claims={claims}
          isAnalyzing={isAnalyzing}
          onRunAnalysis={handleRunAnalysis}
          onOpenReview={() => setIsReviewOpen(true)}
          onOpenReport={() => setIsReportOpen(true)}
        />
      )}

      {activeTab === 'evidence' && (
        <EvidenceWorkspace
          caseId={caseId}
          evidenceList={evidence}
          onEvidenceUpdated={fetchFindings}
        />
      )}

      {activeTab === 'trace' && (
        <EvidenceTraceGraph
          evidenceList={evidence}
          claims={claims}
          relationships={relationships}
          extractions={extractions}
        />
      )}

      {activeTab === 'audit' && (
        <AuditTrailList events={audit_events} />
      )}

      {/* Modals */}
      <HumanReviewModal
        caseId={caseId}
        decision={decision}
        reviews={reviews}
        isOpen={isReviewOpen}
        onClose={() => setIsReviewOpen(false)}
        onReviewSubmitted={fetchFindings}
      />

      <ReportModal
        caseId={caseId}
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
      />
    </div>
  );
};
