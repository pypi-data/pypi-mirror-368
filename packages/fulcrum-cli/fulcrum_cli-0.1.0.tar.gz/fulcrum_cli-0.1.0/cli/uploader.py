from __future__ import annotations

import asyncio
import hashlib
import re
from pathlib import Path
from typing import Optional

import requests
from inspect_ai.log import EvalSample, ToolEvent, read_eval_log, read_eval_log_samples
from inspect_ai.model import (
    ChatMessageAssistant,
    ChatMessageSystem,
    ChatMessageTool,
    ChatMessageUser,
)

from lib.models import (
    ActionMessage,
    BaseMessage,
    ChatMessage,
    Environment,
    MessageType,
    ObservationMessage,
    SolverSpec,
    Trajectory,
)


def convert_messages(sample: EvalSample) -> list[BaseMessage]:
    """
    Convert Inspect AI evaluation sample messages and tool events to BaseMessage list.

    This function processes an Inspect AI sample in two phases:
    1. Chat history from sample.messages (ChatMessageSystem, ChatMessageUser,
       ChatMessageAssistant, ChatMessageTool)
    2. Tool events from sample.events (ToolEvent)

    Conversion strategy:
      * ChatMessageSystem/User/Assistant → MessageType.CHAT
      * ChatMessageAssistant with tool_calls → MessageType.CHAT + MessageType.ACTION (for each tool call)
      * ChatMessageTool → MessageType.OBSERVATION
      * ToolEvent → MessageType.ACTION + MessageType.OBSERVATION (paired)

    Args:
        sample: Inspect AI evaluation sample with messages and events

    Returns:
        List of BaseMessage objects with sequential positioning
    """
    msg_list: list[BaseMessage] = []
    pos = 0

    for m in sample.messages:
        if isinstance(m, (ChatMessageSystem, ChatMessageUser)):
            # Handle both string content and multimodal content (list of Content objects)
            content_str = ""
            if isinstance(m.content, str):
                content_str = m.content
            elif isinstance(m.content, list):
                # For multimodal content, concatenate all text parts
                text_parts = []
                for content_item in m.content:
                    if hasattr(content_item, 'text') and content_item.text:
                        text_parts.append(content_item.text)
                content_str = "\n".join(text_parts)
            else:
                # Fallback for other types
                content_str = str(m.content)

            assert isinstance(m.role, str), (
                f"Expected str for role, got {type(m.role)}: {m.role}"
            )

            msg_list.append(
                BaseMessage(
                    position=pos,
                    type=MessageType.CHAT,
                    value=ChatMessage(content=content_str, role=m.role),
                )
            )
            pos += 1

        elif isinstance(m, ChatMessageAssistant):
            # Handle assistant content
            content_str = ""
            if isinstance(m.content, str):
                content_str = m.content
            elif isinstance(m.content, list):
                # For multimodal content, concatenate all text parts
                text_parts = []
                for content_item in m.content:
                    if hasattr(content_item, 'text') and content_item.text:
                        text_parts.append(content_item.text)
                content_str = "\n".join(text_parts)
            else:
                # Fallback for other types
                content_str = str(m.content)

            # Always add the assistant message if it has content
            if content_str:
                msg_list.append(
                    BaseMessage(
                        position=pos,
                        type=MessageType.CHAT,
                        value=ChatMessage(content=content_str, role=m.role),
                    )
                )
                pos += 1

            # Check for tool calls
            if hasattr(m, 'tool_calls') and m.tool_calls:
                for tool_call in m.tool_calls:
                    # Add ACTION message for each tool call
                    msg_list.append(
                        BaseMessage(
                            position=pos,
                            type=MessageType.ACTION,
                            value=ActionMessage(
                                name=tool_call.function,
                                args=tool_call.arguments
                            ),
                        )
                    )
                    pos += 1

        elif isinstance(m, ChatMessageTool):
            # Assert we require a function name and don't support cases where it's None
            assert isinstance(m.function, str), (
                f"Expected str for function, got {type(m.function)}: {m.function}"
            )

            # Handle both string content and multimodal content
            content_str = ""
            if isinstance(m.content, str):
                content_str = m.content
            elif isinstance(m.content, list):
                # For multimodal content, concatenate all text parts
                text_parts = []
                for content_item in m.content:
                    if hasattr(content_item, 'text') and content_item.text:
                        text_parts.append(content_item.text)
                content_str = "\n".join(text_parts)
            else:
                # Fallback for other types
                content_str = str(m.content)

            # Treat tool‐echoed content as an observation
            msg_list.append(
                BaseMessage(
                    position=pos,
                    type=MessageType.OBSERVATION,
                    value=ObservationMessage(name=m.function, output=content_str),
                )
            )
            pos += 1

    # Process tool events from sample.events (these might be duplicates of tool_calls)
    for ev in sample.events:
        if isinstance(ev, ToolEvent):
            # Assert we only support simple string results, not rich ToolResult objects
            assert isinstance(ev.function, str), (
                f"Expected str for function, got {type(ev.function)}: {ev.function}"
            )

            # Handle both string results and multimodal results
            result_str = ""
            if isinstance(ev.result, str):
                result_str = ev.result
            elif isinstance(ev.result, list):
                # For multimodal content, concatenate all text parts
                text_parts = []
                for content_item in ev.result:
                    if hasattr(content_item, 'text') and content_item.text:
                        text_parts.append(content_item.text)
                result_str = "\n".join(text_parts)
            else:
                # Fallback for other types
                result_str = str(ev.result)

            msg_list.append(
                BaseMessage(
                    position=pos,
                    type=MessageType.ACTION,
                    value=ActionMessage(name=ev.function, args=ev.arguments),
                )
            )
            pos += 1
            msg_list.append(
                BaseMessage(
                    position=pos,
                    type=MessageType.OBSERVATION,
                    value=ObservationMessage(name=ev.function, output=result_str),
                )
            )
            pos += 1

    return msg_list


