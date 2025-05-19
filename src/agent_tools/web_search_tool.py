# Description: A LangGraph Agent Tool for getting results from a Web Search.
# Author: Thomas Purk
# Date: 2025-05-15
# Reference: https://python.langchain.com/docs/integrations/tools/tavily_search/

from langchain.tools import Tool
from langchain_tavily import TavilySearch


_web_searcher = TavilySearch(
    max_results=2
)


def _web_search(query: str) -> dict:
    """ Searches the web for the input string

        Args:
            query (str): The content of the web search query.
        
        Returns:
            dict: The parameters defining the search query and results.
    """
    result = _web_searcher.invoke(query)
    return {"messages": result}

       
# Initialize the tool
web_search_tool = Tool(
    name="web_search_tool",
    func=_web_search,
    description="Use this to preform a web search for addition information needed to answer a question."
)