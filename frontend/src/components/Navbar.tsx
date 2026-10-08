import React from 'react';
import { ShieldAlert, Sparkles, PlusCircle, LayoutDashboard, Database, RefreshCw, FolderOpen, FileText } from 'lucide-react';
import { HealthStatus } from '../types';

interface NavbarProps {
  currentView: 'dashboard' | 'cases' | 'evidence_list' | 'case_detail' | 'create_case';
  onNavigate: (view: 'dashboard' | 'cases' | 'evidence_list' | 'create_case') => void;
  onSeedDemo: (caseIdOrType?: string | number) => void;
  isSeeding: boolean;
  health: HealthStatus | null;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentView,
  onNavigate,
  onSeedDemo,
  isSeeding,
  health,
}) => {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onNavigate('dashboard')}>
          <div className="p-2 bg-sky-500/10 border border-sky-500/30 rounded-lg text-sky-400">
            <ShieldAlert className="w-6 h-6 text-sky-400" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-white tracking-wide">MESSY EVIDENCE</span>
              <span className="text-xs px-2 py-0.5 rounded font-mono font-semibold bg-sky-500/20 text-sky-300 border border-sky-500/30">
                → DECISIONS
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Multimodal Municipal Inspection Verification System
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 sm:space-x-3">
          {health && (
            <div className="hidden xl:flex items-center space-x-2 px-3 py-1 bg-slate-900 border border-slate-800 rounded-full text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-slate-300 font-mono">LOCAL AI ENGINE: ONLINE</span>
            </div>
          )}

          <button
            onClick={() => onSeedDemo(1)}
            disabled={isSeeding}
            className="hidden md:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-500/10 border border-amber-500/30 text-amber-300 hover:bg-amber-500/20 transition disabled:opacity-50"
            title="Load Gate 2 Road Repair Multimodal Hero Demo"
          >
            {isSeeding ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            )}
            <span>{isSeeding ? 'Seeding...' : 'Hero Demo (Gate 2)'}</span>
          </button>

          <button
            onClick={() => onNavigate('dashboard')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
              currentView === 'dashboard'
                ? 'bg-slate-800 text-white border border-slate-700'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>Dashboard</span>
          </button>

          <button
            onClick={() => onNavigate('cases')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
              currentView === 'cases'
                ? 'bg-slate-800 text-white border border-slate-700'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <FolderOpen className="w-3.5 h-3.5 text-sky-400" />
            <span>Cases</span>
          </button>

          <button
            onClick={() => onNavigate('evidence_list')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
              currentView === 'evidence_list'
                ? 'bg-slate-800 text-white border border-slate-700'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Database className="w-3.5 h-3.5 text-emerald-400" />
            <span>Evidence</span>
          </button>

          <button
            onClick={() => onNavigate('create_case')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
              currentView === 'create_case'
                ? 'bg-sky-600 text-white'
                : 'bg-sky-500/10 text-sky-400 border border-sky-500/30 hover:bg-sky-500/20'
            }`}
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>New Case</span>
          </button>
        </div>
      </div>
    </header>
  );
};
