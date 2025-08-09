from pydantic import BaseModel, Field
from typing import List, Optional
from enum import StrEnum

class ExampleElementType(StrEnum):
    """Type of an example element"""
    USER = "user"
    AI = "ai"
    CHAIN_OF_THOUGHT = "chain_of_thought"

class ExampleElement(BaseModel):
    """An element of a chat example"""
    type: ExampleElementType = Field(..., description="Type of the element")
    content: str = Field(..., description="Content of the element")

class ChatExample(BaseModel):
    """Example conversation for training the AI agent"""
    title: str = Field(..., description="Title/description of this example")
    content: List[ExampleElement] = Field(..., description="Sequence of elements in this example")