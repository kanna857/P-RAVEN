"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Search, FolderKanban, Cpu, Mic2, X, Plus, Volume2 } from "lucide-react";
import { useRavenStore } from "@/lib/store";

export function CommandPalette() {
  const { commandPaletteOpen, setCommandPaletteOpen, setVoiceBriefingModal } = useRavenStore();
  const [query, setQuery] = useState("");
  const router = useRouter();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCommandPaletteOpen(!commandPaletteOpen);
      }
      if (e.key === "Escape" && commandPaletteOpen) {
        setCommandPaletteOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [commandPaletteOpen, setCommandPaletteOpen]);

  if (!commandPaletteOpen) return null;

  const actions = [
    {
      title: "Open Sample: Bengaluru Water Quality Investigation",
      category: "Investigations",
      action: () => {
        router.push("/workspace");
        setCommandPaletteOpen(false);
      },
      icon: FolderKanban
    },
    {
      title: "View Gnani AI Model Health & Latency",
      category: "Providers",
      action: () => {
        router.push("/workspace/settings");
        setCommandPaletteOpen(false);
      },
      icon: Cpu
    },
    {
      title: "Synthesize Voice Briefing via Gnani Timbre",
      category: "Voice AI",
      action: () => {
        setCommandPaletteOpen(false);
        setVoiceBriefingModal(true, "Executive summary ready for audio synthesis.");
      },
      icon: Volume2
    },
    {
      title: "View Compliance Audit Trail",
      category: "Governance",
      action: () => {
        router.push("/workspace/audit");
        setCommandPaletteOpen(false);
      },
      icon: Search
    }
  ];

  const filtered = actions.filter((a) =>
    a.title.toLowerCase().includes(query.toLowerCase()) ||
    a.category.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-xl bg-[#0B121D] border border-[#1E2C3D] rounded-xl shadow-2xl overflow-hidden flex flex-col">
        {/* Input Bar */}
        <div className="flex items-center px-4 py-3.5 border-b border-[#1E2C3D] gap-3">
          <Search className="w-4 h-4 text-[#2A8C85]" />
          <input
            autoFocus
            type="text"
            placeholder="Type a command or search workspace..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 bg-transparent text-sm text-[#F6F5F1] placeholder-[#F6F5F1]/40 focus:outline-none"
          />
          <button
            onClick={() => setCommandPaletteOpen(false)}
            className="text-[#F6F5F1]/40 hover:text-[#F6F5F1] p-1"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results */}
        <div className="max-h-72 overflow-y-auto p-2 space-y-1">
          {filtered.length === 0 ? (
            <div className="p-6 text-center text-xs text-[#F6F5F1]/40 font-mono">
              No matching commands found.
            </div>
          ) : (
            filtered.map((item, idx) => {
              const Icon = item.icon;
              return (
                <button
                  key={idx}
                  onClick={item.action}
                  className="w-full flex items-center justify-between p-2.5 rounded hover:bg-[#18263A] text-left transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-4 h-4 text-[#2A8C85] group-hover:scale-105 transition-transform" />
                    <div>
                      <p className="text-xs font-medium text-[#F6F5F1]">{item.title}</p>
                      <p className="text-[10px] text-[#F6F5F1]/50 font-mono">{item.category}</p>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono text-[#F6F5F1]/30 group-hover:text-[#2A8C85]">↵ Select</span>
                </button>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-2 bg-[#101B2B]/60 border-t border-[#1E2C3D] flex items-center justify-between text-[10px] font-mono text-[#F6F5F1]/40">
          <span>Navigate with arrows</span>
          <span>ESC to close</span>
        </div>
      </div>
    </div>
  );
}
