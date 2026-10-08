import React from 'react';
import {
  FolderKanban,
  ArrowRight,
  Sparkles,
  MapPin,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ShieldAlert,
  FileText,
  Database,
  Layers,
  Split,
  Compass
} from 'lucide-react';
import { Case } from '../types';
import { StatsCard } from '../components/StatsCard';

interface DashboardProps {
  cases: Case[];
  onSelectCase: (caseId: string) => void;
  onSeedDemo: (caseIdOrType?: string | number) => void;
  onSeedAllDemos?: () => void;
  isSeeding: boolean;
  onNavigateCreate: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  cases,
  onSelectCase,
  onSeedDemo,
  onSeedAllDemos,
  isSeeding,
  onNavigateCreate,
}) => {
  const verifiedCount = cases.filter((c) => c.status === 'REVIEWED' || c.status === 'VERIFIED').length;
  const conflictCount = cases.filter((c) => c.status === 'ANALYZED').length;
  const highRiskCount = cases.filter((c) => c.id.includes('GATE2') || c.id.includes('DEMO-001') || c.status === 'ANALYZED').length;
  const pendingReviewCount = cases.filter((c) => c.status === 'ANALYZED' || c.status === 'NEW').length;

  const demoCases = [
    {
      id: 'DEMO-001',
      title: 'Demo 1: Conflict (Hero Case)',
      shortDesc: 'Official PDF (Completed) vs Citizen Photo & Audio -> CONFLICT (HIGH)',
      decision: 'CONFLICT',
      severity: 'HIGH',
      badgeColor: 'bg-red-500/10 text-red-400 border-red-500/30',
      icon: Sparkles,
      origin: 'Derived / Public (RDD2020)',
    },
    {
      id: 'DEMO-002',
      title: 'Demo 2: Verified (Smooth Road)',
      shortDesc: 'Official PDF (Completed) matches Smooth Resurfaced Asphalt Photo',
      decision: 'VERIFIED',
      severity: 'LOW',
      badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      icon: CheckCircle2,
      origin: 'Derived / CPPP PWD',
    },
    {
      id: 'DEMO-003',
      title: 'Demo 3: Insufficient Evidence',
      shortDesc: 'Ambiguous Inquiry Ticket without ground photos or work order',
      decision: 'INSUFFICIENT',
      severity: 'LOW',
      badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      icon: AlertTriangle,
      origin: 'Derived / BBMP FMS',
    },
    {
      id: 'DEMO-004',
      title: 'Demo 4: Corroborated Damage',
      shortDesc: 'Multi-witness Photo + Voice + Text (No Prior Work Order)',
      decision: 'PARTIAL',
      severity: 'MEDIUM',
      badgeColor: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
      icon: Layers,
      origin: 'Derived / Civic Reports',
    },
    {
      id: 'DEMO-005',
      title: 'Demo 5: Location Mismatch',
      shortDesc: 'Gate 2 Completion Order vs Gate 5 Road Photo (Spatial Conflict)',
      decision: 'MISMATCH',
      severity: 'LOW',
      badgeColor: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
      icon: Compass,
      origin: 'Spatial Discrepancy',
    },
  ];

  return (
    <div className="space-y-8 pb-12">
      {/* Hero Banner */}
      <div className="relative rounded-2xl bg-gradient-to-br from-slate-900 via-sky-950/40 to-slate-900 border border-slate-800 p-8 overflow-hidden shadow-2xl">
        <div className="absolute right-0 top-0 -mr-16 -mt-16 w-80 h-80 rounded-full bg-sky-500/10 blur-3xl pointer-events-none"></div>

        <div className="relative max-w-4xl space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-mono">
              MUNICIPAL INSPECTION VERIFICATION ENGINE
            </span>
            <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono flex items-center space-x-1">
              <Database className="w-3 h-3 mr-1" />
              <span>Grounded in RDD2020 & OpenCity Datasets</span>
            </span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
            Messy Evidence → Explainable Decisions
          </h1>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed font-sans max-w-3xl">
            "We don't replace the decision maker. We fuse fragmented multimodal real-world evidence—smartphone photos,
            official completion PDFs, citizen audio grievances, and text notes—into transparent, audit-traceable municipal decisions."
          </p>

          {/* Prominent Run Winning Demo Primary Action */}
          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={() => onSeedDemo('DEMO-001')}
              disabled={isSeeding}
              className="group flex items-center space-x-3 px-5 py-3 rounded-xl text-sm font-bold bg-gradient-to-r from-amber-400 via-amber-500 to-amber-400 text-slate-950 hover:from-amber-300 hover:to-amber-400 shadow-xl shadow-amber-500/25 transition transform active:scale-95 disabled:opacity-50"
              title="Execute Hero Inspection Conflict: Official PDF vs Citizen Photo & Audio"
            >
              <Sparkles className="w-4 h-4 text-slate-950 animate-pulse" />
              <div className="text-left">
                <span className="block leading-none text-slate-950 font-black">Run Winning Demo (Hero Case)</span>
                <span className="text-[10px] text-slate-900/80 font-mono font-medium">Gate 2 Road Repair Conflict → CONFLICT (HIGH)</span>
              </div>
            </button>

            {onSeedAllDemos && (
              <button
                onClick={onSeedAllDemos}
                disabled={isSeeding}
                className="flex items-center space-x-2 px-4 py-3 rounded-xl text-xs font-semibold bg-slate-800 text-slate-200 hover:bg-slate-700 border border-slate-700 shadow-md transition disabled:opacity-50"
                title="Seed and analyze all 5 research-backed demo cases simultaneously"
              >
                <Layers className="w-3.5 h-3.5 text-sky-400" />
                <span>Preload All 5 Cases</span>
              </button>
            )}

            <button
              onClick={onNavigateCreate}
              className="flex items-center space-x-1.5 px-4 py-3 rounded-xl text-xs font-semibold bg-slate-800/80 text-slate-300 hover:bg-slate-700 border border-slate-700/80 transition"
            >
              <span>+ Custom Case</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* 5 Core Demo Cases Selector Grid */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-amber-400" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">
              Research-Backed Demo Benchmark Suite (5 Scenarios)
            </h2>
          </div>
          <span className="text-[11px] text-slate-400 font-mono">
            1-Click Seed & Verification
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3 pt-1">
          {demoCases.map((demo) => {
            const Icon = demo.icon;
            return (
              <button
                key={demo.id}
                onClick={() => onSeedDemo(demo.id)}
                disabled={isSeeding}
                className="flex flex-col justify-between text-left p-3.5 rounded-xl bg-slate-950/60 hover:bg-slate-800/60 border border-slate-800/80 hover:border-sky-500/40 transition group disabled:opacity-50 relative overflow-hidden"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-sky-400 font-bold">{demo.id}</span>
                    <span className={`px-2 py-0.5 rounded text-[9px] font-bold border ${demo.badgeColor}`}>
                      {demo.decision}
                    </span>
                  </div>
                  <h3 className="text-xs font-bold text-white group-hover:text-sky-300 transition line-clamp-1">
                    {demo.title}
                  </h3>
                  <p className="text-[11px] text-slate-400 line-clamp-2 leading-tight">
                    {demo.shortDesc}
                  </p>
                </div>

                <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-500">
                  <span className="truncate max-w-[120px]">{demo.origin}</span>
                  <ArrowRight className="w-3 h-3 text-slate-400 group-hover:text-sky-400 group-hover:translate-x-0.5 transition" />
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Stats Cards */}
      <StatsCard
        totalCases={cases.length}
        verifiedCount={verifiedCount}
        conflictCount={conflictCount}
        highRiskCount={highRiskCount}
        pendingReviewCount={pendingReviewCount}
      />

      {/* Case Management Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="p-5 border-b border-slate-800 flex flex-wrap items-center justify-between gap-4 bg-slate-950/40">
          <div>
            <h2 className="font-bold text-white text-base flex items-center space-x-2">
              <FolderKanban className="w-5 h-5 text-sky-400" />
              <span>Active Municipal Cases</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Review real-time inspection requests, evidence packets, and conflict determinations.
            </p>
          </div>

          <span className="text-xs font-mono text-slate-400 px-3 py-1 bg-slate-800 rounded-lg">
            {cases.length} Total Records
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-4">Case ID</th>
                <th className="p-4 font-sans font-semibold">Title</th>
                <th className="p-4">Location</th>
                <th className="p-4">Evidence</th>
                <th className="p-4">Status</th>
                <th className="p-4">Created</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {cases.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-500 font-sans">
                    No cases found. Click "Run Winning Demo" above to seed sample data.
                  </td>
                </tr>
              ) : (
                cases.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => onSelectCase(c.id)}
                    className="hover:bg-slate-800/40 transition cursor-pointer"
                  >
                    <td className="p-4 font-bold text-sky-400">{c.id}</td>
                    <td className="p-4 font-sans font-medium text-white max-w-xs truncate">
                      {c.title}
                    </td>
                    <td className="p-4 text-slate-400">
                      <span className="flex items-center space-x-1">
                        <MapPin className="w-3 h-3 text-slate-500" />
                        <span>{c.location || 'Unspecified'}</span>
                      </span>
                    </td>
                    <td className="p-4">
                      <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 font-bold">
                        {c.evidence_count ?? 0} items
                      </span>
                    </td>
                    <td className="p-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          c.status === 'ANALYZED'
                            ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                            : c.status === 'REVIEWED' || c.status === 'VERIFIED'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        }`}
                      >
                        {c.status}
                      </span>
                    </td>
                    <td className="p-4 text-slate-500">
                      {c.created_at ? c.created_at.substring(0, 10) : '2026-10-08'}
                    </td>
                    <td className="p-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectCase(c.id);
                        }}
                        className="inline-flex items-center space-x-1 px-3 py-1 rounded-lg text-xs font-semibold bg-sky-500/10 text-sky-300 hover:bg-sky-500/20 border border-sky-500/30 transition"
                      >
                        <span>Inspect</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </td>
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
