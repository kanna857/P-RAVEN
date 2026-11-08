import os
import math
import struct
import wave
import hashlib
from typing import List, Tuple, Optional

def compute_sha256(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def extract_waveform_and_meta(file_path: str, mime_type: str, num_bars: int = 64) -> Tuple[Optional[float], Optional[int], Optional[int], List[float]]:
    """
    Attempts to read WAV headers if available, or derives pseudo-waveform for visual display.
    Returns: (duration_seconds, sample_rate, channels, waveform_amplitudes)
    """
    duration = None
    sample_rate = None
    channels = None
    waveform = []

    try:
        if file_path.lower().endswith(".wav"):
            with wave.open(file_path, "rb") as wav_file:
                channels = wav_file.getnchannels()
                sample_rate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                duration = round(n_frames / float(sample_rate), 2)
                
                # Sample amplitude points
                step = max(1, n_frames // num_bars)
                for _ in range(num_bars):
                    frame_data = wav_file.readframes(1)
                    if not frame_data:
                        break
                    # standard 16-bit PCM
                    if wav_file.getsampwidth() == 2:
                        val = abs(struct.unpack("<h", frame_data[:2])[0]) / 32768.0
                        waveform.append(round(min(1.0, max(0.08, val * 1.5)), 3))
                    else:
                        waveform.append(0.3)
                    wav_file.setpos(min(n_frames - 1, wav_file.tell() + step))
    except Exception:
        pass

    # Fallback waveform if file is MP3/WebM/AAC or header couldn't be parsed
    if not waveform or len(waveform) < num_bars:
        file_size = os.path.getsize(file_path)
        # Seeded deterministic pseudo-waveform based on file size and name
        seed = file_size % 1000
        waveform = []
        for i in range(num_bars):
            val = 0.2 + 0.65 * abs(math.sin((i + seed) * 0.35)) * abs(math.cos((i * 1.2 + seed) * 0.2))
            waveform.append(round(min(1.0, max(0.12, val)), 3))

    if not duration:
        # Estimate duration based on size (typical 128kbps)
        file_size = os.path.getsize(file_path)
        duration = round(max(3.0, file_size / (16000 * 2)), 1)
        sample_rate = 16000
        channels = 1

    return duration, sample_rate, channels, waveform
