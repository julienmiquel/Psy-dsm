"""
Handles the generation of audio from text using Google GenAI (Gemini TTS).
"""
import os
import logging
import streamlit as st
from tenacity import retry, stop_after_delay, stop_after_attempt, wait_exponential, before_sleep_log
from google import genai
from google.genai import types

import struct
import numpy as np
import io
import wave
from pydub import AudioSegment

# Configure logging
logger = logging.getLogger(__name__)

# Constants
MODEL_TTS = os.getenv("MODEL_TTS", "gemini-2.5-pro-tts")
TTS_LOCATION = os.getenv("MODEL_TTS_LOCATION", "us-central1")
TTS_LANGUAGE_CODE = "fr-FR"
SAMPLE_RATE = 24000  # Gemini TTS usually defaults to 24kHz for standard voices, need to verify


# Prompts for TTS
TTS_SYSTEM_PROMPT = "You are a professional French podcast speaker."
TTS_VOICE_STYLE = "Engaging, warm, and clear conversation flow."

@st.cache_resource
def get_genai_client() -> genai.Client:
    """Returns a configured Gemini API client."""
    # Note: Vertex AI is enabled based on previous services.py config
    return genai.Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", TTS_LOCATION),
        http_options={'timeout': 600000}
    )

@retry(
    stop=stop_after_attempt(10), # Retry up to 10 times regardless of duration
    wait=wait_exponential(multiplier=2, min=2, max=60),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)
def generate_audio_segment(text: str, speaker_role: str) -> bytes:
    """
    Generates audio for a given text segment using Google GenAI Gemini TTS.
    
    Args:
        text (str): The text to be synthesized.
        speaker_role (str): The role of the speaker (e.g., "Host", "Expert").
        
    Returns:
        bytes: The audio content in MP3 format.
    """
    if not text or len(text.strip()) < 3:
        return b""

    client = get_genai_client()

    # Define voice based on speaker role
    if "Host" in speaker_role or "Animateur" in speaker_role:
        voice_name = "Puck" 
    else: # Expert / Psychologist
        voice_name = "Kore"

    # Configure the generation for audio
    config = types.GenerateContentConfig(
        response_modalities=["audio"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=voice_name
                )
            )
        )
    )

    # Prompt construction
    prompt = f"[{TTS_SYSTEM_PROMPT} \n {TTS_VOICE_STYLE}. Speak in {TTS_LANGUAGE_CODE}]\n\n{text}"

    try:
        response = client.models.generate_content(
            model=MODEL_TTS,
            contents=prompt,
            config=config,
        )
        
        # Extract audio bytes from the response
        # Structure depends on the response format, typically candidates[0].content.parts[0].inline_data
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
             for part in response.candidates[0].content.parts:
                 if part.inline_data:
                     return part.inline_data.data
        return b""

    except Exception as e:
        logger.error(f"Failed to generate audio directly: {e}")
        raise

def create_wav_header(pcm_data: bytes, sample_rate: int = 24000) -> bytes:
    """
    Creates a valid RIFF/WAV header for the given PCM data.
    """
    num_channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = len(pcm_data)
    
    header = b'RIFF'
    header += struct.pack('<I', 36 + data_size)
    header += b'WAVEfmt '
    header += struct.pack('<I', 16) # Subchunk1Size
    header += struct.pack('<H', 1)  # AudioFormat (PCM)
    header += struct.pack('<H', num_channels)
    header += struct.pack('<I', sample_rate)
    header += struct.pack('<I', byte_rate)
    header += struct.pack('<H', block_align)
    header += struct.pack('<H', bits_per_sample)
    header += b'data'
    header += struct.pack('<I', data_size)
    
    return header

def assemble_audio(segments: list[bytes]) -> bytes:
    """
    Assembles multiple raw PCM audio segments into a single WAV file with header.
    """
    full_pcm = b"".join(segments)
    header = create_wav_header(full_pcm)
    return header + full_pcm

