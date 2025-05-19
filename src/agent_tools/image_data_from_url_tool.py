# Description: A LangGraph Agent Tool downloading an image and converting it to a string.
# Author: Thomas Purk
# Date: 2025-05-15
# Reference: https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Schemes/data
# Reference: https://github.com/openai/openai-python?tab=readme-ov-file#vision

from langchain.tools import Tool
import io
import requests
import base64
from PIL import Image

def _prepare_image(url: str) -> dict:
    """ Prepares an image for use by an LLM for question answering

        Args:
            url (str): The path to a file containing the image.
        
        Returns:
            dict: Contains a string of image data.
    """

    try:
        response = requests.get(url)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content))

        # Convert image to base64 for vision model (if needed)
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        data_uri = f"data:image/png;base64,{img_base64}"

        output = {"type": "image_url", "image_url": {"url": data_uri}}
    
    except Exception as e:
        output = f"Error processing image: {str(e)}"
    

    return {"messages": output}


# Initialize the tool
image_data_from_url = Tool(
    name="image_data_from_url",
    func=_prepare_image,
    description="Takes a URL to an image file, download the file, and returns the data for LLM processing."
)