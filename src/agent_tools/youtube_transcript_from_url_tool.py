# Description: A LangGraph Agent Tool for converting audio into text.
# Author: Thomas Purk
# Date: 2025-05-15
# Reference: https://pypi.org/project/openai-whisper/
# Reference: https://pypi.org/project/pytube/

from langchain.tools import Tool
import whisper
import tempfile
from pytube import YouTube

def _prepare_audio(url: str) -> dict:
    """ Prepares an audio transcript for use by an LLM for question answering

        Args:
            url (str): The url of the YouTube video containing the audio.
        
        Returns:
            dict: Contains a string of audio data.
    """

    try:
        # Create the pytube YouTube object
        yt = YouTube(url)

        # Get the audio stream with highest quality
        audio_stream = yt.streams.filter(only_audio=True).first()

        # Save the audio to a temporary file
        # Create a temporary file with a suitable audio extension
        suffix = f".{audio_stream.mime_type.split('/')[-1]}"
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    
        # Download to temporary file path
        audio_stream.download(filename=temp_file.name)

        # Load the Whisper model (base/medium/large for more accuracy)
        audio_model = whisper.load_model("base")      
        transcription = audio_model.transcribe(temp_file.name)
        output = {"audio-transcription": transcription["text"]}
    
    except Exception as e:
        output = f"Error processing audio: {str(e)}"
    

    return {"messages": output}


# Initialize the tool
youtube_transcription_from_url = Tool(
    name="youtube_transcription_from_url",
    func=_prepare_audio,
    description="Takes a URL to a YouTube, downloads the audio only file, and returns a transcription for LLM to use to answer questions. The the video transcript could be a narration describing what is happening on camera."
)