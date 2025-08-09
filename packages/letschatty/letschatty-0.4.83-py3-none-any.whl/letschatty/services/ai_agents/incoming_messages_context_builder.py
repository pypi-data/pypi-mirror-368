from letschatty.models.chat.chat import Chat
from letschatty.models.company.assets.ai_agents.chatty_ai_agent import ChattyAIAgent
from letschatty.models.company.assets.ai_agents.chain_of_thought_in_chat import ChainOfThoughtInChatTrigger
from letschatty.models.company.assets.ai_agents.chatty_ai_mode import ChattyAIMode
from letschatty.services.ai_agents.context_builder import ContextBuilder
from letschatty.models.company.empresa import EmpresaModel

class IncomingMessagesContextBuilder(ContextBuilder):

    @staticmethod
    def build_prompt(agent: ChattyAIAgent, mode_in_chat: ChattyAIMode, company_info:EmpresaModel, chat:Chat) -> str:
        if agent.mode == ChattyAIMode.OFF:
            raise ValueError("Agent is in OFF mode, so it can't be used to build context")
        context = ContextBuilder.common_prompt(agent, mode_in_chat, company_info)
        context += ContextBuilder.relevant_contexts(agent.contexts, chat)
        context += ContextBuilder.relevant_faqs(agent.faqs, chat)
        context += ContextBuilder.relevant_examples(agent.examples, chat)
        context += ContextBuilder.unbreakable_rules(agent)
        context += ContextBuilder.control_triggers(agent)
        context += ContextBuilder.chain_of_thought_instructions(agent, mode_in_chat, ChainOfThoughtInChatTrigger.USER_MESSAGE)
        return context
