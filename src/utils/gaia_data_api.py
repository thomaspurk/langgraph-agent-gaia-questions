# Description: A set of functions for interacting with Hugging Face's GAIA API
# Author: Thomas Purk
# Date: 2025-05-15
# Reference: https://huggingface.co/learn/agents-course/unit4/hands-on

import requests
import os
import json

# Set up environment variables
default_api_url = os.environ.get("DEFAULT_API_URL")
username = os.environ.get("USER_NAME")
agent_code = os.environ.get("AGENT_CODE")



def get_questions(questions_file_path) -> list | str:
    """ Opens the questions.json file if it exists. If not, loads the questions from the API and saves them to file.

        Args:
            questions_file_path (str): The path to a file where the question data will be saved.
    
        Returns:
            list | str: A collection of dict objects which define the parameters of each question. If an error occurs, returns the error message.
    """
    questions_url = f"{default_api_url}/questions"

    if os.path.exists(questions_file_path):
        
        print("STATUS: Reading questions data from file.")
        try:
            with open(questions_file_path, 'r') as file:
                return json.load(file)
            
        except json.JSONDecodeError:
            return f"Error: Could not decode JSON from {questions_file_path}. The file might be empty or contain invalid JSON."
       
        except Exception as e:
           return f"An error occurred: {e}"
    
    else:
        return fetch_gaia_questions(questions_file_path, questions_url)

def fetch_gaia_questions(questions_file_path: str, questions_url: str) -> list:
    """ Loads the questions from the API and saves them to file.

        Args:
            questions_file_path (str): The path to a file where the question data will be saved.
            questions_url (str): The path to the API service endpoint returning the questions data.
    
        Returns:
            list | str: A collection of dict objects which define the parameters of each question. If an error occurs, returns the error message.
    """

    print(f"Fetching questions from: {questions_url}")

    try:
        response = requests.get(questions_url, timeout=15)
        response.raise_for_status()
        questions_data = json.loads(response.text)

        # write data to file
        with open(questions_file_path, 'w', encoding='utf-8') as questions_file:
            json.dump(questions_data, questions_file, ensure_ascii=False, indent=4)

        if not questions_data:
             print("Fetched questions list is empty.")
             return "Fetched questions list is empty or invalid format."
        
        print(f"Fetched {len(questions_data)} questions.")
        return questions_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching questions: {e}")
        return f"Error fetching questions: {e}"
    
    except requests.exceptions.JSONDecodeError as e:
         print(f"Error decoding JSON response from questions endpoint: {e}")
         print(f"Response text: {response.text[:500]}")
         return f"Error decoding server response for questions: {e}"
    
    except Exception as e:
        print(f"An unexpected error occurred fetching questions: {e}")
        return f"An unexpected error occurred fetching questions: {e}"
       
def post_gaia_answers(answers_payload) -> str:
    """ Posts the answers and returns a status message.
    
        Args:
            answers_payload (list): A collection of dict objects which define the parameters of each answer being submitted.
        
        Returns:
            str: A status message.
    """

    submit_url = f"{default_api_url}/submit"


    if type(answers_payload) == str:
        print(f"NO SUBMISSION: {answers_payload}")
        return
    elif type(answers_payload) != list:
        print(f"NO SUBMISSION: Answer Payload not a list {type(answers_payload)}")
        return
    
    
    # Prepare the answer data for submission
    submission_data = {
        "username": username.strip(), 
        "agent_code": agent_code, 
        "answers": answers_payload
    }

    print(f"STATUS: Submitting {len(answers_payload)} answers for user '{username}'...")

    try:
        response = requests.post(submit_url, json=submission_data, timeout=60)
        response.raise_for_status()
        result_data = response.json()
        final_status = (
            f"Submission Successful!\n"
            f"User: {result_data.get('username')}\n"
            f"Overall Score: {result_data.get('score', 'N/A')}% "
            f"({result_data.get('correct_count', '?')}/{result_data.get('total_attempted', '?')} correct)\n"
            f"Message: {result_data.get('message', 'No message received.')}"
        )
        print("Submission successful.")
        print(final_status)
    
    except requests.exceptions.HTTPError as e:
        error_detail = f"Server responded with status {e.response.status_code}."
        try:
            error_json = e.response.json()
            error_detail += f" Detail: {error_json.get('detail', e.response.text)}"
        except requests.exceptions.JSONDecodeError:
            error_detail += f" Response: {e.response.text[:500]}"

        print(f"STATUS: Submission Failed: {error_detail}")
 
    except requests.exceptions.Timeout:
        print("Submission Failed: The request timed out.")

    except requests.exceptions.RequestException as e:
        print(f"Submission Failed: Network error - {e}")

    except Exception as e:
        print(f"An unexpected error occurred during submission: {e}")



    