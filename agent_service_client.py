"""
Calls the agent running on ECS Fargate (behind an Express Mode service)
instead of building/running a local Strands Agent in this process.

Replaces the old get_or_build_agent() + agent(user_text) flow that used
to run the agent directly inside app.py -- the agent itself, its tools,
and the MCP subprocess now live entirely inside the deployed container.
Flask just makes one HTTPS call per message.
https://re-7e3ec149e4fc427db528334d9f762fd9.ecs.ap-south-1.on.aws
"""

import os
import requests

AGENT_URL = "https://re-7e3ec149e4fc427db528334d9f762fd9.ecs.ap-south-1.on.aws" + "/invoke"
REQUEST_TIMEOUT_SECONDS = 90


def invoke(session_id: str, message: str, customer: dict | None) -> str:
    """Send one message to the deployed agent and return its reply text."""
    response = requests.post(
        AGENT_URL,
        json={"prompt": message, "session_id": session_id, "customer": customer},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()["result"]