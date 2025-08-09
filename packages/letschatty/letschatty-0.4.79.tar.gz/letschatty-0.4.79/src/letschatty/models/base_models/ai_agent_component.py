
from typing import List, Any, Optional
from .chatty_asset_model import ChattyAssetPreview, CompanyAssetModel
from pydantic import Field
from ..company.assets.ai_agents.filter_criteria import FilterCriteriaPreview
from ..utils.types.identifier import StrObjectId
from datetime import datetime
from enum import StrEnum

class AiAgentComponentType(StrEnum):
    """Type of the ai agent component"""
    FOLLOW_UP_STRATEGY = "follow_up_strategy"
    CONTEXT = "context"
    CHAT_EXAMPLE = "chat_example"
    FAQ = "faq"

class AiAgentComponentPreview(ChattyAssetPreview):
    """Preview of the AiAgentComponent"""
    start_time: Optional[datetime] = Field(default=None, description="The start time of the component")
    end_time: Optional[datetime] = Field(default=None, description="The end time of the component")
    is_essential: Optional[bool] = Field(default=None, description="Whether the component is essential for the ai agent to work")
    type: AiAgentComponentType = Field(description="The type of the component")
    filter_criteria: List[StrObjectId] = Field(default_factory=list, description="The assets that are related to the component")

    @classmethod
    def get_projection(cls) -> dict[str, Any]:
        return super().get_projection() | {"type": 1, "start_time": 1, "end_time": 1, "is_essential": 1, "type": 1}


class AiAgentComponent(CompanyAssetModel):
    """Protocol for models that have related chatty assets"""
    name: str = Field(description="The name of the component")
    type: AiAgentComponentType = Field(description="The type of the component")
    filter_criteria: List[StrObjectId] = Field(default_factory=list, description="The assets that are related to the component")
    start_time: Optional[datetime] = Field(default=None, description="The start time of the component")
    end_time: Optional[datetime] = Field(default=None, description="The end time of the component")
    is_essential: Optional[bool] = Field(default=False, description="Whether the component is essential for the ai agent to work")

    def has_conditional_filters(self) -> bool:
        """Check if the model has assets restrictions"""
        return len(self.filter_criteria) > 0

