""" TODO """

import os
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState, START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

from agent_tools.web_search_tool import search_tool
from agent_tools.wiki_loader_tool import wiki_loader_tool


class gaia_agent:
    def __init__(self) -> StateGraph:
        """ TODO """

        # Create the agent graph builder object
        self.graph_builder = StateGraph(MessagesState)

        # Generate the chat interface, including the tools
        chat_llm = HuggingFaceEndpoint(
            repo_id=os.environ.get("CHAT_MODEL"),
            huggingfacehub_api_token=os.environ.get("HUGGINGFACEHUB_API_TOKEN"),
        )

        chat_model = ChatHuggingFace(
            llm=chat_llm, 
            verbose=True
        )
        tools = [
            search_tool,
            wiki_loader_tool,
            ]
        chat_model_with_tools = chat_model.bind_tools(tools)

        
        # Define nodes: these do the work
        # chat_node to process the question
        def chat_node(state: MessagesState) -> dict:
            """ Formates an LLM response to the current AgentState message."""
            return {
                "messages": [chat_model_with_tools.invoke(state["messages"])],
            }
        
        self.graph_builder.add_node(
            node="chat_node", 
            action=chat_node
        )

        # Tool node to select the tool requested from the last AI Message
        tool_node = ToolNode(tools=tools)

        self.graph_builder.add_node(
            node="tools", 
            action=tool_node
        )

        self.graph_builder.add_edge(
            start_key=START, # from node
            end_key="chat_node" # to node
        )
            
        # Define edges: these determine how the control flow moves
        self.graph_builder.add_conditional_edges(
            source="chat_node",
            # If the latest message (result) from chat_node is a tool call -> tools_condition routes to tools
            # If the latest message (result) from chat_node is a not a tool call -> tools_condition routes to END
            path=tools_condition,

        )


        # Return the flow to the chat_node to decide what to do next
        self.graph_builder.add_edge(
            start_key="tools", # from node
            end_key="chat_node" # to node
        )

        # Compile the Agent
        self.graph_builder = self.graph_builder.compile()
    
    def __call__(self, content: str) -> str:
        """ Send request to the alfred agent."""

        content_plus = f"""You are an AI Agent who uses tools to help provide accurate and concise answers. I will ask you a question. Your final answer should be a number OR as few words as possible OR a comma separated list of numbers and/or strings. If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise. If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise. If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string.

        You can look up the definition of technical terms using a web search to help you get
        information needed to answer questions. Take your time and a follow all instructions given in the quesiton.
        
        Question:{content}""" 

        input_dict = {"messages": [HumanMessage(content=content_plus)]}
        # response = self.graph_builder.invoke(input_dict)['messages'][-1].content
        response = None
        for chunk in self.graph_builder.stream(input_dict):
            for node, update in chunk.items():
               print( update_reporter(node,update))
               response = update["messages"][-1].content

        return response

def update_reporter(node: str, update: dict) -> str:

    return_string = f"\n{'_' * 25} Update from node: {node}  {'_' * 25}"
    # Assume one message per update
    message = update["messages"][-1]

    return_string += f"\n\n{'=' * 25} {type(message).__name__} {'=' * 25}"

    if(
        hasattr(message, "name") and
        message.name != None
    ):
        return_string += f"\n\nName: {message.name}"

    if hasattr(message, "content"):
        return_string += f"\n\n{message.content[:500]}"
    
    if hasattr(message, "tool_calls"):
        for tool_call in message.tool_calls:
            return_string += f"\n{tool_call}"
    
    return return_string