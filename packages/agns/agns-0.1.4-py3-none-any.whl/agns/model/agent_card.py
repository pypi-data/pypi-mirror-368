from typing import List, Optional
from pydantic import BaseModel


class Skill(BaseModel):
    description: str


class Provider(BaseModel):
    name: str
    url: str


from typing import ClassVar

class AgentCard(BaseModel):
    TYPE_A2A: ClassVar[str] = 'type_a2a'
    TYPE_MCP: ClassVar[str] = 'mcp_type'
    url: str
    name: str
    type: Optional[str] = None
    tag: Optional[str] = None
    github: Optional[str] = None
    skills: Optional[List[Skill]] = None
    status: Optional[str] = None
    version: Optional[str] = None
    examples: Optional[List[str]] = None
    provider: Optional[Provider] = None
    description: Optional[str] = None
    lastRelease: Optional[str] = None
    availability: Optional[str] = None
    monthlyCalls: Optional[str] = None
    documentation: Optional[str] = None
