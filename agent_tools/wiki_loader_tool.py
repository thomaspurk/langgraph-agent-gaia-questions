from langchain_community.document_loaders.wikipedia import WikipediaLoader
from langchain.tools import Tool

def _wiki_load(query: str) -> dict:
    """Find Wikipedia document based on the query.

        Args:
            query: The search query.
        
        Returns:
            dict: Contains a string of formatted documents compatible with LangGraph state messages.
    """
    search_docs = WikipediaLoader(query=query, load_max_docs=1).load()

    return {"messages": search_docs}


# Initialize the tool
wiki_loader_tool = Tool(
    name="wikipedia_page_loader",
    func=_wiki_load,
    description="Use this tool to retreive content from a Wikipedia page to use for addition context needed to answer a question."
)