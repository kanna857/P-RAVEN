"use client";

import { useState } from "react";
import Link from "next/link";
import { 
  Radio, 
  ArrowRight, 
  Play, 
  Pause, 
  ShieldCheck, 
  CheckCircle2, 
  XCircle, 
  Volume2, 
  Sparkles, 
  FileText, 
  Cpu, 
  Globe2, 
  Lock,
  ChevronRight
} from "lucide-react";

export default function LandingPage() {
  const [demoPlaying, setDemoPlaying] = useState(false);
  const [activeStep, setActiveStep] = useState(0);

  const demoSteps = [
    {
      time: "00:00 - 00:04.2",
      speaker: "Speaker 1 (Official)",
      quote: "The municipal corporation declared that over ninety-four percent of all tested pipeline tap water in the eastern zone is completely potable.",
      claim: "94% of tested pipeline tap water in the eastern zone is completely potable under municipal testing.",
      status: "refuted",
      evidence: "KSPCB Regional Tap Water Quality Audit (July 2025): 41.2% E. coli contamination in 160 sampled tap points across 32 wards."
    },
    {
      time: "00:10.0 - 00:15.6",
      speaker: "Speaker 2 (Investigator)",
      quote: "Officials allocated four hundred and twenty crore rupees under the 2025 water infrastructure modernization grant, yet only eighteen percent of pipeline replacements are physically complete.",
      claim: "₹420 crore was allocated under the 2025 water grant, but only 18% of physical pipeline replacement is complete.",
      status: "verified_supported",
      evidence: "Urban Development Dept Gazette Bulletin #88: Sanction of Rs 420.00 Cr, verified physical progress milestone reported at 17.8%."
    },
    {
      time: "00:15.9 - 00:21.4",
      speaker: "Speaker 3 (Local Reporter)",
      quote: "ನಮ್ಮ ವರದಿಯ ಪ್ರಕಾರ, ಕಲುಷಿತ ನೀರಿನಿಂದಾಗಿ ಕಳೆದ ಮೂರು ತಿಂಗಳಲ್ಲಿ ಆರು ನೂರಕ್ಕೂ ಹೆಚ್ಚು ಪ್ರಕರಣಗಳು ದಾಖಲಾಗಿವೆ. (According to our report, over six hundred cases have been registered.)",
      claim: "Over 600 clinical contamination cases were registered over the past three months in East Zone clinics.",
      status: "inconclusive",
      evidence: "Clinical hospital records pending municipal RTI disclosure; casualty links remain inconclusive."
    }
  ];

  return (
    <div className="min-h-screen bg-[#101B2B] text-[#F6F5F1] flex flex-col selection:bg-[#2A8C85] selection:text-white">
      {/* Top Editorial Header */}
      <header className="border-b border-[#1E2C3D] px-6 py-4 bg-[#0B121D]/90 backdrop-blur sticky top-0 z-40">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-[#101B2B] border border-[#2A8C85]/50 flex items-center justify-center text-[#2A8C85]">
              <Radio className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold tracking-wider text-sm text-[#F6F5F1]">RAVEN</span>
                <span className="px-1.5 py-0.2 rounded bg-[#2A8C85]/20 text-[#2A8C85] text-[10px] font-mono border border-[#2A8C85]/40">
                  Voice AI
                </span>
              </div>
              <p className="text-[10px] text-[#F6F5F1]/40 tracking-tight font-mono">
                Responsible Audio Verification & Evidence Navigator
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Link
              href="/workspace/settings"
              className="text-xs font-mono text-[#F6F5F1]/70 hover:text-[#2A8C85] transition-colors hidden sm:block"
            >
              Gnani Integration Status
            </Link>
            <Link
              href="/login"
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-[#2A8C85] text-white text-xs font-medium hover:bg-[#2A8C85]/90 transition-colors shadow-sm"
            >
              <span>Enter Workspace</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-20 pb-16 px-6 max-w-4xl mx-auto text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#18263A] border border-[#2A8C85]/30 text-xs text-[#2A8C85] font-mono">
          <span className="w-1.5 h-1.5 rounded-full bg-[#2A8C85] animate-ping" />
          <span>The Great Indian AI Internship Challenge 2026</span>
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-[#F6F5F1] leading-[1.15]">
          Hear the signal. <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#2A8C85] via-[#C89448] to-[#F6F5F1]">
            Investigate the claim.
          </span>
        </h1>

        <p className="text-base sm:text-lg text-[#F6F5F1]/70 max-w-2xl mx-auto leading-relaxed font-sans">
          A multilingual voice intelligence and evidence investigation platform powered by{" "}
          <strong className="text-[#F6F5F1] font-semibold">Gnani AI Prisma STT</strong> and{" "}
          <strong className="text-[#F6F5F1] font-semibold">Timbre TTS</strong>. Turning spoken Indian languages into searchable transcripts, extracting checkable factual assertions, and empowering analysts with primary source verification.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-4">
          <Link
            href="/login"
            className="w-full sm:w-auto px-6 py-3 rounded-lg bg-[#2A8C85] text-white font-medium text-sm hover:bg-[#2A8C85]/90 transition-colors flex items-center justify-center gap-2 shadow-lg shadow-[#2A8C85]/20"
          >
            <span>Launch Evaluation Workspace</span>
            <ArrowRight className="w-4 h-4" />
          </Link>

          <Link
            href="/workspace/settings"
            className="w-full sm:w-auto px-5 py-3 rounded-lg bg-[#0B121D] border border-[#1E2C3D] hover:border-[#2A8C85]/50 text-[#F6F5F1]/80 hover:text-white font-mono text-xs transition-colors flex items-center justify-center gap-2"
          >
            <Cpu className="w-4 h-4 text-[#C89448]" />
            <span>Inspect Gnani API Pipeline</span>
          </Link>
        </div>
      </section>

      {/* Interactive In-Situ Audio Investigation Preview */}
      <section className="py-12 px-6 max-w-5xl mx-auto w-full">
        <div className="p-1 rounded-2xl bg-gradient-to-b from-[#1E2C3D] to-[#0B121D]">
          <div className="bg-[#0B121D] rounded-2xl p-6 sm:p-8 space-y-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-[#1E2C3D] pb-5">
              <div>
                <span className="text-[10px] font-mono text-[#2A8C85] tracking-wider uppercase">
                  LIVE INTERACTIVE INVESTIGATION PREVIEW
                </span>
                <h3 className="text-base font-bold text-[#F6F5F1] mt-0.5">
                  Bengaluru Tap Water Potability & Capital Grant Claims
                </h3>
                <p className="text-xs text-[#F6F5F1]/50 font-mono">
                  Ingested Audio: Dual-Speaker Press Conference • Language: en-IN / kn-IN (Code-Mixed)
                </p>
              </div>

              {/* Step Selector */}
              <div className="flex items-center gap-1.5 bg-[#101B2B] p-1 rounded-lg border border-[#1E2C3D]">
                {demoSteps.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setActiveStep(i)}
                    className={`px-3 py-1 rounded text-xs font-mono transition-colors ${
                      activeStep === i
                        ? "bg-[#2A8C85] text-white"
                        : "text-[#F6F5F1]/50 hover:text-[#F6F5F1]"
                    }`}
                  >
                    Claim 0{i + 1}
                  </button>
                ))}
              </div>
            </div>

            {/* Interactive Step Display */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {/* 1. Spoken Audio Segment */}
              <div className="p-4 rounded-xl bg-[#101B2B] border border-[#1E2C3D] space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[10px] text-[#2A8C85]">GNANI PRISMA STT</span>
                  <span className="font-mono text-[10px] text-[#F6F5F1]/40">
                    {demoSteps[activeStep].time}
                  </span>
                </div>
                <p className="text-xs text-[#F6F5F1]/80 leading-relaxed font-sans">
                  "{demoSteps[activeStep].quote}"
                </p>
                <div className="pt-2 border-t border-[#1E2C3D] flex items-center justify-between text-[10px] font-mono text-[#F6F5F1]/50">
                  <span>{demoSteps[activeStep].speaker}</span>
                  <span className="text-[#2A8C85]">94% Confidence</span>
                </div>
              </div>

              {/* 2. Extracted Claim */}
              <div className="p-4 rounded-xl bg-[#101B2B] border border-[#1E2C3D] space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[10px] text-[#C89448]">CHECKABLE CLAIM</span>
                  {demoSteps[activeStep].status === "refuted" && (
                    <span className="px-2 py-0.5 rounded bg-[#A63D40]/20 text-[#E06C75] text-[10px] font-mono border border-[#A63D40]/30 flex items-center gap-1">
                      <XCircle className="w-3 h-3" />
                      <span>REFUTED</span>
                    </span>
                  )}
                  {demoSteps[activeStep].status === "verified_supported" && (
                    <span className="px-2 py-0.5 rounded bg-[#2A8C85]/20 text-[#2A8C85] text-[10px] font-mono border border-[#2A8C85]/30 flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>SUPPORTED</span>
                    </span>
                  )}
                  {demoSteps[activeStep].status === "inconclusive" && (
                    <span className="px-2 py-0.5 rounded bg-[#C89448]/20 text-[#C89448] text-[10px] font-mono border border-[#C89448]/30 flex items-center gap-1">
                      <span>INCONCLUSIVE</span>
                    </span>
                  )}
                </div>
                <p className="text-xs text-[#F6F5F1] leading-relaxed font-medium">
                  "{demoSteps[activeStep].claim}"
                </p>
                <div className="pt-2 border-t border-[#1E2C3D] text-[10px] font-mono text-[#F6F5F1]/50">
                  Epistemic Uncertainty: 18% • Factual Assertion
                </div>
              </div>

              {/* 3. Primary Evidence Corroboration */}
              <div className="p-4 rounded-xl bg-[#101B2B] border border-[#1E2C3D] space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[10px] text-[#2A8C85]">PRIMARY RECORD CITATION</span>
                  <ShieldCheck className="w-3.5 h-3.5 text-[#2A8C85]" />
                </div>
                <p className="text-xs text-[#F6F5F1]/90 leading-relaxed italic">
                  "{demoSteps[activeStep].evidence}"
                </p>
                <div className="pt-2 border-t border-[#1E2C3D] text-[10px] font-mono text-[#2A8C85]">
                  Status: Certified State Public Record
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Model Architecture Grid */}
      <section className="py-16 px-6 max-w-5xl mx-auto w-full space-y-8">
        <div className="text-center space-y-2">
          <span className="font-mono text-xs text-[#2A8C85] tracking-wider uppercase">
            RESPONSIBLE AI STACK
          </span>
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#F6F5F1]">
            Architected for Indian Languages & Investigative Rigor
          </h2>
          <p className="text-xs sm:text-sm text-[#F6F5F1]/60 max-w-xl mx-auto">
            Zero hallucinated verdicts. Full transparency between model confidence, source quality, and human analyst adjudication.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
          <div className="p-6 rounded-xl bg-[#0B121D] border border-[#1E2C3D] space-y-3">
            <div className="w-9 h-9 rounded bg-[#2A8C85]/20 border border-[#2A8C85]/40 flex items-center justify-center text-[#2A8C85]">
              <Globe2 className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-semibold text-[#F6F5F1]">Gnani Prisma STT</h3>
            <p className="text-xs text-[#F6F5F1]/60 leading-relaxed">
              Handles telephony audio, multi-speaker crosstalk, and code-mixed Indian vernaculars across 10 Indic languages with millisecond-precision timestamps.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-[#0B121D] border border-[#1E2C3D] space-y-3">
            <div className="w-9 h-9 rounded bg-[#C89448]/20 border border-[#C89448]/40 flex items-center justify-center text-[#C89448]">
              <Volume2 className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-semibold text-[#F6F5F1]">Gnani Timbre TTS</h3>
            <p className="text-xs text-[#F6F5F1]/60 leading-relaxed">
              Synthesizes verified executive briefs into expressive audio with native regional intonation and inline emotional tags for accessible field reports.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-[#0B121D] border border-[#1E2C3D] space-y-3">
            <div className="w-9 h-9 rounded bg-[#18263A] border border-[#1E2C3D] flex items-center justify-center text-[#2A8C85]">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-semibold text-[#F6F5F1]">Evon 30B & Human Review</h3>
            <p className="text-xs text-[#F6F5F1]/60 leading-relaxed">
              Separates epistemic linguistic uncertainty from source authority. Every truth or refutation verdict is explicitly human-reviewed with audit logging.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-[#1E2C3D] px-6 py-8 bg-[#0B121D] text-xs font-mono text-[#F6F5F1]/50">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-[#F6F5F1]">RAVEN</span>
            <span>•</span>
            <span>The Great Indian AI Internship Challenge 2026</span>
          </div>

          <div className="flex items-center gap-6">
            <Link href="/login" className="hover:text-[#2A8C85] transition-colors">
              Evaluator Access
            </Link>
            <Link href="/workspace/settings" className="hover:text-[#2A8C85] transition-colors">
              Gnani API Telemetry
            </Link>
            <Link href="/workspace/audit" className="hover:text-[#2A8C85] transition-colors">
              Audit Logs
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
