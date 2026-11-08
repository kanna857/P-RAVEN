import os
import io
import math
import wave
import struct
from typing import Tuple, List, Dict, Any, Optional

def convert_to_16k_mono_pcm(
    input_path: str,
    output_path: str,
    target_sample_rate: int = 16000,
    apply_highpass_80hz: bool = True,
    apply_peak_normalization: bool = True
) -> Dict[str, Any]:
    """
    Standardizes any WAV audio file into 16 kHz Mono 16-bit PCM WAV.
    Optionally applies an 80Hz high-pass filter and peak normalization to -1.0 dBFS.
    Preserves original audio file at input_path.
    """
    try:
        with wave.open(input_path, "rb") as in_wav:
            channels = in_wav.getnchannels()
            sample_width = in_wav.getsampwidth()
            framerate = in_wav.getframerate()
            n_frames = in_wav.getnframes()
            raw_bytes = in_wav.readframes(n_frames)
    except Exception as exc:
        raise ValueError(f"Unable to read audio file format: {str(exc)}")

    # Unpack 16-bit PCM
    if sample_width != 2:
        # Fallback if 8-bit or 24-bit: handle graceful copy
        with open(input_path, "rb") as f_in, open(output_path, "wb") as f_out:
            f_out.write(f_in.read())
        return {
            "processed_path": output_path,
            "sample_rate": framerate,
            "channels": 1,
            "highpass_applied": False,
            "normalized": False
        }

    total_samples = len(raw_bytes) // 2
    samples = struct.unpack(f"<{total_samples}h", raw_bytes)

    # 1. Downmix to mono if stereo
    if channels > 1:
        mono_samples = []
        for i in range(0, len(samples), channels):
            avg_val = int(sum(samples[i:i+channels]) / channels)
            mono_samples.append(avg_val)
        samples = mono_samples

    # 2. Resample to 16 kHz if necessary (linear interpolation)
    if framerate != target_sample_rate and framerate > 0:
        ratio = float(target_sample_rate) / float(framerate)
        resampled_length = int(len(samples) * ratio)
        resampled = []
        for i in range(resampled_length):
            src_idx = i / ratio
            idx0 = int(src_idx)
            idx1 = min(idx0 + 1, len(samples) - 1)
            frac = src_idx - idx0
            val = int((1.0 - frac) * samples[idx0] + frac * samples[idx1])
            resampled.append(val)
        samples = resampled
        framerate = target_sample_rate

    # 3. Optional 80 Hz First-Order High-Pass Filter (RC Filter)
    # y[i] = alpha * (y[i-1] + x[i] - x[i-1])
    if apply_highpass_80hz:
        dt = 1.0 / framerate
        rc = 1.0 / (2.0 * math.pi * 80.0)
        alpha = rc / (rc + dt)
        filtered = []
        y_prev = 0.0
        x_prev = float(samples[0]) if samples else 0.0
        for s in samples:
            x_curr = float(s)
            y_curr = alpha * (y_prev + x_curr - x_prev)
            filtered.append(int(max(-32768, min(32767, y_curr))))
            y_prev = y_curr
            x_prev = x_curr
        samples = filtered

    # 4. Optional Peak Normalization to -1.0 dBFS (~90% full scale: 29490)
    target_peak = 29490
    max_amp = max([abs(s) for s in samples]) if samples else 0
    normalization_factor = 1.0
    if apply_peak_normalization and max_amp > 100:
        normalization_factor = target_peak / float(max_amp)
        # Avoid boosting background noise more than 3.5x
        normalization_factor = min(3.5, normalization_factor)
        normalized = [int(max(-32768, min(32767, s * normalization_factor))) for s in samples]
        samples = normalized

    # Write out standardized WAV
    with wave.open(output_path, "wb") as out_wav:
        out_wav.setnchannels(1)
        out_wav.setsampwidth(2)
        out_wav.setframerate(target_sample_rate)
        packed = struct.pack(f"<{len(samples)}h", *samples)
        out_wav.writeframes(packed)

    return {
        "processed_path": output_path,
        "sample_rate": target_sample_rate,
        "channels": 1,
        "sample_count": len(samples),
        "duration_seconds": round(len(samples) / float(target_sample_rate), 2),
        "highpass_applied": apply_highpass_80hz,
        "normalization_applied": apply_peak_normalization,
        "gain_applied": round(normalization_factor, 2)
    }


def compute_levenshtein_distance(ref_tokens: List[str], hyp_tokens: List[str]) -> Tuple[int, int, int, int]:
    """
    Computes Levenshtein matrix returning: (distance, substitutions, deletions, insertions)
    """
    r_len = len(ref_tokens)
    h_len = len(hyp_tokens)

    # dp[i][j] stores (cost, S, D, I)
    dp = [[(0, 0, 0, 0) for _ in range(h_len + 1)] for _ in range(r_len + 1)]

    for i in range(1, r_len + 1):
        dp[i][0] = (i, 0, i, 0)  # all deletions
    for j in range(1, h_len + 1):
        dp[0][j] = (j, 0, 0, j)  # all insertions

    for i in range(1, r_len + 1):
        for j in range(1, h_len + 1):
            if ref_tokens[i - 1] == hyp_tokens[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                sub_cost, s, d, ins = dp[i - 1][j - 1]
                del_cost, ds, dd, dins = dp[i - 1][j]
                ins_cost, is_, id_, iins = dp[i][j - 1]

                choice = min(
                    (sub_cost + 1, s + 1, d, ins),
                    (del_cost + 1, ds, dd + 1, dins),
                    (ins_cost + 1, is_, id_, iins + 1),
                    key=lambda x: x[0]
                )
                dp[i][j] = choice

    total_dist, subs, dels, inss = dp[r_len][h_len]
    return total_dist, subs, dels, inss


def calculate_wer_cer(reference_text: str, hypothesis_text: str) -> Dict[str, Any]:
    """
    Computes Word Error Rate (WER) and Character Error Rate (CER).
    WER = (Substitutions + Deletions + Insertions) / Total Reference Words
    CER = (Substitutions + Deletions + Insertions) / Total Reference Characters
    """
    # Clean whitespace and normalize case
    ref_norm = " ".join(reference_text.strip().lower().split())
    hyp_norm = " ".join(hypothesis_text.strip().lower().split())

    ref_words = ref_norm.split()
    hyp_words = hyp_norm.split()

    if not ref_words:
        return {
            "wer": 0.0,
            "cer": 0.0,
            "accuracy_percent": 100.0,
            "reference_word_count": 0,
            "hypothesis_word_count": len(hyp_words),
            "substitutions": 0,
            "deletions": 0,
            "insertions": len(hyp_words)
        }

    # WER calculation
    w_dist, w_subs, w_dels, w_ins = compute_levenshtein_distance(ref_words, hyp_words)
    wer = round(w_dist / float(len(ref_words)), 4)
    accuracy = round(max(0.0, (1.0 - wer) * 100.0), 2)

    # CER calculation
    ref_chars = list(ref_norm.replace(" ", ""))
    hyp_chars = list(hyp_norm.replace(" ", ""))
    c_dist, c_subs, c_dels, c_ins = compute_levenshtein_distance(ref_chars, hyp_chars) if ref_chars else (0, 0, 0, 0)
    cer = round(c_dist / float(max(1, len(ref_chars))), 4)

    return {
        "wer": wer,
        "cer": cer,
        "accuracy_percent": accuracy,
        "reference_word_count": len(ref_words),
        "hypothesis_word_count": len(hyp_words),
        "substitutions": w_subs,
        "deletions": w_dels,
        "insertions": w_ins,
        "character_errors": c_dist
    }
