from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class Turn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    role: Literal['user', 'assistant']
    content: str = Field(min_length=1, max_length=1200)

class ChatRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    message: str = Field(min_length=1, max_length=1500)
    locale: Literal['en', 'fr', 'es'] = 'en'
    history: list[Turn] = Field(default_factory=list, max_length=8)

    @field_validator('message')
    @classmethod
    def non_blank(cls, value):
        if not value.strip():
            raise ValueError('A message is required')
        return value.strip()

    @model_validator(mode='after')
    def history_budget(self):
        if sum(len(t.content) for t in self.history) > 8000:
            raise ValueError('History too long')
        return self

class ModelAnswer(BaseModel):
    answer: str = Field(min_length=1, max_length=5000)
    source_ids: list[str] = Field(default_factory=list, max_length=5)

class Source(BaseModel):
    id: str
    title: str
    path: str

class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
