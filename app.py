import streamlit as st
import openai
from pathlib import Path
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def create_audio(text, voice="alloy"):
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

def main():
    st.set_page_config(page_title="Text to Speech Converter", page_icon="🎧")
    
    st.title("Text to Speech Converter")
    st.write("Convert your text to speech using OpenAI's TTS API")
    
    # Text input
    text_input = st.text_area("Enter your text here:", height=150)
    
    # Voice selection
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
            audio_path = create_audio(text_input, voice_option)
            
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

if __name__ == "__main__":
    main()
