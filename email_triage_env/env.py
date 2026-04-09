"""Main EmailTriageEnv class — OpenEnv-compatible customer support triage environment."""
import uuid
from copy import deepcopy
from typing import Dict, Any, List, Optional, Tuple

from .models import Action, Observation, Reward, EnvironmentState, TicketInfo
from .data import TASK1_TICKETS, TASK2_TICKETS, TASK3_TICKETS
from .graders import (
    grade_classification, grade_routing, grade_response,
    grade_escalation_decision, grade_resolution,
)

TASK_CONFIGS: Dict[str, Any] = {
    "ticket_classification": {
        "description": (
            "Classify each customer support ticket by its category and urgency level. "
            "For each ticket, use the 'classify' action with:\n"
            "  category: billing | technical | account | shipping | general\n"
            "  urgency:  low | medium | high | critical\n"
            "Work through all tickets in the queue."
        ),
        "required_workflow": ["classify"],
        "tickets": TASK1_TICKETS,
        "max_steps": 15,
        "difficulty": "easy",
    },
    "ticket_routing": {
        "description": (
            "For each ticket, perform two actions in order:\n"
            "  1. route  — assign to the correct department:\n"
            "     billing_team | tech_support | account_management | logistics | general_support\n"
            "  2. respond — write a professional initial response to the customer\n"
            "     (at least 100 characters; include: acknowledgment, next steps, timeline)."
        ),
        "required_workflow": ["route", "respond"],
        "tickets": TASK2_TICKETS,
        "max_steps": 25,
        "difficulty": "medium",
    },
    "ticket_resolution": {
        "description": (
            "Handle each ticket through its full lifecycle in order:\n"
            "  1. classify  — set category and urgency\n"
            "  2. route     — assign to correct department\n"
            "  3. respond   — send initial response to customer\n"
            "  4. escalate  — ONLY if the situation warrants it (SLA breaches, legal issues,\n"
            "                 executive involvement, security breaches, regulatory compliance)\n"
            "  5. resolve   — close ticket with a summary of actions taken\n"
            "Use your judgment on when escalation is truly required."
        ),
        "required_workflow": ["classify", "route", "respond", "resolve"],
        "tickets": TASK3_TICKETS,
        "max_steps": 60,
        "difficulty": "hard",
    },
}


