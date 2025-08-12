from typing import Optional, Dict, Any

from langchain_core.language_models import BaseChatModel

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from codemie_tools.pptx.pptx_tool import PPTXTool
from codemie_tools.pptx.tool_vars import PPTX_TOOL


class PPTXToolkit(BaseToolkit):
    """
    A toolkit that integrates the PDFTool for vision-based tasks.
    """
    pptx_bytes: Optional[bytes] = None
    chat_model: Optional[BaseChatModel] = None

    @classmethod
    def get_tools_ui_info(cls, *args, **kwargs):
        """
        Returns the UI information for the toolkit.
        """
        return ToolKit(
            toolkit=ToolSet.POWER_POINT.value,
            tools=[
                Tool(name=PPTX_TOOL.name, label=PPTX_TOOL.label, user_description=PPTX_TOOL.description),
            ]
        ).model_dump()

    def get_tools(self):
        """
        Returns a list of tools available in this toolkit.
        """
        return [PPTXTool(self.pptx_bytes, chat_model = self.chat_model)]

    @classmethod
    def get_toolkit(cls,
        configs: Dict[str, Any],
        chat_model: Optional[Any] = None):
        pptx_bytes = configs.get("pptx_bytes", None)
        return PPTXToolkit(pptx_bytes=pptx_bytes, chat_model=chat_model)
