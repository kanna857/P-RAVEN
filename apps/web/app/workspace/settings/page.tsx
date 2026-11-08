"use client";

import { useEffect, useState } from "react";
import { Cpu, CheckCircle2, AlertTriangle, RefreshCw, Zap, Shield, Key, Globe, Terminal } from "lucide-react";
import { api } from "@/lib/api";
import { NavigationRail } from "@/components/NavigationRail";
import { PersistentAudioPlayer } from "@/components/PersistentAudioPlayer";
import { CommandPalette } from "@/components/CommandPalette";
import { VoiceBriefingModal } from "@/components/VoiceBriefingModal";

export default function SettingsAndHealthPage() {
  const [providerStatus, setProviderStatus] = useState<any>(null);
  const [ollamaStatus, setOllamaStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [pingResult, setPingResult] = useState<any>(null);
  const [pinging, setPinging] = useState(false);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const [data, ollama] = await Promise.all([
        api.getProvidersStatus(),
        api.getOllamaStatus().catch(() => null)
      ]);
      setProviderStatus(data);
      setOllamaStatus(ollama);
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleTestPing = async () => {
    setPinging(true);
    try {
      const res = await api.testProviderConnection();
      setPingResult(res);
    } catch (err: any) {
      setPingResult({ reachable: false, message: err.message, latency_ms: 0 });
    } finally {
      setPinging(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#101B2B] text-[#F6F5F1] overflow-hidden">
      <NavigationRail />
      <CommandPalette />
      <VoiceBriefingModal />

      <main className="flex-1 flex flex-col overflow-y-auto pb-24">
        <header className="p-6 border-b border-[#1E2C3D] flex items-center justify-between bg-[#0B121D]">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs text-[#2A8C85]">SYSTEM INTEGRATION & TELEMETRY</span>
              <span className="px-1.5 py-0.2 rounded bg-[#2A8C85]/20 text-[#2A8C85] text-[10px] font-mono border border-[#2A8C85]/40">
                Official Contest Spec
              </span>
            </div>
            <h1 className="text-xl font-bold tracking-tight text-[#F6F5F1] mt-1">
              Gnani AI Model Status & Connection Health
            </h1>
          </div>

          <button
            onClick={fetchStatus}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded bg-[#18263A] border border-[#1E2C3D] text-xs font-mono text-[#F6F5F1] hover:border-[#2A8C85]"
          >
            <RefreshCw className="w-3.5 h-3.5 text-[#2A8C85]" />
            <span>Refresh Telemetry</span>
          </button>
        </header>

        <div className="p-8 max-w-5xl w-full mx-auto space-y-6">
          {/* Live Smoke Test Ping Widget */}
          <div className="p-5 rounded-xl bg-[#0B121D] border border-[#1E2C3D] space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded bg-[#2A8C85]/20 border border-[#2A8C85]/40 flex items-center justify-center text-[#2A8C85]">
                  <Zap className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-[#F6F5F1]">Live Endpoint Connectivity Smoke Test</h3>
                  <p className="text-xs text-[#F6F5F1]/50 font-mono">Pings official base endpoint: https://api.vachana.ai/stt/v3</p>
                </div>
              </div>

              <button
                disabled={pinging}
                onClick={handleTestPing}
                className="flex items-center gap-2 px-4 py-2 rounded bg-[#2A8C85] text-white text-xs font-medium hover:bg-[#2A8C85]/90 transition-colors disabled:opacity-50"
              >
                {pinging ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Testing Connectivity...</span>
                  </>
                ) : (
                  <>
                    <Zap className="w-3.5 h-3.5" />
                    <span>Run Live Smoke Test</span>
                  </>
                )}
              </button>
            </div>

            {pingResult && (
              <div className="mt-3 p-3.5 rounded bg-[#101B2B] border border-[#1E2C3D] flex items-center justify-between text-xs font-mono">
                <div className="flex items-center gap-2">
                  {pingResult.reachable ? (
                    <CheckCircle2 className="w-4 h-4 text-[#2A8C85]" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-[#A63D40]" />
                  )}
                  <span className="text-[#F6F5F1]">{pingResult.message}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-[10px] text-[#F6F5F1]/40">LATENCY:</span>
                  <span className="text-[#2A8C85] font-bold">{pingResult.latency_ms} ms</span>
                </div>
              </div>
            )}
          </div>

          {/* Model Status Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* 1. Prisma STT */}
            <div className="p-5 rounded-xl bg-[#0B121D] border border-[#1E2C3D] space-y-4">
              <div className="flex items-center justify-between">
                <span className="px-2 py-0.5 rounded bg-[#2A8C85]/20 text-[#2A8C85] text-[10px] font-mono border border-[#2A8C85]/30">
                  {providerStatus?.gnani_prisma?.status === "active_ready" ? "LIVE API KEY SET" : "DEMO SIMULATION ACTIVE"}
                </span>
                <Globe className="w-4 h-4 text-[#2A8C85]" />
              </div>

              <div>
                <h4 className="text-sm font-semibold text-[#F6F5F1]">Gnani Prisma (STT)</h4>
                <p className="text-[11px] font-mono text-[#F6F5F1]/50 mt-0.5">Model: prisma-v3.0</p>
              </div>

              <div className="space-y-1.5 text-xs font-mono pt-3 border-t border-[#1E2C3D] text-[#F6F5F1]/70">
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">Endpoint:</span>
                  <span className="text-[11px] truncate max-w-[150px]">/stt/v3</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">Header:</span>
                  <span>X-API-Key-ID</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">Languages:</span>
                  <span>10 Indic + English</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">Auto Detect:</span>
                  <span className="text-[#2A8C85]">Supported</span>
                </div>
              </div>
            </div>

            {/* 2. Timbre TTS */}
            <div className="p-5 rounded-xl bg-[#0B121D] border border-[#1E2C3D] space-y-4">
              <div className="flex items-center justify-between">
                <span className="px-2 py-0.5 rounded bg-[#C89448]/20 text-[#C89448] text-[10px] font-mono border border-[#C89448]/30">
                  {providerStatus?.gnani_timbre?.status === "active_ready" ? "LIVE API KEY SET" : "SAMPLE SYNTHESIS ACTIVE"}
                </span>
                <Zap className="w-4 h-4 text-[#C89448]" />
              </div>

              <div>
                <h4 className="text-sm font-semibold text-[#F6F5F1]">Gnani Timbre (TTS)</h4>
                <p className="text-[11px] font-mono text-[#F6F5F1]/50 mt-0.5">Model: timbre-v2.5</p>
              </div>

              <div className="space-y-1.5 text-xs font-mono pt-3 border-t border-[#1E2C3D] text-[#F6F5F1]/70">
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">Endpoint:</span>
                  <span className="text-[11px] truncate max-w-[150px]">/api/v1/tts/inference</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">Voices:</span>
                  <span>Nalini, Karan</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">Output:</span>
                  <span>linear_pcm WAV 24kHz</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">Expressiveness:</span>
                  <span className="text-[#C89448]">Inline Audio Tags</span>
                </div>
              </div>
            </div>

            {/* 3. Evon 30B / Reasoning */}
            <div className="p-5 rounded-xl bg-[#0B121D] border border-[#1E2C3D] space-y-4">
              <div className="flex items-center justify-between">
                <span className="px-2 py-0.5 rounded bg-[#18263A] text-[#F6F5F1]/70 text-[10px] font-mono border border-[#1E2C3D]">
                  {providerStatus?.evon_reasoning?.status === "active_ready" ? "HOSTED EVON 30B" : "LOCAL HEURISTIC ENGINE"}
                </span>
                <Shield className="w-4 h-4 text-[#F6F5F1]/60" />
              </div>

              <div>
                <h4 className="text-sm font-semibold text-[#F6F5F1]">Gnani Evon (Reasoning)</h4>
                <p className="text-[11px] font-mono text-[#F6F5F1]/50 mt-0.5">gnani-evon-v3.3-30B-A3B</p>
              </div>

              <div className="space-y-1.5 text-xs font-mono pt-3 border-t border-[#1E2C3D] text-[#F6F5F1]/70">
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">Architecture:</span>
                  <span>Hybrid Mamba2-MoE</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">Serving:</span>
                  <span>vLLM / SGLang OpenAI API</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">Fallback:</span>
                  <span className="text-[#2A8C85]">Syntactic Uncertainty Scorer</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">Truth Verdict:</span>
                  <span className="text-[#C89448]">Human Analyst Required</span>
                </div>
              </div>
            </div>
          </div>

          {/* Row 2: Ollama Local LLM & Nhost BaaS Architectural Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Ollama Local Reasoning Card */}
            <div className="p-5 rounded-xl bg-[#0B121D] border border-[#1E2C3D] space-y-4">
              <div className="flex items-center justify-between">
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono border ${
                  ollamaStatus?.status === "online"
                    ? "bg-[#2A8C85]/20 text-[#2A8C85] border-[#2A8C85]/30"
                    : "bg-[#18263A] text-[#F6F5F1]/50 border-[#1E2C3D]"
                }`}>
                  {ollamaStatus?.status === "online" ? "OLLAMA ENGINE ONLINE" : "OLLAMA OFFLINE (STANDBY)"}
                </span>
                <Cpu className="w-4 h-4 text-[#2A8C85]" />
              </div>

              <div>
                <h4 className="text-sm font-semibold text-[#F6F5F1]">Ollama Local Reasoning Provider</h4>
                <p className="text-[11px] font-mono text-[#F6F5F1]/50 mt-0.5">
                  Host: {ollamaStatus?.endpoint || "http://localhost:11434"} • Active: {ollamaStatus?.active_model || "llama3.2:3b"}
                </p>
              </div>

              <div className="space-y-1.5 text-xs font-mono pt-3 border-t border-[#1E2C3D] text-[#F6F5F1]/70">
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">Installed Models:</span>
                  <span className="text-[#F6F5F1]">
                    {ollamaStatus?.available_models?.length ? ollamaStatus.available_models.join(", ") : "None detected locally"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">RAM Compatibility:</span>
                  <span className="text-[#2A8C85]">8 GB Machine Optimized</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">Lightweight Recommendations:</span>
                  <span className="text-[11px] text-[#C89448]">llama3.2:1b, llama3.2:3b, qwen2.5:1.5b</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">Output Mode:</span>
                  <span>Strict Pydantic JSON Schema</span>
                </div>
              </div>
            </div>

            {/* Nhost BaaS Architectural Selection Card */}
            <div className="p-5 rounded-xl bg-[#0B121D] border border-[#1E2C3D] space-y-4">
              <div className="flex items-center justify-between">
                <span className="px-2 py-0.5 rounded bg-[#2A8C85]/20 text-[#2A8C85] text-[10px] font-mono border border-[#2A8C85]/30">
                  SELECTED BAAS ARCHITECTURE
                </span>
                <Shield className="w-4 h-4 text-[#2A8C85]" />
              </div>

              <div>
                <h4 className="text-sm font-semibold text-[#F6F5F1]">Nhost BaaS (PostgreSQL + S3 Storage)</h4>
                <p className="text-[11px] font-mono text-[#F6F5F1]/50 mt-0.5">
                  Evaluated against Appwrite • Decision: Nhost selected for Relational Integrity
                </p>
              </div>

              <div className="space-y-1.5 text-xs font-mono pt-3 border-t border-[#1E2C3D] text-[#F6F5F1]/70">
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">Primary Database:</span>
                  <span className="text-[#F6F5F1]">PostgreSQL (15 Relational Tables)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">File Storage:</span>
                  <span>MinIO / AWS S3 Compatible</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">GraphQL API:</span>
                  <span className="text-[#2A8C85]">Hasura GraphQL Engine</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#F6F5F1]/40">Evaluation Spec:</span>
                  <span className="text-[#2A8C85]">docs/BACKEND_SELECTION.md</span>
                </div>
              </div>
            </div>
          </div>

          {/* Environment Variables Documentation Card */}
          <div className="p-5 rounded-xl bg-[#0B121D] border border-[#1E2C3D] space-y-3">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-[#2A8C85]" />
              <h3 className="text-sm font-semibold text-[#F6F5F1]">Backend Environment Configuration (.env)</h3>
            </div>
            <p className="text-xs text-[#F6F5F1]/60 leading-relaxed">
              Place your credentials securely in <code className="text-[#2A8C85]">apps/api/.env</code>. Secrets are never leaked to client bundles or browser consoles.
            </p>
            <pre className="p-4 rounded-lg bg-[#101B2B] border border-[#1E2C3D] font-mono text-xs text-[#F6F5F1]/80 overflow-x-auto">
{`# Official Gnani Vachana Platform Credentials
GNANI_API_KEY=your_vachana_api_key_here
GNANI_BASE_URL=https://api.vachana.ai
GNANI_PRISMA_MODEL=prisma-v3.0
GNANI_TIMBRE_MODEL=timbre-v2.5

# Optional Gnani Evon 30B Reasoning Model (Self-hosted or Enterprise API)
EVON_BASE_URL=http://localhost:30000
EVON_API_KEY=
EVON_MODEL_NAME=gnani/gnani-evon-v3.3-30B-A3B

# App Secrets & Local Database
SECRET_KEY=raven-secret-contest-key-2026
DATABASE_URL=sqlite:///./raven.db`}
            </pre>
          </div>
        </div>
      </main>

      <PersistentAudioPlayer />
    </div>
  );
}
