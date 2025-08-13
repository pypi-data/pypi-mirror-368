from pydantic import BaseModel, Field, model_validator
from .context_item import ContextItem
from .chat_example import ChatExample
from typing import List, Optional
from ....utils.definitions import Area
from letschatty.models.utils.types.identifier import StrObjectId
from ....base_models import CompanyAssetModel, ChattyAssetPreview
import logging

logger = logging.getLogger(__name__)

class FollowUpStrategyPreview(ChattyAssetPreview):
    """Preview of the follow up strategy"""
    pass

class FollowUpStrategy(CompanyAssetModel):
    """Individual context item with title and content"""
    name: str = Field(description="Name of the follow up strategy")
    maximum_consecutive_follow_ups: int = Field(default=3, description="Maximum number of consecutive follow ups to be executed")
    maximum_follow_ups_to_be_executed: int = Field(default=3, description="Maximum number of follow ups to be executed in total")
    instructions_and_goals: str = Field(description="The detailed instructions for the follow up and the goals to be achieved")
    contexts: List[ContextItem] = Field(default_factory=list, description="Specific knowleadge base for the follow ups")
    examples: List[ChatExample] = Field(default_factory=list, description="Specific examples of follow ups")
    only_on_weekdays: bool = Field(default=False, description="If true, the follow up will only be executed on weekdays")
    templates_allowed: bool = Field(default=False, description="If true, the agent will send templates if the free conversation window is closed in order to perform the follow up")
    follow_up_intervals_hours: List[int] = Field(
        default=[2, 24, 72],
        description="Hours between follow-ups [1st, 2nd, 3rd, ...]. If more follow-ups than intervals, uses last interval."
    )
    area_after_reaching_max : Area = Field(default=Area.WAITING_AGENT, description="The area where the chat will be transferred after reaching the maximum number of follow ups")

    def get_interval_for_followup(self, followup_number: int) -> int:
        """Get interval for specific follow-up number (1-indexed)"""
        if followup_number <= len(self.follow_up_intervals_hours):
            return self.follow_up_intervals_hours[followup_number - 1]

        return self.follow_up_intervals_hours[-1]


    @model_validator(mode='after')
    def validate_intervals_consistency(self):
        """Ensure follow_up_intervals_hours length matches maximum_consecutive_follow_ups"""
        if len(self.follow_up_intervals_hours) != self.maximum_consecutive_follow_ups:
            raise ValueError(
                f"follow_up_intervals_hours must have exactly {self.maximum_consecutive_follow_ups} items "
                f"to match maximum_consecutive_follow_ups, got {len(self.follow_up_intervals_hours)} items"
            )
        return self


    @classmethod
    def example(cls) -> dict:
        return {
            "maximum_consecutive_follow_ups": 3,
            "maximum_follow_ups_to_be_executed": 5,
            "follow_up_intervals_hours": [2, 24, 72],  # 2h, 1d, 3d
            "instructions_and_goals": "Follow up on proposal, answer questions, close deal",
            "examples": [{"role": "user", "content": "Hello, I'm interested in your product. Can you tell me more about it?"}],
            "contexts": [{"title": "Pricing", "content": "Our pricing structure..."}],
            "only_on_weekdays": True,
            "templates_allowed": False
        }

