"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { FolderKanban, Plus, Search, Mic2, ShieldCheck, ChevronRight, Filter, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import { NavigationRail } from "@/components/NavigationRail";
import { PersistentAudioPlayer } from "@/components/PersistentAudioPlayer";
import { CommandPalette } from "@/components/CommandPalette";
import { VoiceBriefingModal } from "@/components/VoiceBriefingModal";

export default function WorkspaceIndex() {
  const [investigations, setInvestigations] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [newModalOpen, setNewModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [newLang, setNewLang] = useState("indic-auto");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchInvestigations = async () => {
    setLoading(true);
    try {
      const data = await api.listInvestigations(statusFilter, search);
      setInvestigations(data);
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvestigations();
  }, [statusFilter]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    setIsSubmitting(true);
    try {
      await api.createInvestigation({
        title: newTitle,
        description: newDesc,
        primary_language: newLang
      });
      setNewModalOpen(false);
      setNewTitle("");
      setNewDesc("");
      fetchInvestigations();
    } catch (err: any) {
      alert("Failed to create investigation: " + err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#101B2B] text-[#F6F5F1] overflow-hidden">
      <NavigationRail onNewInvestigation={() => setNewModalOpen(true)} />
      <CommandPalette />
      <VoiceBriefingModal />

      <main className="flex-1 flex flex-col overflow-y-auto pb-24">
        {/* Top App Bar */}
        <header className="p-6 border-b border-[#1E2C3D] flex items-center justify-between bg-[#0B121D]">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs text-[#2A8C85]">WORKSPACE / ACTIVE DOSSIERS</span>
              <span className="px-1.5 py-0.2 rounded bg-[#2A8C85]/20 text-[#2A8C85] text-[10px] font-mono border border-[#2A8C85]/40">
                Gnani Prisma Connected
              </span>
            </div>
            <h1 className="text-xl font-bold tracking-tight text-[#F6F5F1] mt-1">
              Audio Evidence Investigations
            </h1>
          </div>

          <button
            onClick={() => setNewModalOpen(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded bg-[#2A8C85] text-white text-xs font-medium hover:bg-[#2A8C85]/90 transition-colors shadow-sm"
          >
            <Plus className="w-4 h-4" />
            <span>New Investigation</span>
          </button>
        </header>

        {/* Content Body */}
        <div className="p-8 max-w-6xl w-full mx-auto space-y-6">
          {/* Search & Filter Controls */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="relative w-full sm:w-96">
              <Search className="w-4 h-4 text-[#F6F5F1]/40 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search investigations by title or keyword..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && fetchInvestigations()}
                className="w-full pl-9 pr-4 py-2 rounded bg-[#0B121D] border border-[#1E2C3D] text-xs text-[#F6F5F1] focus:outline-none focus:border-[#2A8C85]"
              />
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto text-xs font-mono">
              {["all", "active", "under_review", "closed"].map((st) => (
                <button
                  key={st}
                  onClick={() => setStatusFilter(st)}
                  className={`px-3 py-1.5 rounded capitalize transition-colors ${
                    statusFilter === st
                      ? "bg-[#18263A] text-[#2A8C85] border border-[#2A8C85]/40"
                      : "bg-[#0B121D] text-[#F6F5F1]/50 border border-[#1E2C3D] hover:text-[#F6F5F1]"
                  }`}
                >
                  {st.replace("_", " ")}
                </button>
              ))}
            </div>
          </div>

          {/* Investigation Cards */}
          {loading ? (
            <div className="py-20 text-center font-mono text-xs text-[#F6F5F1]/40">
              Loading investigation records...
            </div>
          ) : investigations.length === 0 ? (
            <div className="p-12 text-center border border-dashed border-[#1E2C3D] rounded-xl bg-[#0B121D]">
              <FolderKanban className="w-10 h-10 text-[#2A8C85]/60 mx-auto mb-3" />
              <h3 className="text-sm font-medium text-[#F6F5F1]">No investigations found</h3>
              <p className="text-xs text-[#F6F5F1]/50 mt-1 max-w-sm mx-auto">
                Create a new investigation to ingest multilingual audio recordings or inspect sample cases.
              </p>
              <button
                onClick={() => setNewModalOpen(true)}
                className="mt-4 px-3.5 py-2 rounded bg-[#2A8C85] text-white text-xs font-medium hover:bg-[#2A8C85]/90 inline-flex items-center gap-2"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Create Investigation</span>
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {investigations.map((inv) => (
                <Link
                  key={inv.id}
                  href={`/workspace/investigations/${inv.id}`}
                  className="p-5 rounded-xl bg-[#0B121D] border border-[#1E2C3D] hover:border-[#2A8C85]/60 transition-all hover:shadow-xl hover:shadow-[#2A8C85]/5 flex flex-col justify-between group"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2">
                        {inv.is_sample && (
                          <span className="px-1.5 py-0.5 rounded bg-[#C89448]/20 text-[#C89448] text-[9px] font-mono border border-[#C89448]/40">
                            SAMPLE DOSSIER
                          </span>
                        )}
                        <span className="px-2 py-0.5 rounded bg-[#18263A] text-[10px] font-mono text-[#F6F5F1]/70 uppercase border border-[#1E2C3D]">
                          {inv.status.replace("_", " ")}
                        </span>
                      </div>

                      <span className="text-[10px] font-mono text-[#2A8C85]">
                        {inv.primary_language}
                      </span>
                    </div>

                    <h3 className="text-sm font-semibold text-[#F6F5F1] group-hover:text-[#2A8C85] transition-colors leading-snug">
                      {inv.title}
                    </h3>

                    {inv.description && (
                      <p className="text-xs text-[#F6F5F1]/60 line-clamp-2 mt-2 leading-relaxed">
                        {inv.description}
                      </p>
                    )}
                  </div>

                  <div className="mt-5 pt-3 border-t border-[#1E2C3D] flex items-center justify-between text-xs font-mono text-[#F6F5F1]/50">
                    <div className="flex items-center gap-4">
                      <span className="flex items-center gap-1">
                        <Mic2 className="w-3.5 h-3.5 text-[#2A8C85]" />
                        <span>{inv.audio_assets_count} audio files</span>
                      </span>
                      <span className="flex items-center gap-1">
                        <ShieldCheck className="w-3.5 h-3.5 text-[#C89448]" />
                        <span>{inv.claims_count} claims</span>
                      </span>
                    </div>

                    <span className="flex items-center gap-1 text-[#2A8C85] group-hover:translate-x-1 transition-transform">
                      <span>Open</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Modal: Create Investigation */}
        {newModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <div className="w-full max-w-lg bg-[#0B121D] border border-[#1E2C3D] rounded-xl p-5 space-y-4 shadow-2xl">
              <h3 className="text-sm font-semibold text-[#F6F5F1] flex items-center gap-2">
                <Plus className="w-4 h-4 text-[#2A8C85]" />
                <span>Create Evidence Investigation</span>
              </h3>

              <form onSubmit={handleCreate} className="space-y-3 text-xs">
                <div>
                  <label className="block text-xs font-mono text-[#F6F5F1]/60 mb-1">
                    INVESTIGATION TITLE
                  </label>
                  <input
                    required
                    type="text"
                    placeholder="e.g. Maharashtra Rural Electrification Fund Verification"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    className="w-full px-3 py-2 rounded bg-[#101B2B] border border-[#1E2C3D] text-[#F6F5F1]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-mono text-[#F6F5F1]/60 mb-1">
                    DESCRIPTION / SCOPE
                  </label>
                  <textarea
                    rows={3}
                    placeholder="Describe the context, recorded source, and checkable claims..."
                    value={newDesc}
                    onChange={(e) => setNewDesc(e.target.value)}
                    className="w-full p-2.5 rounded bg-[#101B2B] border border-[#1E2C3D] text-[#F6F5F1]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-mono text-[#F6F5F1]/60 mb-1">
                    PRIMARY AUDIO LANGUAGE (GNANI PRISMA)
                  </label>
                  <select
                    value={newLang}
                    onChange={(e) => setNewLang(e.target.value)}
                    className="w-full px-3 py-2 rounded bg-[#101B2B] border border-[#1E2C3D] text-[#F6F5F1]"
                  >
                    <option value="indic-auto">Auto Indic Language Detection</option>
                    <option value="en-IN">Indian English</option>
                    <option value="hi-IN">Hindi</option>
                    <option value="kn-IN">Kannada</option>
                    <option value="ta-IN">Tamil</option>
                    <option value="te-IN">Telugu</option>
                    <option value="mr-IN">Marathi</option>
                    <option value="gu-IN">Gujarati</option>
                    <option value="bn-IN">Bengali</option>
                    <option value="ml-IN">Malayalam</option>
                    <option value="pa-IN">Punjabi</option>
                  </select>
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setNewModalOpen(false)}
                    className="px-3 py-1.5 rounded bg-[#18263A] text-xs text-[#F6F5F1]/60 hover:text-[#F6F5F1]"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="px-4 py-1.5 rounded bg-[#2A8C85] text-xs text-white font-medium hover:bg-[#2A8C85]/90 disabled:opacity-50"
                  >
                    {isSubmitting ? "Creating..." : "Create Investigation"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>

      <PersistentAudioPlayer />
    </div>
  );
}
