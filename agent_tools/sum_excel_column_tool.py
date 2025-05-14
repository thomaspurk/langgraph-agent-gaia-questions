from langchain.tools import Tool
import json
import pandas

def _sum_column(series: str) -> dict:
    """ Adds the items in an Excel Table Column that is represented as a JSON string of a Panadas Series

        Args:
            series (str): A JSON string containing numeric values.
        
        Returns:
            dict: The sum of the column.
    """

    try:
        json_object = json.loads(series)
        series_object = pandas.Series(json_object)
        

        output = {"column-sum": sum(series_object)}
    
    except Exception as e:
        output = f"Error processing JSON Series: {str(e)}"
    
    return {"messages": output}


# Initialize the tool
sum_excel_column = Tool(
    name="series_sum_from_json",
    func=_sum_column,
    description="Takes a JSON string of number values compatible with a Pandas Series, and returns the sum of the string."
)