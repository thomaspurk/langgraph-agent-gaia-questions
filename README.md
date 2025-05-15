# hf-agents-course-final-assignment

Create an agent that can answer GAIA LLM Assistant evaluation

## Development Environment setup

OS MacOS Sonoma 14.7.4

1. Clone the GitHub repository

2. Create a virtual Python Environment.
   NOTE: The .venv folder is listed in the .gitignore file.

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Create a .env.development.local file. See the file template.env.development.local for required variables.
   NOTE: The .env.development.local file is listed in the .gitignore file.

4. Converting audio files into transcripts is done using openai-whisper. Run following command to give the python environment SSL access to download the models.

```shell
/Applications/Python\ 3.13/Install\ Certificates.command
```

## Tools

- Wiki Lookup
- RAG - Web Search Retreiver
- Image processing
- Video Processing
- Audio Processing
- XLSX Processng
- Coding Agent
- Think Act Observe
