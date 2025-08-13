from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from vector_bridge.schema.helpers.enums import (AIProviders, AnthropicModels,
                                                DeepSeekModels, OpenAIModels)

DEFAULT_INSTRUCTION = "default"
DEFAULT_AGENT = "default"
FORWARD_DIALOGUE_TO_AGENT = "forward_dialogue_to_agent"


class InstructionsSorting(str, Enum):
    created_at = "created_at"
    updated_at = "updated_at"


class InstructionType(str, Enum):
    text = "text"
    voice = "voice"


class Position(BaseModel):
    x: float
    y: float


class OpenAI(BaseModel):
    api_key: str
    model: OpenAIModels
    max_tokens: int
    frequency_penalty: float
    presence_penalty: float
    temperature: float


class AzureOpenAI(OpenAI):
    endpoint: str = Field(default="")


class Anthropic(BaseModel):
    api_key: str
    model: AnthropicModels
    max_tokens: int
    temperature: float


class DeepSeek(BaseModel):
    api_key: str
    model: DeepSeekModels
    max_tokens: int
    frequency_penalty: float
    presence_penalty: float
    temperature: float


class VLLM(BaseModel):
    endpoint: str
    model: str
    max_tokens: int
    frequency_penalty: float
    presence_penalty: float
    temperature: float


class AI(BaseModel):
    default_ai: AIProviders
    open_ai: OpenAI
    # azure_open_ai: AzureOpenAI
    anthropic: Anthropic
    deepseek: DeepSeek
    vllm: VLLM


class Prompts(BaseModel):
    system_prompt: str
    message_prompt: str
    knowledge_prompt: str


class Subordinate(BaseModel):
    subordinate_name: str
    delegation_decision: str


class AgentCreate(BaseModel):
    agent_name: str
    ai_provider: AIProviders
    model: str
    endpoint: Union[str, None] = None


class Agent(BaseModel):
    agent_name: str
    ai_provider: AIProviders
    model: str
    endpoint: Union[str, None] = None
    prompts: Prompts
    functions: List[str]
    subordinates: Dict[str, Subordinate] = Field(default_factory=dict)
    tool_choice: Optional[str]
    position: Position

    def get_subordinate_by_name(self, name: str):
        return self.subordinates.get(name)


class AgentPosition(BaseModel):
    agent_name: str
    position: Position


class AgentPositions(BaseModel):
    agents: List[AgentPosition]


class InstructionCreate(BaseModel):
    instruction_name: str
    instruction_type: InstructionType = Field(default=InstructionType.text)
    description: str
    open_ai_api_key: str = ""
    # azure_open_ai_api_key: str = ""
    # azure_open_ai_endpoint: str = ""
    anthropic_api_key: str = ""
    deepseek_api_key: str = ""


class Instruction(BaseModel):
    integration_id: str
    instruction_id: str
    instruction_name: str
    instruction_type: InstructionType = Field(default=InstructionType.text)
    description: str = Field(default="")
    created_at: datetime = Field(default=None)
    created_by: str = Field(default="")
    updated_at: datetime = Field(default=None)
    updated_by: str = Field(default="")
    ai: AI
    agents: Dict[str, Agent]
    max_turns: int
    debug: bool

    @property
    def uuid(self):
        return self.instruction_id

    @property
    def ai_provider(self):
        if self.is_open_ai:
            return self.ai.open_ai
        elif self.is_anthropic:
            return self.ai.anthropic
        elif self.is_deepseek:
            return self.ai.deepseek

    @property
    def is_open_ai(self):
        return self.ai.default_ai == AIProviders.OPEN_AI

    @property
    def is_anthropic(self):
        return self.ai.default_ai == AIProviders.ANTHROPIC

    @property
    def is_deepseek(self):
        return self.ai.default_ai == AIProviders.DEEP_SEEK

    def get_agent_by_name(self, name: str):
        return self.agents.get(name)

    def get_system_prompt(self, agent_name: str = DEFAULT_AGENT):
        agent = self.get_agent_by_name(name=agent_name)
        if agent:
            return agent.prompts.system_prompt

    def get_message_prompt(self, agent_name: str = DEFAULT_AGENT):
        agent = self.get_agent_by_name(name=agent_name)
        if agent:
            return agent.prompts.message_prompt

    def get_knowledge_prompt(self, agent_name: str = DEFAULT_AGENT):
        agent = self.get_agent_by_name(name=agent_name)
        if agent:
            return agent.prompts.knowledge_prompt


class PaginatedInstructions(BaseModel):
    instructions: List[Instruction] = Field(default_factory=list)
    limit: int
    last_evaluated_key: Optional[str] = None
    has_more: bool = False
