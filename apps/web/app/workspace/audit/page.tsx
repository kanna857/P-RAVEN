"use client";

import { useEffect, useState } from "react";
import { History, Activity, ShieldCheck, Clock, ArrowDownLeft, Terminal } from "lucide-react";
import { api } from "@/lib/api";
import { NavigationRail } from "@/components/NavigationRail";
import { PersistentAudioPlayer } from "@/components/PersistentAudioPlayer";
import { CommandPalette } from "@/components/CommandPalette";
import { VoiceBriefingModal } from "@/components/VoiceBriefingModal";

export default function AuditPage() {
  const [auditEvents, setAuditEvents] = useState<any[]>([]);
  const [usageMetrics, setUsageMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [events, usage] = await Promise.all([
        api.getAuditTrail(),
        api.getUsageMetrics()
      ]);
      setAuditEvents(events);
      setUsageMetrics(usage);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="flex h-screen bg-[#101B2B] text-[#F6F5F1] overflow-hidden">
      <NavigationRail />
      <CommandPalette />
      <VoiceBriefingModal />

      <main className="flex-1 flex flex-col overflow-y-auto pb-24">
        <header className="p-6 border-b border-[#1E2C3D] flex items-center justify-between bg-[#0B121D]">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs text-[#2A8C85]">SECURITY & GOVERNANCE</span>
              <span className="px-1.5 py-0.2 rounded bg-[#18263A] text-[#F6F5F1]/60 text-[10px] font-mono border border-[#1E2C3D]">
                Immutable Audit Trail
              </span>
            </div>
            <h1 className="text-xl font-bold tracking-tight text-[#F6F5F1] mt-1">
              Audit Logs & Provider Telemetry
            </h1>
          </div>
        </header>

        <div className="p-8 max-w-5xl w-full mx-auto space-y-6">
          {/* Metrics Overview Cards */}
          {usageMetrics?.summary && (
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-[#0B121D] border border-[#1E2C3D]">
                <span className="text-[10px] font-mono text-[#F6F5F1]/50">API CALLS LOGGED</span>
                <p className="text-2xl font-bold text-[#F6F5F1] mt-1">{usageMetrics.summary.total_requests}</p>
                <span className="text-[10px] font-mono text-[#2A8C85]">100% Success Rate</span>
              </div>

              <div className="p-4 rounded-xl bg-[#0B121D] border border-[#2A8C85]/30">
                <span className="text-[10px] font-mono text-[#2A8C85]">PRISMA AUDIO SECONDS</span>
                <p className="text-2xl font-bold text-[#2A8C85] mt-1">{usageMetrics.summary.total_audio_seconds_processed}s</p>
                <span className="text-[10px] font-mono text-[#F6F5F1]/50">Multilingual Ingestion</span>
              </div>

              <div className="p-4 rounded-xl bg-[#0B121D] border border-[#C89448]/30">
                <span className="text-[10px] font-mono text-[#C89448]">TIMBRE TTS CHARS</span>
                <p className="text-2xl font-bold text-[#C89448] mt-1">{usageMetrics.summary.total_tts_characters_synthesized}</p>
                <span className="text-[10px] font-mono text-[#F6F5F1]/50">Neural Briefing Syntheses</span>
              </div>

              <div className="p-4 rounded-xl bg-[#0B121D] border border-[#1E2C3D]">
                <span className="text-[10px] font-mono text-[#F6F5F1]/50">AVERAGE LATENCY</span>
                <p className="text-2xl font-bold text-[#F6F5F1] mt-1">{usageMetrics.summary.average_latency_ms} ms</p>
                <span className="text-[10px] font-mono text-[#2A8C85]">Optimized Payload</span>
              </div>
            </div>
          )}

          {/* Audit Events Stream */}
          <div className="p-5 rounded-xl bg-[#0B121D] border border-[#1E2C3D] space-y-4">
            <div className="flex items-center gap-2">
              <History className="w-4 h-4 text-[#2A8C85]" />
              <h3 className="text-sm font-semibold text-[#F6F5F1]">Chronological Action Trail</h3>
            </div>

            <div className="divide-y divide-[#1E2C3D]/60 text-xs">
              {auditEvents.length === 0 ? (
                <div className="py-8 text-center font-mono text-xs text-[#F6F5F1]/40">
                  No audit events recorded yet.
                </div>
              ) : (
                auditEvents.map((evt) => (
                  <div key={evt.id} className="py-3 flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <div className="w-7 h-7 rounded bg-[#101B2B] border border-[#1E2C3D] flex items-center justify-center text-[#2A8C85] flex-shrink-0 mt-0.5">
                        <Terminal className="w-3.5 h-3.5" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-0.5">
                          <span className="font-mono text-xs font-semibold text-[#F6F5F1]">
                            {evt.action}
                          </span>
                          <span className="px-1.5 py-0.2 rounded bg-[#18263A] text-[9px] font-mono text-[#F6F5F1]/60 uppercase border border-[#1E2C3D]">
                            {evt.resource_type}
                          </span>
                        </div>
                        {evt.details && (
                          <p className="text-[11px] font-mono text-[#F6F5F1]/60">
                            {JSON.stringify(evt.details)}
                          </p>
                        )}
                      </div>
                    </div>

                    <span className="font-mono text-[10px] text-[#F6F5F1]/40 flex-shrink-0">
                      {new Date(evt.created_at).toLocaleString()}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>

      <PersistentAudioPlayer />
    </div>
  );
}
