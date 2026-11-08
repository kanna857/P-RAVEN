"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  FolderKanban, 
  Mic2, 
  ShieldCheck, 
  Cpu, 
  FileText, 
  History, 
  Search, 
  LogOut, 
  Volume2, 
  Radio, 
  Plus
} from "lucide-react";
import { useRavenStore } from "@/lib/store";

export function NavigationRail({ onNewInvestigation }: { onNewInvestigation?: () => void }) {
  const pathname = usePathname();
  const setCommandPaletteOpen = useRavenStore((s) => s.setCommandPaletteOpen);

  const navItems = [
    { label: "Investigations", href: "/workspace", icon: FolderKanban },
    { label: "Provider Health", href: "/workspace/settings", icon: Cpu },
    { label: "Audit & Usage", href: "/workspace/audit", icon: History },
  ];

  return (
    <aside className="w-64 bg-[#0B121D] border-r border-[#1E2C3D] flex flex-col justify-between h-screen select-none z-30">
      <div>
        {/* Logo and Brand */}
        <div className="p-5 border-b border-[#1E2C3D]/80 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 rounded bg-[#101B2B] border border-[#2A8C85]/40 flex items-center justify-center text-[#2A8C85] group-hover:border-[#2A8C85] transition-colors">
              <Radio className="w-5 h-5 animate-pulse text-[#2A8C85]" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-semibold tracking-wider text-base text-[#F6F5F1]">RAVEN</span>
                <span className="text-[10px] px-1.5 py-0.2 rounded bg-[#2A8C85]/20 text-[#2A8C85] border border-[#2A8C85]/30 uppercase font-mono">Gnani</span>
              </div>
              <p className="text-[11px] text-[#F6F5F1]/50 tracking-tight">Audio Evidence Navigator</p>
            </div>
          </Link>
        </div>

        {/* Global Search / Command Bar Trigger */}
        <div className="p-3">
          <button
            onClick={() => setCommandPaletteOpen(true)}
            className="w-full flex items-center justify-between px-3 py-2 rounded bg-[#101B2B] border border-[#1E2C3D] text-xs text-[#F6F5F1]/60 hover:text-[#F6F5F1] hover:border-[#2A8C85]/50 transition-colors"
          >
            <span className="flex items-center gap-2">
              <Search className="w-3.5 h-3.5 text-[#2A8C85]" />
              <span>Search workspace...</span>
            </span>
            <kbd className="px-1.5 py-0.5 rounded bg-[#0B121D] text-[10px] text-[#F6F5F1]/40 border border-[#1E2C3D]">⌘K</kbd>
          </button>
        </div>

        {/* New Investigation Action */}
        <div className="px-3 pb-3">
          <button
            onClick={onNewInvestigation}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded bg-[#2A8C85] text-white text-xs font-medium hover:bg-[#2A8C85]/90 transition-colors shadow-sm"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Investigation</span>
          </button>
        </div>

        {/* Main Nav Items */}
        <nav className="px-2 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== "/workspace" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded text-xs font-medium transition-colors ${
                  isActive
                    ? "bg-[#18263A] text-[#F6F5F1] border-l-2 border-[#2A8C85]"
                    : "text-[#F6F5F1]/70 hover:text-[#F6F5F1] hover:bg-[#101B2B]"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-[#2A8C85]" : "text-[#F6F5F1]/50"}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Models in Use Indicator */}
        <div className="mx-3 mt-6 p-3 rounded bg-[#101B2B]/70 border border-[#1E2C3D]">
          <div className="flex items-center justify-between text-[11px] font-mono text-[#F6F5F1]/60 mb-2">
            <span>PIPELINE ENGINE</span>
            <span className="inline-block w-2 h-2 rounded-full bg-[#2A8C85] animate-ping" />
          </div>
          <div className="space-y-1.5 text-xs">
            <div className="flex items-center justify-between text-[#F6F5F1]/80">
              <span className="text-[11px] text-[#F6F5F1]/50">STT:</span>
              <span className="font-mono text-[11px] text-[#2A8C85]">Prisma v3.0</span>
            </div>
            <div className="flex items-center justify-between text-[#F6F5F1]/80">
              <span className="text-[11px] text-[#F6F5F1]/50">TTS:</span>
              <span className="font-mono text-[11px] text-[#C89448]">Timbre v2.5</span>
            </div>
            <div className="flex items-center justify-between text-[#F6F5F1]/80">
              <span className="text-[11px] text-[#F6F5F1]/50">Reasoning:</span>
              <span className="font-mono text-[11px] text-[#F6F5F1]/70">Evon 30B / Heuristic</span>
            </div>
          </div>
        </div>
      </div>

      {/* User Footer */}
      <div className="p-3 border-t border-[#1E2C3D] bg-[#0B121D]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-[#18263A] border border-[#2A8C85]/40 flex items-center justify-center text-xs font-mono font-medium text-[#2A8C85]">
              VR
            </div>
            <div>
              <p className="text-xs font-medium text-[#F6F5F1]">Dr. Vikram Rao</p>
              <p className="text-[10px] text-[#F6F5F1]/50 font-mono">Senior Lead Analyst</p>
            </div>
          </div>
          <Link
            href="/login"
            title="Sign out"
            className="p-1.5 rounded hover:bg-[#18263A] text-[#F6F5F1]/50 hover:text-[#F6F5F1] transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </aside>
  );
}
