import logging
from typing import Literal

from duowen_agent.error import ObserverException
from duowen_agent.llm import MessagesSet, UserMessage
from duowen_agent.utils.core_utils import json_observation
from langgraph.types import Command, interrupt

from .base import BaseNode
from ..entity import State, Plan


class HumanFeedback(BaseNode):

    def __init__(self, **kwargs):
        super().__init__()

    def run(
        self,
        state: State,
    ) -> Command[Literal["planner", "research_team", "reporter", "__end__"]]:
        current_plan = state.current_plan
        # check if the plan is auto accepted
        auto_accepted_plan = state.auto_accepted_plan
        if not auto_accepted_plan:
            feedback = interrupt("Please Review the Plan.")

            # if the feedback is not accepted, return the planner node
            if feedback and str(feedback).upper().startswith("[EDIT_PLAN]"):
                return Command(
                    update={
                        "messages": MessagesSet([UserMessage(content=feedback)]),
                    },
                    goto="planner",
                )
            elif feedback and str(feedback).upper().startswith("[ACCEPTED]"):
                logging.info("Plan is accepted by user.")
            else:
                raise TypeError(f"Interrupt value of {feedback} is not supported.")

        # if the plan is accepted, run the following node
        plan_iterations = state.plan_iterations if state.plan_iterations else 0
        goto = "research_team"
        try:
            new_plan = json_observation(current_plan, Plan)
            plan_iterations += 1
            if new_plan.has_enough_context:
                goto = "reporter"
        except ObserverException as e:
            logging.warning(f"Planner response error:{str(e)}")
            if plan_iterations > 0:
                return Command(goto="reporter")
            else:
                return Command(goto="__end__")

        return Command(
            update={
                "current_plan": new_plan,
                "plan_iterations": plan_iterations,
                "locale": new_plan.locale,
            },
            goto=goto,
        )

    async def arun(self, *args, **kwargs):
        raise NotImplementedError
