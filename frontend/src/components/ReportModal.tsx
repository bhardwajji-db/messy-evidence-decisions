import React from 'react';
import { X, Printer, ExternalLink, Download } from 'lucide-react';
import { api } from '../api/client';

interface ReportModalProps {
  caseId: string;
  isOpen: boolean;
  onClose: () => void;
}

export const ReportModal: React.FC<ReportModalProps> = ({ caseId, isOpen, onClose }) => {
  if (!isOpen) return null;

  const reportUrl = `/api/cases/${encodeURIComponent(caseId)}/report?format=html`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-5xl w-full h-[90vh] flex flex-col overflow-hidden shadow-2xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
          <div>
            <h3 className="font-bold text-white text-base">Official Municipal Evidence Audit Report</h3>
            <p className="text-xs text-slate-400">Formal printable audit certification for Case {caseId}</p>
          </div>

          <div className="flex items-center space-x-2">
            <a
              href={reportUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-200 hover:bg-slate-700 border border-slate-700"
            >
              <ExternalLink className="w-3.5 h-3.5 text-sky-400" />
              <span>Open in New Tab</span>
            </a>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="flex-1 bg-white">
          <iframe src={reportUrl} className="w-full h-full border-0" title="Municipal Report" />
        </div>
      </div>
    </div>
  );
};
