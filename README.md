---
title: Email Triage Environment
emoji: 📧
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
tags:
  - openenv
---

# Email Triage Environment

An **OpenEnv-compatible** environment where AI agents process a queue of customer support tickets through a realistic triage workflow — classifying urgency, routing to the right team, drafting responses, deciding when to escalate, and resolving tickets.

## Why This Environment?

Every company with a support team faces the same challenge: triaging incoming tickets correctly is high-stakes, requires judgment, and is expensive to staff. This environment lets you train and evaluate agents on:

- **Urgency/category recognition** — distinguishing a production outage from a billing question
- **Routing accuracy** — knowing which team handles what
- **Response quality** — professional, keyword-rich initial replies
- **Escalation judgment** — knowing when a legal/SLA/security issue needs human escalation
- **End-to-end resolution** — closing tickets with proper summaries

---

## Tasks

| Task | Difficulty | Tickets | Max Steps | Workflow |
|------|-----------|---------|-----------|---------|
| `ticket_classification` | Easy | 5 | 15 | classify |
| `ticket_routing` | Medium | 5 | 25 | route → respond |
| `ticket_resolution` | Hard | 8 | 60 | classify → route → respond → (escalate?) → resolve |

### Task 1: `ticket_classification` (Easy)
Classify each ticket's **category** (`billing` / `technical` / `account` / `shipping` / `general`) and **urgency** (`low` / `medium` / `high` / `critical`). One action per ticket.

**Reward:** `0.5 × category_correct + 0.5 × urgency_score` (off-by-one urgency = 0.5)

### Task 2: `ticket_routing` (Medium)
For each ticket: (1) route to the correct department, (2) write a professional initial response. Requires understanding which team handles what and composing relevant responses.

**Reward:** `0.4 × routing_correct + 0.6 × response_quality` (keyword coverage + length)

### Task 3: `ticket_resolution` (Hard)
Full lifecycle per ticket. Agent must decide whether to escalate based on ticket severity (SLA breaches, security incidents, GDPR/legal issues, executive involvement). Eight tickets, mix of escalation-required and non-escalation cases.

**Reward:** `0.6 × resolution_quality + 0.4 × escalation_decision_correct` (at resolve step); partial rewards for classify/route/respond steps.

---

## Action Space

```json
// Classify urgency and category
{"action_type": "classify", "ticket_id": "TKT-101", "category": "technical", "urgency": "critical"}

// Route to department
{"action_type": "route", "ticket_id": "TKT-201", "department": "tech_support"}

// Send initial response
{"action_type": "respond", "ticket_id": "TKT-201", "message": "Thank you for reporting this..."}

// Escalate (task 3 only, when warranted)
{"action_type": "escalate", "ticket_id": "TKT-301", "message": "SLA breach with $2M ARR client..."}

// Resolve ticket
{"action_type": "resolve", "ticket_id": "TKT-301", "message": "Root cause identified, patch deployed..."}
```

Departments: `billing_team` | `tech_support` | `account_management` | `logistics` | `general_support`

---

## Observation Space

```json
{
  "current_ticket": {
    "ticket_id": "TKT-101",
    "subject": "...",
    "body": "...",
    "sender_name": "...",
    "sender_email": "...",
    "created_at": "...",
    "previous_interactions": [],
    "metadata": {}
  },
  "queue_remaining": 4,
  "resolved_count": 1,
  "step_number": 2,
  "max_steps": 15,
  "task_name": "ticket_classification",
  "task_description": "...",
  "required_workflow": ["classify"],
  "ticket_workflow_state": {"classified": false, "routed": false, ...},
  "available_actions": ["classify"],
  "feedback": "Classification — category: ✓, urgency: ✗. Score: 0.50",
  "cumulative_score": 0.75,
  "episode_done": false
}
```

---

## Setup & Usage

### Python (direct)

```bash
pip install -r requirements.txt

python - <<'EOF'
from email_triage_env import EmailTriageEnv, Action

env = EmailTriageEnv(task_name="ticket_classification")
obs = env.reset()

while not obs.episode_done:
    # Your agent here
    action = Action(
        action_type="classify",
        ticket_id=obs.current_ticket.ticket_id,
        category="technical",
        urgency="high"
    )
    obs, reward, done, info = env.step(action)
    print(f"Reward: {reward.value:.2f} | {reward.reason}")

print(f"Final score: {env.close():.2f}")
EOF
```

### Docker

```bash
docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
```

API available at `http://localhost:7860`. See `/docs` for interactive Swagger UI.

### REST API

```bash
# Reset
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_name": "ticket_classification"}'

# Step
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{"session_id": "...", "action": {"action_type": "classify", "ticket_id": "TKT-101", "category": "technical", "urgency": "critical"}}'
```

### Inference Script

```bash
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o-mini"
export HF_TOKEN="sk-..."

python inference.py
```

---

## Baseline Scores

Measured with `gpt-4o-mini` at temperature 0:

| Task | Score |
|------|-------|
| `ticket_classification` | ~0.85 |
| `ticket_routing` | ~0.70 |
| `ticket_resolution` | ~0.55 |

---

## Reward Design

Rewards are **partial and immediate** — the agent gets signal at each step, not just episode end:

- **Classification:** Urgency near-misses (off by one level) get 0.5 instead of 0, avoiding harsh zero gradients for reasonable answers.
- **Routing:** Binary (correct department = 1.0) since routing is deterministic.
- **Response quality:** Keyword coverage weighted 70%, length 30% — encourages substantive, relevant replies.
- **Escalation:** Scored as a binary decision at resolve time, so the agent learns the tradeoff between over-escalating and under-escalating.
- **Episode score:** Mean of per-ticket scores, so partial completion is rewarded proportionally.

---

## Project Structure

```
email-triage-env/
├── email_triage_env/
│   ├── __init__.py      # Package exports
│   ├── models.py        # Pydantic types: Action, Observation, Reward, EnvironmentState
│   ├── data.py          # Ticket data with ground-truth labels (15 tickets across 3 tasks)
│   ├── graders.py       # Scoring functions per action type
│   ├── env.py           # EmailTriageEnv class (reset/step/state/close)
│   └── server.py        # FastAPI server for HF Spaces deployment
├── inference.py         # Baseline inference script (OpenAI client)
├── openenv.yaml         # OpenEnv metadata spec
├── requirements.txt
├── Dockerfile
└── README.md
```
"# email-triage-env" 
