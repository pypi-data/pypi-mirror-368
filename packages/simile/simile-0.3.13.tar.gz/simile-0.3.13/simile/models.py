from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
import uuid


class Population(BaseModel):
    population_id: uuid.UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PopulationInfo(BaseModel):
    population_id: uuid.UUID
    name: str
    description: Optional[str] = None
    agent_count: int


class DataItem(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    data_type: str
    content: Any
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class Agent(BaseModel):
    agent_id: uuid.UUID
    name: str
    population_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    data_items: List[DataItem] = Field(default_factory=list)


class CreatePopulationPayload(BaseModel):
    name: str
    description: Optional[str] = None


class InitialDataItemPayload(BaseModel):
    data_type: str
    content: Any
    metadata: Optional[Dict[str, Any]] = None


class CreateAgentPayload(BaseModel):
    name: str
    population_id: Optional[uuid.UUID] = None
    agent_data: Optional[List[InitialDataItemPayload]] = None


class CreateDataItemPayload(BaseModel):
    data_type: str
    content: Any
    metadata: Optional[Dict[str, Any]] = None


class UpdateDataItemPayload(BaseModel):
    content: Any
    metadata: Optional[Dict[str, Any]] = None


class DeletionResponse(BaseModel):
    message: str


# --- Generation Operation Models ---
class OpenGenerationRequest(BaseModel):
    question: str
    data_types: Optional[List[str]] = None
    exclude_data_types: Optional[List[str]] = None
    images: Optional[Dict[str, str]] = (
        None  # Dict of {description: url} for multiple images
    )
    reasoning: bool = False


class OpenGenerationResponse(BaseModel):
    question: str
    answer: str
    reasoning: Optional[str] = ""


class ClosedGenerationRequest(BaseModel):
    question: str
    options: List[str]
    data_types: Optional[List[str]] = None
    exclude_data_types: Optional[List[str]] = None
    images: Optional[Dict[str, str]] = None
    reasoning: bool = False


class ClosedGenerationResponse(BaseModel):
    question: str
    options: List[str]
    response: str
    reasoning: Optional[str] = ""


class AddContextRequest(BaseModel):
    context: str


class AddContextResponse(BaseModel):
    message: str
    session_id: uuid.UUID


# --- Survey Session Models ---
class TurnType(str, Enum):
    """Enum for different types of conversation turns."""

    CONTEXT = "context"
    IMAGE = "image"
    OPEN_QUESTION = "open_question"
    CLOSED_QUESTION = "closed_question"


class BaseTurn(BaseModel):
    """Base model for all conversation turns."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    type: TurnType

    class Config:
        use_enum_values = True


class ContextTurn(BaseTurn):
    """A context turn that provides background information."""

    type: Literal[TurnType.CONTEXT] = TurnType.CONTEXT
    user_context: str


class ImageTurn(BaseTurn):
    """A standalone image turn (e.g., for context or reference)."""

    type: Literal[TurnType.IMAGE] = TurnType.IMAGE
    images: Dict[str, str]
    caption: Optional[str] = None


class OpenQuestionTurn(BaseTurn):
    """An open question-answer turn."""

    type: Literal[TurnType.OPEN_QUESTION] = TurnType.OPEN_QUESTION
    user_question: str
    user_images: Optional[Dict[str, str]] = None
    llm_response: Optional[str] = None


class ClosedQuestionTurn(BaseTurn):
    """A closed question-answer turn."""

    type: Literal[TurnType.CLOSED_QUESTION] = TurnType.CLOSED_QUESTION
    user_question: str
    user_options: List[str]
    user_images: Optional[Dict[str, str]] = None
    llm_response: Optional[str] = None

    @validator("user_options")
    def validate_options(cls, v):
        if not v:
            raise ValueError("Closed questions must have at least one option")
        if len(v) < 2:
            raise ValueError("Closed questions should have at least two options")
        return v

    @validator("llm_response")
    def validate_response(cls, v, values):
        if (
            v is not None
            and "user_options" in values
            and v not in values["user_options"]
        ):
            raise ValueError(f"Response '{v}' must be one of the provided options")
        return v


# Union type for all possible turn types
SurveySessionTurn = Union[ContextTurn, ImageTurn, OpenQuestionTurn, ClosedQuestionTurn]


class SurveySessionCreateResponse(BaseModel):
    id: uuid.UUID  # Session ID
    agent_id: uuid.UUID
    created_at: datetime
    status: str


class SurveySessionDetailResponse(BaseModel):
    """Detailed survey session response with typed conversation turns."""

    id: uuid.UUID
    agent_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    status: str
    conversation_history: List[SurveySessionTurn] = Field(default_factory=list)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SurveySessionListItemResponse(BaseModel):
    """Summary response for listing survey sessions."""

    id: uuid.UUID
    agent_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    status: str
    turn_count: int = Field(description="Number of turns in conversation history")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SurveySessionCloseResponse(BaseModel):
    id: uuid.UUID  # Session ID
    status: str
    updated_at: datetime
    message: Optional[str] = None
