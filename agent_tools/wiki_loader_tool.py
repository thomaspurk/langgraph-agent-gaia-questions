from langchain_community.document_loaders import WikipediaLoader
from langchain.tools import Tool

#search_docs = 

def _load(query: str) -> dict:
    """Find Wikipedia document based on the query.

        Args:
            query: The search query.
        
        Returns:
            dict: Contains a string of formatted documents compatible with LangGraph state messages.
    """
    search_docs = WikipediaLoader(query=query, load_max_docs=1).load()

    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )
    return {"context": formatted_search_docs}


# Initialize the tool
wiki_loader_tool = Tool(
    name="Wikipedia Page Loader",
    func=_load,
    description="Use this tool to retreive content from a Wikipedia page to use for addition context needed to answer a question."
)