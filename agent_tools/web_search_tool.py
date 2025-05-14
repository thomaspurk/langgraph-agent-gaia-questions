""" 

    A new vector store will be used for each question
    TODO - This could be refactored as a class
"""
import os
from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchResults


_web_searcher = DuckDuckGoSearchResults(
    max_result=5
)


def _search(query):
    """TODO"""
    result = _web_searcher(query)
    return result

       
# Initialize the tool
search_tool = Tool(
    name="search",
    func=_search,
    description="Use this to preform a web search for addition information needed to answer a question."
)