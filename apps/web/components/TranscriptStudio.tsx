"use client";

import { useState } from "react";
import { Play, Edit2, Check, X, Download, FileText, ChevronDown } from "lucide-react";
import { useRavenStore } from "@/lib/store";
import { api } from "@/lib/api";

interface Segment {
  id: string;
  job_id: string;
  start_time: number;
  end_time: number;
  text: string;
  speaker_label: string;
  confidence?: number;
  language?: string;
  order_index: number;
}

export function TranscriptStudio({
  transcriptJobId,
  segments,
  detectedLanguage,
  onSegmentUpdated
}: {
  transcriptJobId?: string;
  segments: Segment[];
  detectedLanguage?: string;
  onSegmentUpdated: () => void;
}) {
  const { currentTime, seekTo } = useRavenStore();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");
  const [editSpeaker, setEditSpeaker] = useState("");
  const [exportOpen, setExportOpen] = useState(false);

  const formatSecs = (s: number) => {
    const mins = Math.floor(s / 60);
    const secs = (s % 60).toFixed(1);
    return `${mins.toString().padStart(2, "0")}:${secs.padStart(4, "0")}`;
  };

  const startEdit = (seg: Segment) => {
    setEditingId(seg.id);
    setEditText(seg.text);
    setEditSpeaker(seg.speaker_label);
  };

  const saveEdit = async (seg: Segment) => {
    if (!transcriptJobId) return;
    try {
      await api.updateSegment(transcriptJobId, seg.id, editText, editSpeaker);
      setEditingId(null);
      onSegmentUpdated();
    } catch (e: any) {
      alert("Failed to save correction: " + e.message);
    }
  };

  return (
    <div className="bg-[#0B121D] border border-[#1E2C3D] rounded-xl overflow-hidden flex flex-col h-full">
      {/* Studio Header */}
      <div className="p-4 border-b border-[#1E2C3D] flex items-center justify-between bg-[#101B2B]">
        <div className="flex items-center gap-3">
          <FileText className="w-4 h-4 text-[#2A8C85]" />
          <div>
            <h3 className="text-xs font-semibold text-[#F6F5F1] tracking-wide uppercase font-mono">
              TRANSCRIPT STUDIO
            </h3>
            <p className="text-[11px] text-[#F6F5F1]/50 font-mono">
              Detected: <span className="text-[#2A8C85]">{detectedLanguage || "indic-auto"}</span> • {segments.length} verified segments
            </p>
          </div>
        </div>

        {/* Export Dropdown */}
        <div className="relative">
          <button
            onClick={() => setExportOpen(!exportOpen)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#18263A] border border-[#1E2C3D] text-xs text-[#F6F5F1] hover:border-[#2A8C85]/50 transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-[#2A8C85]" />
            <span>Export</span>
            <ChevronDown className="w-3 h-3 text-[#F6F5F1]/40" />
          </button>

          {exportOpen && transcriptJobId && (
            <div className="absolute right-0 mt-1 w-36 bg-[#0B121D] border border-[#1E2C3D] rounded shadow-xl py-1 z-20 font-mono text-xs">
              <a
                href={api.getTranscriptExportUrl(transcriptJobId, "srt")}
                download
                onClick={() => setExportOpen(false)}
                className="block px-3 py-1.5 text-[#F6F5F1]/80 hover:bg-[#18263A] hover:text-[#2A8C85]"
              >
                SubRip (.SRT)
              </a>
              <a
                href={api.getTranscriptExportUrl(transcriptJobId, "txt")}
                download
                onClick={() => setExportOpen(false)}
                className="block px-3 py-1.5 text-[#F6F5F1]/80 hover:bg-[#18263A] hover:text-[#2A8C85]"
              >
                Plain Text (.TXT)
              </a>
              <a
                href={api.getTranscriptExportUrl(transcriptJobId, "json")}
                download
                onClick={() => setExportOpen(false)}
                className="block px-3 py-1.5 text-[#F6F5F1]/80 hover:bg-[#18263A] hover:text-[#2A8C85]"
              >
                Structured (.JSON)
              </a>
            </div>
          )}
        </div>
      </div>

      {/* Segments Stream */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {segments.length === 0 ? (
          <div className="text-center py-16 text-xs text-[#F6F5F1]/40 font-mono">
            No transcript segments yet. Upload an audio recording to trigger Gnani Prisma STT.
          </div>
        ) : (
          segments.map((seg) => {
            const isPlayingThis = currentTime >= seg.start_time && currentTime <= seg.end_time;
            const isEditing = editingId === seg.id;

            return (
              <div
                key={seg.id}
                className={`p-3.5 rounded-lg border transition-all ${
                  isPlayingThis
                    ? "bg-[#18263A]/90 border-[#2A8C85] shadow-lg shadow-[#2A8C85]/10"
                    : "bg-[#101B2B]/60 border-[#1E2C3D] hover:border-[#2A8C85]/40"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {/* Timestamp seek button */}
                    <button
                      onClick={() => seekTo(seg.start_time)}
                      className="flex items-center gap-1 px-2 py-0.5 rounded bg-[#0B121D] border border-[#1E2C3D] font-mono text-[10px] text-[#2A8C85] hover:border-[#2A8C85] transition-colors"
                    >
                      <Play className="w-2.5 h-2.5 fill-[#2A8C85]" />
                      <span>{formatSecs(seg.start_time)} - {formatSecs(seg.end_time)}</span>
                    </button>

                    <span className="text-xs font-medium text-[#F6F5F1]/80 font-mono">
                      {seg.speaker_label}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    {seg.confidence && (
                      <span className="text-[10px] font-mono text-[#F6F5F1]/40">
                        {Math.round(seg.confidence * 100)}% conf
                      </span>
                    )}

                    {!isEditing && (
                      <button
                        onClick={() => startEdit(seg)}
                        title="Correct transcript"
                        className="p-1 rounded text-[#F6F5F1]/40 hover:text-[#F6F5F1] hover:bg-[#18263A] transition-colors"
                      >
                        <Edit2 className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                </div>

                {isEditing ? (
                  <div className="space-y-2 mt-2">
                    <input
                      type="text"
                      value={editSpeaker}
                      onChange={(e) => setEditSpeaker(e.target.value)}
                      placeholder="Speaker label"
                      className="w-full px-2 py-1 rounded bg-[#0B121D] border border-[#1E2C3D] text-xs text-[#F6F5F1] font-mono"
                    />
                    <textarea
                      value={editText}
                      onChange={(e) => setEditText(e.target.value)}
                      rows={3}
                      className="w-full p-2 rounded bg-[#0B121D] border border-[#1E2C3D] text-xs text-[#F6F5F1] focus:outline-none focus:border-[#2A8C85]"
                    />
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => setEditingId(null)}
                        className="px-2.5 py-1 rounded bg-[#18263A] text-xs text-[#F6F5F1]/60 hover:text-[#F6F5F1]"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => saveEdit(seg)}
                        className="flex items-center gap-1 px-3 py-1 rounded bg-[#2A8C85] text-xs text-white font-medium hover:bg-[#2A8C85]/90"
                      >
                        <Check className="w-3 h-3" />
                        <span>Save Revision</span>
                      </button>
                    </div>
                  </div>
                ) : (
                  <p
                    onClick={() => seekTo(seg.start_time)}
                    className="text-xs text-[#F6F5F1]/90 leading-relaxed cursor-pointer select-text hover:text-white transition-colors"
                  >
                    {seg.text}
                  </p>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
