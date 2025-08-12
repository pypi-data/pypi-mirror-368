from typing import Optional, Dict, Any

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from langchain_core.language_models import BaseChatModel

from codemie_tools.pdf.pdf_tool import PDFTool
from codemie_tools.pdf.tool_vars import PDF_TOOL


class PDFToolkit(BaseToolkit):
    """
    A toolkit that integrates the PDFTool for vision-based tasks.
    """
    pdf_bytes: Optional[bytes] = None
    chat_model: Optional[BaseChatModel] = None

    @classmethod
    def get_tools_ui_info(cls, *args, **kwargs):
        """
        Returns the UI information for the toolkit.
        """
        return ToolKit(
            toolkit=ToolSet.PDF.value,
            tools=[
                Tool(name=PDF_TOOL.name, label=PDF_TOOL.label, user_description=PDF_TOOL.description),
            ]
        ).model_dump()

    def get_tools(self):
        """
        Returns a list of tools available in this toolkit.
        """
        return [PDFTool(self.pdf_bytes, chat_model = self.chat_model)]

    @classmethod
    def get_toolkit(cls,
        configs: Dict[str, Any],
        chat_model: Optional[Any] = None):
        pdf_bytes = configs.get("pdf_bytes", None)
        return PDFToolkit(pdf_bytes=pdf_bytes, chat_model=chat_model)
