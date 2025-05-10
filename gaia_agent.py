""" TODO """

import os
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

# Generate the AgentState
class _AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class gaia_agent:
    def __init__(self) -> StateGraph:
        """ TODO """

        # Generate the chat interface, including the tools
        chat_llm = HuggingFaceEndpoint(
            repo_id=os.environ.get("CHAT_MODEL"),
            huggingfacehub_api_token=os.environ.get("HUGGINGFACEHUB_API_TOKEN"),
        )

        chat_model = ChatHuggingFace(
            llm=chat_llm, 
            verbose=True
        )

        # Create the agent graph

        
        # The graph
        self.agent_graph = StateGraph(_AgentState)

        # Define nodes: these do the work

        # Assistant to process the question
        def assistant(state: _AgentState) -> dict:
            """ Formates an LLM response to the current AgentState message."""
            return {
                "messages": [chat_model.invoke(state["messages"])],
            }
        
        self.agent_graph.add_node(
            node="assistant", 
            action=assistant
        )

        # Assistant to check the answer and update if necessary

        def verify_and_correct(state: _AgentState) -> dict:
            """ Double check."""

            messages = state["messages"]
            last_human_message = [msg for msg in messages if isinstance(msg, HumanMessage)][-1]
            last_ai_message = [msg for msg in messages if isinstance(msg, AIMessage)][-1]

            verification_prompt = (
                f"Question: {last_human_message}\n"
                f"Proposed Answer: {last_ai_message}\n\n"
                "Evaluate the answer against all the criteria in the question. If it's accurate and complete, return it as-is. "
                "If it's incorrect, update the answer."
            )

            corrected_answer = chat_model.invoke([HumanMessage(content=verification_prompt)])
            return {"messages": [corrected_answer]}
        
        self.agent_graph.add_node(
            node="checker", 
            action=verify_and_correct
        )


        # Define edges: these determine how the control flow moves
        self.agent_graph.add_edge(
            start_key=START, # from node
            end_key="assistant" # to node
        )
        self.agent_graph.add_edge(
            start_key="assistant", # from node
            end_key="checker" # to node
        )

        # Compile the Agent
        self.agent_graph = self.agent_graph.compile(debug=True)
    
    def __call__(self, content: str) -> str:
        """ Send request to the alfred agent."""

        content_plus = "You are a general AI assistant. I will ask you a question. Your final answer should be a number OR as few words as possible OR a comma separated list of numbers and/or strings. If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise. If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise. If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string. Take you time and a follow all instructions given in the quesiton step by step Question: " + content
        input_dict = {"messages": content_plus}
        response = self.agent_graph.invoke(input_dict)
        return response['messages'][-1].content