"""
Voice I/O module for Shaheen-Jarvis framework.
Handles speech-to-text and text-to-speech functionality.
"""

import logging
from typing import Optional
import warnings

# Suppress warnings for audio libraries
warnings.filterwarnings("ignore", category=UserWarning)


class VoiceIO:
    """Handles voice input and output for Jarvis."""
    
    def __init__(self, config_manager):
        """
        Initialize voice I/O with configuration.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize STT and TTS engines
        self.stt_engine = None
        self.tts_engine = None
        
        self._init_tts()
        self._init_stt()
    
    def _init_tts(self):
        """Initialize text-to-speech engine."""
        tts_backend = self.config.get('voice.tts_backend', 'pyttsx3')
        
        try:
            if tts_backend == 'pyttsx3':
                import pyttsx3
                self.tts_engine = pyttsx3.init()
                
                # Configure voice properties
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    self.tts_engine.setProperty('voice', voices[0].id)
                
                self.tts_engine.setProperty('rate', 200)  # Speed
                self.tts_engine.setProperty('volume', 0.9)  # Volume
                
                self.logger.info("Initialized pyttsx3 TTS engine")
            
            elif tts_backend == 'gTTS':
                # gTTS requires internet connection and will be used on-demand
                self.logger.info("Selected gTTS backend (requires internet)")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS engine: {e}")
            self.tts_engine = None
    
    def _init_stt(self):
        """Initialize speech-to-text engine."""
        stt_backend = self.config.get('voice.stt_backend', 'google-speech')
        
        try:
            # Always try Google Speech Recognition first as it's most reliable
            import speech_recognition as sr
            self.stt_engine = sr.Recognizer()
            
            # Try to find the best microphone
            try:
                # List available microphones
                mic_list = sr.Microphone.list_microphone_names()
                self.logger.info(f"Available microphones: {mic_list[:3]}...")  # Show first 3
                
                # Use default microphone
                self.microphone = sr.Microphone()
                
                # Adjust for ambient noise with shorter duration
                print("🎤 Calibrating microphone... Please be quiet for 2 seconds.")
                with self.microphone as source:
                    self.stt_engine.adjust_for_ambient_noise(source, duration=2)
                    
                # Configure recognizer settings
                self.stt_engine.energy_threshold = 300  # Minimum audio energy to consider for recording
                self.stt_engine.dynamic_energy_threshold = True
                self.stt_engine.pause_threshold = 0.8  # Seconds of non-speaking audio before phrase is complete
                self.stt_engine.phrase_threshold = 0.3  # Minimum seconds of speaking audio before we consider the phrase started
                
                self.logger.info("Initialized Google Speech Recognition with optimized settings")
                
            except Exception as mic_error:
                self.logger.error(f"Microphone setup error: {mic_error}")
                # Still try to create a basic setup
                self.microphone = sr.Microphone()
                self.stt_engine.energy_threshold = 4000  # Higher threshold if calibration failed
                
        except ImportError as e:
            self.logger.error(f"SpeechRecognition not available: {e}")
            self.stt_engine = None
        except Exception as e:
            self.logger.error(f"Failed to initialize STT engine: {e}")
            self.stt_engine = None
    
    def _init_google_speech(self):
        """Fallback to Google Speech Recognition."""
        try:
            import speech_recognition as sr
            self.stt_engine = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            with self.microphone as source:
                self.stt_engine.adjust_for_ambient_noise(source)
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Speech: {e}")
    
    def speak(self, text: str) -> None:
        """
        Convert text to speech.
        
        Args:
            text: Text to speak
        """
        if not text:
            return
        
        tts_backend = self.config.get('voice.tts_backend', 'pyttsx3')
        
        try:
            if tts_backend == 'pyttsx3' and self.tts_engine:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            
            elif tts_backend == 'gTTS':
                self._speak_with_gtts(text)
            
            else:
                self.logger.warning("No TTS engine available")
                
        except Exception as e:
            self.logger.error(f"Error in text-to-speech: {e}")
    
    def _speak_with_gtts(self, text: str):
        """
        Use gTTS for text-to-speech.
        
        Args:
            text: Text to speak
        """
        try:
            from gtts import gTTS
            import pygame
            import io
            
            # Generate speech
            tts = gTTS(text=text, lang='en')
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Play audio
            pygame.mixer.init()
            pygame.mixer.music.load(audio_buffer)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
                
        except Exception as e:
            self.logger.error(f"Error with gTTS: {e}")
    
    def listen(self, timeout: int = 10, phrase_time_limit: int = 5) -> Optional[str]:
        """
        Listen for voice input and convert to text.
        
        Args:
            timeout: Seconds to wait for speech to start
            phrase_time_limit: Maximum seconds to record speech
            
        Returns:
            Recognized text or None if recognition failed
        """
        try:
            # Always use Google Speech Recognition for reliability
            return self._listen_with_speech_recognition(timeout, phrase_time_limit)
                
        except Exception as e:
            self.logger.error(f"Error in speech recognition: {e}")
            return None
    
    def _listen_with_whisper(self) -> Optional[str]:
        """
        Use Whisper for speech recognition.
        
        Returns:
            Recognized text or None
        """
        try:
            import whisper
            import sounddevice as sd
            import numpy as np
            import tempfile
            import wave
            
            # Record audio
            duration = 5  # seconds
            sample_rate = 16000
            
            self.logger.info("Listening... (speak now)")
            audio_data = sd.rec(int(duration * sample_rate), 
                              samplerate=sample_rate, 
                              channels=1, 
                              dtype=np.int16)
            sd.wait()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_data.tobytes())
                
                # Transcribe with Whisper
                result = self.whisper_model.transcribe(temp_file.name)
                return result['text'].strip()
                
        except Exception as e:
            self.logger.error(f"Error with Whisper recognition: {e}")
            return None
    
    def _listen_with_speech_recognition(self, timeout: int, phrase_time_limit: int) -> Optional[str]:
        """
        Use SpeechRecognition library for speech recognition.
        
        Args:
            timeout: Seconds to wait for speech
            phrase_time_limit: Maximum recording time
            
        Returns:
            Recognized text or None
        """
        if not self.stt_engine or not hasattr(self, 'microphone'):
            self.logger.error("Speech recognition not properly initialized")
            return None
        
        try:
            import speech_recognition as sr
            
            print("🎤 Listening... Please speak clearly into your microphone.")
            self.logger.info("Listening for speech input...")
            
            # Listen for audio with improved settings
            with self.microphone as source:
                try:
                    # Listen with longer timeout and better phrase detection
                    audio = self.stt_engine.listen(
                        source, 
                        timeout=timeout, 
                        phrase_time_limit=phrase_time_limit
                    )
                    print("🔄 Processing speech...")
                    
                except sr.WaitTimeoutError:
                    print("⏰ No speech detected within timeout period.")
                    return None
            
            # Try Google Speech Recognition with better error handling
            try:
                print("🌐 Using Google Speech Recognition...")
                text = self.stt_engine.recognize_google(audio, language='en-US')
                if text:
                    print(f"✅ Recognized: {text}")
                    return text.strip()
                else:
                    print("❌ Empty result from speech recognition")
                    return None
                    
            except sr.UnknownValueError:
                print("❌ Could not understand the audio. Please speak more clearly.")
                self.logger.warning("Speech recognition could not understand audio")
                return None
                
            except sr.RequestError as e:
                print(f"❌ Speech recognition service error: {e}")
                self.logger.error(f"Speech recognition request error: {e}")
                
                # Fall back to offline recognition if available
                print("🔄 Trying offline recognition...")
                try:
                    text = self.stt_engine.recognize_sphinx(audio)
                    if text:
                        print(f"✅ Offline recognition: {text}")
                        return text.strip()
                except (sr.UnknownValueError, sr.RequestError):
                    print("❌ Offline recognition also failed")
                    pass
                    
                return None
                    
        except Exception as e:
            print(f"❌ Unexpected error in speech recognition: {e}")
            self.logger.error(f"Unexpected error in speech recognition: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        Check if voice I/O is available.
        
        Returns:
            True if both TTS and STT are available
        """
        return self.tts_engine is not None and self.stt_engine is not None
