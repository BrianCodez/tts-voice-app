import streamlit as st
import openai
from pathlib import Path
from dotenv import load_dotenv
import os
import time
import requests
import json

# Load environment variables
load_dotenv()

# Configure API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")

def get_murf_voices():
    """Fetch available voices from Murf AI API"""
    try:
        url = "https://api.murf.ai/v1/speech/voices"
        headers = {
            'Accept': 'application/json',
            'token': MURF_API_KEY,
            'api-key': MURF_API_KEY
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return []
            
        voices = response.json()
        return voices
    except Exception as e:
        st.error(f"Error fetching Murf AI voices: {str(e)}")
        return []

def create_audio_openai(text, voice="alloy"):
    """Create audio from text using OpenAI's TTS API"""
    try:
        response = openai.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # Create output directory if it doesn't exist
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Generate unique filename based on timestamp
        timestamp = int(time.time())
        output_path = output_dir / f"speech_{timestamp}.mp3"
        
        # Save the audio file
        response.stream_to_file(str(output_path))
        return str(output_path)
    except Exception as e:
        st.error(f"Error creating audio: {str(e)}")
        return None

def create_audio_murf(text, voice_id, style, rate, pitch):
    """Create audio from text using Murf AI API"""
    try:
        url = "https://api.murf.ai/v1/speech/generate"
        
        headers = {
            'Accept': 'application/json',
            'token': MURF_API_KEY,
            'api-key': MURF_API_KEY,
            'Content-Type': 'application/json'
        }
        
        payload = {
            "voiceId": voice_id,
            "style": style,
            "text": text,
            "rate": rate,
            "pitch": pitch,
            "format": "MP3",
            "channelType": "MONO",
            "modelVersion": "GEN2",
            "sampleRate": 24000,
            "pronunciationDictionary": {},
            "encodeAsBase64": False  # Get URL instead of base64 encoded audio
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
        # Parse the JSON response
        response_data = response.json()
        
        # Check if we have an audio URL in the response
        if 'audioFile' in response_data:
            audio_url = response_data['audioFile']
            
            # Download the audio file from the URL
            audio_response = requests.get(audio_url)
            if audio_response.status_code == 200:
                # Create output directory if it doesn't exist
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)
                
                # Generate unique filename based on timestamp
                timestamp = int(time.time())
                output_path = output_dir / f"speech_{timestamp}.mp3"
                
                # Save the audio file
                with open(output_path, "wb") as f:
                    f.write(audio_response.content)
                    
                return str(output_path), audio_url
            else:
                st.error(f"Error downloading audio file: {audio_response.status_code}")
                return None
        else:
            st.error("No audio URL in API response")
            st.json(response_data)  # Display the response for debugging
            return None
            
    except Exception as e:
        st.error(f"Error creating audio with Murf AI: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="Text to Speech Converter", page_icon="🎧")
    
    st.title("Text to Speech Converter")
    
    # Service selection
    service = st.selectbox(
        "Select TTS Service:",
        ["OpenAI", "Murf AI"]
    )
    
    # Text input
    text_input = st.text_area("Enter your text here:", height=150)
    
    if service == "OpenAI":
        st.write("Using OpenAI's TTS API")
        # OpenAI voice selection
        voice_option = st.selectbox(
            "Select a voice:",
            ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        )
        
        # Process button
        if st.button("Convert to Speech"):
            if not text_input.strip():
                st.warning("Please enter some text to convert.")
                return
                
            if not openai.api_key:
                st.error("Please set your OpenAI API key in the .env file.")
                return
                
            with st.spinner("Converting text to speech..."):
                audio_path = create_audio_openai(text_input, voice_option)
                
                if audio_path:
                    st.success("Audio generated successfully!")
                    
                    # Audio playback
                    with open(audio_path, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format="audio/mp3")
                    
                    # Download button
                    st.download_button(
                        label="Download MP3",
                        data=audio_bytes,
                        file_name=Path(audio_path).name,
                        mime="audio/mp3"
                    )
    
    else:  # Murf AI
        st.write("Using Murf AI's TTS API")
        
        if not MURF_API_KEY:
            st.error("Please set your Murf AI API key in the .env file.")
            return
            
        # Fetch available voices
        voices = get_murf_voices()
        
        if not voices:
            st.error("Unable to fetch Murf AI voices. Please check your API key and try again.")
            return
            
        # Create voice selection options
        voice_options = []
        voice_styles = {}
        for voice in voices:
            display_name = f"{voice['displayName']} ({voice['accent']}) - {voice['gender']}"
            voice_options.append((voice['voiceId'], display_name))
            voice_styles[voice['voiceId']] = voice['availableStyles']
        
        # Murf AI voice selection and parameters
        selected_voice_id, _ = st.selectbox(
            "Select a voice:",
            options=voice_options,
            format_func=lambda x: x[1]
        )
        
        # Style selection based on selected voice
        style = st.selectbox(
            "Select style:",
            options=voice_styles.get(selected_voice_id, [])
        )
        
        rate = st.slider("Speech rate:", min_value=-50, max_value=50, value=0)  # Updated range
        pitch = st.slider("Pitch:", min_value=-50, max_value=50, value=0)  # Updated range
        
        # Process button
        if st.button("Convert to Speech"):
            if not text_input.strip():
                st.warning("Please enter some text to convert.")
                return
                
            with st.spinner("Converting text to speech..."):
                result = create_audio_murf(text_input, selected_voice_id, style, rate, pitch)
                
                if result:
                    audio_path, audio_url = result
                    st.success("Audio generated successfully!")
                    
                    # Audio playback
                    with open(audio_path, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format="audio/mp3")
                    
                    # Download button
                    st.download_button(
                        label="Download MP3",
                        data=audio_bytes,
                        file_name=Path(audio_path).name,
                        mime="audio/mp3"
                    )
                    
                    # Direct link to audio
                    st.markdown(f"[Click here to listen in browser]({audio_url})")

if __name__ == "__main__":
    main()
