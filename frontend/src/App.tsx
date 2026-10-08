import React, { useState, useEffect } from 'react';
import { Case, HealthStatus } from './types';
import { api } from './api/client';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { CaseDetail } from './pages/CaseDetail';
import { CreateCase } from './pages/CreateCase';
import { CasesPage } from './pages/CasesPage';
import { EvidenceList } from './pages/EvidenceList';

export function App() {
  const [currentView, setCurrentView] = useState<'dashboard' | 'cases' | 'evidence_list' | 'case_detail' | 'create_case'>('dashboard');
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [cases, setCases] = useState<Case[]>([]);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isSeeding, setIsSeeding] = useState(false);

  const loadData = async () => {
    try {
      const [caseList, healthData] = await Promise.all([
        api.listCases(),
        api.getHealth().catch(() => null),
      ]);
      setCases(caseList);
      if (healthData) setHealth(healthData);
    } catch (err) {
      console.error('Failed fetching app initialization data:', err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSeedDemo = async (caseIdOrType: string | number = 'DEMO-001') => {
    setIsSeeding(true);
    try {
      const res = await api.seedDemoCase(caseIdOrType, true);
      await loadData();
      setSelectedCaseId(res.case_id);
      setCurrentView('case_detail');
    } catch (err: any) {
      alert(`Demo case ${caseIdOrType} initialization failed: ${err.message}`);
    } finally {
      setIsSeeding(false);
    }
  };

  const handleSeedAllDemos = async () => {
    setIsSeeding(true);
    try {
      await api.seedAllDemoCases(true);
      await loadData();
      alert('All 5 research-backed demo cases seeded and analyzed successfully!');
    } catch (err: any) {
      alert(`Seeding all demo cases failed: ${err.message}`);
    } finally {
      setIsSeeding(false);
    }
  };

  const handleSelectCase = (caseId: string) => {
    setSelectedCaseId(caseId);
    setCurrentView('case_detail');
  };

  const handleCaseCreated = (caseId: string) => {
    loadData();
    setSelectedCaseId(caseId);
    setCurrentView('case_detail');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar
        currentView={currentView}
        onNavigate={(view) => {
          setCurrentView(view);
          setSelectedCaseId(null);
        }}
        onSeedDemo={handleSeedDemo}
        isSeeding={isSeeding}
        health={health}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        {currentView === 'dashboard' && (
          <Dashboard
            cases={cases}
            onSelectCase={handleSelectCase}
            onSeedDemo={handleSeedDemo}
            onSeedAllDemos={handleSeedAllDemos}
            isSeeding={isSeeding}
            onNavigateCreate={() => setCurrentView('create_case')}
          />
        )}

        {currentView === 'cases' && (
          <CasesPage
            cases={cases}
            onSelectCase={handleSelectCase}
            onNavigateCreate={() => setCurrentView('create_case')}
          />
        )}

        {currentView === 'evidence_list' && (
          <EvidenceList
            onSelectCase={handleSelectCase}
          />
        )}

        {currentView === 'case_detail' && selectedCaseId && (
          <CaseDetail
            caseId={selectedCaseId}
            onBack={() => {
              setCurrentView('dashboard');
              setSelectedCaseId(null);
              loadData();
            }}
          />
        )}

        {currentView === 'create_case' && (
          <CreateCase
            onCaseCreated={handleCaseCreated}
            onCancel={() => setCurrentView('dashboard')}
          />
        )}
      </main>

      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500 font-mono">
        MESSY EVIDENCE → DECISIONS • Explainable Multimodal Municipal Verification Engine • Hackathon MVP
      </footer>
    </div>
  );
}

export default App;
