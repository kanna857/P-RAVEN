"use client";

import { useEffect, useRef, useState } from "react";
import { Play, Pause, RotateCcw, Volume2, VolumeX, FastForward, Radio } from "lucide-react";
import { useRavenStore } from "@/lib/store";

export function PersistentAudioPlayer() {
  const {
    activeAudio,
    isPlaying,
    currentTime,
    duration,
    playbackRate,
    seekTarget,
    setIsPlaying,
    setCurrentTime,
    setDuration,
    setPlaybackRate,
    clearSeekTarget
  } = useRavenStore();

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isMuted, setIsMuted] = useState(false);

  // Sync seekTarget when another component seeks (e.g. clicking a transcript timestamp or claim)
  useEffect(() => {
    if (seekTarget !== null && audioRef.current) {
      audioRef.current.currentTime = seekTarget;
      setCurrentTime(seekTarget);
      if (!isPlaying) {
        audioRef.current.play().then(() => setIsPlaying(true)).catch(() => {});
      }
      clearSeekTarget();
    }
  }, [seekTarget, clearSeekTarget, setCurrentTime, isPlaying, setIsPlaying]);

  // Handle play / pause toggle
  const togglePlay = () => {
    if (!audioRef.current || !activeAudio) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().then(() => setIsPlaying(true)).catch(() => {});
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration || activeAudio?.duration || 0);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = val;
      setCurrentTime(val);
    }
  };

  const cycleSpeed = () => {
    const speeds = [0.75, 1.0, 1.25, 1.5, 2.0];
    const nextIdx = (speeds.indexOf(playbackRate) + 1) % speeds.length;
    const nextSpeed = speeds[nextIdx];
    setPlaybackRate(nextSpeed);
    if (audioRef.current) {
      audioRef.current.playbackRate = nextSpeed;
    }
  };

  const toggleMute = () => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const formatTime = (secs: number) => {
    if (!secs || isNaN(secs)) return "00:00";
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  if (!activeAudio) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-[#0B121D]/95 backdrop-blur border-t border-[#1E2C3D] px-6 py-3.5 z-40 flex items-center justify-between text-xs select-none">
      <audio
        ref={audioRef}
        src={activeAudio.url}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => setIsPlaying(false)}
      />

      {/* Audio Info */}
      <div className="flex items-center gap-3 w-1/4">
        <div className="w-8 h-8 rounded bg-[#101B2B] border border-[#2A8C85]/30 flex items-center justify-center text-[#2A8C85] flex-shrink-0">
          <Radio className="w-4 h-4 animate-pulse" />
        </div>
        <div className="truncate">
          <p className="font-medium text-[#F6F5F1] truncate">{activeAudio.title}</p>
          <p className="text-[10px] font-mono text-[#F6F5F1]/50">Synchronized Audio Channel</p>
        </div>
      </div>

      {/* Central Controls and Scrubber */}
      <div className="flex flex-col items-center gap-1.5 w-2/4 max-w-xl">
        <div className="flex items-center gap-4">
          <button
            onClick={() => {
              if (audioRef.current) {
                audioRef.current.currentTime = Math.max(0, audioRef.current.currentTime - 5);
              }
            }}
            title="Rewind 5s"
            className="p-1 rounded text-[#F6F5F1]/60 hover:text-[#F6F5F1] transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={togglePlay}
            className="w-8 h-8 rounded-full bg-[#2A8C85] text-white flex items-center justify-center hover:bg-[#2A8C85]/90 transition-colors shadow-sm"
          >
            {isPlaying ? <Pause className="w-4 h-4 fill-white" /> : <Play className="w-4 h-4 fill-white ml-0.5" />}
          </button>

          <button
            onClick={cycleSpeed}
            className="px-1.5 py-0.5 rounded bg-[#101B2B] border border-[#1E2C3D] font-mono text-[10px] text-[#2A8C85] hover:border-[#2A8C85]/50 transition-colors"
          >
            {playbackRate}x
          </button>
        </div>

        {/* Progress Bar */}
        <div className="w-full flex items-center gap-3">
          <span className="font-mono text-[10px] text-[#F6F5F1]/50 w-9 text-right">
            {formatTime(currentTime)}
          </span>
          <input
            type="range"
            min={0}
            max={duration || 100}
            step={0.1}
            value={currentTime}
            onChange={handleSeek}
            className="w-full h-1.5 bg-[#18263A] rounded-lg appearance-none cursor-pointer accent-[#2A8C85]"
          />
          <span className="font-mono text-[10px] text-[#F6F5F1]/50 w-9">
            {formatTime(duration)}
          </span>
        </div>
      </div>

      {/* Right Tools: Volume & Mute */}
      <div className="flex items-center justify-end gap-3 w-1/4">
        <button
          onClick={toggleMute}
          className="p-1.5 rounded text-[#F6F5F1]/60 hover:text-[#F6F5F1] transition-colors"
        >
          {isMuted ? <VolumeX className="w-4 h-4 text-[#A63D40]" /> : <Volume2 className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
}
