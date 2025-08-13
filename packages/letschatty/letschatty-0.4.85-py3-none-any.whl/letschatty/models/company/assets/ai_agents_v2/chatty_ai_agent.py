from pydantic import Field, field_validator
from typing import List, Any, Optional, ClassVar
from ....base_models import CompanyAssetModel
from ....base_models.chatty_asset_model import ChattyAssetPreview
from .chatty_ai_mode import ChattyAIMode
from ....utils.types.identifier import StrObjectId
from enum import StrEnum

class Tool(StrEnum):
    """Tool model"""
    CALENDAR_SCHEDULER = "calendar_scheduler"

class ChattyAIAgentPreview(ChattyAssetPreview):
    """Preview of the Chatty AI Agent"""
    general_objective: str = Field(..., description="General objective of the AI agent")

    @classmethod
    def get_projection(cls) -> dict[str, Any]:
        return super().get_projection() | {"general_objective": 1}

    @classmethod
    def from_asset(cls, asset: 'ChattyAIAgent') -> 'ChattyAIAgentPreview':
        return cls(
            _id=asset.id,
            name=asset.name,
            company_id=asset.company_id,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            general_objective=asset.general_objective
        )

class ChattyAIAgent(CompanyAssetModel):
    """AI Agent configuration model"""
    # Basic Information
    mode: ChattyAIMode = Field(default=ChattyAIMode.OFF)
    name: str = Field(..., description="Name of the AI agent")
    personality: str = Field(..., description="Detailed personality description of the agent")
    general_objective: str = Field(..., description="General objective/goal of the agent")
    unbreakable_rules: List[str] = Field(default_factory=list, description="List of unbreakable rules")
    control_triggers: List[str] = Field(default_factory=list, description="Triggers for human handoff")
    integration_user_id : Optional[StrObjectId] = Field(default=None, description="Integration user id")
    test_source_id: Optional[StrObjectId] = Field(default=None, description="Test source id")
    n8n_webhook_url: Optional[str] = Field(default=None, description="N8N webhook url")
    tools: List[Tool] = Field(default_factory=list, description="List of tools to be used by the agent")
    calendars: List[str] = Field(default_factory=list, description="List of emails to be used as calendars")
    preview_class: ClassVar[type[ChattyAIAgentPreview]] = ChattyAIAgentPreview

    # Configuration
    follow_up_strategies: List[StrObjectId] = Field(default_factory=list, description="List of follow-up strategy ids")
    contexts: List[StrObjectId] = Field(default_factory=list, description="List of context items")
    faqs: List[StrObjectId] = Field(default_factory=list, description="Frequently asked questions")
    examples: List[StrObjectId] = Field(default_factory=list, description="Training examples")

    @field_validator('personality')
    @classmethod
    def validate_personality_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Personality cannot be empty")
        return v.strip()

    @field_validator('general_objective')
    @classmethod
    def validate_objective_not_empty(cls, v):
        if not v.strip():
            raise ValueError("General objective cannot be empty")
        return v.strip()

    @property
    def integrated_user_id(self) -> StrObjectId:
        """Get the integrated user id"""
        if self.integration_user_id is None:
            raise ValueError(f"Chatty AI Agent {self.id} has no integration user id")
        return self.integration_user_id

    @property
    def test_trigger(self) -> str:
        """Get the test trigger"""
        return f"Hola! Quiero testear al Chatty AI Agent {self.name} {self.id}"

    ###example json
    {
        "id": "507f1f77bcf86cd799439011",
        "name": "Chatty AI Agent",
        "mode": "OFF",
        "personality": "Chatty AI Agent",
        "general_objective": "Chatty AI Agent",
        "unbreakable_rules": ["unbreakable rule 1", "unbreakable rule 2"],
        "control_triggers": ["control trigger 1", "control trigger 2"],
        "integration_user": {
            "id": "507f1f77bcf86cd799439011",
            "name": "Integration User"
        },
        "test_source_url": "https://test.com",
        "n8n_webhook_url": "https://n8n.com",
        "tools": ["CALENDAR_SCHEDULER"],
        "calendars": ["calendar 1", "calendar 2"],
    }