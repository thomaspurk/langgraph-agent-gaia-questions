import json

def write_individual_answer(question: dict, answer: str, path: str):
    """ Creates a tracking file for each answer.
     
        Args:
            question (dict): A set of parameters defining the question.
            answer (str): The text answer to the question.
            path (str): The folder to save the file in.
    """

    try:
        answer_file_path = f"{path}{question["task_id"]}.json"
        question['answer'] = answer

        # write data to file
        with open(answer_file_path, 'w', encoding='utf-8') as answers_file:
            json.dump(question, answers_file, ensure_ascii=False, indent=4)

    except Exception as e:
        raise e 

def update_reporter(node: str, update: dict) -> str:
    """ Format agent stream status update dicts as a string that is readable in a console out put.

        Args:
            node (str): The name of the execution node.
            update (dict): A collection of parameters defining the update information.
        
        Returns:
            str: A status string reading for printing to the console.
    """

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