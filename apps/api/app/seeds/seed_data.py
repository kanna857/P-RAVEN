import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.security import hash_password
from app.models import (
    User, Workspace, WorkspaceMembership, Investigation, AudioAsset,
    TranscriptionJob, TranscriptSegment, Claim, EvidenceSource,
    ClaimEvidenceLink, ReviewDecision, Report, ProviderUsage, AuditEvent
)
from app.database import SessionLocal, Base, engine

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "analyst@raven.ai").first():
            print("Database already contains seed data.")
            return

        print("Seeding RAVEN intelligence database with sample investigative investigations...")

        # 1. Users
        password_hash = hash_password("RavenInvestigate2026!")
        analyst_user = User(
            id=str(uuid.uuid4()),
            email="analyst@raven.ai",
            hashed_password=password_hash,
            full_name="Dr. Vikram Rao",
            role="senior_researcher",
            is_active=True
        )
        admin_user = User(
            id=str(uuid.uuid4()),
            email="admin@raven.ai",
            hashed_password=password_hash,
            full_name="Sarah Menon",
            role="admin",
            is_active=True
        )
        db.add_all([analyst_user, admin_user])
        db.flush()

        # 2. Workspace
        workspace = Workspace(
            id=str(uuid.uuid4()),
            name="Civic Evidence & Audio Lab",
            slug="civic-evidence-lab",
            description="Special investigative unit focused on regional civic infrastructure and public expenditure veracity."
        )
        db.add(workspace)
        db.flush()

        # Memberships
        m1 = WorkspaceMembership(workspace_id=workspace.id, user_id=analyst_user.id, role="owner")
        m2 = WorkspaceMembership(workspace_id=workspace.id, user_id=admin_user.id, role="admin")
        db.add_all([m1, m2])

        # 3. Investigation 1: Bengaluru Drinking Water & Pipeline Fund Claims (SAMPLE)
        inv1 = Investigation(
            id=str(uuid.uuid4()),
            workspace_id=workspace.id,
            author_id=analyst_user.id,
            title="[SAMPLE] Bengaluru Water Infrastructure & Potability Verification",
            description="Analysis of leaked municipal press briefing and ward committee recordings regarding East Zone pipeline replacement progress and water quality compliance.",
            status="under_review",
            primary_language="indic-auto",
            tags=["civic", "water_quality", "public_funds", "karnataka", "bengaluru"],
            is_sample=True,
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        db.add(inv1)
        db.flush()

        # Audio Asset 1
        audio1 = AudioAsset(
            id=str(uuid.uuid4()),
            investigation_id=inv1.id,
            filename="bengaluru_water_briefing_july2025.wav",
            file_path="uploads/bengaluru_water_briefing_july2025.wav",
            mime_type="audio/wav",
            size_bytes=3420000,
            duration_seconds=27.5,
            sample_rate=16000,
            channels=1,
            source_type="upload",
            waveform_data=[
                0.22, 0.45, 0.68, 0.52, 0.31, 0.44, 0.76, 0.82, 0.65, 0.48,
                0.35, 0.55, 0.72, 0.91, 0.64, 0.41, 0.28, 0.51, 0.79, 0.85,
                0.62, 0.39, 0.25, 0.42, 0.67, 0.74, 0.58, 0.36, 0.21, 0.49,
                0.69, 0.88, 0.73, 0.54, 0.32, 0.47, 0.71, 0.83, 0.66, 0.45,
                0.29, 0.53, 0.78, 0.94, 0.71, 0.46, 0.33, 0.57, 0.81, 0.69,
                0.52, 0.38, 0.24, 0.46, 0.65, 0.78, 0.61, 0.43, 0.27, 0.50,
                0.72, 0.85, 0.63, 0.37
            ]
        )
        db.add(audio1)
        db.flush()

        # Transcription Job 1
        job1 = TranscriptionJob(
            id=str(uuid.uuid4()),
            audio_asset_id=audio1.id,
            provider="gnani_prisma",
            model_name="prisma-v3.0",
            language_code="indic-auto",
            detected_language="en-IN / kn-IN (Code-Mixed)",
            status="completed",
            execution_time_ms=1120,
            completed_at=datetime.utcnow() - timedelta(days=2)
        )
        db.add(job1)
        db.flush()

        # Transcript Segments
        seg1 = TranscriptSegment(
            id=str(uuid.uuid4()),
            job_id=job1.id,
            start_time=0.0,
            end_time=4.2,
            text="The municipal corporation declared that over ninety-four percent of all tested pipeline tap water in the eastern zone is completely potable.",
            speaker_label="Speaker 1 (Official)",
            confidence=0.96,
            language="en-IN",
            order_index=0
        )
        seg2 = TranscriptSegment(
            id=str(uuid.uuid4()),
            job_id=job1.id,
            start_time=4.3,
            end_time=9.8,
            text="However, independent laboratory samples collected from thirty-two wards in July revealed coliform bacterial contamination exceeding permissible BIS 10500 standards.",
            speaker_label="Speaker 2 (Investigator)",
            confidence=0.94,
            language="en-IN",
            order_index=1
        )
        seg3 = TranscriptSegment(
            id=str(uuid.uuid4()),
            job_id=job1.id,
            start_time=10.0,
            end_time=15.6,
            text="Officials allocated four hundred and twenty crore rupees under the 2025 water infrastructure modernization grant, yet only eighteen percent of pipeline replacements are physically complete.",
            speaker_label="Speaker 2 (Investigator)",
            confidence=0.91,
            language="en-IN",
            order_index=2
        )
        seg4 = TranscriptSegment(
            id=str(uuid.uuid4()),
            job_id=job1.id,
            start_time=15.9,
            end_time=21.4,
            text="ನಮ್ಮ ವರದಿಯ ಪ್ರಕಾರ, ಕಲುಷಿತ ನೀರಿನಿಂದಾಗಿ ಕಳೆದ ಮೂರು ತಿಂಗಳಲ್ಲಿ ಆರು ನೂರಕ್ಕೂ ಹೆಚ್ಚು ಪ್ರಕರಣಗಳು ದಾಖಲಾಗಿವೆ. (According to our report, over six hundred cases have been registered due to contaminated water over the last three months.)",
            speaker_label="Speaker 3 (Local Reporter)",
            confidence=0.93,
            language="kn-IN",
            order_index=3
        )
        seg5 = TranscriptSegment(
            id=str(uuid.uuid4()),
            job_id=job1.id,
            start_time=21.7,
            end_time=27.5,
            text="The municipal health commissioner denied any link between the pipeline repairs and reported gastrointestinal admissions in the peripheral hospitals.",
            speaker_label="Speaker 1 (Official)",
            confidence=0.89,
            language="en-IN",
            order_index=4
        )
        db.add_all([seg1, seg2, seg3, seg4, seg5])
        db.flush()

        # Claims
        claim1 = Claim(
            id=str(uuid.uuid4()),
            investigation_id=inv1.id,
            segment_id=seg1.id,
            claim_text="94% of tested pipeline tap water in the eastern zone is completely potable under municipal testing.",
            category="statistical",
            extracted_by="evon_reasoning",
            uncertainty_score=0.15,
            status="refuted",
            order_index=0
        )
        claim2 = Claim(
            id=str(uuid.uuid4()),
            investigation_id=inv1.id,
            segment_id=seg2.id,
            claim_text="Coliform bacterial contamination exceeds permissible BIS 10500 standards across 32 wards.",
            category="statistical",
            extracted_by="evon_reasoning",
            uncertainty_score=0.18,
            status="verified_supported",
            order_index=1
        )
        claim3 = Claim(
            id=str(uuid.uuid4()),
            investigation_id=inv1.id,
            segment_id=seg3.id,
            claim_text="₹420 crore was allocated under the 2025 water grant, but only 18% of physical pipeline replacement is complete.",
            category="policy",
            extracted_by="evon_reasoning",
            uncertainty_score=0.22,
            status="verified_supported",
            order_index=2
        )
        claim4 = Claim(
            id=str(uuid.uuid4()),
            investigation_id=inv1.id,
            segment_id=seg4.id,
            claim_text="Over 600 clinical contamination cases were registered over the past three months in East Zone clinics.",
            category="event",
            extracted_by="evon_reasoning",
            uncertainty_score=0.35,
            status="inconclusive",
            order_index=3
        )
        db.add_all([claim1, claim2, claim3, claim4])
        db.flush()

        # Evidence Sources
        ev1 = EvidenceSource(
            id=str(uuid.uuid4()),
            source_type="court_record",
            title="Karnataka State Pollution Control Board - Regional Tap Water Quality Audit (July 2025)",
            url="https://kspcb.karnataka.gov.in/audits/water-east-bengaluru-2025",
            publisher="KSPCB Technical Monitoring Division",
            publication_date=datetime(2025, 7, 24),
            excerpt="Laboratory testing of 160 tap samples across 32 municipal wards revealed E. coli presence in 41.2% of samples, directly violating BIS 10500 potable water thresholds.",
            reliability_tier="primary_verified",
            notes="Certified lab test certificates attached in appendix C."
        )
        ev2 = EvidenceSource(
            id=str(uuid.uuid4()),
            source_type="government_gazette",
            title="Urban Development Department Budget Disbursement Bulletin #88",
            url="https://udd.karnataka.gov.in/orders/2025/grant-420cr-water.pdf",
            publisher="Government of Karnataka Urban Development Dept",
            publication_date=datetime(2025, 3, 15),
            excerpt="Sanction of Rs 420.00 Crores for pipeline rejuvenation. Physical audit progress reported at 17.8% as of Q2 milestone review.",
            reliability_tier="primary_verified",
            notes="Corroborates the 18% physical progress figure against ₹420 crore grant."
        )
        db.add_all([ev1, ev2])
        db.flush()

        # Link claims and evidence
        link1 = ClaimEvidenceLink(
            id=str(uuid.uuid4()),
            claim_id=claim1.id,
            evidence_id=ev1.id,
            relevance_rationale="KSPCB official testing contradicts the municipal corporation's 94% potability assertion.",
            supports_or_refutes="refutes"
        )
        link2 = ClaimEvidenceLink(
            id=str(uuid.uuid4()),
            claim_id=claim2.id,
            evidence_id=ev1.id,
            relevance_rationale="Confirms coliform exceeding BIS standards across 32 surveyed wards.",
            supports_or_refutes="supports"
        )
        link3 = ClaimEvidenceLink(
            id=str(uuid.uuid4()),
            claim_id=claim3.id,
            evidence_id=ev2.id,
            relevance_rationale="Government order confirms both ₹420 Cr sanction and 17.8% completion rate.",
            supports_or_refutes="supports"
        )
        db.add_all([link1, link2, link3])
        db.flush()

        # Review Decisions
        rev1 = ReviewDecision(
            id=str(uuid.uuid4()),
            claim_id=claim1.id,
            reviewer_id=analyst_user.id,
            decision="refuted",
            analyst_notes="Refuted by official KSPCB water testing report citing 41.2% E. coli contamination in tested eastern wards.",
            confidence_rating=5
        )
        rev2 = ReviewDecision(
            id=str(uuid.uuid4()),
            claim_id=claim3.id,
            reviewer_id=analyst_user.id,
            decision="supported",
            analyst_notes="Verified via Urban Development Dept Bulletin #88 confirming 17.8% physical milestone progress against ₹420 Cr allocation.",
            confidence_rating=5
        )
        db.add_all([rev1, rev2])
        db.flush()

        # Report 1
        rep1 = Report(
            id=str(uuid.uuid4()),
            investigation_id=inv1.id,
            title="Executive Verification Dossier: East Bengaluru Tap Water & Capital Expenditure",
            executive_summary="Investigation into municipal assertions indicates substantive discrepancies between public claims of 94% water potability and certified KSPCB test results showing bacterial contamination across 32 wards. Furthermore, capital expenditure tracking confirms only 17.8% physical pipeline delivery against ₹420 crore allocated.",
            methodology="Cross-verification of speech audio transcript using Gnani Prisma v3.0, verified against KSPCB certified laboratory audits and Urban Development Department Gazettes.",
            limitations="Clinical hospital admission records remain pending public health RTI response; medical causality is noted as inconclusive.",
            verdict_summary={
                "total_claims": 4,
                "verified_supported": 2,
                "refuted": 1,
                "inconclusive": 1,
                "evidence_strength": "High (State Regulatory & Gazette Records)"
            }
        )
        db.add(rep1)

        # Provider Usage Samples
        u1 = ProviderUsage(
            id=str(uuid.uuid4()),
            provider="gnani_prisma",
            endpoint="/stt/v3",
            characters_or_seconds=27.5,
            estimated_units=0.45,
            status_code=200,
            latency_ms=1120
        )
        u2 = ProviderUsage(
            id=str(uuid.uuid4()),
            provider="gnani_timbre",
            endpoint="/api/v1/tts/inference",
            characters_or_seconds=340,
            estimated_units=0.25,
            status_code=200,
            latency_ms=860
        )
        db.add_all([u1, u2])

        # Audit Event
        aud1 = AuditEvent(
            id=str(uuid.uuid4()),
            actor_id=analyst_user.id,
            action="INVESTIGATION_CREATED",
            resource_type="investigation",
            resource_id=inv1.id,
            details={"title": inv1.title, "mode": "sample_seed"}
        )
        db.add(aud1)

        db.commit()
        print("Successfully seeded RAVEN database with Dr. Vikram Rao (analyst@raven.ai) and sample investigation.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
