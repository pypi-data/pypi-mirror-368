import io
from typing import Dict, Any, Optional

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool

from codemie_tools.text.text_tool import TextTool
from codemie_tools.text.tool_vars import TEXT_TOOL


class TextFileToolkit(BaseToolkit):
    file_content: Optional[bytes] = None
    file_name: Optional[str] = None

    @classmethod
    def get_tools_ui_info(cls, *args, **kwargs):
        return ToolKit(
            toolkit=ToolSet.TEXT,
            tools=[
                Tool.from_metadata(TEXT_TOOL),
            ]
        ).model_dump()

    def get_tools(self):
        text_tool = TextTool(file_content=self.file_content)
        return [text_tool]

    @classmethod
    def get_toolkit(cls, configs: Dict[str, Any]):
        file_content = configs.get("file_content", None)
        file_name = configs.get("file_name", None)
        return cls(file_content=file_content, file_name=file_name)
