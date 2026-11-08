"use client";

import { useState } from "react";
import { ShieldCheck, AlertTriangle, HelpCircle, CheckCircle2, XCircle, Search, Sparkles, Loader2, ArrowRight } from "lucide-react";
import { useRavenStore } from "@/lib/store";
import { api } from "@/lib/api";

interface ClaimItem {
  id: string;
  claim_text: string;
  category: string;
  uncertainty_score: number;
  status: string;
  review_stage?: string;
  senior_reviewer_id?: string;
  senior_notes?: string;
  senior_signed_at?: string;
  entities?: any[];
  coreference_notes?: string;
  order_index: number;
  evidence_count?: number;
  start_time?: number;
  end_time?: number;
}

export function ClaimExplorer({
  investigationId,
  claims,
  onRefresh
}: {
  investigationId: string;
  claims: ClaimItem[];
  onRefresh: () => void;
}) {
  const { seekTo, setSelectedClaimId, selectedClaimId } = useRavenStore();
  const [filter, setFilter] = useState("all");
  const [isExtracting, setIsExtracting] = useState(false);
  const [reviewingClaim, setReviewingClaim] = useState<ClaimItem | null>(null);
  const [seniorReviewingClaim, setSeniorReviewingClaim] = useState<ClaimItem | null>(null);
  const [decision, setDecision] = useState("verified_supported");
  const [seniorDecision, setSeniorDecision] = useState<"senior_approved" | "changes_requested">("senior_approved");
  const [seniorNotes, setSeniorNotes] = useState("");
  const [analystNotes, setAnalystNotes] = useState("");
  const [confidenceRating, setConfidenceRating] = useState(4);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSeniorReviewSubmit = async () => {
    if (!seniorReviewingClaim || !seniorNotes.trim()) {
      alert("Please provide senior review notes.");
      return;
    }

    setIsSubmitting(true);
    try {
      await api.seniorReviewClaim(seniorReviewingClaim.id, seniorDecision, seniorNotes);
      setSeniorReviewingClaim(null);
      setSeniorNotes("");
      onRefresh();
    } catch (e: any) {
      alert("Senior review failed: " + e.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleExtract = async () => {
    setIsExtracting(true);
    try {
      await api.extractClaims(investigationId);
      onRefresh();
    } catch (e: any) {
      alert("Claim extraction failed: " + e.message);
    } finally {
      setIsExtracting(false);
    }
  };

  const handleReviewSubmit = async () => {
    if (!reviewingClaim || !analystNotes.trim()) {
      alert("Please enter analyst verification notes.");
      return;
    }

    setIsSubmitting(true);
    try {
      await api.reviewClaim(reviewingClaim.id, decision, analystNotes, confidenceRating);
      setReviewingClaim(null);
      setAnalystNotes("");
      onRefresh();
    } catch (e: any) {
      alert("Review submission failed: " + e.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const filtered = claims.filter((c) => {
    if (filter === "all") return true;
    if (filter === "unreviewed") return c.status === "unreviewed";
    if (filter === "verified") return c.status.includes("supported");
    if (filter === "refuted") return c.status.includes("refuted");
    if (filter === "inconclusive") return c.status === "inconclusive";
    return true;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "verified_supported":
      case "supported":
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-[#2A8C85]/20 text-[#2A8C85] border border-[#2A8C85]/30 text-[10px] font-mono">
            <CheckCircle2 className="w-3 h-3" />
            <span>SUPPORTED</span>
          </span>
        );
      case "refuted":
      case "verified_refuted":
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-[#A63D40]/20 text-[#E06C75] border border-[#A63D40]/30 text-[10px] font-mono">
            <XCircle className="w-3 h-3" />
            <span>REFUTED</span>
          </span>
        );
      case "inconclusive":
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-[#C89448]/20 text-[#C89448] border border-[#C89448]/30 text-[10px] font-mono">
            <HelpCircle className="w-3 h-3" />
            <span>INCONCLUSIVE</span>
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-[#242C35] text-[#F6F5F1]/50 border border-[#1E2C3D] text-[10px] font-mono">
            <span>UNREVIEWED</span>
          </span>
        );
    }
  };

  return (
    <div className="bg-[#0B121D] border border-[#1E2C3D] rounded-xl overflow-hidden flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-[#1E2C3D] flex items-center justify-between bg-[#101B2B]">
        <div className="flex items-center gap-3">
          <ShieldCheck className="w-4 h-4 text-[#C89448]" />
          <div>
            <h3 className="text-xs font-semibold text-[#F6F5F1] tracking-wide uppercase font-mono">
              CLAIM EXPLORER & VERIFICATION
            </h3>
            <p className="text-[11px] text-[#F6F5F1]/50 font-mono">
              Human-in-the-loop evidence adjudication • {claims.length} checkable statements
            </p>
          </div>
        </div>

        {/* Action: Extract Claims with Evon/Heuristic */}
        <button
          onClick={handleExtract}
          disabled={isExtracting}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#18263A] border border-[#1E2C3D] text-xs text-[#F6F5F1] hover:border-[#2A8C85]/50 transition-colors disabled:opacity-50"
        >
          {isExtracting ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin text-[#2A8C85]" />
              <span className="font-mono text-[11px]">Extracting Claims...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-3.5 h-3.5 text-[#2A8C85]" />
              <span className="font-mono text-[11px]">Extract Claims</span>
            </>
          )}
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 p-2 px-4 border-b border-[#1E2C3D] bg-[#0B121D] text-xs font-mono">
        {["all", "unreviewed", "verified", "refuted", "inconclusive"].map((tab) => (
          <button
            key={tab}
            onClick={() => setFilter(tab)}
            className={`px-2.5 py-1 rounded capitalize transition-colors ${
              filter === tab
                ? "bg-[#18263A] text-[#2A8C85] border border-[#2A8C85]/40"
                : "text-[#F6F5F1]/50 hover:text-[#F6F5F1]"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Claims List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {filtered.length === 0 ? (
          <div className="text-center py-16 text-xs text-[#F6F5F1]/40 font-mono">
            No claims found for the selected filter.
          </div>
        ) : (
          filtered.map((claim) => {
            const isSelected = selectedClaimId === claim.id;

            return (
              <div
                key={claim.id}
                className={`p-4 rounded-lg border transition-all ${
                  isSelected
                    ? "bg-[#18263A] border-[#2A8C85] shadow-lg shadow-[#2A8C85]/10"
                    : "bg-[#101B2B]/70 border-[#1E2C3D] hover:border-[#2A8C85]/40"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {getStatusBadge(claim.status)}
                    <span className="px-1.5 py-0.5 rounded bg-[#0B121D] text-[10px] font-mono text-[#F6F5F1]/60 uppercase border border-[#1E2C3D]">
                      {claim.category}
                    </span>
                    {claim.review_stage === "senior_approved" ? (
                      <span className="px-1.5 py-0.5 rounded bg-emerald-950/60 text-[10px] font-mono text-emerald-400 border border-emerald-800/50">
                        Senior Signed-Off
                      </span>
                    ) : claim.review_stage === "primary_adjudicated" ? (
                      <span className="px-1.5 py-0.5 rounded bg-amber-950/60 text-[10px] font-mono text-amber-400 border border-amber-800/50">
                        Primary Adjudicated
                      </span>
                    ) : claim.review_stage === "changes_requested" ? (
                      <span className="px-1.5 py-0.5 rounded bg-rose-950/60 text-[10px] font-mono text-rose-400 border border-rose-800/50">
                        Changes Requested
                      </span>
                    ) : null}
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-[#F6F5F1]/50">
                      Uncertainty: {Math.round(claim.uncertainty_score * 100)}%
                    </span>
                    {claim.start_time !== undefined && (
                      <button
                        onClick={() => seekTo(claim.start_time!)}
                        className="px-1.5 py-0.5 rounded bg-[#0B121D] text-[10px] font-mono text-[#2A8C85] hover:border hover:border-[#2A8C85]"
                      >
                        Seek {claim.start_time.toFixed(1)}s
                      </button>
                    )}
                  </div>
                </div>

                <p className="text-xs text-[#F6F5F1] leading-relaxed mb-3">
                  "{claim.claim_text}"
                </p>

                <div className="flex items-center justify-between pt-2 border-t border-[#1E2C3D]/60 text-xs">
                  <button
                    onClick={() => setSelectedClaimId(claim.id)}
                    className="flex items-center gap-1.5 text-[11px] font-mono text-[#2A8C85] hover:underline"
                  >
                    <span>Inspect Evidence ({claim.evidence_count || 0})</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>

                  <div className="flex items-center gap-2">
                    {claim.review_stage === "primary_adjudicated" && (
                      <button
                        onClick={() => {
                          setSeniorReviewingClaim(claim);
                          setSeniorDecision("senior_approved");
                        }}
                        className="px-2.5 py-1 rounded bg-[#2A8C85]/20 border border-[#2A8C85]/40 text-[11px] font-mono text-[#2A8C85] hover:bg-[#2A8C85]/30"
                      >
                        Senior Sign-Off
                      </button>
                    )}

                    <button
                      onClick={() => {
                        setReviewingClaim(claim);
                        setDecision(claim.status !== "unreviewed" ? claim.status : "verified_supported");
                      }}
                      className="px-2.5 py-1 rounded bg-[#18263A] border border-[#1E2C3D] text-[11px] font-mono text-[#F6F5F1] hover:border-[#2A8C85]"
                    >
                      Adjudicate Claim
                    </button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Review Adjudication Modal */}
      {reviewingClaim && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg bg-[#0B121D] border border-[#1E2C3D] rounded-xl p-5 space-y-4 shadow-2xl">
            <h4 className="text-sm font-semibold text-[#F6F5F1] flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#2A8C85]" />
              <span>Human Analyst Adjudication</span>
            </h4>

            <div className="p-3 rounded bg-[#101B2B] border border-[#1E2C3D] text-xs text-[#F6F5F1]/80 italic">
              "{reviewingClaim.claim_text}"
            </div>

            <div>
              <label className="block text-xs font-mono text-[#F6F5F1]/60 mb-1.5">
                VERIFICATION VERDICT
              </label>
              <select
                value={decision}
                onChange={(e) => setDecision(e.target.value)}
                className="w-full px-3 py-2 rounded bg-[#101B2B] border border-[#1E2C3D] text-xs text-[#F6F5F1]"
              >
                <option value="verified_supported">Supported by Primary Evidence</option>
                <option value="refuted">Refuted by Primary Evidence</option>
                <option value="inconclusive">Inconclusive / Insufficient Public Corroboration</option>
                <option value="needs_context">Needs Additional Civic Context</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono text-[#F6F5F1]/60 mb-1.5">
                ANALYST JUSTIFICATION & CITATIONS
              </label>
              <textarea
                value={analystNotes}
                onChange={(e) => setAnalystNotes(e.target.value)}
                placeholder="Reference regulatory reports, official gazettes, or verified laboratory certificates..."
                rows={4}
                className="w-full p-2.5 rounded bg-[#101B2B] border border-[#1E2C3D] text-xs text-[#F6F5F1] focus:outline-none focus:border-[#2A8C85]"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setReviewingClaim(null)}
                className="px-3 py-1.5 rounded bg-[#18263A] text-xs text-[#F6F5F1]/60 hover:text-[#F6F5F1]"
              >
                Cancel
              </button>
              <button
                disabled={isSubmitting}
                onClick={handleReviewSubmit}
                className="px-4 py-1.5 rounded bg-[#2A8C85] text-xs text-white font-medium hover:bg-[#2A8C85]/90 disabled:opacity-50"
              >
                {isSubmitting ? "Saving..." : "Commit Verdict"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Second Analyst / Senior Review Modal */}
      {seniorReviewingClaim && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg bg-[#0B121D] border border-[#1E2C3D] rounded-xl p-5 space-y-4 shadow-2xl">
            <h4 className="text-sm font-semibold text-[#F6F5F1] flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#C89448]" />
              <span>Senior Analyst Sign-Off (Dual Review)</span>
            </h4>

            <div className="p-3 rounded bg-[#101B2B] border border-[#1E2C3D] text-xs text-[#F6F5F1]/80 italic">
              "{seniorReviewingClaim.claim_text}"
            </div>

            <div>
              <label className="block text-xs font-mono text-[#F6F5F1]/60 mb-1.5">
                SENIOR ADJUDICATION DECISION
              </label>
              <select
                value={seniorDecision}
                onChange={(e: any) => setSeniorDecision(e.target.value)}
                className="w-full px-3 py-2 rounded bg-[#101B2B] border border-[#1E2C3D] text-xs text-[#F6F5F1]"
              >
                <option value="senior_approved">Sign-Off & Approve Determination</option>
                <option value="changes_requested">Request Additional Evidentiary Review</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono text-[#F6F5F1]/60 mb-1.5">
                SENIOR REVIEWER AUDIT NOTES
              </label>
              <textarea
                value={seniorNotes}
                onChange={(e) => setSeniorNotes(e.target.value)}
                placeholder="Document verified regulatory sources, statutory cross-checks, or revision instructions..."
                rows={4}
                className="w-full p-2.5 rounded bg-[#101B2B] border border-[#1E2C3D] text-xs text-[#F6F5F1] focus:outline-none focus:border-[#2A8C85]"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setSeniorReviewingClaim(null)}
                className="px-3 py-1.5 rounded bg-[#18263A] text-xs text-[#F6F5F1]/60 hover:text-[#F6F5F1]"
              >
                Cancel
              </button>
              <button
                disabled={isSubmitting}
                onClick={handleSeniorReviewSubmit}
                className="px-4 py-1.5 rounded bg-[#C89448] text-xs text-black font-semibold hover:bg-[#C89448]/90 disabled:opacity-50"
              >
                {isSubmitting ? "Submitting..." : "Sign-Off Dual Review"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
