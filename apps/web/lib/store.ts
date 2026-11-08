import { create } from "zustand";

interface ActiveAudio {
  assetId: string;
  url: string;
  title: string;
  duration?: number;
}

interface RavenStore {
  // Audio Player
  activeAudio: ActiveAudio | null;
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  playbackRate: number;
  seekTarget: number | null;
  setActiveAudio: (audio: ActiveAudio | null) => void;
  setIsPlaying: (playing: boolean) => void;
  setCurrentTime: (time: number) => void;
  setDuration: (duration: number) => void;
  setPlaybackRate: (rate: number) => void;
  seekTo: (time: number) => void;
  clearSeekTarget: () => void;

  // Active Inspector / Context
  selectedClaimId: string | null;
  setSelectedClaimId: (id: string | null) => void;
  commandPaletteOpen: boolean;
  setCommandPaletteOpen: (open: boolean) => void;

  // Voice briefing modal
  voiceBriefingModalOpen: boolean;
  voiceBriefingText: string;
  setVoiceBriefingModal: (open: boolean, text?: string) => void;
}

export const useRavenStore = create<RavenStore>((set) => ({
  activeAudio: null,
  isPlaying: false,
  currentTime: 0,
  duration: 0,
  playbackRate: 1.0,
  seekTarget: null,

  setActiveAudio: (audio) => set({ activeAudio: audio, isPlaying: false, currentTime: 0 }),
  setIsPlaying: (isPlaying) => set({ isPlaying }),
  setCurrentTime: (currentTime) => set({ currentTime }),
  setDuration: (duration) => set({ duration }),
  setPlaybackRate: (playbackRate) => set({ playbackRate }),
  seekTo: (time) => set({ seekTarget: time, currentTime: time }),
  clearSeekTarget: () => set({ seekTarget: null }),

  selectedClaimId: null,
  setSelectedClaimId: (selectedClaimId) => set({ selectedClaimId }),

  commandPaletteOpen: false,
  setCommandPaletteOpen: (commandPaletteOpen) => set({ commandPaletteOpen }),

  voiceBriefingModalOpen: false,
  voiceBriefingText: "",
  setVoiceBriefingModal: (open, text = "") => set({ voiceBriefingModalOpen: open, voiceBriefingText: text })
}));
