import os, shutil, uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user
from typing import Optional

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}


@router.post("/", response_model=schemas.PrescriptionOut, status_code=201)
def upload_prescription(
    file: Optional[UploadFile] = File(None),
    symptom_notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not file and not symptom_notes:
        raise HTTPException(status_code=400, detail="Provide a file or symptom notes")

    file_path = None
    file_type = None

    if file:
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail="Only JPG, PNG, or PDF allowed")

        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        save_path = os.path.join(UPLOAD_DIR, filename)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_path = save_path
        file_type = "pdf" if file.content_type == "application/pdf" else "image"

    prescription = models.Prescription(
        user_id=current_user.id,
        file_path=file_path,
        file_type=file_type,
        symptom_notes=symptom_notes
    )
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    return prescription


@router.get("/", response_model=list[schemas.PrescriptionOut])
def list_prescriptions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Prescription).filter(
        models.Prescription.user_id == current_user.id
    ).all()