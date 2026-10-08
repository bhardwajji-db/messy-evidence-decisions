import React, { useState, useEffect } from 'react';
import { PlusCircle, ArrowLeft, FolderPlus, MapPin, User, FileText, CheckCircle2, Search } from 'lucide-react';
import { api } from '../api/client';
import { OfficialRecord } from '../types';

interface CreateCaseProps {
  onCaseCreated: (caseId: string) => void;
  onCancel: () => void;
}

export const CreateCase: React.FC<CreateCaseProps> = ({ onCaseCreated, onCancel }) => {
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Road / Infrastructure');
  const [location, setLocation] = useState('');
  const [reporter, setReporter] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [matchingRecords, setMatchingRecords] = useState<OfficialRecord[]>([]);
  const [isSearchingRecords, setIsSearchingRecords] = useState(false);

  useEffect(() => {
    if (!location.trim() || location.trim().length < 2) {
      setMatchingRecords([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearchingRecords(true);
      try {
        const records = await api.getOfficialRecords(location.trim());
        setMatchingRecords(records);
      } catch (err) {
        console.warn('Failed querying official records:', err);
      } finally {
        setIsSearchingRecords(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [location]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      const created = await api.createCase({
        title,
        category,
        location,
        reporter,
        description,
      });
      onCaseCreated(created.id);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to create case');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 pb-12">
      <button
        onClick={onCancel}
        className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white transition"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Dashboard</span>
      </button>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl space-y-6">
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-4">
          <div className="p-2.5 rounded-xl bg-sky-500/10 border border-sky-500/30 text-sky-400">
            <FolderPlus className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Create Municipal Inspection Case</h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Initialize a new multimodal evidence dossier for road repair verification.
            </p>
          </div>
        </div>

        {errorMsg && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-xs">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
              Case Title / Incident Subject *
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Road Repair Verification — Gate 2"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-sky-500 transition"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-sky-500 transition"
              >
                <option value="Road / Infrastructure">Road / Infrastructure (Potholes, Asphalt)</option>
                <option value="Municipal Drainage">Municipal Drainage & Floodwater</option>
                <option value="Street Lighting">Street Lighting & Electrical</option>
                <option value="Traffic Signage">Traffic Signage & Markings</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                Location / Road Milestone
              </label>
              <input
                type="text"
                placeholder="e.g. Gate 2 Road, North Sector Ring Road"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-sky-500 transition"
              />
            </div>
          </div>

          {/* Matching Official Records Panel */}
          {matchingRecords.length > 0 && (
            <div className="p-4 rounded-xl bg-sky-950/40 border border-sky-500/40 space-y-2.5 animate-fadeIn">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-sky-300 font-semibold text-xs">
                  <CheckCircle2 className="w-4 h-4 text-sky-400" />
                  <span>Matching Official Records ({matchingRecords.length})</span>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-900/60 text-sky-200 border border-sky-700/50">
                  Pre-Seeded Record Found
                </span>
              </div>
              <p className="text-[11px] text-slate-300">
                Official municipal record already exists for this location — you only need to upload current field evidence.
              </p>
              <div className="space-y-1.5 pt-1">
                {matchingRecords.map((rec) => (
                  <div
                    key={rec.id}
                    className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs font-mono text-slate-200 flex flex-wrap items-center justify-between gap-2"
                  >
                    <span className="font-bold text-sky-300">
                      {rec.work_order_id} — {rec.location} — Status: {rec.status} — {rec.completion_date || 'null'}
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                      {rec.department || 'Municipal Works'} | {rec.issue}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
              Reporting Entity / Source
            </label>
            <input
              type="text"
              placeholder="e.g. Citizen Taskforce / Ward Inspector / PWD Portal"
              value={reporter}
              onChange={(e) => setReporter(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-sky-500 transition"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
              Initial Context Notes (optional)
            </label>
            <textarea
              rows={3}
              placeholder="Enter initial context, complaint ticket ID, or inspection parameters..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-sky-500 transition"
            />
          </div>

          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-xs text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !title.trim()}
              className="px-5 py-2.5 rounded-xl text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white shadow-lg shadow-sky-600/20 transition disabled:opacity-50"
            >
              {isSubmitting ? 'Creating Case...' : 'Create Case & Open Workspace'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
