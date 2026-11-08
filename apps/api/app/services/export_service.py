import json
from typing import List, Dict, Any
from app.models import TranscriptSegment, Report

def format_timestamp_srt(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def export_segments_srt(segments: List[TranscriptSegment]) -> str:
    lines = []
    for idx, seg in enumerate(segments, 1):
        start_str = format_timestamp_srt(seg.start_time)
        end_str = format_timestamp_srt(seg.end_time)
        lines.append(f"{idx}")
        lines.append(f"{start_str} --> {end_str}")
        lines.append(f"[{seg.speaker_label}]: {seg.text}")
        lines.append("")
    return "\n".join(lines)

def export_segments_txt(segments: List[TranscriptSegment]) -> str:
    lines = []
    for seg in segments:
        lines.append(f"[{seg.start_time:05.1f}s - {seg.end_time:05.1f}s] {seg.speaker_label}: {seg.text}")
    return "\n".join(lines)

def export_segments_json(segments: List[TranscriptSegment]) -> str:
    data = [
        {
            "id": s.id,
            "order_index": s.order_index,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "speaker": s.speaker_label,
            "text": s.text,
            "confidence": s.confidence,
            "language": s.language
        }
        for s in segments
    ]
    return json.dumps(data, indent=2, ensure_ascii=False)

def export_report_markdown(report: Report, investigation_title: str, claims: List[Any], evidence_links: List[Any]) -> str:
    md = [
        f"# RAVEN INVESTIGATION REPORT",
        f"## {report.title}",
        f"**Subject:** {investigation_title}",
        f"**Generated:** {report.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "---",
        "",
        "### 1. Executive Summary",
        report.executive_summary,
        "",
        "### 2. Methodology & Evidence Standard",
        report.methodology or "Rigorous multi-source cross-reference against primary records, government gazettes, and official datasets. Epistemic uncertainty weighted according to linguistic qualification and primary source availability.",
        "",
        "### 3. Investigation Scope & Verified Claims",
        f"Total Claims Analyzed: {len(claims)}",
        ""
    ]

    for idx, c in enumerate(claims, 1):
        status_badge = f"[{c.status.upper()}]"
        md.append(f"#### Claim {idx}: {status_badge} {c.claim_text}")
        md.append(f"- **Category:** {c.category}")
        md.append(f"- **Extracted by:** {c.extracted_by}")
        md.append(f"- **Uncertainty Score:** {c.uncertainty_score * 100:.1f}%")
        
        # Associated reviews
        if hasattr(c, "review_decisions") and c.review_decisions:
            latest_review = c.review_decisions[-1]
            md.append(f"- **Analyst Verdict:** {latest_review.decision} (Confidence {latest_review.confidence_rating}/5)")
            md.append(f"- **Analyst Note:** {latest_review.analyst_notes}")

        md.append("")

    if report.limitations:
        md.extend([
            "### 4. Known Limitations & Caveats",
            report.limitations,
            ""
        ])

    md.extend([
        "---",
        "*Report verified via RAVEN (Responsible Audio Verification & Evidence Navigator). Notice: This document reflects analyst evaluations of recorded audio claims against submitted corroborating records.*"
    ])

    return "\n".join(md)
