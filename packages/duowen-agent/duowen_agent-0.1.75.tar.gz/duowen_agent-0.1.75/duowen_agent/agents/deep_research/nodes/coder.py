import logging
from datetime import datetime
from typing import Literal

from duowen_agent.llm import OpenAIChat
from duowen_agent.tools.base import BaseTool
from duowen_agent.utils.string_template import StringTemplate
from langgraph.types import Command

from .base import BaseNode
from .exec_agent import _setup_and_execute_agent_step
from ..entity import State


def _prompt(locale="zh-CN"):
    return StringTemplate(
        """---
CURRENT_TIME: {{ CURRENT_TIME }}
---

You are `coder` agent that is managed by `supervisor` agent.
You are a professional software engineer proficient in Python scripting. Your task is to analyze requirements, implement efficient solutions using Python, and provide clear documentation of your methodology and results.

# Steps

1. **Analyze Requirements**: Carefully review the task description to understand the objectives, constraints, and expected outcomes.
2. **Plan the Solution**: Determine whether the task requires Python. Outline the steps needed to achieve the solution.
3. **Implement the Solution**:
   - Use Python for data analysis, algorithm implementation, or problem-solving.
   - Print outputs using `print(...)` in Python to display results or debug values.
4. **Test the Solution**: Verify the implementation to ensure it meets the requirements and handles edge cases.
5. **Document the Methodology**: Provide a clear explanation of your approach, including the reasoning behind your choices and any assumptions made.
6. **Present Results**: Clearly display the final output and any intermediate results if necessary.

# Notes

- Always ensure the solution is efficient and adheres to best practices.
- Handle edge cases, such as empty files or missing inputs, gracefully.
- Use comments in code to improve readability and maintainability.
- If you want to see the output of a value, you MUST print it out with `print(...)`.
- Always and only use Python to do the math.
- Always use `yfinance` for financial market data:
    - Get historical data with `yf.download()`
    - Access company info with `Ticker` objects
    - Use appropriate date ranges for data retrieval
- Required Python packages are pre-installed:
    - `pandas` for data manipulation
    - `numpy` for numerical operations
    - `yfinance` for financial market data
- Always output in the locale of **{{ locale }}**.

""",
        template_format="jinja2",
    ).format(
        CURRENT_TIME=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        locale=locale,
    )


class Coder(BaseNode):

    def __init__(self, llm: OpenAIChat, default_tools: list[BaseTool], **kwargs):
        super().__init__()
        self.llm = llm
        self.default_tools = default_tools

    def run(
        self,
        state: State,
    ) -> Command[Literal["research_team"]]:
        """Coder node that do code analysis."""
        logging.info("Coder node is coding.")
        return _setup_and_execute_agent_step(
            state=state,
            agent_type="coder",
            llm=self.llm,
            default_tools=self.default_tools,
            prefix_prompt=_prompt(state.locale),
        )

    async def arun(self, *args, **kwargs):
        raise NotImplementedError
