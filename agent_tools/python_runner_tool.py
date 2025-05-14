from langchain.tools import Tool
import contextlib
import io
import requests

def _execute_python(url: str) -> dict:
    """Adds the output of python code to the agent's messages collection

        Args:
            url (str): The path to a file containing the python code.
        
        Returns:
            dict: Contains a string of formatted documents compatible with LangGraph state messages.
    """

    try:
        response = requests.get(url)
        response.raise_for_status()
        code = response.text

        buffer = io.StringIO()
        exec_globals = {"__name__": "__main__"}
        with contextlib.redirect_stdout(buffer):
            exec(code, exec_globals)
        output = buffer.getvalue()
        if output == "":
            output = "Code executed with no output."
    except Exception as e:
        output = f"Error during code execution: {str(e)}"
    

    return {"messages": output}


# Initialize the tool
python_runner_tool = Tool(
    name="execute_python_code_from_url",
    func=_execute_python,
    description="Takes a URL to a python file, downloads the file, then executes the code."
)