import logging
from .model.agent_card import AgentCard

class AgentResolver:
    def __init__(self):
        pass

    # find the best agent and tool_name
    async def resolve(self, arguments: dict = None, agents: list[AgentCard] = None) -> tuple[AgentCard, str]:
        if list is None or len(list) == 0:
            logging.error('The agents list is empty!')
            return None
        if arguments is None or len(arguments):
            logging.warning('The arguments is empty!')
        agent = agents[0]
        tool_name = None
        return (agent, tool_name)
