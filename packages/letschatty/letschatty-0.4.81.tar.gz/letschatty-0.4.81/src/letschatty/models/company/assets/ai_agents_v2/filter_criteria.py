from enum import StrEnum
from typing import List
from pydantic import BaseModel, Field, ConfigDict
from letschatty.models.base_models.chatty_asset_model import CompanyAssetModel, ChattyAssetPreview
from letschatty.models.utils.types.identifier import StrObjectId
from letschatty.models.company.assets.company_assets import CompanyAssetType

class AttributeType(StrEnum):
    """This class represents the type of an item.
    It is used to represent the type of an item in a related asset or filter condition.
    """
    QUALITY_SCORE = "quality_score"
    BUSINESS_AREAS = "business_areas"
    FUNNELS = "funnels"
    PRODUCTS = "products"
    SALES = "sales"
    TAGS = "tags"
    SOURCES = "sources"
    GLOBAL_FILTER = "global_filter"


class Attribute(BaseModel):
    """This class is used to represent the id and type of an item.
    It is used to represent the id and type of an item in a related asset or filter condition.
    """
    attribute_id: StrObjectId | str = Field(frozen=True, description="The id of the item, could either be an object id if it's a chatty asset, or a string if it's a member of a string enum as quality score")
    attribute_type : AttributeType = Field(frozen=True, description="The type of the item")

    model_config = ConfigDict(
        extra = "ignore"
    )


class FilterCriteriaPreview(ChattyAssetPreview):
    """Preview of the filter criteria"""
    pass

class FilterCriteria(CompanyAssetModel):
    """This class represents the combination of AND and OR filters.
    Inner arrays represent OR conditions, outer array represents AND conditions.
    Example: [[A, B], [C]] means (A OR B) AND (C)
    """
    name: str = Field(description="The name of the filter criteria")
    filters: List[List[Attribute]] = Field(default_factory=list)
    is_global: bool = Field(default=False, description="Whether the filter criteria is global")

    model_config = ConfigDict(
        extra = "ignore"
    )


    ###example json
    {
        "id": "507f1f77bcf86cd799439011",
        "name": "Filter criteria",
        "filters": [[{"attribute_id": "507f1f77bcf86cd799439011", "attribute_type": "quality_score"}, {"attribute_id": "good", "attribute_type": "tags"}], [{"attribute_id": "507f1f77bcf86cd799439012", "attribute_type": "business_areas"}]],
        "is_global": False
    }