def extract_gaia_question_id(messages: list[BaseMessage]) -> str:
    """
    Extract the question text from GAIA messages and generate a consistent ID.

    GAIA format typically has the question in the second message after "here is the question".
    We'll use a hash of the normalized question text to create a consistent ID.

    Args:
        messages: List of BaseMessage objects

    Returns:
        A consistent ID based on the question text, or empty string if not found
    """
    # Look for the question text in the messages
    for msg in messages:
        if msg.type == MessageType.CHAT and isinstance(msg.value, ChatMessage):
            content = msg.value.content.lower()

            # Look for "here is the question" pattern
            match = re.search(r"here is the question[:\s]*(.+)", content, re.IGNORECASE | re.DOTALL)
            if match:
                question_text = match.group(1).strip()

                # Normalize the question text to ensure consistency
                # Remove extra whitespace and punctuation variations
                normalized = re.sub(r'\s+', ' ', question_text)
                normalized = normalized.strip()

                # Generate a hash of the normalized question
                if normalized:
                    # Use first 8 chars of hash for readability
                    question_hash = hashlib.md5(normalized.encode()).hexdigest()[:8]
                    # Also include first few words for human readability
                    words = normalized.split()[:5]
                    readable_part = "_".join(words)
                    # Clean up the readable part
                    readable_part = re.sub(r'[^a-zA-Z0-9_]', '', readable_part)
                    return f"gaia_{readable_part}_{question_hash}"

    return ""


def sample_to_trajectory(
    sample: EvalSample,
    model_name: str = "",
    tools: list[str] | None = None,
    use_gaia_question_id: bool = False
) -> Trajectory:
    """
    Convert an Inspect AI evaluation sample to a Trajectory object.

    Extracts key information from the sample and converts messages using convert_messages().

    Score conversion logic:
      * 'C' → 1 (correct/success)
      * 'I' → 0 (incorrect/failure)
      * Numeric values → preserved as float
      * Invalid/None → 0 (no score or invalid format)

    Args:
        sample: Inspect AI evaluation sample containing messages, events, scores, etc.
        model_name: Name of the model used for evaluation (default: "")
        tools: List of allowed tools for the solver (default: None → [])
        use_gaia_question_id: If True, extract ID from GAIA question text (default: False)

    Returns:
        Trajectory object with:
          * id: question-based ID for GAIA or stringified sample.id
          * score: converted score (0 or 1)
          * status: "error" if sample.error else "finished"
          * solver_spec: SolverSpec with model, iterations=1, allowed_tools
          * messages: converted BaseMessage list from convert_messages()
          * metadata: sample.metadata
    """
    score = next(iter(sample.scores.values())).value if sample.scores else None

    # Handle different score formats safely
    if score == "C":
        score = 1
    elif score == "I":
        score = 0
    elif score is not None:
        # Try to preserve float scores
        try:
            score = float(score)
        except (ValueError, TypeError):
            # If conversion fails, default to 0
            score = 0
    else:
        # No score available
        score = 0

    # Convert messages first
    messages = convert_messages(sample)

    # Determine the trajectory ID
    traj_id = str(sample.id)
    if use_gaia_question_id:
        question_id = extract_gaia_question_id(messages)
        if question_id:
            traj_id = question_id

    # Extract solution patch from metadata if available
    solution = None
    if sample.metadata and "patch" in sample.metadata:
        solution = sample.metadata["patch"]

    return Trajectory(
        id=traj_id,
        score=score,
        status="error" if sample.error else "finished",
        solver_spec=SolverSpec(
            model=model_name, iterations=1, allowed_tools=tools or []
        ),
        messages=messages,
        metadata=sample.metadata,
        solution=solution,
    )


