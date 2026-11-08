"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { 
  ChevronLeft, 
  UploadCloud, 
  Sparkles, 
  Volume2, 
  FileDown, 
  Play, 
  Radio, 
  ShieldCheck, 
  FileText, 
  Loader2,
  Share2
} from "lucide-react";
import { api } from "@/lib/api";
import { useRavenStore } from "@/lib/store";
import { NavigationRail } from "@/components/NavigationRail";
import { PersistentAudioPlayer } from "@/components/PersistentAudioPlayer";
import { CommandPalette } from "@/components/CommandPalette";
import { TranscriptStudio } from "@/components/TranscriptStudio";
import { ClaimExplorer } from "@/components/ClaimExplorer";
import { EvidenceInspector } from "@/components/EvidenceInspector";
import { AudioLabModal } from "@/components/AudioLabModal";
import { VoiceBriefingModal } from "@/components/VoiceBriefingModal";

export default function InvestigationDetailPage() {
  const params = useParams();
  const id = params?.id as string;
  const router = useRouter();

  const [investigation, setInvestigation] = useState<any>(null);
  const [transcript, setTranscript] = useState<any>(null);
  const [claims, setClaims] = useState<any[]>([]);
  const [evidenceList, setEvidenceList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [audioLabOpen, setAudioLabOpen] = useState(false);
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [generatedReport, setGeneratedReport] = useState<any>(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);

  const { setActiveAudio, setVoiceBriefingModal } = useRavenStore();

  const loadData = async () => {
    if (!id) return;
    try {
      const inv = await api.getInvestigation(id);
      setInvestigation(inv);

      // Load transcript
      try {
        const trans = await api.getTranscript(id);
        setTranscript(trans);

        // Preload active audio into persistent player
        if (trans.audio_asset_id) {
          setActiveAudio({
            assetId: trans.audio_asset_id,
            url: api.getAudioFileUrl(trans.audio_asset_id),
            title: inv.title
          });
        }
      } catch (_) {}

      // Load claims
      const cl = await api.listClaims(id);
      setClaims(cl);

      // Load evidence
      const ev = await api.listEvidence(id);
      setEvidenceList(ev);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleGenerateReport = async () => {
    setIsGeneratingReport(true);
    try {
      const rep = await api.generateReport(id, `Verification Dossier: ${investigation.title}`);
      setGeneratedReport(rep);
      setReportModalOpen(true);
    } catch (err: any) {
      alert("Report generation failed: " + err.message);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#101B2B] text-[#F6F5F1] font-mono text-xs">
        <Loader2 className="w-5 h-5 animate-spin text-[#2A8C85] mr-2" />
        <span>Loading investigation intelligence dossier...</span>
      </div>
    );
  }

  if (!investigation) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#101B2B] text-[#F6F5F1] font-mono text-xs">
        Investigation not found. <Link href="/workspace" className="text-[#2A8C85] ml-2 underline">Return</Link>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-[#101B2B] text-[#F6F5F1] overflow-hidden">
      <NavigationRail />
      <CommandPalette />
      <VoiceBriefingModal />
      <AudioLabModal
        isOpen={audioLabOpen}
        onClose={() => setAudioLabOpen(false)}
        investigationId={id}
        onSuccess={loadData}
      />

      <main className="flex-1 flex flex-col overflow-hidden pb-24">
        {/* Dossier Header */}
        <header className="p-4 px-6 border-b border-[#1E2C3D] flex items-center justify-between bg-[#0B121D] flex-shrink-0">
          <div className="flex items-center gap-4">
            <Link
              href="/workspace"
              className="p-1.5 rounded hover:bg-[#18263A] text-[#F6F5F1]/60 hover:text-[#F6F5F1] transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </Link>

            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-[10px] text-[#2A8C85] uppercase">
                  INVESTIGATION DOSSIER
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-[#18263A] text-[#F6F5F1]/60 border border-[#1E2C3D]">
                  {investigation.status.replace("_", " ").toUpperCase()}
                </span>
                {investigation.is_sample && (
                  <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-[#C89448]/20 text-[#C89448] border border-[#C89448]/40">
                    SAMPLE VERIFIED
                  </span>
                )}
                {claims.length > 0 && (
                  <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-[#101B2B] text-[#2A8C85] border border-[#2A8C85]/30">
                    Dual Review: {claims.filter(c => c.review_stage === "senior_approved").length}/{claims.length} ({Math.round((claims.filter(c => c.review_stage === "senior_approved").length / Math.max(1, claims.length)) * 100)}%)
                  </span>
                )}
              </div>
              <h1 className="text-base font-bold text-[#F6F5F1] tracking-tight">
                {investigation.title}
              </h1>
            </div>
          </div>

          {/* Action Toolbar */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setAudioLabOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#18263A] border border-[#1E2C3D] text-xs text-[#F6F5F1] hover:border-[#2A8C85] transition-colors"
            >
              <UploadCloud className="w-3.5 h-3.5 text-[#2A8C85]" />
              <span>Ingest Audio</span>
            </button>

            <button
              onClick={() => {
                const sampleBrief = `Executive voice summary for ${investigation.title}. Verified audio claims show primary contamination discrepancies against state records.`;
                setVoiceBriefingModal(true, sampleBrief);
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#18263A] border border-[#1E2C3D] text-xs text-[#F6F5F1] hover:border-[#C89448] transition-colors"
            >
              <Volume2 className="w-3.5 h-3.5 text-[#C89448]" />
              <span>Timbre Briefing</span>
            </button>

            <button
              disabled={isGeneratingReport}
              onClick={handleGenerateReport}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#2A8C85] text-white text-xs font-medium hover:bg-[#2A8C85]/90 transition-colors disabled:opacity-50"
            >
              {isGeneratingReport ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <FileDown className="w-3.5 h-3.5" />
              )}
              <span>Generate Report</span>
            </button>
          </div>
        </header>

        {/* 3-Column Workspace Grid */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-4 p-4 overflow-hidden">
          {/* Column 1: Transcript Studio (4 cols) */}
          <div className="lg:col-span-4 h-full overflow-hidden">
            <TranscriptStudio
              transcriptJobId={transcript?.id}
              segments={transcript?.segments || []}
              detectedLanguage={transcript?.detected_language}
              onSegmentUpdated={loadData}
            />
          </div>

          {/* Column 2: Claim Explorer (4 cols) */}
          <div className="lg:col-span-4 h-full overflow-hidden">
            <ClaimExplorer
              investigationId={id}
              claims={claims}
              onRefresh={loadData}
            />
          </div>

          {/* Column 3: Evidence Workspace (4 cols) */}
          <div className="lg:col-span-4 h-full overflow-hidden">
            <EvidenceInspector
              investigationId={id}
              evidenceList={evidenceList}
              onRefresh={loadData}
            />
          </div>
        </div>

        {/* Report Dossier Modal */}
        {reportModalOpen && generatedReport && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
            <div className="w-full max-w-2xl bg-[#0B121D] border border-[#1E2C3D] rounded-xl shadow-2xl p-6 space-y-4 max-h-[85vh] flex flex-col">
              <div className="flex items-center justify-between border-b border-[#1E2C3D] pb-3">
                <div className="flex items-center gap-2">
                  <FileText className="w-5 h-5 text-[#2A8C85]" />
                  <h3 className="text-sm font-semibold text-[#F6F5F1]">Executive Investigation Report</h3>
                </div>
                <div className="flex items-center gap-2">
                  <a
                    href={api.getReportExportUrl(generatedReport.id, "markdown")}
                    download
                    className="px-2.5 py-1 rounded bg-[#18263A] border border-[#1E2C3D] text-[11px] font-mono text-[#2A8C85] hover:border-[#2A8C85]"
                  >
                    Download Markdown
                  </a>
                  <a
                    href={api.getReportExportUrl(generatedReport.id, "json")}
                    download
                    className="px-2.5 py-1 rounded bg-[#18263A] border border-[#1E2C3D] text-[11px] font-mono text-[#F6F5F1]/70 hover:border-[#2A8C85]"
                  >
                    JSON
                  </a>
                  <button
                    onClick={() => setReportModalOpen(false)}
                    className="px-2 py-1 rounded text-xs text-[#F6F5F1]/50 hover:text-[#F6F5F1]"
                  >
                    ✕
                  </button>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto space-y-4 text-xs pr-2">
                <div className="p-3.5 rounded bg-[#101B2B] border border-[#1E2C3D]">
                  <h4 className="font-mono text-[10px] text-[#2A8C85] uppercase mb-1">EXECUTIVE SUMMARY</h4>
                  <p className="text-[#F6F5F1]/90 leading-relaxed">{generatedReport.executive_summary}</p>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div className="p-3 rounded bg-[#101B2B] border border-[#1E2C3D] text-center">
                    <span className="text-[10px] font-mono text-[#F6F5F1]/50">TOTAL CLAIMS</span>
                    <p className="text-xl font-bold text-[#F6F5F1] mt-1">{generatedReport.verdict_summary?.total_claims || 0}</p>
                  </div>
                  <div className="p-3 rounded bg-[#101B2B] border border-[#2A8C85]/30 text-center">
                    <span className="text-[10px] font-mono text-[#2A8C85]">SUPPORTED</span>
                    <p className="text-xl font-bold text-[#2A8C85] mt-1">{generatedReport.verdict_summary?.supported || 0}</p>
                  </div>
                  <div className="p-3 rounded bg-[#101B2B] border border-[#A63D40]/30 text-center">
                    <span className="text-[10px] font-mono text-[#E06C75]">REFUTED</span>
                    <p className="text-xl font-bold text-[#E06C75] mt-1">{generatedReport.verdict_summary?.refuted || 0}</p>
                  </div>
                </div>

                <div className="p-3.5 rounded bg-[#101B2B] border border-[#1E2C3D]">
                  <h4 className="font-mono text-[10px] text-[#F6F5F1]/50 uppercase mb-1">METHODOLOGY & STANDARDS</h4>
                  <p className="text-[#F6F5F1]/80 leading-relaxed">{generatedReport.methodology}</p>
                </div>

                <div className="p-3.5 rounded bg-[#101B2B] border border-[#1E2C3D]">
                  <h4 className="font-mono text-[10px] text-[#C89448] uppercase mb-1">LIMITATIONS & RTI CAVEATS</h4>
                  <p className="text-[#F6F5F1]/80 leading-relaxed">{generatedReport.limitations}</p>
                </div>

                <div className="p-3.5 rounded bg-[#0A1017] border border-[#1E2C3D] flex items-center justify-between">
                  <div>
                    <span className="font-mono text-[10px] text-[#F6F5F1]/50 uppercase block">APPROVAL WORKFLOW</span>
                    <span className="text-xs font-semibold text-[#2A8C85] capitalize">
                      Status: {generatedReport.approval_status?.replace("_", " ") || "Under Senior Review"}
                    </span>
                  </div>
                  {generatedReport.approval_status !== "senior_approved" && (
                    <button
                      onClick={async () => {
                        try {
                          await api.approveReport(generatedReport.id, "approve", "Report validated against official audit records.");
                          setGeneratedReport({ ...generatedReport, approval_status: "senior_approved" });
                          alert("Report successfully approved with Senior Analyst sign-off!");
                        } catch (e: any) {
                          alert(e.message);
                        }
                      }}
                      className="px-3 py-1.5 rounded bg-[#C89448] hover:bg-[#C89448]/90 text-black text-xs font-semibold"
                    >
                      Senior Reviewer Sign-Off
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      <PersistentAudioPlayer />
    </div>
  );
}
