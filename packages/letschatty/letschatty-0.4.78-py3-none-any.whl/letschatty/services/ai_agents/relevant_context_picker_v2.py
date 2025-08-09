
# from letschatty.models.company.assets.ai_agents.related_asset import FilterItem, FilterItemType
# from letschatty.models.company.assets.company_assets import CompanyAssetType
# from letschatty.models.chat.chat import Chat
# from typing import List, Type
# from letschatty.models.base_models.related_asset_mixin import AiAgentComponent
# from letschatty.models.company.assets.ai_agents.related_asset import ItemsConditionalFilter, GlobalConditionalFilter
# from letschatty.models.chat.quality_scoring import QualityScore

# class RelevantContextPicker:

#     @staticmethod
#     def should_be_used(ai_agent_item : AiAgentComponent, chat:Chat) -> bool:
#         if ai_agent_item.has_conditional_filters():
#             return RelevantContextPicker.check_global_and_local_filters_on_chat(ai_agent_item, chat)
#         return True

#     @staticmethod
#     def is_ANY_OR_filter_matched(or_filters: List[FilterItem], chat:Chat) -> bool:
#         if not or_filters:
#             return True
#         if not any(RelevantContextPicker.is_item_related_to_chat(or_filter, chat) for or_filter in or_filters):
#             return False
#         return True

#     @staticmethod
#     def are_ALL_AND_filter_matched(conditional_filter: ItemsConditionalFilter, chat:Chat) -> bool:
#         if not conditional_filter.filters:
#             return True
#         if not all(RelevantContextPicker.is_ANY_OR_filter_matched(or_filters, chat) for or_filters in conditional_filter.filters):
#             return False
#         return True

#     @staticmethod
#     def is_item_related_to_chat(item_id_and_type : FilterItem, chat:Chat) -> bool:
#         if item_id_and_type.type == FilterItemType.TAGS:
#             return item_id_and_type.id in chat.assigned_tag_ids
#         if item_id_and_type.type == FilterItemType.PRODUCTS:
#             return item_id_and_type.id in chat.assigned_product_ids or item_id_and_type.id in chat.bought_product_ids
#         if item_id_and_type.type == FilterItemType.SOURCES:
#             return item_id_and_type.id in chat.assigned_source_ids
#         if item_id_and_type.type == FilterItemType.QUALITY_SCORE:
#             return QualityScore(chat.client.lead_quality) == item_id_and_type.id
#         if item_id_and_type.type == FilterItemType.SALES:
#             return item_id_and_type.id in chat.bought_product_ids
#         if item_id_and_type.type == FilterItemType.BUSINESS_AREAS:
#             raise NotImplementedError("Business areas are not supported yet")
#         if item_id_and_type.type == FilterItemType.FUNNELS:
#             raise NotImplementedError("Funnels are not supported yet")
#         return False

#     @staticmethod
#     def check_global_and_local_filters_on_chat(ai_agent_item : AiAgentComponent, chat:Chat) -> bool:
#         """Check if the chat passes the global and local filters of the ai agent item"""
#         local_filters_passed = RelevantContextPicker.are_ALL_AND_filter_matched(ai_agent_item.filter_criteria, chat)
#         global_filters_passed = RelevantContextPicker.are_ALL_AND_filter_matched(ai_agent_item.global_conditional_filters, chat)
#         return local_filters_passed and global_filters_passed



