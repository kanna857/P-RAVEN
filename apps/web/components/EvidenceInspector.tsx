"use client";

import { useState } from "react";
import { Link2, ExternalLink, Plus, Trash2, X, CheckCircle, XCircle, Shield } from "lucide-react";
import { useRavenStore } from "@/lib/store";
import { api } from "@/lib/api";

interface EvidenceItem {
  link_id: string;
  claim_id: string;
  claim_text: string;
  evidence_id: string;
  title: string;
  url?: string;
  publisher?: string;
  publication_date?: string;
  excerpt?: string;
  reliability_tier: string;
  supports_or_refutes: string;
  relevance_rationale?: string;
}

export function EvidenceInspector({
  investigationId,
  evidenceList,
  onRefresh
}: {
  investigationId: string;
  evidenceList: EvidenceItem[];
  onRefresh: () => void;
}) {
  const { selectedClaimId, setSelectedClaimId } = useRavenStore();
  const [isAdding, setIsAdding] = useState(false);
  const [title, setTitle] = useState("");
  const [url, setUrl] = useState("");
  const [publisher, setPublisher] = useState("");
  const [excerpt, setExcerpt] = useState("");
  const [stance, setStance] = useState("supports");
  const [tier, setTier] = useState("primary_verified");
  const [rationale, setRationale] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Filter evidence by selected claim if one is picked
  const filteredEvidence = selectedClaimId
    ? evidenceList.filter((e) => e.claim_id === selectedClaimId)
    : evidenceList;

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedClaimId) {
      alert("Please select a claim to attach evidence to.");
      return;
    }

    setIsSubmitting(true);
    try {
      await api.addEvidence({
        claim_id: selectedClaimId,
        title,
        url,
        publisher,
        excerpt,
        reliability_tier: tier,
        supports_or_refutes: stance,
        relevance_rationale: rationale
      });

      setTitle("");
      setUrl("");
      setPublisher("");
      setExcerpt("");
      setRationale("");
      setIsAdding(false);
      onRefresh();
    } catch (err: any) {
      alert("Failed to attach evidence: " + err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRemove = async (linkId: string) => {
    if (!confirm("Are you sure you want to remove this evidence citation?")) return;
    try {
      await api.removeEvidence(linkId);
      onRefresh();
    } catch (err: any) {
      alert("Failed to remove citation: " + err.message);
    }
  };

  return (
    <div className="bg-[#0B121D] border border-[#1E2C3D] rounded-xl overflow-hidden flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-[#1E2C3D] flex items-center justify-between bg-[#101B2B]">
        <div className="flex items-center gap-2.5">
          <Link2 className="w-4 h-4 text-[#2A8C85]" />
          <div>
            <h3 className="text-xs font-semibold text-[#F6F5F1] tracking-wide uppercase font-mono">
              EVIDENCE WORKSPACE
            </h3>
            <p className="text-[11px] text-[#F6F5F1]/50 font-mono">
              {selectedClaimId ? "Filtered to selected claim" : "All investigation citations"}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {selectedClaimId && (
            <button
              onClick={() => setSelectedClaimId(null)}
              className="text-[11px] font-mono text-[#F6F5F1]/50 hover:text-[#F6F5F1] px-2 py-1 rounded bg-[#18263A]"
            >
              Clear Filter
            </button>
          )}

          {selectedClaimId && (
            <button
              onClick={() => setIsAdding(!isAdding)}
              className="flex items-center gap-1 px-2.5 py-1 rounded bg-[#2A8C85] text-white text-xs font-medium hover:bg-[#2A8C85]/90 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Link Source</span>
            </button>
          )}
        </div>
      </div>

      {/* Add Evidence Form */}
      {isAdding && (
        <form onSubmit={handleAdd} className="p-4 border-b border-[#1E2C3D] bg-[#101B2B]/90 space-y-3 text-xs">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[11px] text-[#2A8C85]">ATTACH CORROBORATING SOURCE</span>
            <button type="button" onClick={() => setIsAdding(false)} className="text-[#F6F5F1]/50 hover:text-[#F6F5F1]">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          <input
            required
            type="text"
            placeholder="Document or Report Title (e.g., KSPCB Regional Water Audit)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-2.5 py-1.5 rounded bg-[#0B121D] border border-[#1E2C3D] text-[#F6F5F1]"
          />

          <div className="grid grid-cols-2 gap-2">
            <input
              type="url"
              placeholder="Source URL (Optional)"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full px-2.5 py-1.5 rounded bg-[#0B121D] border border-[#1E2C3D] text-[#F6F5F1]"
            />
            <input
              type="text"
              placeholder="Publisher / Authority"
              value={publisher}
              onChange={(e) => setPublisher(e.target.value)}
              className="w-full px-2.5 py-1.5 rounded bg-[#0B121D] border border-[#1E2C3D] text-[#F6F5F1]"
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <select
              value={stance}
              onChange={(e) => setStance(e.target.value)}
              className="w-full px-2.5 py-1.5 rounded bg-[#0B121D] border border-[#1E2C3D] text-[#F6F5F1]"
            >
              <option value="supports">Supports Claim</option>
              <option value="refutes">Refutes Claim</option>
              <option value="contextualizes">Adds Neutral Context</option>
            </select>

            <select
              value={tier}
              onChange={(e) => setTier(e.target.value)}
              className="w-full px-2.5 py-1.5 rounded bg-[#0B121D] border border-[#1E2C3D] text-[#F6F5F1]"
            >
              <option value="primary_verified">Primary Official / Gazette / Court</option>
              <option value="secondary_reputable">Reputable News / Academic Paper</option>
              <option value="unverified_claim">Unverified Third-Party Allegation</option>
            </select>
          </div>

          <textarea
            placeholder="Direct Excerpt or Laboratory Finding..."
            value={excerpt}
            onChange={(e) => setExcerpt(e.target.value)}
            rows={2}
            className="w-full p-2 rounded bg-[#0B121D] border border-[#1E2C3D] text-[#F6F5F1]"
          />

          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsAdding(false)}
              className="px-3 py-1 rounded bg-[#18263A] text-[#F6F5F1]/60"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-1 rounded bg-[#2A8C85] text-white font-medium hover:bg-[#2A8C85]/90 disabled:opacity-50"
            >
              {isSubmitting ? "Linking..." : "Attach Evidence"}
            </button>
          </div>
        </form>
      )}

      {/* Citations List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {filteredEvidence.length === 0 ? (
          <div className="text-center py-16 text-xs text-[#F6F5F1]/40 font-mono">
            {selectedClaimId
              ? "No evidence linked to this claim yet. Click 'Link Source' to corroborate."
              : "Select a claim in the Claim Explorer to view or attach evidence."}
          </div>
        ) : (
          filteredEvidence.map((ev) => (
            <div
              key={ev.link_id}
              className="p-3.5 rounded-lg bg-[#101B2B]/70 border border-[#1E2C3D] space-y-2 text-xs"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    {ev.supports_or_refutes === "supports" ? (
                      <span className="flex items-center gap-1 text-[10px] font-mono text-[#2A8C85]">
                        <CheckCircle className="w-3 h-3" />
                        <span>SUPPORTS</span>
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-[10px] font-mono text-[#E06C75]">
                        <XCircle className="w-3 h-3" />
                        <span>REFUTES</span>
                      </span>
                    )}

                    <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-[#18263A] text-[#F6F5F1]/60 border border-[#1E2C3D]">
                      {ev.reliability_tier.replace("_", " ").toUpperCase()}
                    </span>
                  </div>
                  <h4 className="font-medium text-[#F6F5F1] leading-snug">{ev.title}</h4>
                  {ev.publisher && (
                    <p className="text-[11px] font-mono text-[#F6F5F1]/50 mt-0.5">{ev.publisher}</p>
                  )}
                </div>

                <button
                  onClick={() => handleRemove(ev.link_id)}
                  title="Remove citation link"
                  className="p-1 rounded text-[#F6F5F1]/30 hover:text-[#A63D40] transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>

              {ev.excerpt && (
                <p className="p-2 rounded bg-[#0B121D] border border-[#1E2C3D]/60 text-[11px] text-[#F6F5F1]/80 italic">
                  "{ev.excerpt}"
                </p>
              )}

              {ev.relevance_rationale && (
                <p className="text-[11px] text-[#2A8C85]/90">
                  <span className="font-mono text-[10px] text-[#F6F5F1]/40 uppercase">Rationale:</span> {ev.relevance_rationale}
                </p>
              )}

              {ev.url && (
                <a
                  href={ev.url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-[10px] font-mono text-[#2A8C85] hover:underline"
                >
                  <span>{ev.url}</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </a>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
