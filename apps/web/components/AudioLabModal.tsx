"use client";

import { useState, useRef } from "react";
import { UploadCloud, Mic, Square, Check, AlertCircle, Loader2, X, Music } from "lucide-react";
import { api } from "@/lib/api";

const LANGUAGES = [
  { code: "indic-auto", label: "Auto Indic Language Detection (Recommended)" },
  { code: "en-IN", label: "Indian English (en-IN)" },
  { code: "hi-IN", label: "Hindi (hi-IN)" },
  { code: "kn-IN", label: "Kannada (kn-IN)" },
  { code: "ta-IN", label: "Tamil (ta-IN)" },
  { code: "te-IN", label: "Telugu (te-IN)" },
  { code: "mr-IN", label: "Marathi (mr-IN)" },
  { code: "gu-IN", label: "Gujarati (gu-IN)" },
  { code: "bn-IN", label: "Bengali (bn-IN)" },
  { code: "ml-IN", label: "Malayalam (ml-IN)" },
  { code: "pa-IN", label: "Punjabi (pa-IN)" },
];

export function AudioLabModal({
  isOpen,
  onClose,
  investigationId,
  onSuccess
}: {
  isOpen: boolean;
  onClose: () => void;
  investigationId: string;
  onSuccess: () => void;
}) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [language, setLanguage] = useState("indic-auto");
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [status, setStatus] = useState<"idle" | "uploading" | "transcribing" | "success" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<any>(null);

  if (!isOpen) return null;

  // Handle Drag & Drop
  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  // Start Mic Recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        const recordedFile = new File([audioBlob], `mic_recording_${Date.now()}.wav`, { type: "audio/wav" });
        setSelectedFile(recordedFile);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setRecordingSeconds(0);
      timerRef.current = setInterval(() => {
        setRecordingSeconds((prev) => prev + 1);
      }, 1000);
    } catch (err: any) {
      setErrorMessage("Microphone access permission denied: " + err.message);
      setStatus("error");
    }
  };

  // Stop Mic Recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearInterval(timerRef.current);
    }
  };

  // Execute Upload and Transcription
  const handleProcess = async () => {
    if (!selectedFile) return;

    setStatus("uploading");
    setErrorMessage("");

    try {
      // 1. Upload audio asset
      const asset = await api.uploadAudio(selectedFile, investigationId, isRecording ? "microphone" : "upload");
      
      // 2. Invoke Gnani Prisma transcription
      setStatus("transcribing");
      await api.transcribeAudio(asset.id, language, "prisma-v3.0");

      setStatus("success");
      setTimeout(() => {
        onSuccess();
        onClose();
      }, 1000);
    } catch (err: any) {
      setStatus("error");
      setErrorMessage(err.message || "Failed to process audio.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg bg-[#0B121D] border border-[#1E2C3D] rounded-xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-[#1E2C3D] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded bg-[#2A8C85]/20 border border-[#2A8C85]/40 flex items-center justify-center text-[#2A8C85]">
              <Music className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-[#F6F5F1]">Audio Lab Intake</h3>
              <p className="text-[11px] text-[#F6F5F1]/50 font-mono">Gnani Prisma Multilingual Speech-to-Text</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded text-[#F6F5F1]/40 hover:text-[#F6F5F1]">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          {/* Dropzone */}
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleFileDrop}
            className={`border border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer ${
              selectedFile
                ? "border-[#2A8C85] bg-[#2A8C85]/5"
                : "border-[#1E2C3D] hover:border-[#2A8C85]/50 bg-[#101B2B]"
            }`}
            onClick={() => {
              const input = document.createElement("input");
              input.type = "file";
              input.accept = "audio/*";
              input.onchange = (e: any) => {
                if (e.target.files?.[0]) setSelectedFile(e.target.files[0]);
              };
              input.click();
            }}
          >
            <UploadCloud className="w-8 h-8 text-[#2A8C85] mx-auto mb-2" />
            {selectedFile ? (
              <div>
                <p className="text-xs font-medium text-[#F6F5F1]">{selectedFile.name}</p>
                <p className="text-[10px] font-mono text-[#2A8C85] mt-1">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Ready for Prisma
                </p>
              </div>
            ) : (
              <div>
                <p className="text-xs text-[#F6F5F1]/70">Drag & drop evidence audio (WAV, MP3, M4A, WebM)</p>
                <p className="text-[10px] text-[#F6F5F1]/40 font-mono mt-1">Maximum 50MB per file</p>
              </div>
            )}
          </div>

          {/* Microphone Option */}
          <div className="flex items-center justify-between p-3 rounded bg-[#101B2B] border border-[#1E2C3D]">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${isRecording ? "bg-red-500 animate-ping" : "bg-[#2A8C85]"}`} />
              <div>
                <p className="text-xs font-medium text-[#F6F5F1]">
                  {isRecording ? `Recording... (${recordingSeconds}s)` : "Live Microphone Capture"}
                </p>
                <p className="text-[10px] text-[#F6F5F1]/50 font-mono">Capture press briefing or field interview</p>
              </div>
            </div>

            {isRecording ? (
              <button
                onClick={stopRecording}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-red-600 hover:bg-red-700 text-white text-xs font-medium"
              >
                <Square className="w-3.5 h-3.5 fill-white" />
                <span>Stop</span>
              </button>
            ) : (
              <button
                onClick={startRecording}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#18263A] hover:bg-[#1E2C3D] border border-[#1E2C3D] text-[#F6F5F1] text-xs font-medium"
              >
                <Mic className="w-3.5 h-3.5 text-[#2A8C85]" />
                <span>Record</span>
              </button>
            )}
          </div>

          {/* Language Selector */}
          <div>
            <label className="block text-xs font-mono text-[#F6F5F1]/60 mb-1.5">
              TARGET RECOGNITION LANGUAGE (GNANI PRISMA)
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full px-3 py-2 rounded bg-[#101B2B] border border-[#1E2C3D] text-xs text-[#F6F5F1] focus:outline-none focus:border-[#2A8C85]"
            >
              {LANGUAGES.map((l) => (
                <option key={l.code} value={l.code} className="bg-[#0B121D]">
                  {l.label}
                </option>
              ))}
            </select>
          </div>

          {/* Error Banner */}
          {status === "error" && (
            <div className="p-3 rounded bg-red-950/40 border border-red-800/50 flex items-center gap-2 text-xs text-red-200">
              <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-400" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Success Banner */}
          {status === "success" && (
            <div className="p-3 rounded bg-[#2A8C85]/20 border border-[#2A8C85]/50 flex items-center gap-2 text-xs text-[#F6F5F1]">
              <Check className="w-4 h-4 flex-shrink-0 text-[#2A8C85]" />
              <span>Audio successfully transcribed and segments generated!</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 bg-[#101B2B]/60 border-t border-[#1E2C3D] flex items-center justify-between">
          <p className="text-[10px] font-mono text-[#F6F5F1]/40">
            Engine: Gnani Prisma v3.0 REST Pipeline
          </p>
          <button
            disabled={!selectedFile || status === "uploading" || status === "transcribing"}
            onClick={handleProcess}
            className="flex items-center gap-2 px-4 py-2 rounded bg-[#2A8C85] text-white text-xs font-medium hover:bg-[#2A8C85]/90 transition-colors disabled:opacity-50"
          >
            {status === "uploading" && (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Uploading...</span>
              </>
            )}
            {status === "transcribing" && (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Gnani Prisma Transcribing...</span>
              </>
            )}
            {(status === "idle" || status === "error" || status === "success") && (
              <span>Start Voice Processing</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
