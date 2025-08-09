from json import JSONDecodeError, dumps
from typing import Any, Union
from uuid import UUID

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, LLMResult
from langchain_core.prompt_values import ChatPromptValue
from pydantic import BaseModel
from pydantic.v1 import BaseModel as BaseModelV1

Stringable = (str, int, float)


def convert_to_jsonable(obj: Any) -> Union[str, dict, list]:
    if isinstance(obj, (AgentFinish, AgentAction, ChatPromptValue)):
        return convert_to_jsonable(obj.messages)
    elif isinstance(obj, (ChatGeneration)):
        return convert_to_jsonable(obj.message)
    elif isinstance(obj, Document):
        return convert_to_jsonable(obj.model_dump(include={"page_content", "metadata"}))
    elif isinstance(obj, LLMResult):
        return convert_to_jsonable(obj.generations[0])
    elif isinstance(obj, (AIMessageChunk, AIMessage)) and obj.tool_calls:
        # Map the `type` to `role`.
        dumped = obj.model_dump(include={"content", "type", "tool_calls"})
        dumped["role"] = dumped.pop("type")
        return convert_to_jsonable(dumped)
    elif isinstance(obj, ToolMessage):
        # Map the `type` to `role`.
        dumped = obj.model_dump(include={"content", "type", "status", "tool_call_id"})
        dumped["role"] = dumped.pop("type")
        return convert_to_jsonable(dumped)
    elif isinstance(obj, BaseMessage):
        # Map the `type` to `role`.
        dumped = obj.model_dump(include={"content", "type"})
        dumped["role"] = dumped.pop("type")
        return convert_to_jsonable(dumped)
    elif isinstance(obj, BaseModel):
        return convert_to_jsonable(
            obj.model_dump(mode="json", exclude_none=True, exclude_unset=True, exclude_defaults=True)
        )
    elif isinstance(obj, BaseModelV1):
        return convert_to_jsonable(obj.dict(exclude_unset=True, exclude_none=True, exclude_defaults=True))
    elif isinstance(obj, list):
        return [convert_to_jsonable(o) for o in obj]
    elif isinstance(obj, dict):
        return {key: convert_to_jsonable(value) for key, value in obj.items() if value}
    return obj


def serialize_to_str(obj: Any) -> str:
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, (UUID, float)):
        return str(obj)
    else:
        try:
            return dumps(convert_to_jsonable(obj))
        except (TypeError, JSONDecodeError):
            return str(type(obj))
