"""Email Triage Environment Client."""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from .models import EmailTriageAction, EmailTriageObservation


class EmailTriageEnvClient(
    EnvClient[EmailTriageAction, EmailTriageObservation, State]
):
    """
    Client for the Email Triage Environment.

    Maintains a persistent WebSocket connection to the environment server,
    enabling efficient multi-step ticket triage interactions.

    Example:
        >>> with EmailTriageEnvClient(base_url="http://localhost:7860") as client:
        ...     result = client.reset()
        ...     print(result.observation.current_ticket)
        ...
        ...     action = EmailTriageAction(
        ...         action_type="classify",
        ...         ticket_id="TKT-101",
        ...         category="technical",
        ...         urgency="critical"
        ...     )
        ...     result = client.step(action)
        ...     print(result.reward)
    """

    def _step_payload(self, action: EmailTriageAction) -> Dict:
        return action.model_dump(exclude_none=True)

    def _parse_result(self, payload: Dict) -> StepResult[EmailTriageObservation]:
        obs_data = payload.get("observation", payload)
        observation = EmailTriageObservation(
            done=payload.get("done", False),
            reward=payload.get("reward"),
            metadata=obs_data.get("metadata", {}),
            current_ticket=obs_data.get("current_ticket"),
            queue_remaining=obs_data.get("queue_remaining", 0),
            resolved_count=obs_data.get("resolved_count", 0),
            step_number=obs_data.get("step_number", 0),
            max_steps=obs_data.get("max_steps", 60),
            task_name=obs_data.get("task_name", ""),
            task_description=obs_data.get("task_description", ""),
            required_workflow=obs_data.get("required_workflow", []),
            ticket_workflow_state=obs_data.get("ticket_workflow_state", {}),
            feedback=obs_data.get("feedback"),
            cumulative_score=obs_data.get("cumulative_score", 0.0),
            available_actions=obs_data.get("available_actions", []),
        )
        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
