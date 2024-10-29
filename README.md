# Text to Speech Converter

A Streamlit web application that converts text to speech using OpenAI's Text-to-Speech (TTS) API. This application allows users to input text and generate high-quality audio files with various voice options.

## Features

- Clean and intuitive web interface
- Multiple voice options (alloy, echo, fable, onyx, nova, shimmer)
- Real-time audio preview
- Download capability for generated MP3 files
- Automatic file organization with timestamp-based naming

## Prerequisites

- Python 3.x
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd tts-voice-app
```

2. Create and activate a virtual environment:
```bash
python -m venv ttsapp
source ttsapp/Scripts/activate  # On Windows
# OR
source ttsapp/bin/activate     # On Unix/MacOS
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Docker Installation

You can also run the application using Docker:

1. Build the Docker image:
```bash
docker build -t tts-app .
```

2. Run the container:
```bash
docker run -p 8501:8501 -v $(pwd)/output:/app/output -v $(pwd)/.env:/app/.env --name tts-app-container tts-app
```

This will:
- Map port 8501 to access the Streamlit interface
- Mount the output directory to persist generated audio files
- Mount the .env file to provide environment variables
- Create a container named 'tts-app-container'

Access the application at http://localhost:8501

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the provided local URL (typically http://localhost:8501)

3. Enter your text in the text area

4. Select your preferred voice option

5. Click "Convert to Speech" to generate the audio

6. Use the audio player to preview the generated speech

7. Download the MP3 file using the "Download MP3" button

## Project Structure

```
tts-voice-app/
├── app.py              # Main application file
├── requirements.txt    # Project dependencies
├── .env               # Environment variables (create this file)
├── Dockerfile         # Docker configuration file
└── output/            # Generated audio files directory
```

## Dependencies

- streamlit - Web application framework
- openai - OpenAI API client
- python-dotenv - Environment variable management

## Notes

- Generated audio files are saved in the `output` directory with timestamp-based filenames
- The application supports various voice options provided by OpenAI's TTS API
- Make sure to keep your OpenAI API key secure and never commit it to version control
