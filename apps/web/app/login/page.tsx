"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Radio, ShieldCheck, ArrowRight, Loader2, Sparkles, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await api.login(email, password);
      router.push("/workspace");
    } catch (err: any) {
      setError(err.message || "Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  const handleDemoAccess = async () => {
    setDemoLoading(true);
    setError("");

    try {
      await api.demoLogin();
      router.push("/workspace");
    } catch (err: any) {
      setError(err.message || "Demo login failed.");
    } finally {
      setDemoLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#101B2B] text-[#F6F5F1] flex flex-col justify-between p-6">
      <header className="flex items-center justify-between max-w-6xl w-full mx-auto">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded bg-[#0B121D] border border-[#2A8C85]/50 flex items-center justify-center text-[#2A8C85]">
            <Radio className="w-4 h-4" />
          </div>
          <span className="font-bold tracking-wider text-sm">RAVEN</span>
        </Link>

        <span className="text-[11px] font-mono text-[#F6F5F1]/50">
          The Great Indian AI Internship Challenge 2026
        </span>
      </header>

      <div className="max-w-md w-full mx-auto my-12 bg-[#0B121D] border border-[#1E2C3D] rounded-2xl p-8 shadow-2xl space-y-6">
        <div>
          <span className="font-mono text-[10px] text-[#2A8C85] tracking-wider uppercase">
            SECURE ANALYST ACCESS
          </span>
          <h2 className="text-xl font-bold tracking-tight text-[#F6F5F1] mt-1">
            Access RAVEN Intelligence
          </h2>
          <p className="text-xs text-[#F6F5F1]/60 mt-1">
            Sign in to your investigative evidence workspace or proceed using evaluator access.
          </p>
        </div>

        {/* 1-Click Evaluation Access Button */}
        <button
          onClick={handleDemoAccess}
          disabled={demoLoading}
          className="w-full flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-[#18263A] to-[#101B2B] border border-[#2A8C85]/60 hover:border-[#2A8C85] transition-all group"
        >
          <div className="flex items-center gap-3 text-left">
            <div className="w-9 h-9 rounded-lg bg-[#2A8C85]/20 border border-[#2A8C85]/40 flex items-center justify-center text-[#2A8C85]">
              <Sparkles className="w-5 h-5 text-[#2A8C85]" />
            </div>
            <div>
              <p className="text-xs font-semibold text-[#F6F5F1]">1-Click Evaluator Demo Access</p>
              <p className="text-[10px] font-mono text-[#2A8C85]">Instant entry as Dr. Vikram Rao</p>
            </div>
          </div>
          {demoLoading ? (
            <Loader2 className="w-4 h-4 animate-spin text-[#2A8C85]" />
          ) : (
            <ArrowRight className="w-4 h-4 text-[#2A8C85] group-hover:translate-x-1 transition-transform" />
          )}
        </button>

        <div className="flex items-center gap-3">
          <div className="flex-1 h-px bg-[#1E2C3D]" />
          <span className="font-mono text-[10px] text-[#F6F5F1]/40 uppercase">or standard sign in</span>
          <div className="flex-1 h-px bg-[#1E2C3D]" />
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-red-950/40 border border-red-800/50 flex items-center gap-2 text-xs text-red-200">
            <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4 text-xs">
          <div>
            <label className="block text-[11px] font-mono text-[#F6F5F1]/60 mb-1">EMAIL ADDRESS</label>
            <input
              required
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="analyst@raven.ai"
              className="w-full px-3 py-2 rounded-lg bg-[#101B2B] border border-[#1E2C3D] text-[#F6F5F1] focus:outline-none focus:border-[#2A8C85]"
            />
          </div>

          <div>
            <label className="block text-[11px] font-mono text-[#F6F5F1]/60 mb-1">PASSWORD</label>
            <input
              required
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              className="w-full px-3 py-2 rounded-lg bg-[#101B2B] border border-[#1E2C3D] text-[#F6F5F1] focus:outline-none focus:border-[#2A8C85]"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg bg-[#2A8C85] text-white font-medium hover:bg-[#2A8C85]/90 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            <span>Sign In to Terminal</span>
          </button>
        </form>

        <p className="text-[10px] text-center font-mono text-[#F6F5F1]/40">
          Default seed credentials: analyst@raven.ai / RavenInvestigate2026!
        </p>
      </div>

      <footer className="text-center text-[11px] font-mono text-[#F6F5F1]/40">
        RAVEN • Responsible Audio Verification & Evidence Navigator
      </footer>
    </div>
  );
}
