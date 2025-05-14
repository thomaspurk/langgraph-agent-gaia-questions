""" 
    TODO - This could be refactored as a class
"""
import os
from langchain.tools import Tool
from langchain_tavily import TavilySearch


_web_searcher = TavilySearch(
    max_results=2
)


def _web_search(query: str) -> dict:
    """TODO"""
    result = _web_searcher.invoke(query)
    return {"messages": result}

       
# Initialize the tool
web_search_tool = Tool(
    name="web_search_tool",
    func=_web_search,
    description="Use this to preform a web search for addition information needed to answer a question."
)