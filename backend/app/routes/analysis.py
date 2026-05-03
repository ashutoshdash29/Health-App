import os, json
import google.generativeai as genai
import fitz  # PyMuPDF
from PIL import Image
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
router = APIRouter(prefix="/analysis", tags=["analysis"])

PROMPT_TEMPLATE = """
You are a medical information assistant. Analyze the following prescription and patient symptoms.

Patient symptoms / notes:
{symptoms}

From the prescription and symptoms, extract and return a JSON object with exactly these keys:
{{
  "medicines": [
    {{"name": "...", "dosage": "...", "frequency": "...", "duration": "..."}}
  ],
  "doctor_advice": "...",
  "lifestyle_changes": "...",
  "identified_conditions": "..."
}}

Return ONLY valid JSON. No explanation, no markdown.
"""

def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    return "\n".join(page.get_text() for page in doc)


@router.post("/{prescription_id}", response_model=schemas.AnalysisOut)
def analyze_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    prescription = db.query(models.Prescription).filter(
        models.Prescription.id == prescription_id,
        models.Prescription.user_id == current_user.id
    ).first()

    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    # Return cached analysis if it exists
    if prescription.analysis:
        return prescription.analysis

    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = PROMPT_TEMPLATE.format(symptoms=prescription.symptom_notes or "Not provided")

    try:
        if prescription.file_path and prescription.file_type == "image":
            img = Image.open(prescription.file_path)
            response = model.generate_content([prompt, img])
        elif prescription.file_path and prescription.file_type == "pdf":
            pdf_text = extract_text_from_pdf(prescription.file_path)
            response = model.generate_content(f"{prompt}\n\nPrescription text:\n{pdf_text}")
        else:
            response = model.generate_content(prompt)

        raw = response.text.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    analysis = models.Analysis(
        prescription_id=prescription.id,
        medicines=json.dumps(parsed.get("medicines", [])),
        doctor_advice=parsed.get("doctor_advice", ""),
        lifestyle_changes=parsed.get("lifestyle_changes", ""),
        raw_response=raw
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


@router.get("/{prescription_id}", response_model=schemas.AnalysisOut)
def get_analysis(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    prescription = db.query(models.Prescription).filter(
        models.Prescription.id == prescription_id,
        models.Prescription.user_id == current_user.id
    ).first()
    if not prescription or not prescription.analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return prescription.analysis