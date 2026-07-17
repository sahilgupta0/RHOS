"""
RHOS Root Agent — Sequential Agent Orchestrator.

Orchestrates all sub-agents in sequence using Google ADK SequentialAgent.
Each agent writes to session state via output_key, and subsequent agents
read from that shared state.
"""

from __future__ import annotations

import logging

from google.adk.agents import SequentialAgent

from app.agents.conversation_agent import conversation_agent
from app.agents.history_agent import history_agent
from app.agents.triage_agent import triage_agent
from app.agents.medicine_agent import medicine_agent
from app.agents.doctor_agent import doctor_agent
from app.agents.followup_agent import followup_agent

logger = logging.getLogger(__name__)

# The root agent orchestrates all sub-agents sequentially.
# Vision agent is excluded from the default pipeline — it's invoked
# on-demand only when images are uploaded.
root_agent = SequentialAgent(
    name="rhos_root_agent",
    description=(
        "RHOS Clinical Decision Support Pipeline. "
        "Orchestrates conversation analysis, history review, triage classification, "
        "medication safety, clinical summary, and follow-up planning."
    ),
    sub_agents=[
        conversation_agent,
        history_agent,
        triage_agent,
        medicine_agent,
        doctor_agent,
        followup_agent,
    ],
)
