"""FastAPI server exposing the EmailTriageEnv as an OpenEnv-compatible REST API."""
import uuid
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .env import EmailTriageEnv, TASK_CONFIGS
from .models import Action, Observation, Reward, EnvironmentState

app = FastAPI(
    title="Email Triage Environment",
    description="OpenEnv-compatible customer support ticket triage environment.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory sessions: session_id -> EmailTriageEnv
_sessions: Dict[str, EmailTriageEnv] = {}


# ---- Request / Response models ----

class ResetRequest(BaseModel):
    task_name: str = "ticket_classification"
    session_id: Optional[str] = None


class ResetResponse(BaseModel):
    session_id: str
    observation: Observation


class StepRequest(BaseModel):
    session_id: str
    action: Action


class StepResponse(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: dict


# ---- Endpoints ----

@app.get("/health")
def health():
    return {"status": "ok", "environment": "email-triage", "version": "1.0.0"}


@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            {
                "name": name,
                "description": cfg["description"],
                "difficulty": cfg["difficulty"],
                "max_steps": cfg["max_steps"],
                "required_workflow": cfg["required_workflow"],
                "num_tickets": len(cfg["tickets"]),
            }
            for name, cfg in TASK_CONFIGS.items()
        ]
    }


@app.post("/reset", response_model=ResetResponse)
def reset(req: ResetRequest = None):
    if req is None:
        req = ResetRequest()
    if req.task_name not in TASK_CONFIGS:
        raise HTTPException(status_code=400, detail=f"Unknown task '{req.task_name}'")
    session_id = req.session_id or str(uuid.uuid4())
    env = EmailTriageEnv(task_name=req.task_name)
    obs = env.reset()
    _sessions[session_id] = env
    return ResetResponse(session_id=session_id, observation=obs)


@app.post("/step", response_model=StepResponse)
def step(req: StepRequest):
    env = _sessions.get(req.session_id)
    if env is None:
        raise HTTPException(status_code=404, detail="Session not found. Call POST /reset first.")
    obs, reward, done, info = env.step(req.action)
    return StepResponse(observation=obs, reward=reward, done=done, info=info)


@app.get("/state", response_model=EnvironmentState)
def get_state(session_id: str):
    env = _sessions.get(session_id)
    if env is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return env.state()


@app.post("/close")
def close(session_id: str):
    env = _sessions.pop(session_id, None)
    if env is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    score = env.close()
    return {"session_id": session_id, "final_score": score}


@app.get("/")
def root():
    return {
        "name": "Email Triage Environment",
        "description": "OpenEnv customer support ticket triage environment",
        "endpoints": ["/reset", "/step", "/state", "/tasks", "/health"],
        "tasks": list(TASK_CONFIGS.keys()),
    }