class EmailTriageEnv:
    """
    Customer Support Email Triage OpenEnv Environment.

    An AI agent processes a queue of customer support tickets by classifying,
    routing, responding to, and resolving them. Three tasks of increasing difficulty
    model the real-world support workflow.

    Usage:
        env = EmailTriageEnv(task_name="ticket_classification")
        obs = env.reset()
        while not done:
            action = agent.decide(obs)
            obs, reward, done, info = env.step(action)
        score = env.close()
    """

    def __init__(self, task_name: str = "ticket_classification"):
        if task_name not in TASK_CONFIGS:
            raise ValueError(
                f"Unknown task '{task_name}'. Choose from: {list(TASK_CONFIGS.keys())}"
            )
        self.task_name = task_name
        self._episode_id = ""
        self._step = 0
        self._tickets: List[Dict] = []
        self._ticket_states: Dict[str, Dict] = {}
        self._current_idx = 0
        self._ticket_scores: List[float] = []
        self._done = False
        self._last_feedback: Optional[str] = None

    # ------------------------------------------------------------------
    # OpenEnv interface
    # ------------------------------------------------------------------

    def reset(self) -> Observation:
        """Reset the environment for a new episode and return initial observation."""
        cfg = TASK_CONFIGS[self.task_name]
        self._episode_id = str(uuid.uuid4())
        self._step = 0
        self._tickets = deepcopy(cfg["tickets"])
        self._ticket_states = {}
        self._current_idx = 0
        self._ticket_scores = []
        self._done = False
        self._last_feedback = None

        for t in self._tickets:
            tid = t["ticket"]["ticket_id"]
            self._ticket_states[tid] = {
                "classified": False,
                "routed": False,
                "responded": False,
                "escalated": False,
                "was_escalated": False,
                "resolved": False,
                "actions_taken": [],
                "workflow_scores": {},
                "score": 0.0,
            }
        return self._make_observation()

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict]:
        """
        Execute one action.

        Returns:
            observation: Updated observation
            reward:      Per-step reward (0.0–1.0)
            done:        True when episode is complete
            info:        Dict with 'error', 'ticket_id', 'ticket_complete', 'episode_score'
        """
        self._step += 1
        cfg = TASK_CONFIGS[self.task_name]

        if self._done:
            return self._make_observation(), Reward(value=0.0, reason="Episode already done"), True, {"error": "episode_done"}

        if self._current_idx >= len(self._tickets):
            self._done = True
            return self._make_observation(), Reward(value=0.0, reason="No more tickets"), True, {"error": None}

        current_ticket_data = self._tickets[self._current_idx]
        current_tid = current_ticket_data["ticket"]["ticket_id"]

        if action.ticket_id != current_tid:
            msg = f"Wrong ticket_id '{action.ticket_id}'. Current ticket is '{current_tid}'."
            self._last_feedback = msg
            return self._make_observation(), Reward(value=0.0, reason=msg), False, {"error": msg}

        reward, feedback, ticket_complete = self._process_action(action, current_ticket_data)
        self._last_feedback = feedback

        if ticket_complete:
            tstate = self._ticket_states[current_tid]
            scores = list(tstate["workflow_scores"].values())
            ticket_score = sum(scores) / max(1, len(scores))
            tstate["score"] = round(ticket_score, 4)
            self._ticket_scores.append(ticket_score)
            self._current_idx += 1

        # Episode done when all tickets processed or max_steps reached
        if self._current_idx >= len(self._tickets):
            self._done = True
        elif self._step >= cfg["max_steps"]:
            self._done = True
            # Zero-score any unfinished tickets
            while len(self._ticket_scores) < len(self._tickets):
                self._ticket_scores.append(0.0)

        episode_score = self._compute_episode_score() if self._done else None
        info: Dict[str, Any] = {
            "ticket_id": current_tid,
            "ticket_complete": ticket_complete,
            "episode_score": episode_score,
            "error": None,
        }
        return self._make_observation(), reward, self._done, info

    def state(self) -> EnvironmentState:
        """Return a full snapshot of the current environment state."""
        cfg = TASK_CONFIGS[self.task_name]
        current_tid = (
            self._tickets[self._current_idx]["ticket"]["ticket_id"]
            if self._current_idx < len(self._tickets)
            else None
        )
        return EnvironmentState(
            task_name=self.task_name,
            episode_id=self._episode_id,
            step=self._step,
            max_steps=cfg["max_steps"],
            tickets_total=len(self._tickets),
            tickets_resolved=self._current_idx,
            tickets_remaining=len(self._tickets) - self._current_idx,
            current_ticket_id=current_tid,
            ticket_states=deepcopy(self._ticket_states),
            cumulative_score=self._compute_episode_score(),
            done=self._done,
        )

    def close(self) -> float:
        """Close the environment and return the final episode score (0.0–1.0)."""
        return self._compute_episode_score()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_episode_score(self) -> float:
        if not self._ticket_scores:
            return 0.01
        raw = sum(self._ticket_scores) / len(self._ticket_scores)
        # Scores must be strictly within (0, 1)
        return max(0.01, min(0.99, round(raw, 4)))

    def _process_action(
        self, action: Action, ticket_data: Dict
    ) -> Tuple[Reward, str, bool]:
        """Execute a single action; return (reward, feedback, ticket_complete)."""
        tid = action.ticket_id
        tstate = self._ticket_states[tid]
        gt = ticket_data["ground_truth"]
        tstate["actions_taken"].append(action.action_type)

        # ---- CLASSIFY ----
        if action.action_type == "classify":
            if tstate["classified"]:
                return Reward(value=0.0, reason="Already classified"), "Already classified.", False
            if not action.category or not action.urgency:
                msg = "classify requires both 'category' and 'urgency'."
                return Reward(value=0.0, reason=msg), msg, False

            scores = grade_classification(action.category, action.urgency, gt)
            tstate["classified"] = True
            tstate["workflow_scores"]["classify"] = scores["total"]
            cat_ok = "OK" if scores["category"] == 1 else "WRONG"
            urg_detail = "OK" if scores["urgency"] == 1 else "PARTIAL" if scores["urgency"] == 0.5 else "WRONG"
            feedback = f"Classification - category:{cat_ok}, urgency:{urg_detail}. Score: {scores['total']:.2f}"
            ticket_complete = self.task_name == "ticket_classification"
            return Reward(value=scores["total"], breakdown=scores, reason=feedback), feedback, ticket_complete

        # ---- ROUTE ----
        elif action.action_type == "route":
            if tstate["routed"]:
                return Reward(value=0.0, reason="Already routed"), "Already routed.", False
            if not action.department:
                msg = "route requires 'department'."
                return Reward(value=0.0, reason=msg), msg, False

            scores = grade_routing(action.department, gt)
            tstate["routed"] = True
            tstate["workflow_scores"]["route"] = scores["total"]
            correct = scores["total"] == 1.0
            routing_detail = "correct" if correct else f"expected {gt['department']}, got {action.department}"
            feedback = f"Routing - {'OK' if correct else 'WRONG'} ({routing_detail}). Score: {scores['total']:.2f}"
            # In task_routing, ticket completes after both route+respond
            ticket_complete = (
                self.task_name == "ticket_routing" and tstate["routed"] and tstate["responded"]
            )
            return Reward(value=scores["total"], breakdown=scores, reason=feedback), feedback, ticket_complete

        # ---- RESPOND ----
        elif action.action_type == "respond":
            if tstate["responded"]:
                return Reward(value=0.0, reason="Already responded"), "Already responded.", False
            if not action.message or len(action.message.strip()) < 20:
                msg = "respond message must be at least 20 characters."
                return Reward(value=0.0, reason=msg), msg, False

            scores = grade_response(action.message, gt)
            tstate["responded"] = True
            tstate["workflow_scores"]["respond"] = scores["total"]
            feedback = (
                f"Response — keyword coverage: {scores['keyword_coverage']:.0%}, "
                f"length ok: {'✓' if scores['length']>=0.5 else '✗'}. Score: {scores['total']:.2f}"
            )
            ticket_complete = (
                self.task_name == "ticket_routing" and tstate["routed"] and tstate["responded"]
            )
            return Reward(value=scores["total"], breakdown=scores, reason=feedback), feedback, ticket_complete

        # ---- ESCALATE ----
        elif action.action_type == "escalate":
            if tstate["escalated"]:
                return Reward(value=0.0, reason="Already escalated"), "Already escalated.", False
            tstate["escalated"] = True
            tstate["was_escalated"] = True
            feedback = "Escalation recorded. Proceed to resolve the ticket."
            # Escalation score computed at resolve time; return 0 now
            return Reward(value=0.0, reason="Escalation recorded (scored at resolution)"), feedback, False

        # ---- RESOLVE ----
        elif action.action_type == "resolve":
            if tstate["resolved"]:
                return Reward(value=0.0, reason="Already resolved"), "Already resolved.", False
            if not action.message or len(action.message.strip()) < 20:
                msg = "resolve message must be at least 20 characters."
                return Reward(value=0.0, reason=msg), msg, False

            res_score = grade_resolution(action.message, gt)
            esc_score = grade_escalation_decision(tstate["was_escalated"], gt)
            tstate["resolved"] = True
            tstate["workflow_scores"]["escalation_decision"] = esc_score
            tstate["workflow_scores"]["resolve"] = res_score

            should = gt.get("requires_escalation", False)
            esc_verdict = "correct" if esc_score == 1 else ("should have escalated" if should else "should NOT have escalated")
            feedback = f"Resolution score: {res_score:.2f}. Escalation decision: {esc_verdict}."
            combined = 0.6 * res_score + 0.4 * esc_score
            return (
                Reward(value=round(combined, 4), breakdown={"resolution": res_score, "escalation": esc_score}, reason=feedback),
                feedback,
                True,  # resolve always completes the ticket in task3
            )

        else:
            msg = f"Unknown action_type: {action.action_type}"
            return Reward(value=0.0, reason=msg), msg, False

    def _get_available_actions(self, tstate: Dict) -> List[str]:
        if self.task_name == "ticket_classification":
            return [] if tstate["classified"] else ["classify"]

        if self.task_name == "ticket_routing":
            available = []
            if not tstate["routed"]:
                available.append("route")
            if not tstate["responded"]:
                available.append("respond")
            return available

        # ticket_resolution — strict order
        if not tstate["classified"]:
            return ["classify"]
        if not tstate["routed"]:
            return ["route"]
        if not tstate["responded"]:
            return ["respond"]
        if not tstate["resolved"]:
            actions = ["resolve"]
            if not tstate["escalated"]:
                actions.insert(0, "escalate")
            return actions
        return []

    def _make_observation(self) -> Observation:
        cfg = TASK_CONFIGS[self.task_name]

        if self._current_idx >= len(self._tickets):
            return Observation(
                current_ticket=None,
                queue_remaining=0,
                resolved_count=len(self._tickets),
                step_number=self._step,
                max_steps=cfg["max_steps"],
                task_name=self.task_name,
                task_description=cfg["description"],
                required_workflow=cfg["required_workflow"],
                feedback=self._last_feedback,
                cumulative_score=self._compute_episode_score(),
                available_actions=[],
                episode_done=True,
            )

        ticket_data = self._tickets[self._current_idx]
        ticket = TicketInfo(**ticket_data["ticket"])
        tid = ticket.ticket_id
        tstate = self._ticket_states[tid]

        return Observation(
            current_ticket=ticket,
            queue_remaining=len(self._tickets) - self._current_idx,
            resolved_count=self._current_idx,
            step_number=self._step,
            max_steps=cfg["max_steps"],
            task_name=self.task_name,
            task_description=cfg["description"],
            required_workflow=cfg["required_workflow"],
            ticket_workflow_state={
                "classified": tstate["classified"],
                "routed": tstate["routed"],
                "responded": tstate["responded"],
                "escalated": tstate["escalated"],
                "resolved": tstate["resolved"],
                "actions_taken": tstate["actions_taken"],
            },
            feedback=self._last_feedback,
            cumulative_score=self._compute_episode_score(),
            available_actions=self._get_available_actions(tstate),
            episode_done=False,
        )
