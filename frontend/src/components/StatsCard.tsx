import React from 'react';
import { AlertTriangle, CheckCircle2, ShieldAlert, FolderKanban, UserCheck } from 'lucide-react';

interface StatsCardProps {
  totalCases: number;
  verifiedCount: number;
  conflictCount: number;
  highRiskCount: number;
  pendingReviewCount: number;
}

export const StatsCard: React.FC<StatsCardProps> = ({
  totalCases,
  verifiedCount,
  conflictCount,
  highRiskCount,
  pendingReviewCount,
}) => {
  const cards = [
    {
      title: 'Total Ingested Cases',
      value: totalCases,
      icon: FolderKanban,
      color: 'text-slate-200',
      border: 'border-slate-800',
      bg: 'bg-slate-900/50',
    },
    {
      title: 'Evidence Conflicts',
      value: conflictCount,
      icon: AlertTriangle,
      color: 'text-red-400',
      border: 'border-red-500/30',
      bg: 'bg-red-500/10',
    },
    {
      title: 'High / Critical Risk',
      value: highRiskCount,
      icon: ShieldAlert,
      color: 'text-amber-400',
      border: 'border-amber-500/30',
      bg: 'bg-amber-500/10',
    },
    {
      title: 'Verified Repairs',
      value: verifiedCount,
      icon: CheckCircle2,
      color: 'text-emerald-400',
      border: 'border-emerald-500/30',
      bg: 'bg-emerald-500/10',
    },
    {
      title: 'Pending Human Review',
      value: pendingReviewCount,
      icon: UserCheck,
      color: 'text-sky-400',
      border: 'border-sky-500/30',
      bg: 'bg-sky-500/10',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
      {cards.map((c, i) => {
        const Icon = c.icon;
        return (
          <div
            key={i}
            className={`p-4 rounded-xl border ${c.border} ${c.bg} backdrop-blur flex flex-col justify-between`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400 font-medium">{c.title}</span>
              <Icon className={`w-4 h-4 ${c.color}`} />
            </div>
            <div className="mt-3">
              <span className={`text-2xl font-bold font-mono ${c.color}`}>
                {c.value}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
