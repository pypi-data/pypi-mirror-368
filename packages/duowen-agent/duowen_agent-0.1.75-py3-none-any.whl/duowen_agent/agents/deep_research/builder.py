from duowen_agent.llm import OpenAIChat
from duowen_agent.tools.bocha_search import Bocha
from duowen_agent.tools.crawler import Crawler
from duowen_agent.tools.python_repl import PythonREPLTool
from langgraph.graph import StateGraph, START, END

from .entity import State
from .nodes import (
    BackgroundInvestigation,
    Coordinator,
    Planner,
    ResearchTeam,
    Researcher,
    Reporter,
    HumanFeedback,
    Coder,
)

web_search_tool = Bocha(max_results=5)
web_search_tool.name = "web_search_tool"

crawl_tool = Crawler()
crawl_tool.name = "crawl_tool"

python_repl_tool = PythonREPLTool()


def web_search(question) -> str:
    _bocha = Bocha(max_results=5)
    return _bocha.search(question).content_with_weight


def _build_base_graph(llm: OpenAIChat):
    builder = StateGraph(State)
    builder.add_edge(START, "coordinator")
    builder.add_node("coordinator", Coordinator(llm=llm).run)
    builder.add_node(
        "background_investigator",
        BackgroundInvestigation(llm=llm, retrieval=web_search).run,
    )
    builder.add_node("planner", Planner(llm=llm).run)
    builder.add_node("reporter", Reporter(llm=llm).run)
    builder.add_node("research_team", ResearchTeam(llm=llm).run)
    builder.add_node(
        "researcher",
        Researcher(llm=llm, default_tools=[web_search_tool]).run,  # crawl_tool
    )
    builder.add_node("coder", Coder(llm=llm, default_tools=[python_repl_tool]).run)
    builder.add_node("human_feedback", HumanFeedback().run)
    builder.add_edge("reporter", END)
    return builder


def build_graph(llm: OpenAIChat):
    """Build and return the agent workflow graph without memory."""
    # build state graph
    builder = _build_base_graph(llm)
    return builder.compile()
