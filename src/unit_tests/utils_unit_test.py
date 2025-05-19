import os
import json
from dotenv import load_dotenv
from langchain_core.messages import AIMessage

# This test case is designed to run in a local development environment
# Load the local environment configuration
load_dotenv(".env.development.local")
from src.utils.utils import write_individual_answer, update_reporter

task_id = 9876543210
task_data = {
        "task_id": task_id,
        "question": "This is a question.",
        "Level": "1",
        "file_name": ""
    }

def test_write_individual_answer():
    # should write a file with the correct name

    # ARRANGE
    input_question = task_data
    input_answer = "This is an answer."
    input_path = "src/unit_tests/input_output/"
    expected_result = f"src/unit_tests/input_output/{task_id}.json"

    # ACT
    # no return value 
    write_individual_answer(
        question=input_question,
        answer=input_answer,
        path=input_path
    )

    # ASSERT
    assert os.path.exists(expected_result) == True

def test_write_individual_answer_contents():
    # should write the correct answer data to file

    # ARRANGE
    input = f"src/unit_tests/input_output/{task_id}.json"
    expected_result = task_data.copy()
    expected_result["answer"] = "This is an answer."

    # ACT

    with open(input, 'r') as f:
     result =  json.load(f)

    # ASSERT
    assert result == expected_result

def test_update_reporter():
    # should write the correct answer data to file

    # ARRANGE
    input_node = "test"
    input_messages = {
       "messages": [
            AIMessage(
                name="test",
                content="This is a Test AI Message",
                tool_calls=[
                    {
                        "id": "test_tool",
                        "name": "test_tool",
                        "args": {"test": "test"}
                    }
                ]
            )
        ]
    }
    expected_result = """
_________________________ Update from node: test  _________________________

========================= AIMessage =========================

Name: test

This is a Test AI Message
{'name': 'test_tool', 'args': {'test': 'test'}, 'id': 'test_tool', 'type': 'tool_call'}"""

    # ACT
    result = update_reporter(input_node, input_messages)
  
    # ASSERT
    assert result == expected_result
