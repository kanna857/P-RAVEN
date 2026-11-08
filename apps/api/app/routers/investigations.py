from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.database import get_db
from app.models import Investigation, AudioAsset, Claim, Report, AuditEvent, WorkspaceMembership
from app.schemas import InvestigationCreate, InvestigationResponse
from app.routers.auth import get_current_user, User

router = APIRouter(prefix="/investigations", tags=["investigations"])

@router.get("", response_model=List[InvestigationResponse])
def list_investigations(
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Investigation)
    if status and status != "all":
        query = query.filter(Investigation.status == status)
    if search:
        query = query.filter(Investigation.title.ilike(f"%{search}%"))

    investigations = query.order_by(Investigation.created_at.desc()).all()

    results = []
    for inv in investigations:
        audio_count = db.query(AudioAsset).filter(AudioAsset.investigation_id == inv.id).count()
        claims_count = db.query(Claim).filter(Claim.investigation_id == inv.id).count()
        results.append(
            InvestigationResponse(
                id=inv.id,
                title=inv.title,
                description=inv.description,
                status=inv.status,
                primary_language=inv.primary_language,
                tags=inv.tags or [],
                is_sample=inv.is_sample,
                created_at=inv.created_at,
                updated_at=inv.updated_at,
                author_id=inv.author_id,
                workspace_id=inv.workspace_id,
                audio_assets_count=audio_count,
                claims_count=claims_count
            )
        )
    return results

@router.post("", response_model=InvestigationResponse)
def create_investigation(
    inv_in: InvestigationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ws_membership = db.query(WorkspaceMembership).filter(WorkspaceMembership.user_id == current_user.id).first()
    workspace_id = inv_in.workspace_id or (ws_membership.workspace_id if ws_membership else None)
    
    if not workspace_id:
        raise HTTPException(status_code=400, detail="User must belong to a workspace to create investigations.")

    new_inv = Investigation(
        id=str(uuid.uuid4()),
        workspace_id=workspace_id,
        author_id=current_user.id,
        title=inv_in.title,
        description=inv_in.description,
        primary_language=inv_in.primary_language or "indic-auto",
        tags=inv_in.tags or [],
        status="active",
        is_sample=False
    )
    db.add(new_inv)
    
    audit = AuditEvent(
        actor_id=current_user.id,
        action="INVESTIGATION_CREATED",
        resource_type="investigation",
        resource_id=new_inv.id,
        details={"title": new_inv.title}
    )
    db.add(audit)
    db.commit()
    db.refresh(new_inv)

    return InvestigationResponse(
        id=new_inv.id,
        title=new_inv.title,
        description=new_inv.description,
        status=new_inv.status,
        primary_language=new_inv.primary_language,
        tags=new_inv.tags or [],
        is_sample=new_inv.is_sample,
        created_at=new_inv.created_at,
        updated_at=new_inv.updated_at,
        author_id=new_inv.author_id,
        workspace_id=new_inv.workspace_id,
        audio_assets_count=0,
        claims_count=0
    )

@router.get("/{id}", response_model=InvestigationResponse)
def get_investigation(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    inv = db.query(Investigation).filter(Investigation.id == id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    audio_count = db.query(AudioAsset).filter(AudioAsset.investigation_id == inv.id).count()
    claims_count = db.query(Claim).filter(Claim.investigation_id == inv.id).count()

    return InvestigationResponse(
        id=inv.id,
        title=inv.title,
        description=inv.description,
        status=inv.status,
        primary_language=inv.primary_language,
        tags=inv.tags or [],
        is_sample=inv.is_sample,
        created_at=inv.created_at,
        updated_at=inv.updated_at,
        author_id=inv.author_id,
        workspace_id=inv.workspace_id,
        audio_assets_count=audio_count,
        claims_count=claims_count
    )

@router.delete("/{id}")
def delete_investigation(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    inv = db.query(Investigation).filter(Investigation.id == id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    title = inv.title
    db.delete(inv)
    
    audit = AuditEvent(
        actor_id=current_user.id,
        action="INVESTIGATION_DELETED",
        resource_type="investigation",
        resource_id=id,
        details={"title": title}
    )
    db.add(audit)
    db.commit()
    return {"message": "Investigation successfully deleted", "id": id}
