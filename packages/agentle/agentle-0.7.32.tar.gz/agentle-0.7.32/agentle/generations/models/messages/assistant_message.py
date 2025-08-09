"""
Module defining the AssistantMessage class representing messages from assistants.
"""

from __future__ import annotations

from collections.abc import MutableSequence, Sequence
from typing import Any, Literal, cast

from rsb.models.base_model import BaseModel
from rsb.models.field import Field

from agentle.generations.models.message_parts.file import FilePart
from agentle.generations.models.message_parts.text import TextPart
from agentle.generations.models.message_parts.tool_execution_suggestion import (
    ToolExecutionSuggestion,
)
from agentle.generations.tools.tool import Tool
from agentle.generations.tools.tool_execution_result import ToolExecutionResult


class AssistantMessage(BaseModel):
    """
    Represents a message from an assistant in the system.

    This class can contain a sequence of different message parts including
    text, files, and tool execution suggestions.
    """

    role: Literal["assistant"] = Field(
        default="assistant",
        description="Discriminator field to identify this as an assistant message. Always set to 'assistant'.",
    )

    parts: MutableSequence[
        TextPart | FilePart | ToolExecutionSuggestion | ToolExecutionResult | Tool[Any]
    ] = Field(
        description="The sequence of message parts that make up this assistant message.",
    )

    def insert_at_end(
        self,
        parts: TextPart
        | FilePart
        | Tool[Any]
        | ToolExecutionSuggestion
        | ToolExecutionResult
        | Sequence[
            TextPart
            | FilePart
            | Tool[Any]
            | ToolExecutionSuggestion
            | ToolExecutionResult
        ],
    ) -> None:
        if isinstance(parts, Sequence):
            self.parts.extend(parts)
            return
        self.parts.append(parts)

    @property
    def tool_calls(self) -> Sequence[ToolExecutionSuggestion]:
        tool_calls = cast(
            Sequence[ToolExecutionSuggestion],
            list(
                filter(
                    lambda part: isinstance(part, ToolExecutionSuggestion), self.parts
                )
            ),
        )

        return tool_calls

    def without_tool_calls(self) -> AssistantMessage:
        return AssistantMessage(
            parts=list(
                filter(
                    lambda part: not isinstance(
                        part, (ToolExecutionSuggestion, ToolExecutionResult)
                    ),
                    self.parts,
                )
            )
        )
