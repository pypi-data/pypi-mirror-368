import logging
from typing import Literal

from duowen_agent.llm import OpenAIChat
from langgraph.types import Command

from .base import BaseNode
from ..entity import State, StepType


class ResearchTeam(BaseNode):

    def __init__(self, llm: OpenAIChat, **kwargs):
        super().__init__()
        self.llm = llm

    def run(
        self,
        state: State,
    ) -> Command[Literal["planner", "researcher", "coder"]]:
        logging.info("Research team is collaborating on tasks.")
        current_plan = state.current_plan
        if not current_plan or not current_plan.steps:
            return Command(goto="planner")
        if all(step.execution_res for step in current_plan.steps):
            return Command(goto="planner")
        for step in current_plan.steps:
            if not step.execution_res:
                break
        if step.step_type and step.step_type == StepType.RESEARCH:
            return Command(goto="researcher")
        if step.step_type and step.step_type == StepType.PROCESSING:
            return Command(goto="coder")
        return Command(goto="planner")

    async def arun(self, *args, **kwargs):
        raise NotImplementedError
