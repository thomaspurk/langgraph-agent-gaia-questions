from langchain.tools import Tool
import io
import requests
import whisper
import tempfile

def _prepare_audio(url: str) -> dict:
    """ Prepares an audio transcript for use by an LLM for question answering

        Args:
            url (str): The path to a file containing the audio.
        
        Returns:
            dict: Contains a string of audio data.
    """

    try:
        response = requests.get(url)
        response.raise_for_status()
        audio_data = io.BytesIO(response.content)

            # Save the audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
            temp_audio_file.write(audio_data.read())
            temp_audio_file_path = temp_audio_file.name

        # Load the Whisper model (base/medium/large for more accuracy)
        audio_model = whisper.load_model("base")      
        transcription = audio_model.transcribe(temp_audio_file_path)
        output = {"audio-transcription": transcription["text"]}
    
    except Exception as e:
        output = f"Error processing audio: {str(e)}"
    

    return {"messages": output}


# Initialize the tool
audio_transcription_from_url = Tool(
    name="audio_transcription_from_url",
    func=_prepare_audio,
    description="Takes a URL to an audio file, downloads the file, and returns a transcription for LLM to use to answer questions."
)