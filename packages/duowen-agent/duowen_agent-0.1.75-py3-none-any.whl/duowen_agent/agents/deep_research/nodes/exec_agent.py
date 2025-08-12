import logging
from typing import Literal

from duowen_agent.agents.react import ReactAgent, ReactResult
from duowen_agent.llm import MessagesSet, OpenAIChat
from duowen_agent.tools.base import BaseTool
from langgraph.types import Command

from ..entity import State


def create_agent(
    llm: OpenAIChat,
    tools: list[BaseTool],
    prefix_prompt: str = None,
    max_iterations: int = 25,
) -> ReactAgent:

    return ReactAgent(
        llm=llm, tools=tools, max_iterations=max_iterations, prefix_prompt=prefix_prompt
    )


def _execute_agent_step(
    state: State, agent: ReactAgent, agent_name: str
) -> Command[Literal["research_team"]]:
    """Helper function to execute a step using the specified agent."""
    current_plan = state.current_plan
    observations = state.observations

    # Find the first unexecuted step
    current_step = None
    completed_steps = []
    for step in current_plan.steps:
        if not step.execution_res:
            current_step = step
            break
        else:
            completed_steps.append(step)

    if not current_step:
        logging.warning("No unexecuted step found")
        return Command(goto="research_team")

    logging.info(f"Executing step: {current_step.title}")

    # Format completed steps information
    completed_steps_info = ""
    if completed_steps:
        completed_steps_info = "# Existing Research Findings\n\n"
        for i, step in enumerate(completed_steps):
            completed_steps_info += f"## Existing Finding {i+1}: {step.title}\n\n"
            completed_steps_info += f"<finding>\n{step.execution_res}\n</finding>\n\n"

    # Prepare the input for the agent with completed steps info
    agent_input = MessagesSet().add_user(
        f"{completed_steps_info}# Current Task\n\n## Title\n\n{current_step.title}\n\n## Description\n\n{current_step.description}\n\n## Locale\n\n{state.locale}"
    )

    # Add citation reminder for researcher agent
    if agent_name == "researcher":
        agent_input.add_user(
            "IMPORTANT: DO NOT include inline citations in the text. Instead, track all sources and include a References section at the end using link reference format. Include an empty line between each citation for better readability. Use this format for each reference:\n- [Source Title](URL)\n\n- [Another Source](URL)",
        )

    response_content = ""
    for i in agent.run(instruction=agent_input, verbose=False):
        if isinstance(i, ReactResult):
            response_content = i.result
            break

    # Process the result
    # response_content = result["messages"][-1].content
    logging.debug(f"{agent_name.capitalize()} full response: {response_content}")

    # Update the step with the execution result
    current_step.execution_res = response_content
    logging.info(f"Step '{current_step.title}' execution completed by {agent_name}")

    return Command(
        update={
            "messages": MessagesSet().add_user(response_content),
            "observations": observations + [response_content],
        },
        goto="research_team",
    )


def _setup_and_execute_agent_step(
    state: State,
    agent_type: str,
    llm: OpenAIChat,
    default_tools: list[BaseTool],
    prefix_prompt: str = None,
) -> Command[Literal["research_team"]]:

    agent = create_agent(llm=llm, tools=default_tools, prefix_prompt=prefix_prompt)
    return _execute_agent_step(state, agent, agent_type)
