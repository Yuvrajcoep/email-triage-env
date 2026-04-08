"""Pydantic models for the Email Triage Environment."""
from __future__ import annotations
from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field

TicketCategory = Literal["billing", "technical", "account", "shipping", "general"]
TicketUrgency = Literal["low", "medium", "high", "critical"]
Department = Literal[
    "billing_team", "tech_support", "account_management", "logistics", "general_support"
]
ActionType = Literal["classify", "route", "respond", "escalate", "resolve"]


class TicketInfo(BaseModel):
    ticket_id: str
    subject: str
    body: str
    sender_name: str
    sender_email: str
    created_at: str
    previous_interactions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Action(BaseModel):
    """An action the agent takes in the environment."""
    action_type: ActionType = Field(description="Type of action to perform")
    ticket_id: str = Field(description="ID of the ticket to act on")
    # For classify
    category: Optional[TicketCategory] = Field(None, description="Ticket category")
    urgency: Optional[TicketUrgency] = Field(None, description="Urgency level")
    # For route
    department: Optional[Department] = Field(None, description="Target department")
    # For respond / escalate / resolve
    message: Optional[str] = Field(None, description="Message content")


class Reward(BaseModel):
    """Reward signal returned after each step."""
    value: float = Field(ge=0.0, le=1.0, description="Reward between 0.0 and 1.0")
    breakdown: Dict[str, float] = Field(default_factory=dict)
    reason: str = ""


class Observation(BaseModel):
    """Agent observation at each step."""
    current_ticket: Optional[TicketInfo] = None
    queue_remaining: int = Field(description="Tickets left to process")
    resolved_count: int = Field(description="Tickets completed so far")
    step_number: int
    max_steps: int
    task_name: str
    task_description: str
    required_workflow: List[str] = Field(description="Ordered actions required per ticket")
    ticket_workflow_state: Dict[str, Any] = Field(default_factory=dict)
    feedback: Optional[str] = Field(None, description="Feedback on last action")
    cumulative_score: float = 0.0
    available_actions: List[str] = Field(default_factory=list)
    episode_done: bool = False


class EnvironmentState(BaseModel):
    """Full environment state snapshot."""
    task_name: str
    episode_id: str
    step: int
    max_steps: int
    tickets_total: int
    tickets_resolved: int
    tickets_remaining: int
    current_ticket_id: Optional[str]
    ticket_states: Dict[str, Dict[str, Any]]
    cumulative_score: float
    done: bool
