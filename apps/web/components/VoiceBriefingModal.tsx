"use client";

import { useState } from "react";
import { Volume2, Play, Pause, Loader2, X, Download, AlertCircle, Check } from "lucide-react";
import { useRavenStore } from "@/lib/store";
import { api } from "@/lib/api";

export function VoiceBriefingModal() {
  const { voiceBriefingModalOpen, voiceBriefingText, setVoiceBriefingModal } = useRavenStore();
  const [text, setText] = useState(voiceBriefingText || "");
  const [voice, setVoice] = useState("Nalini");
  const [language, setLanguage] = useState("en-IN");
  const [speed, setSpeed] = useState(1.0);
  const [status, setStatus] = useState<"idle" | "synthesizing" | "ready" | "error">("idle");
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  if (!voiceBriefingModalOpen) return null;

  const handleSynthesize = async () => {
    if (!text.trim()) return;

    setStatus("synthesizing");
    setErrorMessage("");

    try {
      const res = await api.synthesizeVoice(text, voice, language);
      setAudioUrl(res.audio_url);
      setStatus("ready");
    } catch (err: any) {
      setStatus("error");
      setErrorMessage(err.message || "Synthesis failed.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg bg-[#0B121D] border border-[#1E2C3D] rounded-xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-[#1E2C3D] flex items-center justify-between bg-[#101B2B]">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded bg-[#C89448]/20 border border-[#C89448]/40 flex items-center justify-center text-[#C89448]">
              <Volume2 className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-[#F6F5F1]">Gnani Timbre Voice Briefing</h3>
              <p className="text-[11px] text-[#F6F5F1]/50 font-mono">Neural Voice Audio Dossier</p>
            </div>
          </div>
          <button
            onClick={() => setVoiceBriefingModal(false)}
            className="p-1 rounded text-[#F6F5F1]/40 hover:text-[#F6F5F1]"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          <div>
            <label className="block text-xs font-mono text-[#F6F5F1]/60 mb-1.5">
              BRIEFING TEXT CONTENT
            </label>
            <textarea
              rows={4}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter text to synthesize into spoken audio..."
              className="w-full p-2.5 rounded bg-[#101B2B] border border-[#1E2C3D] text-xs text-[#F6F5F1] focus:outline-none focus:border-[#2A8C85]"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-mono text-[#F6F5F1]/60 mb-1.5">VOICE PROFILE</label>
              <select
                value={voice}
                onChange={(e) => setVoice(e.target.value)}
                className="w-full px-2.5 py-1.5 rounded bg-[#101B2B] border border-[#1E2C3D] text-xs text-[#F6F5F1]"
              >
                <option value="Nalini">Nalini (Female, Expressive)</option>
                <option value="Karan">Karan (Male, Authoritative)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono text-[#F6F5F1]/60 mb-1.5">LANGUAGE</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full px-2.5 py-1.5 rounded bg-[#101B2B] border border-[#1E2C3D] text-xs text-[#F6F5F1]"
              >
                <option value="en-IN">Indian English</option>
                <option value="hi-IN">Hindi</option>
                <option value="kn-IN">Kannada</option>
                <option value="ta-IN">Tamil</option>
                <option value="te-IN">Telugu</option>
              </select>
            </div>
          </div>

          {/* Player when ready */}
          {status === "ready" && audioUrl && (
            <div className="p-3.5 rounded bg-[#101B2B] border border-[#2A8C85]/40 space-y-2">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-xs text-[#2A8C85] font-mono">
                  <Check className="w-3.5 h-3.5" />
                  <span>Briefing Synthesized Successfully</span>
                </span>
                <a
                  href={`http://localhost:8000${audioUrl}`}
                  download="raven_briefing.wav"
                  className="flex items-center gap-1 text-[11px] font-mono text-[#F6F5F1]/60 hover:text-[#2A8C85]"
                >
                  <Download className="w-3 h-3" />
                  <span>WAV</span>
                </a>
              </div>
              <audio controls className="w-full h-8" src={`http://localhost:8000${audioUrl}`} />
            </div>
          )}

          {status === "error" && (
            <div className="p-3 rounded bg-red-950/40 border border-red-800/50 flex items-center gap-2 text-xs text-red-200">
              <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-400" />
              <span>{errorMessage}</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 bg-[#101B2B]/60 border-t border-[#1E2C3D] flex items-center justify-between">
          <p className="text-[10px] font-mono text-[#F6F5F1]/40">
            Model: Gnani Timbre (REST Inference / WAV)
          </p>
          <button
            disabled={status === "synthesizing" || !text.trim()}
            onClick={handleSynthesize}
            className="flex items-center gap-2 px-4 py-2 rounded bg-[#C89448] text-[#101B2B] text-xs font-semibold hover:bg-[#C89448]/90 transition-colors disabled:opacity-50"
          >
            {status === "synthesizing" ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Synthesizing Audio...</span>
              </>
            ) : (
              <>
                <Volume2 className="w-3.5 h-3.5" />
                <span>Generate Voice Briefing</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
