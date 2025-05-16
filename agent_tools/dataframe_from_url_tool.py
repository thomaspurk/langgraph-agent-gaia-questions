# Description: A LangGraph Agent Tool for converting an XLSX file to a Pandas JSON string.
# Author: Thomas Purk
# Date: 2025-05-15
# Reference: https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html

from langchain.tools import Tool
import io
import requests
import pandas

def _prepare_dataframe(url: str) -> dict:
    """ Prepares a Pandas Dataframe for use by an LLM for question answering

        Args:
            url (str): The path to a file containing the excel file.
        
        Returns:
            dict: Contains a string of spreadsheet data.
    """

    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pandas.read_excel(io.BytesIO(response.content))

        output = {"dataframe": df.to_json()}
    
    except Exception as e:
        output = f"Error processing image: {str(e)}"
    
    return {"messages": output}


# Initialize the tool
dataframe_from_url = Tool(
    name="dataframe_from_url",
    func=_prepare_dataframe,
    description="Takes a URL to an XLSX file, downloads the file, and returns a pandas dataframe string for LLM processing."
)