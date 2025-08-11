from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.adk.plugins.base_plugin import BasePlugin
from sparkden.assistants.models import ProgressItemStatus


class ProgressInfoPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="progress_info")

    async def before_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> None:
        progress_info = callback_context.state.get("progress_info") or {}
        progress_info[callback_context.agent_name] = ProgressItemStatus.RUNNING
        callback_context.state["progress_info"] = progress_info

    async def after_model_callback(
        self, *, callback_context: CallbackContext, llm_response: LlmResponse
    ) -> LlmResponse | None:
        progress_info = callback_context.state.get("progress_info")
        if progress_info:
            progress_info.pop(callback_context.agent_name, None)
            callback_context.state["progress_info"] = progress_info
        else:
            callback_context.state["progress_info"] = None
