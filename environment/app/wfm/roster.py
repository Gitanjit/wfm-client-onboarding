"""Agents: data/agents/<client>.csv -> list of Agent."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from wfm.config import DATA_DIR


@dataclass(frozen=True)
class Agent:
    agent_id: str
    contract: str            # "FT" | "PT"
    skills: frozenset[str]   # queues the agent may serve


def load_agents(client: str) -> list[Agent]:
    df = pd.read_csv(DATA_DIR / "agents" / f"{client}.csv", dtype=str)
    return [Agent(r.agent_id, r.contract, frozenset(r.skills.split(";"))) for r in df.itertuples(index=False)]
