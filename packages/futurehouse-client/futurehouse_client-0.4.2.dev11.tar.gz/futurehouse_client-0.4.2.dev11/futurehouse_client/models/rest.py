from datetime import datetime
from enum import StrEnum, auto
from uuid import UUID

from pydantic import BaseModel, ConfigDict, JsonValue


class FinalEnvironmentRequest(BaseModel):
    status: str


class StoreAgentStatePostRequest(BaseModel):
    agent_id: str
    step: str
    state: JsonValue
    trajectory_timestep: int


class StoreEnvironmentFrameRequest(BaseModel):
    agent_state_point_in_time: str
    current_agent_step: str
    state: JsonValue
    trajectory_timestep: int


class ExecutionStatus(StrEnum):
    QUEUED = auto()
    IN_PROGRESS = "in progress"
    FAIL = auto()
    SUCCESS = auto()
    CANCELLED = auto()

    def is_terminal_state(self) -> bool:
        return self in self.terminal_states()

    @classmethod
    def terminal_states(cls) -> set["ExecutionStatus"]:
        return {cls.SUCCESS, cls.FAIL, cls.CANCELLED}


class WorldModel(BaseModel):
    """
    Payload for creating a new world model snapshot.

    This model is sent to the API.
    """

    content: str
    prior: UUID | str | None = None
    name: str | None = None
    description: str | None = None
    trajectory_id: UUID | str | None = None
    model_metadata: JsonValue | None = None
    project_id: UUID | str | None = None


class WorldModelResponse(BaseModel):
    """
    Response model for a world model snapshot.

    This model is received from the API.
    """

    id: UUID | str
    prior: UUID | str | None
    name: str
    description: str | None
    content: str
    trajectory_id: UUID | str | None
    email: str | None
    model_metadata: JsonValue | None
    enabled: bool
    created_at: datetime


class UserAgentRequestStatus(StrEnum):
    """Enum for the status of a user agent request."""

    PENDING = auto()
    RESPONDED = auto()
    EXPIRED = auto()
    CANCELLED = auto()


class UserAgentRequest(BaseModel):
    """Sister model for UserAgentRequestsDB."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    trajectory_id: UUID
    response_trajectory_id: UUID | None = None
    request: JsonValue
    response: JsonValue | None = None
    request_world_model_edit_id: UUID | None = None
    response_world_model_edit_id: UUID | None = None
    expires_at: datetime | None = None
    user_response_task: JsonValue | None = None
    status: UserAgentRequestStatus
    created_at: datetime | None = None
    modified_at: datetime | None = None


class UserAgentRequestPostPayload(BaseModel):
    """Payload to create a new user agent request."""

    trajectory_id: UUID
    request: JsonValue
    request_world_model_edit_id: UUID | None = None
    status: UserAgentRequestStatus = UserAgentRequestStatus.PENDING
    expires_in_seconds: int | None = None
    user_response_task: JsonValue | None = None
    notify_user: JsonValue = {"email": True, "sms": False}


class UserAgentResponsePayload(BaseModel):
    """Payload for a user to submit a response to a request."""

    response: JsonValue
    response_world_model_edit_id: UUID | None = None


class DiscoveryResponse(BaseModel):
    """Response model for a discovery request. This model is received from the API."""

    discovery_id: UUID | str
    project_id: UUID | str
    world_model_id: UUID | str
    dataset_id: UUID | str
    description: str
    associated_trajectories: list[UUID | str]
    validation_level: int
    created_at: datetime
