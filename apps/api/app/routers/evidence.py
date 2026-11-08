import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import EvidenceSource, ClaimEvidenceLink, Claim, AuditEvent
from app.schemas import EvidenceCreateRequest, EvidenceResponse, CrawlRequest, CrawlResponse
from app.crawler.evidence_crawler import crawl_evidence_url, compare_claim_to_evidence
from app.routers.auth import get_current_user, User

router = APIRouter(prefix="/evidence", tags=["evidence"])

@router.post("/crawl", response_model=CrawlResponse)
async def crawl_evidence(
    req: CrawlRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crawls permitted public URLs with Scrapy + Trafilatura, verifies anti-SSRF,
    computes SHA-256 provenance fingerprint, and performs claim stance comparison.
    """
    crawl_res = await crawl_evidence_url(req.url)
    if not crawl_res["success"]:
        return CrawlResponse(
            success=False,
            url=req.url,
            error=crawl_res.get("error", "Crawling failed")
        )

    stance = "contextualizes"
    confidence = 0.5
    rationale = "General factual context extracted via Scrapy"

    # If linked to a claim, perform automated stance comparison
    claim = None
    if req.claim_id:
        claim = db.query(Claim).filter(Claim.id == req.claim_id).first()
        if claim and crawl_res.get("excerpt"):
            comp = compare_claim_to_evidence(claim.claim_text, crawl_res["excerpt"])
            stance = comp["stance"]
            confidence = comp["confidence"]
            rationale = comp["rationale"]

    # Persist as verified EvidenceSource
    source_id = str(uuid.uuid4())
    pub_date = None
    if crawl_res.get("date"):
        try:
            pub_date = datetime.fromisoformat(crawl_res["date"].replace("Z", "+00:00"))
        except Exception:
            pub_date = None

    ev_source = EvidenceSource(
        id=source_id,
        source_type="web",
        title=crawl_res.get("title") or req.url,
        url=req.url,
        canonical_url=crawl_res.get("canonical_url"),
        publisher=crawl_res.get("publisher"),
        author=crawl_res.get("author"),
        publication_date=pub_date,
        excerpt=crawl_res.get("excerpt"),
        reliability_tier="primary_verified",
        provenance_sha256=crawl_res.get("provenance_sha256"),
        notes=rationale
    )
    db.add(ev_source)
    db.flush()

    evidence_id = ev_source.id

    # If linked to claim, add link
    if claim:
        link_id = str(uuid.uuid4())
        link = ClaimEvidenceLink(
            id=link_id,
            claim_id=claim.id,
            evidence_id=ev_source.id,
            relevance_rationale=rationale,
            supports_or_refutes=stance
        )
        db.add(link)

    audit = AuditEvent(
        actor_id=current_user.id,
        action="EVIDENCE_CRAWLED_SCRAPY",
        resource_type="evidence_source",
        resource_id=source_id,
        details={
            "url": req.url,
            "provenance_sha256": crawl_res.get("provenance_sha256"),
            "stance": stance,
            "claim_id": req.claim_id
        }
    )
    db.add(audit)
    db.commit()

    return CrawlResponse(
        success=True,
        url=req.url,
        title=crawl_res.get("title"),
        author=crawl_res.get("author"),
        date=crawl_res.get("date"),
        canonical_url=crawl_res.get("canonical_url"),
        excerpt=crawl_res.get("excerpt"),
        provenance_hash=crawl_res.get("provenance_sha256"),
        reliability_tier="primary_verified",
        stance=stance,
        confidence=confidence,
        rationale=rationale,
        evidence_id=evidence_id
    )

@router.post("")
def add_evidence(
    req: EvidenceCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    claim = db.query(Claim).filter(Claim.id == req.claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Create Evidence Source
    source_id = str(uuid.uuid4())
    ev_source = EvidenceSource(
        id=source_id,
        source_type=req.source_type or "web",
        title=req.title,
        url=req.url,
        canonical_url=req.canonical_url,
        publisher=req.publisher,
        author=req.author,
        publication_date=req.publication_date,
        excerpt=req.excerpt,
        reliability_tier=req.reliability_tier or "primary_verified",
        provenance_sha256=req.provenance_sha256,
        notes=req.relevance_rationale
    )
    db.add(ev_source)
    db.flush()

    # Link to Claim
    link_id = str(uuid.uuid4())
    link = ClaimEvidenceLink(
        id=link_id,
        claim_id=claim.id,
        evidence_id=ev_source.id,
        relevance_rationale=req.relevance_rationale,
        supports_or_refutes=req.supports_or_refutes or "supports"
    )
    db.add(link)

    audit = AuditEvent(
        actor_id=current_user.id,
        action="EVIDENCE_LINKED",
        resource_type="evidence_source",
        resource_id=ev_source.id,
        details={
            "claim_id": claim.id,
            "supports_or_refutes": link.supports_or_refutes,
            "title": ev_source.title
        }
    )
    db.add(audit)
    db.commit()

    return {
        "link_id": link.id,
        "evidence_id": ev_source.id,
        "title": ev_source.title,
        "url": ev_source.url,
        "publisher": ev_source.publisher,
        "supports_or_refutes": link.supports_or_refutes,
        "reliability_tier": ev_source.reliability_tier,
        "relevance_rationale": link.relevance_rationale,
        "created_at": ev_source.created_at
    }

@router.get("")
def list_evidence(
    investigation_id: str = Query(...),
    claim_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = (
        db.query(ClaimEvidenceLink, EvidenceSource, Claim)
        .join(EvidenceSource, EvidenceSource.id == ClaimEvidenceLink.evidence_id)
        .join(Claim, Claim.id == ClaimEvidenceLink.claim_id)
        .filter(Claim.investigation_id == investigation_id)
    )

    if claim_id:
        query = query.filter(ClaimEvidenceLink.claim_id == claim_id)

    results = query.all()

    return [
        {
            "link_id": link.id,
            "claim_id": claim.id,
            "claim_text": claim.claim_text,
            "evidence_id": source.id,
            "title": source.title,
            "url": source.url,
            "canonical_url": source.canonical_url,
            "publisher": source.publisher,
            "author": source.author,
            "publication_date": source.publication_date,
            "retrieval_date": source.retrieval_date,
            "excerpt": source.excerpt,
            "reliability_tier": source.reliability_tier,
            "provenance_sha256": source.provenance_sha256,
            "source_type": source.source_type,
            "supports_or_refutes": link.supports_or_refutes,
            "relevance_rationale": link.relevance_rationale
        }
        for link, source, claim in results
    ]

@router.delete("/{link_id}")
def remove_evidence_link(
    link_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    link = db.query(ClaimEvidenceLink).filter(ClaimEvidenceLink.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Evidence link not found")

    claim_id = link.claim_id
    db.delete(link)

    audit = AuditEvent(
        actor_id=current_user.id,
        action="EVIDENCE_UNLINKED",
        resource_type="claim_evidence_link",
        resource_id=link_id,
        details={"claim_id": claim_id}
    )
    db.add(audit)
    db.commit()

    return {"message": "Evidence link successfully removed", "id": link_id}
