import React from 'react';
import { History, ShieldCheck, Clock } from 'lucide-react';
import { AuditEvent } from '../types';

interface AuditTrailListProps {
  events: AuditEvent[];
}

export const AuditTrailList: React.FC<AuditTrailListProps> = ({ events }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <History className="w-4 h-4 text-sky-400" />
          <h3 className="font-semibold text-white text-sm">Chain of Custody & Audit Trail</h3>
        </div>
        <span className="text-xs font-mono text-slate-500">{events.length} Events Logged</span>
      </div>

      <div className="relative border-l border-slate-800 ml-3 space-y-4 py-1">
        {events.length === 0 ? (
          <div className="pl-4 text-xs text-slate-500">No audit events recorded yet.</div>
        ) : (
          events.map((evt) => (
            <div key={evt.id} className="relative pl-6">
              <span className="absolute -left-1.5 top-1 w-3 h-3 rounded-full bg-slate-800 border border-sky-500/50"></span>
              <div className="flex items-center space-x-2 text-[11px] font-mono">
                <span className="text-sky-400 font-bold">{evt.event_type}</span>
                <span className="text-slate-500">•</span>
                <span className="text-slate-500">{evt.timestamp.replace('T', ' ').substring(0, 19)}</span>
              </div>
              <p className="text-xs text-slate-300 mt-0.5">{evt.description}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
