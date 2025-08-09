from .client import LazyClient
from .model.agent_card import AgentCard
from .agent import Agent

agns = LazyClient()

__all__ = ["agns", "AgentCard", "Agent"]
