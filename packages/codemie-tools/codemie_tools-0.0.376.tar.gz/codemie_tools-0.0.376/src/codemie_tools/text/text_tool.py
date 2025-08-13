from typing import Type, Any, Optional

import chardet
from pydantic import BaseModel, Field

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.text.tool_vars import TEXT_TOOL

class TextToolInput(BaseModel):
    file_name: str = Field(description="Name of the file you are trying to read.")

class TextTool(CodeMieTool):
    """ Tool for working with data from Plain Text files. """
    args_schema: Optional[Type[BaseModel]] = TextToolInput
    name: str = TEXT_TOOL.name
    label: str = TEXT_TOOL.label
    description: str = TEXT_TOOL.description
    file_content: Any = Field(exclude=True)

    def execute(self, file_name: str):
        bytes_data = self.bytes_content()
        encoding_info = chardet.detect(bytes_data)
        encoding = encoding_info.get('encoding') if encoding_info and encoding_info.get('encoding') else 'utf-8'

        try:
            data = bytes_data.decode(encoding)
        except UnicodeDecodeError:
            data = bytes_data.decode('utf-8', errors='replace')

        return str(data)

    def bytes_content(self) -> bytes:
        """
        Returns the content of the file as bytes
        """
        if self.file_content is None:
            raise ValueError("File content is not set")
        if isinstance(self.file_content, bytes):
            return self.file_content

        return self.file_content.encode('utf-8')
