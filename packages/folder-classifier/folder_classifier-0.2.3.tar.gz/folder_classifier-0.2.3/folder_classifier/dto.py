from __future__ import annotations

from textwrap import dedent
from typing import List, Union, Literal, Optional

from pydantic import BaseModel, Field, confloat


class ModelConfig(BaseModel):
    app_name: str
    deployment: str


class AppConfig(BaseModel):
    model: ModelConfig


class File(BaseModel):
    name: str
    type: Literal["file"]


class Folder(BaseModel):
    name: str
    type: Literal["folder"]
    # Discriminated union: 'type' field is used to select between File and Folder
    items: Optional[List[Union[File, Folder]]] = Field(default_factory=list)
    model_config = {
        "json_schema_extra": {
            # Override the OpenAPI example to avoid the default 'string' entry
            "example": dedent("""{
                "name": "string",
                "type": "folder",
                "items": [
                    {
                      "name": "string",
                      "type": "file"
                    }
                  ]
                }""")
        }
    }


class Listing(BaseModel):
    items: List[str]


Folder.model_rebuild()
FolderClassificationRequest = Listing

class FolderClassificationResponse(BaseModel):
    category: Literal["matter", "other"]
    confidence: confloat(ge=0.0, le=1.0)