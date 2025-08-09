from typing_extensions import override
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import AgentCard, AgentSkill, AgentCapabilities
from a2a.utils import new_agent_text_message
import uvicorn

# Define the Agent Skill
skill = AgentSkill(
    id='hello_world',
    name='Returns hello world',
    description='Just returns hello world',
    tags=['hello world'],
    examples=['hi', 'hello world'],
)

# Define the Agent Card (simplified, without AgentAuthentication)
agent_card = AgentCard(
    name='Hello World Agent',
    description='Just a hello world agent',
    url='http://localhost:9999/',
    version='1.0.0',
    defaultInputModes=['text'],
    defaultOutputModes=['text'],
    capabilities=AgentCapabilities(),
    skills=[skill],
    authentication=['public'],  # Use a list of schemes instead
)

# Define the Agent Logic
class HelloWorldAgent:
    """Hello World Agent."""
    async def invoke(self) -> str:
        return 'Hello World'

# Define the Agent Executor
class HelloWorldAgentExecutor(AgentExecutor):
    """Agent Executor for Hello World Agent."""
    def __init__(self):
        self.agent = HelloWorldAgent()

    @override
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        result = await self.agent.invoke()
        event_queue.enqueue_event(new_agent_text_message(result))

    @override
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception('cancel not supported')

# Main Server Setup
if __name__ == '__main__':
    # Set up the request handler
    request_handler = DefaultRequestHandler(
        agent_executor=HelloWorldAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    # Create the A2A Starlette application
    server_app_builder = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    # Start the server
    uvicorn.run(server_app_builder.build(), host='0.0.0.0', port=9999)