from typing import List

from llmflow.enumeration.role import Role
from llmflow.schema.message import Message, Trajectory
import json
import re
from loguru import logger

def merge_messages_content(messages: List[Message | dict]) -> str:
    content_collector = []
    for i, message in enumerate(messages):
        if isinstance(message, dict):
            message = Message(**message)

        if message.role is Role.ASSISTANT:
            line = f"### step.{i} role={message.role.value} content=\n{message.reasoning_content}\n\n{message.content}\n"
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    line += f" - tool call={tool_call.name}\n   params={tool_call.arguments}\n"
            content_collector.append(line)

        elif message.role is Role.USER:
            line = f"### step.{i} role={message.role.value} content=\n{message.content}\n"
            content_collector.append(line)

        elif message.role is Role.TOOL:
            line = f"### step.{i} role={message.role.value} tool call result=\n{message.content}\n"
            content_collector.append(line)

    return "\n".join(content_collector)


def parse_json_experience_response(response: str) -> List[dict]:
    """Parse JSON formatted experience response"""
    try:
        # Extract JSON blocks
        json_pattern = r'```json\s*([\s\S]*?)\s*```'
        json_blocks = re.findall(json_pattern, response)

        if json_blocks:
            parsed = json.loads(json_blocks[0])

            # Handle array format
            if isinstance(parsed, list):
                experiences = []
                for exp_data in parsed:
                    if isinstance(exp_data, dict) and (
                            ("when_to_use" in exp_data and "experience" in exp_data) or
                            ("condition" in exp_data and "experience" in exp_data)
                    ):
                        experiences.append(exp_data)

                return experiences


            # Handle single object
            elif isinstance(parsed, dict) and (
                    ("when_to_use" in parsed and "experience" in parsed) or
                    ("condition" in parsed and "experience" in parsed)
            ):
                return [parsed]

        # Fallback: try to parse entire response
        parsed = json.loads(response)
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict):
            return [parsed]

    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON experience response: {e}")

    return []

def get_trajectory_context(trajectory: Trajectory, step_sequence: List[Message]) -> str:
    """Get context of step sequence within trajectory"""
    try:
        # Find position of step sequence in trajectory
        start_idx = 0
        for i, step in enumerate(trajectory.messages):
            if step == step_sequence[0]:
                start_idx = i
                break

        # Extract before and after context
        context_before = trajectory.messages[max(0, start_idx - 2):start_idx]
        context_after = trajectory.messages[start_idx + len(step_sequence):start_idx + len(step_sequence) + 2]

        context = f"Query: {trajectory.metadata.get('query', 'N/A')}\n"

        if context_before:
            context += "Previous steps:\n" + "\n".join(
                [f"- {step.content[:100]}..." for step in context_before]) + "\n"

        if context_after:
            context += "Following steps:\n" + "\n".join([f"- {step.content[:100]}..." for step in context_after])

        return context

    except Exception as e:
        logger.error(f"Error getting trajectory context: {e}")
        return f"Query: {trajectory.metadata.get('query', 'N/A')}"