from typing import Any, Optional

from pydantic import BaseModel



class FileObject(BaseModel):

    """
    A representation of a file object.

    Attributes:
        name (str): The name of the file.
        mime_type (str): The type of the file.
        path (str): The path where the file is located.
        owner (str): The owner of the file.
        content (Any, optional): The content of the file. Defaults to None.
    """
    name: str
    mime_type: str
    path: str
    owner: str
    content: Optional[Any] = None