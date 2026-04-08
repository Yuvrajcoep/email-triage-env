"""Root-level Pydantic models for the Email Triage Environment."""

from typing import Any, Dict, List, Literal, Optional

from openenv.core.env_server.types import Action, Observation
from pydantic import Field

TicketCategory = Literal["billing", "technical", "account", "shipping", "general"]
TicketUrgency = Literal["low", "medium", "high", "critical"]
Department = Literal[
    "billing_team", "tech_support", "account_management", "logistics", "general_support"
]
ActionType = Literal["classify", "route", "respond", "escalate", "resolve"]


class EmailTriageAction(Action):
    """Action for the Email Triage environment."""

    action_type: ActionType = Field(description="Type of action to perform")
    ticket_id: str = Field(description="ID of the ticket to act on")
    category: Optional[TicketCategory] = Field(None, description="For classify action")
    urgency: Optional[TicketUrgency] = Field(None, description="For classify action")
    department: Optional[Department] = Field(None, description="For route action")
    message: Optional[str] = Field(None, description="For respond/escalate/resolve")


class EmailTriageObservation(Observation):
    """Observation from the Email Triage environment."""

    current_ticket: Optional[Dict[str, Any]] = Field(None, description="Current ticket to process")
    queue_remaining: int = Field(0, description="Tickets left to process")
    resolved_count: int = Field(0, description="Tickets completed so far")
    step_number: int = Field(0)
    max_steps: int = Field(60)
    task_name: str = Field("")
    task_description: str = Field("")
    required_workflow: List[str] = Field(default_factory=list)
    ticket_workflow_state: Dict[str, Any] = Field(default_factory=dict)
    feedback: Optional[str] = Field(None)
    cumulative_score: float = Field(0.0)
    available_actions: List[str] = Field(default_factory=list)
