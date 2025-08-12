from __future__ import annotations

import os
from collections import defaultdict
from enum import Enum
from typing import Any, Optional, Union

import requests
from pydantic import BaseModel, Field, field_validator


class MessageType(str, Enum):
    """Types of messages in agent trajectories."""

    CHAT = "chat"
    ACTION = "action"
    OBSERVATION = "observation"


class ChatMessage(BaseModel):
    """Chat messages (user instructions, agent thoughts, etc)."""

    content: str
    role: str = Field(
        ..., description="Role of the message sender (user, assistant, etc)"
    )


class ActionMessage(BaseModel):
    """Agent's tool call/command."""

    name: str = Field(..., description="Name of the tool or action")
    args: dict[str, Any] = Field(
        default_factory=dict, description="Arguments for the action"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Action name cannot be empty")
        return v.strip()


class ObservationMessage(BaseModel):
    """Environment's response/output."""

    name: str = Field(
        ..., description="Name of the tool that produced this observation"
    )
    output: str = Field(..., description="The observation output")


class BaseMessage(BaseModel):
    """Base message model with common fields."""

    position: Optional[int] = Field(None, description="Position in the trajectory")
    value: Union[ChatMessage, ActionMessage, ObservationMessage]
    type: MessageType
    metadata: Optional[dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata for the message"
    )


class SolverSpec(BaseModel):
    """Information about the model and scaffolding configuration used."""

    model: str
    iterations: int
    allowed_tools: Optional[list]


class TrajectoryStats(BaseModel):
    """Pre-computed statistics for a trajectory."""

    total_messages: int = 0
    num_actions: int = 0
    num_chat_messages: int = 0
    num_observations: int = 0

    # Message type categorization (CHAT, ACTION, OBSERVATION)
    message_type_counts: dict[str, int] = Field(default_factory=dict)
    message_type_list: list[str] = Field(default_factory=list)

    # Semantic categorization (LLM-predicted categories)
    semantic_category_counts: dict[str, int] = Field(default_factory=dict)
    semantic_category_list: list[str] = Field(default_factory=list)

    # Score info
    score: Optional[float] = None
    success: bool = False  # True if score == 1.0


class Trajectory(BaseModel):
    """
    A single agent execution trace over a problem instance.
    """

    score: Optional[float] = None
    messages: list[BaseMessage]
    status: Optional[str] = None
    solver_spec: Optional[SolverSpec] = None

    id: Optional[str] = ""
    db_id: Optional[str] = ""
    run_id: Optional[str] = ""
    summary: Optional[str] = ""
    features: Optional[dict] = Field(default_factory=dict)
    stats: Optional[TrajectoryStats] = None
    issues: Optional[dict[str, Any]] = Field(default_factory=dict)

    # Additional fields for SWE-bench compatibility
    metadata: Optional[dict[str, Any]] = None  # Store additional trajectory metadata
    solution: Optional[str] = None  # Store the solution for this trajectory
    solution_explanation: Optional[str] = (
        None  # Concise LLM-generated explanation of the solution
    )

    # Flagging fields
    flagged: Optional[bool] = False
    flag_comment: Optional[str] = None

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the trajectory."""
        self.messages.append(message)


class Environment:
    """Manages multiple ModelRuns for comparison and collective analysis."""

    def __init__(
        self,
        name: str,
        backend_url: str,
        tools: list[str] | None = None,
        model_name: str | None = None,
        mode: str | None = None,
        iterations: int | None = None,
        test_budget: int | None = None,
    ):
        """Initialize an environment and register it with the API."""
        self.name = name
        self.trajectories = defaultdict(list)
        self.tools = tools or []
        self.backend_url = backend_url

        self.api_key = os.environ.get("FULCRUM_API_KEY")

        # Create environment in the API
        try:
            request_data = {
                "name": name,
                "tools": self.tools,
                "model_name": model_name,
                "mode": mode,
                "iterations": iterations,
                "test_budget": test_budget,
            }

            headers = {"X-API-Key": self.api_key}

            response = requests.post(
                f"{self.backend_url}/api/environments",
                json=request_data,
                headers=headers,
            )
            response.raise_for_status()
            result = response.json()

            if result.get("success"):
                print(f"Environment '{name}' registered successfully")
            else:
                print(
                    f"Warning: Environment registration returned: {result.get('message', 'Unknown response')}"
                )

        except requests.exceptions.RequestException as e:
            print(f"Error registering environment with API: {e}")
            # Continue even if API registration fails

    def save_trajectory(
        self,
        traj: Trajectory,
        force_refresh: bool = False,
    ):
        # Use id directly as key
        if traj.id is None:
            raise ValueError("Trajectory ID is required to save trajectory")

        problem_id = traj.id

        self.trajectories[problem_id].append(traj)

        request_data = {
            "trajectory": traj.model_dump(
                mode="json"
            ),  # Pydantic v2: properly serializes enums
            "env_id": self.name,
            "force_refresh": force_refresh,
        }

        headers = {"X-API-Key": self.api_key}

        # Send to API endpoint
        try:
            req_url = f"{self.backend_url}/api/trajectories/save"

            response = requests.post(req_url, json=request_data, headers=headers)

            response.raise_for_status()
            result = response.json()

            if not result.get("success"):
                print(
                    f"Warning: Failed to save trajectory to server: {result.get('message', 'Unknown error')}"
                )

        except requests.exceptions.RequestException as e:
            print(f"Error saving trajectory to server: {e}")

    async def save_trajectories_batch(
        self, trajectories: list[Trajectory], force_refresh: bool = False
    ) -> dict:
        """
        Save multiple trajectories in batch using the batch upload API.

        Args:
            trajectories: List of trajectories to save

        Returns:
            dictionary with upload results
        """
        # Add trajectories to local storage
        for traj in trajectories:
            problem_id = traj.id
            self.trajectories[problem_id].append(traj)

        # Prepare batch request
        request_data = {
            "trajectories": [traj.model_dump(mode="json") for traj in trajectories],
            "env_id": self.name,
            "force_refresh": force_refresh,
        }

        # Send to batch API endpoint
        try:
            req_url = f"{self.backend_url}/api/trajectory/save_batch"

            headers = {"X-API-Key": self.api_key}

            response = requests.post(req_url, json=request_data, headers=headers)

            response.raise_for_status()
            result = response.json()

            if not result.get("success"):
                print(
                    f"Warning: Batch upload had failures: {result.get('message', 'Unknown error')}"
                )
                if result.get("errors"):
                    for error in result["errors"]:
                        print(f"  - {error['trajectory_id']}: {error['error']}")

            return result

        except requests.exceptions.RequestException as e:
            print(f"Error in batch upload: {e}")
            raise