def mix_audio(voice_bytes: bytes, music_bytes: bytes, music_volume: float = 0.2) -> bytes:
    """
    Mixes voice track with background music.
    Loops the music to match voice duration and adjusts volume.
    
    Args:
        voice_bytes: The assembled WAV bytes of the voice track.
        music_bytes: The WAV bytes of the music track.
        music_volume: Volume of music relative to voice (0.0 to 1.0).
        
    Returns:
        bytes: The mixed audio in WAV format.
    """
    try:
        # Load Voice
        # Note: bytes are full WAVs with headers. We need to skip header or use wave module to read.
        # Since we use standard WAV structure, let's use a safe helper or memory file
        # But wave module requires seekable file
        
        def read_wav(data):
            with wave.open(io.BytesIO(data), 'rb') as wav_file:
                params = wav_file.getparams()
                frames = wav_file.readframes(wav_file.getnframes())
                # Convert to numpy array (assume 16-bit PCM mono for now as per our creation)
                # If stereo, logic needs adjustment. Our create_wav_header says mono (1 channel).
                # But Lyria output might be stereo? We need to check Lyria output.
                # Assuming Lyria is stereo, we might need to mix stereo to mono or upmix voice.
                # Let's handle both as int16
                audio_array = np.frombuffer(frames, dtype=np.int16)
                if params.nchannels == 2:
                    audio_array = audio_array.reshape(-1, 2)
                return audio_array, params

        voice_array, voice_params = read_wav(voice_bytes)
        music_array, music_params = read_wav(music_bytes)
        
        # Ensure sample rates match? 
        # If not, we should resample. For now, assume they are close or identical (24k vs 44.1k?)
        # Gemini TTS is 24k. Lyria is likely 44.1k or 48k.
        # Simple mixing requires same rate.
        # If rates differ, this is complex without scipy/librosa.
        # Let's hope for the best or implement simple resampling?
        # A simple linear interpolation for resampling if rates differ:
        # Resample if needed
        if voice_params.framerate != music_params.framerate:
             logger.warning(f"Resampling: Voice={voice_params.framerate}Hz, Music={music_params.framerate}Hz")
             
             target_rate = max(voice_params.framerate, music_params.framerate)
             
             def resample_array(arr, current_rate, target_rate):
                 if current_rate == target_rate:
                     return arr
                 duration = len(arr) / current_rate
                 target_len = int(duration * target_rate)
                 
                 # Create time points
                 x_old = np.linspace(0, duration, len(arr))
                 x_new = np.linspace(0, duration, target_len)
                 
                 # Interpolate
                 # Handle multi-channel
                 if arr.ndim == 1:
                     return np.interp(x_new, x_old, arr).astype(arr.dtype)
                 else:
                     # Interpolate each channel
                     new_channels = []
                     for i in range(arr.shape[1]):
                         chan = arr[:, i]
                         new_chan = np.interp(x_new, x_old, chan)
                         new_channels.append(new_chan)
                     return np.column_stack(new_channels).astype(arr.dtype)

             voice_array = resample_array(voice_array, voice_params.framerate, target_rate)
             music_array = resample_array(music_array, music_params.framerate, target_rate)
             
             # Update params (simplification, we just use target_rate for output)
             out_rate = target_rate
        else:
             out_rate = voice_params.framerate

        # Adjust music volume
        music_array = music_array.astype(np.float32) * music_volume
        
        # Loop music to match voice length
        voice_len = len(voice_array)
        music_len = len(music_array)
        
        if music_len < voice_len:
            repeat_factor = int(np.ceil(voice_len / music_len))
            # Tile checks dimensions
            if music_array.ndim == 1:
                music_looped = np.tile(music_array, repeat_factor)[:voice_len]
            else:
                 music_looped = np.tile(music_array, (repeat_factor, 1))[:voice_len, :]
        else:
            music_looped = music_array[:voice_len]
            
        # Handle Channel Mismatch (Mono Voice vs Stereo Music)
        if voice_params.nchannels == 1 and music_params.nchannels == 2:
            # Duplicate voice to stereo
            voice_array_stereo = np.column_stack((voice_array, voice_array))
            mixed = voice_array_stereo + music_looped
            out_channels = 2
        elif voice_params.nchannels == 2 and music_params.nchannels == 1:
            # Duplicate music to stereo
            music_looped_stereo = np.column_stack((music_looped, music_looped))
            mixed = voice_array + music_looped_stereo
            out_channels = 2
        else:
            # Same channels
            mixed = voice_array + music_looped
            out_channels = voice_params.nchannels

        # Clip and convert back to int16
        mixed = np.clip(mixed, -32768, 32767).astype(np.int16)
        
        # Write to bytes
        # We need to write a new WAV file
        out_bytes = io.BytesIO()
        with wave.open(out_bytes, 'wb') as wav_out:
            wav_out.setnchannels(out_channels)
            wav_out.setsampwidth(2) # 16 bit
            wav_out.setsampwidth(2) # 16 bit
            wav_out.setframerate(int(out_rate)) # Use target rate
            wav_out.writeframes(mixed.tobytes())
            
        return out_bytes.getvalue()

    except Exception as e:
        logger.error(f"Mixing failed: {e}")
        return voice_bytes # Fallback to just voice


def convert_to_mp3(audio_bytes: bytes) -> bytes:
    """
    Converts WAV/PCM bytes to MP3 bytes using pydub.
    """
    try:
        # Check if it has a header or is raw
        # Try loading as WAV first (since assemble_audio adds header)
        audio = AudioSegment.from_wav(io.BytesIO(audio_bytes))
        
        output = io.BytesIO()
        audio.export(output, format="mp3", bitrate="192k")
        return output.getvalue()
    except Exception as e:
        logger.error(f"MP3 conversion failed: {e}")
        # Fallback to returning original bytes (likely WAV) but this might break things expecting MP3
        # Ideally we raise or handle
        raise


