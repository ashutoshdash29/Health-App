from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import auth, prescriptions, analysis

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Health Companion API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(prescriptions.router)
app.include_router(analysis.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}