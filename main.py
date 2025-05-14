""" TODO """

# Reference: https://huggingface.co/spaces/fisherman611/gaia-agent/blob/main/agent.py

import os
import json
from agents.gaia_agent import gaia_agent
from gaia_data_api import get_questions, post_gaia_answers

# Load the local environment configuration
from dotenv import load_dotenv
load_dotenv(".env.development.local")

answers_file_path = 'data/answers.json'

def main():
    """ TODO """
    questions_data = get_questions()
    answers_payload = get_answers()

    if type(questions_data) != list:
        print(f"STATUS: Questions Data not a list {type(questions_data)}")
        return

    if type(answers_payload) != list:
        print(f"STATUS: Answer Payload not a list {type(answers_payload)}")
        return
    
    print(f"Running agent on {len(questions_data)} questions...")

    answer_agent = gaia_agent()

    temp_list = [
        "8e867cd7-cff9-4e6c-867a-ff5ddc2550be",
        "4fc2f1ae-8625-45b5-ab34-ad4433bc21f8"
    ]

    for question in questions_data:
        task_id = question.get("task_id")
        question_text = question.get("question")
        if not task_id or question_text is None:
            print(f"Skipping item with missing task_id or question: {question}")
            continue

        if os.path.exists(f"data/answers/{task_id}.json"):
            print(f"Skipping item {task_id}. Good answer already exists")
            continue

        if not task_id in temp_list:
            continue # for development, focus on one question at a time
        try:

            submitted_answer = answer_agent(question_text)
            answers_payload.append({"task_id": task_id, "submitted_answer": submitted_answer})
            write_answer(question.copy(), submitted_answer)
        except Exception as e:
             print(f"ERROR: Running agent on task {task_id}: {e}")

    # write data to file
    with open(answers_file_path, 'w', encoding='utf-8') as answers_file:
        json.dump(answers_payload, answers_file, ensure_ascii=False, indent=4)



def get_answers() -> list | str:
    """ TODO """
    # Load answers.json file if it exists
    if os.path.exists(answers_file_path):
        print("STATUS: Reading answsers data from file.")
        try:
            with open(answers_file_path, 'r') as file:
                return json.load(file) # Happy Path
        except json.JSONDecodeError:
            return f"Could not decode JSON from {answers_file_path}. The file might be empty or contain invalid JSON."
        except Exception as e:
            return f"An error occurred: {e}"
    else:
        return []

def write_answer(question: dict, answer: str):
    """ TODO """

    try:
        answer_file_path = f"data/answers/{question.get("task_id")}.json"
        question['answer'] = answer

        # write data to file
        with open(answer_file_path, 'w', encoding='utf-8') as answers_file:
            json.dump(question, answers_file, ensure_ascii=False, indent=4)

    except Exception as e:
        raise e 


if __name__ == "__main__":
    main()