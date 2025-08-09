import requests
import os
from dotenv import load_dotenv
from typing import Optional, List
from .model.agent_card import AgentCard
from .agent import Agent
from typing import Any


class AgentNameServiceClient:
    DEFAULT_SERVICE_URL = "https://app.clearentitlement.com"
    PATH_GET_AGENTS = "/ce/admin/Agents"
    agents: dict[str, Agent]

    def __init__(self, service_url: Optional[str] = None):
        self.service_url = (service_url or self.DEFAULT_SERVICE_URL).rstrip("/")
        self.agents = dict()  # Initialize agents dict

    def get_agent_card(self, name: str) -> AgentCard:
        response = requests.get(f"{self.service_url}/agents/{name}")
        response.raise_for_status()
        return AgentCard(**response.json())

    def list_agents(self) -> List[AgentCard]:
        response = requests.get(f"{self.service_url}/agents")
        response.raise_for_status()
        return [AgentCard(**agent) for agent in response.json()]

    def lookup(self, name: Optional[str] = None) -> dict[str, Agent] | Agent | None:
        if not self.agents:
            self.agents = self._get_agents()
        if name is None:
            return self.agents
        if not self.agents.get(name):
            return None
        # If name is provided, get the specific agent card, otherwise use the first one
        return self.agents.get(name)
    
    
    def _get_agents(self) -> dict[str, Agent]:
        """
        Fetch agents from the API and return a dict mapping agent name to Agent instance.
        """
        print("Fetching agents from API...")
        url = f"{self.service_url}{self.PATH_GET_AGENTS}"
        api_key = os.getenv("AGNS_API_KEY")
        if not api_key:
            raise ValueError("AGNS_API_KEY environment variable is not set")
        print("API Key:", api_key)  # Debugging line to check API key

        headers = {"ApiKey": api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        agents_json = response.json()
        print("API response:", agents_json)

        agents_dict = dict[str, Agent]()
        for agent in agents_json:
            try:
                card = self._convert_agent_api_response(agent)
                agents_dict[card.name] = Agent(card=card)
            except Exception as e:
                print(f"Skipping agent due to error: {e}, data: {agent}")

        print("Total agents fetched:", len(agents_dict))
        return agents_dict
            
    def _convert_agent_api_response(self, agent: dict[str, Any]) -> AgentCard:
        """
        Convert API agent dict to AgentCard-compatible object.
        Adjust the mapping as needed based on your API response.
        """
        metadata = agent.get("metadata", {})
        return AgentCard(**metadata)

class LazyClient:
    def __init__(self):
        self._client: Optional[AgentNameServiceClient] = None

    def _get_default_client(self) -> AgentNameServiceClient:
        load_dotenv()  # Load .env once, only when needed
        return AgentNameServiceClient()

    def __getattr__(self, item: str) -> Any:
        if self._client is None:
            self._client = self._get_default_client()
        return getattr(self._client, item)