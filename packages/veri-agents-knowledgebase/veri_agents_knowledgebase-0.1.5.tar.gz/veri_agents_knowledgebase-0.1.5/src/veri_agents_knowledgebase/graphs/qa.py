import json
import logging
import asyncio
from datetime import datetime
from typing import Any, NotRequired, Sequence, Callable, TypedDict, Union, Unpack, cast

from langchain_core.language_models import (
    LanguageModelLike,
)
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import ToolNode, create_react_agent
from langgraph.prebuilt.chat_agent_executor import StructuredResponseSchema
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage
from langfuse.callback import CallbackHandler as LangfuseCallbackHandler
from langchain_core.runnables import RunnableConfig

from veri_agents_knowledgebase import Knowledgebase

log = logging.getLogger(__name__)


class QaAgentKwargs(TypedDict):
    llm: LanguageModelLike
    knowledgebases: Sequence[Knowledgebase]
    system_prompt: str
    tools: NotRequired[Sequence[BaseTool | Callable] | None]
    response_format: NotRequired[
        Union[StructuredResponseSchema, tuple[str, StructuredResponseSchema]]
    ]


def create_qa_agent(
    **kwargs: Unpack[QaAgentKwargs],
) -> CompiledGraph:
    tools: list[BaseTool | Callable] = list(*(kwargs.pop("tools", None) or []))
    knowledgebases: Sequence[Knowledgebase] = kwargs.pop(
        "knowledgebases"
    )  # pyright: ignore[reportAssignmentType]
    system_prompt: str = kwargs.pop(
        "system_prompt"
    )  # pyright: ignore[reportAssignmentType]
    llm: LanguageModelLike = kwargs.pop("llm")  # pyright: ignore[reportAssignmentType]

    for _, knowledgebase in enumerate(knowledgebases):
        tools.extend(
            knowledgebase.get_tools(
                retrieve_tools=True,
                list_tools=True,
                write_tools=False,
            )
        )
    tool_node = ToolNode(tools)

    system_prompt += f"""Today's date is: {datetime.now().strftime("%Y-%m-%d")}."""

    return create_react_agent(
        model=llm, tools=tool_node, prompt=system_prompt, **cast(dict, kwargs)
    )


class QaKwargs(QaAgentKwargs):
    response_format: (  # pyright: ignore[reportIncompatibleVariableOverride]
        str | StructuredResponseSchema | None
    )


async def qa(
    prompt: str,
    retries: int = 3,
    config: RunnableConfig | None = None,
    **kwargs: Unpack[QaKwargs],
) -> dict[str, Any] | Any:
    response_format: str | StructuredResponseSchema | None = cast(
        Any, kwargs.pop("response_format")
    )

    if isinstance(response_format, str):
        response_format = json.loads(response_format)

    if isinstance(response_format, dict):
        response_format.setdefault("title", "QA_AdhocResult")
        response_format.setdefault("description", "")

    qa_snapshot_agent = create_qa_agent(
        response_format=cast(
            Union[StructuredResponseSchema, tuple[str, StructuredResponseSchema]],
            response_format,
        ),
        **cast(dict, kwargs),
    )

    for retry in range(retries):
        try:
            res = await qa_snapshot_agent.ainvoke(
                input={"messages": [HumanMessage(content=prompt)]},
                config=config,
            )

            if response_format is None:
                return cast(
                    dict,
                    res,
                )[
                    "messages"
                ][-1].content
            else:
                return cast(
                    dict,
                    res,
                )["structured_response"]
        except Exception as e:
            log.warning("QA (attempt %d): error: %s. Retrying...", retry, e)
            await asyncio.sleep(3)

    raise RuntimeError("QA invocation failed after %d retries" % retries)
