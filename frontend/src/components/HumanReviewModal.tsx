import React, { useState } from 'react';
import { X, UserCheck, ShieldAlert, CheckCircle2, AlertTriangle, FileQuestion } from 'lucide-react';
import { Decision, Review } from '../types';
import { api } from '../api/client';

interface HumanReviewModalProps {
  caseId: string;
  decision?: Decision;
  reviews: Review[];
  isOpen: boolean;
  onClose: () => void;
  onReviewSubmitted: () => void;
}

export const HumanReviewModal: React.FC<HumanReviewModalProps> = ({
  caseId,
  decision,
  reviews,
  isOpen,
  onClose,
  onReviewSubmitted,
}) => {
  const [reviewerName, setReviewerName] = useState('Senior Municipal Inspector R. Sharma');
  const [actionType, setActionType] = useState<'APPROVE' | 'OVERRIDE' | 'REQUEST_EVIDENCE'>('APPROVE');
  const [overrideDecision, setOverrideDecision] = useState('PHYSICAL_INSPECTION_ORDERED');
  const [reason, setReason] = useState(
    'Concur with AI finding. Multimodal contradiction between official completion order and real-world citizen evidence warrants immediate physical dispatch.'
  );
  const [evidenceNeeded, setEvidenceNeeded] = useState('Geotagged Asphalt Density Core Sample & Contractor Signature');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewerName.trim() || !reason.trim()) return;
    setIsSubmitting(true);
    try {
      if (actionType === 'REQUEST_EVIDENCE') {
        await api.requestMoreEvidence(caseId, reviewerName, evidenceNeeded, reason);
      } else {
        const finalDecision =
          actionType === 'APPROVE'
            ? decision?.decision || 'APPROVED'
            : overrideDecision;
        await api.submitReview(caseId, reviewerName, finalDecision, reason);
      }
      onReviewSubmitted();
      onClose();
    } catch (err: any) {
      alert(`Review submission failed: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center space-x-2">
            <div className="p-2 rounded-lg bg-sky-500/10 border border-sky-500/30 text-sky-400">
              <UserCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base">Municipal Human Review & Override</h3>
              <p className="text-xs text-slate-400">
                Human-in-the-loop audit protocol required before irreversible administrative action.
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* AI Decision Summary Box */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-[10px] uppercase font-mono tracking-wider text-slate-500">
                Current AI Decision
              </span>
              <div className="text-sm font-bold text-white mt-0.5">
                {decision?.decision || 'NO PRIOR DECISION'}
              </div>
              <div className="text-xs text-slate-400 font-mono mt-0.5">
                Recommended Action: {decision?.recommended_action || 'N/A'}
              </div>
            </div>
            <span className="px-2.5 py-1 rounded text-xs font-mono font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30">
              {decision?.severity || 'LOW'} SEVERITY
            </span>
          </div>

          {/* Action Choice Tabs */}
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => {
                setActionType('APPROVE');
                setReason('Concur with AI finding. Conflicting evidence requires physical inspection.');
              }}
              className={`p-3 rounded-lg border text-xs font-semibold flex flex-col items-center justify-center space-y-1 transition ${
                actionType === 'APPROVE'
                  ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Approve Finding</span>
            </button>

            <button
              type="button"
              onClick={() => {
                setActionType('OVERRIDE');
                setReason('Overriding based on departmental audit review.');
              }}
              className={`p-3 rounded-lg border text-xs font-semibold flex flex-col items-center justify-center space-y-1 transition ${
                actionType === 'OVERRIDE'
                  ? 'bg-amber-500/20 border-amber-500/50 text-amber-300'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              <AlertTriangle className="w-4 h-4" />
              <span>Override Decision</span>
            </button>

            <button
              type="button"
              onClick={() => {
                setActionType('REQUEST_EVIDENCE');
                setReason('Evidence is currently insufficient or ambiguous. Awaiting certified contractor receipts.');
              }}
              className={`p-3 rounded-lg border text-xs font-semibold flex flex-col items-center justify-center space-y-1 transition ${
                actionType === 'REQUEST_EVIDENCE'
                  ? 'bg-sky-500/20 border-sky-500/50 text-sky-300'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              <FileQuestion className="w-4 h-4" />
              <span>Request More Evidence</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Authorized Reviewer Name / Title
              </label>
              <input
                type="text"
                required
                value={reviewerName}
                onChange={(e) => setReviewerName(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
              />
            </div>

            {actionType === 'OVERRIDE' && (
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  New Override Determination
                </label>
                <select
                  value={overrideDecision}
                  onChange={(e) => setOverrideDecision(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
                >
                  <option value="PHYSICAL_INSPECTION_ORDERED">Physical Field Inspection Ordered</option>
                  <option value="CONTRACTOR_PENALTY_INITIATED">Contractor Penalty Initiated</option>
                  <option value="WORK_ORDER_CANCELLED">Work Order Revoked / Cancelled</option>
                  <option value="VERIFIED_APPROVED">Override to Verified / Dismissed</option>
                </select>
              </div>
            )}

            {actionType === 'REQUEST_EVIDENCE' && (
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Specific Documentation Required
                </label>
                <input
                  type="text"
                  required
                  value={evidenceNeeded}
                  onChange={(e) => setEvidenceNeeded(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
                />
              </div>
            )}
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Official Justification & Audit Justification
            </label>
            <textarea
              required
              rows={3}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-xs text-white focus:outline-none focus:border-sky-500 font-mono"
            />
          </div>

          {/* Prior Reviews Log */}
          {reviews.length > 0 && (
            <div className="pt-2 border-t border-slate-800">
              <span className="text-[11px] font-mono text-slate-400 block mb-2">
                Prior Review History ({reviews.length})
              </span>
              <div className="max-h-28 overflow-y-auto space-y-1.5">
                {reviews.map((r) => (
                  <div key={r.id} className="p-2 rounded bg-slate-950 text-[11px] font-mono text-slate-300">
                    <span className="font-bold text-sky-400">{r.reviewer}</span> set to{' '}
                    <span className="text-white font-bold">{r.new_decision}</span>: "{r.reason}"
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-end space-x-2 pt-2 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white rounded-lg transition disabled:opacity-50"
            >
              {isSubmitting ? 'Recording Audit...' : 'Commit Review Decision'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
