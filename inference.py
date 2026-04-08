"""
Inference Script — Email Triage Environment
============================================
Mandatory env vars:
    API_BASE_URL   LLM endpoint  (default: https://api.openai.com/v1)
    MODEL_NAME     Model ID      (default: gpt-4o-mini)
    HF_TOKEN       API key

Stdout format (required by evaluator):
    [START] task=<name> env=email-triage model=<model>
    [STEP]  step=<n> action=<json> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<0.00> rewards=<r1,r2,...>
"""
import json
import os
import sys
from typing import List

from openai import OpenAI

from email_triage_env import EmailTriageEnv, Action

# ---- Configuration (mandatory env vars) ----
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY", "")
LOCAL_IMAGE_NAME = os.getenv("IMAGE_NAME", "email-triage-env")  # for from_docker_image() if used

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

# ---- System prompt ----
SYSTEM_PROMPT = """You are an expert customer support manager processing a ticket queue.

At each step you will receive the current environment observation as JSON. You must respond
with a SINGLE valid JSON action object — no other text, no markdown, no explanation.

Action schemas:
  classify  → {"action_type":"classify",  "ticket_id":"TKT-XXX", "category":"billing|technical|account|shipping|general", "urgency":"low|medium|high|critical"}
  route     → {"action_type":"route",     "ticket_id":"TKT-XXX", "department":"billing_team|tech_support|account_management|logistics|general_support"}
  respond   → {"action_type":"respond",   "ticket_id":"TKT-XXX", "message":"<professional customer reply, 100+ chars>"}
  escalate  → {"action_type":"escalate",  "ticket_id":"TKT-XXX", "message":"<reason for escalation>"}
  resolve   → {"action_type":"resolve",   "ticket_id":"TKT-XXX", "message":"<resolution summary>"}

Rules:
- Use the ticket_id shown in current_ticket.ticket_id.
- Follow the available_actions list — only use listed action types.
- For respond/resolve/escalate, write substantive messages (100+ characters).
- Escalate only when truly warranted: SLA breaches, security incidents, legal/regulatory issues, executive involvement.
"""


def get_action(obs_json: str) -> dict:
    """Call the LLM to decide the next action."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Observation:\n{obs_json}\n\nNext action:"},
        ],
        response_format={"type": "json_object"},
        temperature=0,
        max_tokens=512,
    )
    return json.loads(response.choices[0].message.content)


def run_task(task_name: str) -> float:
    """Run a full episode for one task. Returns final score."""
    env = EmailTriageEnv(task_name=task_name)
    cfg_max_steps = {"ticket_classification": 15, "ticket_routing": 25, "ticket_resolution": 60}
    max_steps = cfg_max_steps.get(task_name, 60)

    obs = env.reset()
    print(f"[START] task={task_name} env=email-triage model={MODEL_NAME}", flush=True)

    rewards: List[float] = []
    step = 0
    done = False

    while not done and step < max_steps:
        step += 1

        # Build observation string (exclude ground truth / internal fields)
        obs_dict = obs.model_dump()
        obs_json = json.dumps(obs_dict, indent=2, default=str)

        try:
            action_dict = get_action(obs_json)
        except Exception as e:
            err = str(e).replace("\n", " ")
            print(f"[STEP] step={step} action=null reward=0.00 done=false error={err}", flush=True)
            rewards.append(0.0)
            break

        try:
            action = Action(**action_dict)
        except Exception as e:
            err = str(e).replace("\n", " ")
            action_str = json.dumps(action_dict, separators=(",", ":"))
            print(f"[STEP] step={step} action={action_str} reward=0.00 done=false error={err}", flush=True)
            rewards.append(0.0)
            continue

        action_str = json.dumps(action_dict, separators=(",", ":"))

        try:
            obs, reward, done, info = env.step(action)
            error = info.get("error") or "null"
            rewards.append(reward.value)
            print(
                f"[STEP] step={step} action={action_str} reward={reward.value:.2f} "
                f"done={str(done).lower()} error={error}",
                flush=True,
            )
        except Exception as e:
            err = str(e).replace("\n", " ")
            print(
                f"[STEP] step={step} action={action_str} reward=0.00 done=false error={err}",
                flush=True,
            )
            rewards.append(0.0)
            break

    final_score = env.close()
    success = final_score >= 0.5
    rewards_str = ",".join(f"{r:.2f}" for r in rewards) if rewards else "0.00"
    print(
        f"[END] success={str(success).lower()} steps={step} score={final_score:.2f} rewards={rewards_str}",
        flush=True,
    )
    return final_score


def main():
    tasks = [
        "ticket_classification",
        "ticket_routing",
        "ticket_resolution",
    ]
    all_scores = []
    for task in tasks:
        score = run_task(task)
        all_scores.append(score)

    overall = sum(all_scores) / len(all_scores)
    print(f"\nOverall average score: {overall:.2f}", file=sys.stderr)


if __name__ == "__main__":
    main()
