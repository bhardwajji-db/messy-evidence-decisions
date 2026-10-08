import React, { useState } from 'react';
import {
  FileImage,
  FileText,
  Mic,
  MessageSquare,
  Upload,
  Sparkles,
  ExternalLink,
  CheckCircle,
  Clock,
  AlertCircle,
  Hash,
  MapPin,
  User,
  Plus
} from 'lucide-react';
import { Evidence } from '../types';
import { api } from '../api/client';

interface EvidenceWorkspaceProps {
  caseId: string;
  evidenceList: Evidence[];
  onEvidenceUpdated: () => void;
}

export const EvidenceWorkspace: React.FC<EvidenceWorkspaceProps> = ({
  caseId,
  evidenceList,
  onEvidenceUpdated,
}) => {
  const [activeTab, setActiveTab] = useState<'list' | 'upload_file' | 'add_text'>('list');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [sourceType, setSourceType] = useState<string>('IMAGE');
  const [location, setLocation] = useState<string>('');
  const [uploader, setUploader] = useState<string>('');
  const [textContent, setTextContent] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [extractingId, setExtractingId] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      await api.uploadEvidence(caseId, uploadFile, undefined, sourceType, location, uploader);
      setUploadFile(null);
      setActiveTab('list');
      onEvidenceUpdated();
    } catch (err: any) {
      setErrorMsg(err.message || 'Upload failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTextUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!textContent.trim()) return;
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      await api.uploadEvidence(caseId, undefined, textContent, 'TEXT', location, uploader);
      setTextContent('');
      setActiveTab('list');
      onEvidenceUpdated();
    } catch (err: any) {
      setErrorMsg(err.message || 'Text upload failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleExtractSingle = async (evidenceId: string) => {
    setExtractingId(evidenceId);
    try {
      await api.extractEvidence(evidenceId);
      onEvidenceUpdated();
    } catch (err: any) {
      alert(`Extraction failed: ${err.message}`);
    } finally {
      setExtractingId(null);
    }
  };

  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'IMAGE':
        return <FileImage className="w-4 h-4 text-emerald-400" />;
      case 'PDF':
      case 'DOCUMENT':
        return <FileText className="w-4 h-4 text-rose-400" />;
      case 'AUDIO':
        return <Mic className="w-4 h-4 text-violet-400" />;
      case 'TEXT':
        return <MessageSquare className="w-4 h-4 text-amber-400" />;
      default:
        return <FileText className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
      {/* Workspace Header & Action Tabs */}
      <div className="p-4 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 bg-slate-950/40">
        <div>
          <h3 className="font-semibold text-white text-sm flex items-center space-x-2">
            <span>Evidence Workspace</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-mono">
              {evidenceList.length} items
            </span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Ingest real-world photos, documents, citizen voice clips, and complaint logs.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveTab('list')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
              activeTab === 'list'
                ? 'bg-slate-800 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Evidence List
          </button>
          <button
            onClick={() => setActiveTab('upload_file')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
              activeTab === 'upload_file'
                ? 'bg-sky-600 text-white'
                : 'bg-slate-800/80 text-slate-300 hover:bg-slate-800'
            }`}
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload File</span>
          </button>
          <button
            onClick={() => setActiveTab('add_text')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
              activeTab === 'add_text'
                ? 'bg-sky-600 text-white'
                : 'bg-slate-800/80 text-slate-300 hover:bg-slate-800'
            }`}
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Text Note</span>
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="m-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Upload File Form */}
      {activeTab === 'upload_file' && (
        <form onSubmit={handleFileUpload} className="p-5 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Source Category
              </label>
              <select
                value={sourceType}
                onChange={(e) => setSourceType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
              >
                <option value="IMAGE">Image / Photo (Road surface, Pothole)</option>
                <option value="PDF">PDF / Document (Work completion order)</option>
                <option value="AUDIO">Audio / Voice Note (Citizen complaint)</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Location Reference (optional)
              </label>
              <input
                type="text"
                placeholder="e.g. Gate 2 Road"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Uploader / Source Entity
              </label>
              <input
                type="text"
                placeholder="e.g. Ward Inspector / Helpline"
                value={uploader}
                onChange={(e) => setUploader(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Select Evidence File
            </label>
            <input
              type="file"
              required
              onChange={(e) => setUploadFile(e.target.files ? e.target.files[0] : null)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-300 file:mr-4 file:py-1 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-sky-500/10 file:text-sky-400 hover:file:bg-sky-500/20"
            />
          </div>

          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setActiveTab('list')}
              className="px-4 py-2 text-xs text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !uploadFile}
              className="px-4 py-2 text-xs font-semibold bg-sky-600 text-white rounded-lg hover:bg-sky-500 disabled:opacity-50"
            >
              {isSubmitting ? 'Uploading...' : 'Ingest & Store Evidence'}
            </button>
          </div>
        </form>
      )}

      {/* Add Text Note Form */}
      {activeTab === 'add_text' && (
        <form onSubmit={handleTextUpload} className="p-5 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Location Mentioned
              </label>
              <input
                type="text"
                placeholder="e.g. Gate 2, North Sector"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Source / Citizen Name
              </label>
              <input
                type="text"
                placeholder="e.g. Citizen Helpline / Resident"
                value={uploader}
                onChange={(e) => setUploader(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Complaint / Grievance Text
            </label>
            <textarea
              required
              rows={4}
              placeholder="Enter complaint details, mentioning road damage, pothole, completion claims, duration..."
              value={textContent}
              onChange={(e) => setTextContent(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-xs text-white focus:outline-none focus:border-sky-500"
            />
          </div>

          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setActiveTab('list')}
              className="px-4 py-2 text-xs text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !textContent.trim()}
              className="px-4 py-2 text-xs font-semibold bg-sky-600 text-white rounded-lg hover:bg-sky-500 disabled:opacity-50"
            >
              {isSubmitting ? 'Recording...' : 'Save Text Evidence'}
            </button>
          </div>
        </form>
      )}

      {/* Evidence List */}
      {activeTab === 'list' && (
        <div className="divide-y divide-slate-800">
          {evidenceList.length === 0 ? (
            <div className="p-8 text-center text-slate-500 text-xs">
              No evidence uploaded yet. Click "Upload File", "Add Text Note", or "Load Hero Demo".
            </div>
          ) : (
            evidenceList.map((ev) => (
              <div
                key={ev.id}
                className="p-4 hover:bg-slate-800/40 transition flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-1.5 flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] font-mono font-semibold bg-slate-800 border border-slate-700 text-slate-300">
                      {getSourceIcon(ev.source_type)}
                      <span>{ev.id}</span>
                    </span>
                    <span className="text-xs font-medium text-white truncate max-w-xs md:max-w-md">
                      {ev.file_name}
                    </span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded font-mono font-semibold ${
                        ev.processing_status === 'EXTRACTED'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : ev.processing_status === 'PROCESSING'
                          ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}
                    >
                      {ev.processing_status}
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-slate-400 font-mono">
                    <span className="flex items-center space-x-1" title={ev.file_hash}>
                      <Hash className="w-3 h-3 text-slate-500" />
                      <span>{ev.file_hash.substring(0, 14)}...</span>
                    </span>
                    {ev.location && (
                      <span className="flex items-center space-x-1">
                        <MapPin className="w-3 h-3 text-slate-500" />
                        <span className="text-slate-300">{ev.location}</span>
                      </span>
                    )}
                    {ev.uploader && (
                      <span className="flex items-center space-x-1">
                        <User className="w-3 h-3 text-slate-500" />
                        <span>{ev.uploader}</span>
                      </span>
                    )}
                  </div>

                  {ev.raw_text && (
                    <div className="mt-2 p-2 rounded bg-slate-950 border border-slate-800/80 text-[11px] text-slate-300 font-mono line-clamp-2">
                      "{ev.raw_text}"
                    </div>
                  )}
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  <a
                    href={api.getEvidenceFileUrl(ev.id)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-1.5 rounded-lg border border-slate-700 bg-slate-800/60 text-slate-300 hover:text-white hover:bg-slate-700 text-xs flex items-center space-x-1"
                    title="View Original Evidence File"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    <span className="hidden sm:inline">Inspect</span>
                  </a>

                  {ev.processing_status !== 'EXTRACTED' && (
                    <button
                      onClick={() => handleExtractSingle(ev.id)}
                      disabled={extractingId === ev.id}
                      className="px-2.5 py-1.5 rounded-lg border border-sky-500/30 bg-sky-500/10 text-sky-300 hover:bg-sky-500/20 text-xs font-medium flex items-center space-x-1 disabled:opacity-50"
                    >
                      <Sparkles className="w-3 h-3" />
                      <span>{extractingId === ev.id ? 'Extracting...' : 'Extract'}</span>
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
