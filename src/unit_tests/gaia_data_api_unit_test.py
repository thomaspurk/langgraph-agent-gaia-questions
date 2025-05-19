# Note: post_gaia_answers function note test. Do not want to post data during a test.

import os
from src.utils.gaia_data_api import get_questions, fetch_gaia_questions

from dotenv import load_dotenv
# This test case is designed to run in a local development environment
# Load the local environment configuration
load_dotenv(".env.development.local")

default_api_url = os.environ.get("DEFAULT_API_URL")


questions_file_path = 'src/unit_tests/input_output/questions.json'
bad_questions_file_path = 'src/unit_tests/input_output/bad_question_file.json'
questions_url = f"{default_api_url}/questions"


def test_fetch_gaia_questions():
    """should get questions from the API and save to file """

    # ARRANGE
    input = questions_file_path
    expected_result = 20

    # ACT
    # no return value 
    result = len(fetch_gaia_questions(input, questions_url))

    # ASSERT
    assert os.path.exists(input) == True
    assert result == expected_result

def test_fetch_gaia_questions_bad_url():
    """should return an error if pass a bad url """

    # ARRANGE
    input = "bad-url"

    # ACT
    # no return value 
    result = fetch_gaia_questions(questions_file_path, input)

    # ASSERT
    assert "Error fetching questions" in result

def test_fetch_gaia_questions_bad_path():
    """should return an error if passed a bad path"""

    # ARRANGE
    input = "/bad-path"

    # ACT
    # no return value 
    result = fetch_gaia_questions(input, questions_url)

    # ASSERT
    assert "An unexpected error occurred fetching questions" in result

def test_get_questions():
    """should return an error if passed a bad path"""

    # ARRANGE
    input = questions_file_path
    expected_result = 20

    # ACT
    # no return value 
    result = len(get_questions(input))

    # ASSERT
    assert result == expected_result

def test_get_questions_bad_json_file():
    """should return an error if passed a path to a file with bad JSON"""

    # ARRANGE
    input = bad_questions_file_path

    # ACT
    # no return value 
    result = get_questions(input)

    # ASSERT
    assert "Error: Could not decode JSON from" in result