def sanitize_env_name(name: str) -> str:
    """Sanitize environment name by replacing problematic characters."""
    # Replace slashes with dashes
    sanitized = name.replace('/', '-')
    # Replace other problematic characters if needed
    sanitized = sanitized.replace('\\', '-')
    sanitized = sanitized.replace(':', '-')
    # Remove any leading/trailing whitespace or dashes
    sanitized = sanitized.strip('-').strip()
    return sanitized


async def upload_batch(env: Environment, trajectories: list[Trajectory], batch_number: int):
    """Upload a batch of trajectories and return results."""
    if not trajectories:
        return

    print(f"[Batch {batch_number}] Uploading {len(trajectories)} trajectories...")
    result = await env.save_trajectories_batch(trajectories)

    if result:
        success = result.get("successful_uploads", 0)
        failed = result.get("failed_uploads", 0)
        print(
            f"[Batch {batch_number}] Complete: {success} successful, {failed} failed"
        )

    return result


def upload_inspect_log(
    log_file: str,
    api: str = "http://localhost:8000",
    batch_size: int = 400,
    env_name: Optional[str] = None,
) -> None:
    """
    Upload an Inspect AI log file to Fulcrum backend.
    
    Args:
        log_file: Path to Inspect .eval or .json log file
        api: Backend API root URL
        batch_size: Number of trajectories to upload in each batch
        env_name: Override environment name (defaults to sanitized task name)
    """
    log_path = Path(log_file).expanduser().resolve()
    log = read_eval_log(log_path, resolve_attachments=False)

    # --- Build Environment from header ---------------------------------------
    # Use provided env name or fall back to sanitized task name
    if env_name:
        environment_name = env_name
        print(f"Using provided environment name: {environment_name}")
    else:
        environment_name = sanitize_env_name(log.eval.task)
        print(f"Original task name: {log.eval.task}")
        print(f"Sanitized environment name: {environment_name}")

    env = Environment(
        name=environment_name,
        backend_url=api,
        tools=log.plan.steps[0].params.get("tools", [])
        if log.plan and log.plan.steps
        else [],
        model_name=log.eval.model,
        iterations=log.eval.config.epochs or 1,
        mode="eval",
        test_budget=None,
    )

    # --- Process samples in batches for efficiency ---------------------------
    batch = []
    total_processed = 0
    total_successful = 0
    total_failed = 0
    batch_num = 0

    print(f"Starting batch upload with batch size {batch_size}...")
    print(f"Total samples to process: {log.results.total_samples}")

    # Process all samples
    for sample in read_eval_log_samples(log_path, resolve_attachments=False):
        traj = sample_to_trajectory(sample, model_name=log.eval.model, tools=env.tools)
        traj.metadata["inspect_sample_id"] = sample.id
        traj.metadata["inspect_path"] = str(log_path)

        batch.append(traj)

        # Upload when batch is full
        if len(batch) >= batch_size:
            batch_num += 1
            result = asyncio.run(upload_batch(env, batch, batch_num))
            if result:
                total_successful += result.get("successful_uploads", 0)
                total_failed += result.get("failed_uploads", 0)
            total_processed += len(batch)
            print(
                f"Progress: {total_processed}/{log.results.total_samples} trajectories processed"
            )
            batch = []

    # Upload any remaining trajectories
    if batch:
        batch_num += 1
        result = asyncio.run(upload_batch(env, batch, batch_num))
        if result:
            total_successful += result.get("successful_uploads", 0)
            total_failed += result.get("failed_uploads", 0)
        total_processed += len(batch)

    print(f"\n✔  Import complete for '{environment_name}':")
    print(f"   Total trajectories: {log.results.total_samples}")
    print(f"   Successfully uploaded: {total_successful}")
    if total_failed > 0:
        print(f"   Failed uploads: {total_failed}")

    # Aggregate issues for all runs in the environment
    print(f"\nAggregating issues for all runs in environment '{environment_name}'...")
    try:
        headers = {"X-API-Key": env.api_key}
        response = requests.post(
            f"{env.backend_url}/api/environments/{environment_name}/aggregate-issues",
            params={"force_refresh": False},
            headers=headers
        )
        response.raise_for_status()
        result = response.json()

        if result.get("success"):
            print(f"✔  Issue aggregation complete:")
            print(f"   Runs processed: {result.get('runs_processed', 0)}")
            print(f"   Runs with issues: {result.get('runs_with_issues', 0)}")
            print(f"   {result.get('message', '')}")
        else:
            print(f"⚠  Issue aggregation returned unexpected response: {result}")

    except requests.exceptions.RequestException as e:
        print(f"⚠  Warning: Failed to aggregate issues: {e}")
        print("   You can manually aggregate issues later using the API")