from langchain.tools import Tool
import io
import requests
import pandas

def _prepare_dataframe(url: str) -> dict:
    """ Prepares a Pandas Dataframe for use by an LLM for question answering

        Args:
            url (str): The path to a file containing the excel file.
        
        Returns:
            dict: Contains a string of image data.
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