""" TODO """

import os
import time

from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState, START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

from agent_tools.web_search_tool import web_search_tool
from agent_tools.wiki_loader_tool import wiki_loader_tool
from agent_tools.python_runner_tool import python_runner_tool
from agent_tools.image_data_from_url_tool import image_data_from_url
from agent_tools.dataframe_from_url_tool import dataframe_from_url
from agent_tools.sum_excel_column_tool import sum_excel_column
from agent_tools.audio_transcript_from_url_tool import audio_transcription_from_url
from agent_tools.youtube_transcript_from_url_tool import youtube_transcription_from_url

# Some LLM API rate limits can be reached if answering all questions at once.
# Pause a number of seconds after each tool call invoked by the conditional edge
rate_limit_pause = 10 # 10 = 10,000 milliseconds


class gaia_agent:
    def __init__(self) -> StateGraph:
        """ TODO """

        # Create the agent graph builder object
        self.graph_builder = StateGraph(MessagesState)

        # Generate the chat interface, including the tools
        chat_model = init_chat_model(os.environ.get("CHAT_MODEL"))

        tools = [
            web_search_tool,
            wiki_loader_tool,
            python_runner_tool,
            image_data_from_url,
            dataframe_from_url,
            sum_excel_column,
            audio_transcription_from_url,
            youtube_transcription_from_url
        ]
        chat_model_with_tools = chat_model.bind_tools(tools)

        
        # Define nodes: these do the work
        # chat_node to process the question
        def chat_node(state: MessagesState) -> dict:
            """ Formates an LLM response to the current MessageState message."""

            # Hacky workaround to rate limit issues. Add a little pause each time
            # the llm is called to hopefully avoid the limit.
            time.sleep(rate_limit_pause)
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
        self.graph = self.graph_builder.compile()
    
    def __call__(self, content: str) -> str:
        """ Send request to the alfred agent."""

        content_plus = f"""You are an AI Agent who uses tools to help provide accurate and concise answers. I will ask you a question. Your final answer should be a number OR as few words as possible OR a comma separated list of numbers and/or strings. If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise. If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise. If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string.

        Think through and follow all instructions carefully. Pay close attention to the formatting instructions.

        Question:{content}""" 

        messages = [HumanMessage(content=content_plus)]
        # messages = self.graph.invoke({"messages": messages})
        # for m in messages["messages"]:
        #     m.pretty_print()
        # response = messages["messages"][-1].content

        response = None
        for chunk in self.graph.stream({"messages": messages}):
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