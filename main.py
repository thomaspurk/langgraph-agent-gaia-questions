""" TODO """

# Load the local environment configuration first
# Some local packages depend on env settings
from dotenv import load_dotenv
load_dotenv(".env.development.local")

import os
import json
from agents.gaia_agent import gaia_agent
from gaia_data_api import get_questions, post_gaia_answers

# Set up environment variables
username = os.environ.get("USER_NAME")
hf_token = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
default_api_url = os.environ.get("DEFAULT_API_URL")
agent_code = os.environ.get("AGENT_CODE")

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

    # To exclude questions from being processed, so you can deal with a subset, comment out questions in this list.
    temp_list = [
        "cabe07ed-9eca-40ea-8ead-410ef5e83f91", # web search - Wrong, LibreText doc has changed no longer includes the answer
        "3cef3a44-215e-4aed-8e3b-b1e3f08063b7", # web search - Wrong, includes some botanical fruits
        "305ac316-eef6-4446-960a-92d80d542f82", # web search - Correct
        "3f57289b-8c60-48be-bd80-01f8099ca449", # web search - Wrong, not finding the correct batter
        "840bfca7-4f7b-481a-8794-c560c340185d", # web search - Correct
        "bda648d7-d618-4883-88f4-3466eabd860e", # web search - Correct
        "cf106601-ab4f-4af9-b045-5295fe67b37d", # web search - Correct
        "a0c07678-e491-4bbc-8f0b-07405144218f", # web search - Correct
        "5a0c1adf-205e-4841-a666-7c3ef95def9d", # web search - Correct
        "8e867cd7-cff9-4e6c-867a-ff5ddc2550be", # wiki loader - Correct
        "4fc2f1ae-8625-45b5-ab34-ad4433bc21f8", # wiki loader and web search - Correct
        "7bd855d8-463d-4ed5-93ca-5fe35145f733", # excel processor - Correct
        "2d83110e-a098-4ebb-9987-066c06fa42d0", # chat only - Correct
        "6f37996b-2ac7-44b0-8e68-6d28256631b4", # chat only - Correct
        "f918266a-b3e0-4914-865d-4faa564f1aef", # code interpreter - Correct
        "cca530fc-4052-43b2-b130-b30968d8aa44", # image processor - Correct
        # "a1e91b78-d3d8-4675-bb8d-62741b4b68a6", # video processor
        # "9d191bce-651d-4746-be2d-7ef8ecadb9c2", # video processor
        "1f975693-876d-457b-a649-393859e79bf3", # audio processing - Correct
        "99c9cc74-fdc8-46c6-8f8d-3ce2d3bfeea3", # audio processing - Correct
    ]

    for question in questions_data:
        task_id = question.get("task_id")
        question_text = question.get("question")
        file_name = question.get("file_name")

        # Check for task id
        if not task_id or question_text is None:
            print(f"Skipping item with missing task_id or question: {question}")
            continue

        if not task_id in temp_list:
            continue # for development purposes, focus on a subset of questions



        # NOTE: The asnwers folder is excluded by .gitignore
        # Do not hit the LLM again for answers that have been processed and look correct.
        # Load the answer from file.
        # Delete all files under "/data/answers" to start fresh
        if os.path.exists(f"data/answers/{task_id}.json"):
            
            with open(f"data/answers/{task_id}.json", 'r') as file:
                submitted_answer = json.load(file)["answer"]
            print(f"Answer file found, loading from file: {task_id}. Answer: {submitted_answer}")

        else: # Ask the agent for an answer

            try:  
                # Append information about files attached to the question if they exist
                if file_name != "":
                    question_text += f"\n\nThe file path is: {default_api_url}/files/{task_id}"
            
                # Ask the agent to answer the question
                submitted_answer = answer_agent(question_text)

            except Exception as e:
               submitted_answer = f"ERROR: Running agent on task {task_id}: {e}"

            # Save the answer in the unofficial "answers" folder.
            write_individual_answer(question.copy(), submitted_answer)

        # Save the answer in the official collection.
        answers_payload.append({"task_id": task_id, "submitted_answer": submitted_answer})
           
    # Write official answers to file, this is that data that will be submitted.
    with open(answers_file_path, 'w', encoding='utf-8') as answers_file: # overwrite
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

def write_individual_answer(question: dict, answer: str):
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