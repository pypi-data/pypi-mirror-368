import logging
from typing import Literal, Callable

from duowen_agent.agents.component.merge_contexts import DetectionMergeContexts
from duowen_agent.llm import OpenAIChat
from langgraph.types import Command

from .base import BaseNode
from ..entity import State


class BackgroundInvestigation(BaseNode):

    def __init__(self, llm: OpenAIChat, retrieval: Callable[[str], str], **kwargs):
        super().__init__()
        self.llm = llm
        self.retrieval = retrieval

    def run(
        self,
        state: State,
    ) -> Command[Literal["planner"]]:
        question = DetectionMergeContexts(llm_instance=self.llm).run(state.messages)

        background_investigation_results = self.retrieval(question)

        logging.info(
            f"Background investigation results: {background_investigation_results}"
        )

        return Command(
            update={
                "background_investigation_results": background_investigation_results
            },
            goto="planner",
        )

    async def arun(self, *args, **kwargs):
        raise NotImplementedError
