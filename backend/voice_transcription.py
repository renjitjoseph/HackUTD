"""
Real-time voice transcription system for sales call analysis.
Captures audio in 15-second chunks and maintains a 30-second rolling context.
"""

import pyaudio
import wave
import threading
import queue
import time
from datetime import datetime
from collections import deque
import speech_recognition as sr
from typing import Optional, Callable
import io


class VoiceTranscriber:
    """
    Handles real-time audio capture and transcription with rolling buffer.
    """
    
    # Audio configuration
    CHUNK_SIZE = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000  # 16kHz is optimal for speech recognition
    
    # Time windows
    CHUNK_DURATION = 15  # seconds - send new transcript every 15s
    CONTEXT_DURATION = 30  # seconds - keep last 30s of context
    
    def __init__(self, on_transcript: Optional[Callable] = None):
        """
        Initialize the voice transcriber.
        
        Args:
            on_transcript: Callback function called when new transcript is ready.
                          Receives (new_chunk: str, full_context: str)
        """
        self.on_transcript = on_transcript
        self.recognizer = sr.Recognizer()
        self.audio_interface = pyaudio.PyAudio()
        
        # Buffers
        self.audio_buffer = []  # Current 15s chunk
        self.transcript_history = deque(maxlen=2)  # Last 2 chunks (30s)
        
        # Control flags
        self.is_recording = False
        self.stream = None
        self.recording_thread = None
        
        # Stats
        self.chunks_processed = 0
        self.start_time = None
        
    def start(self):
        """Start recording and transcription."""
        if self.is_recording:
            print("Already recording!")
            return
            
        self.is_recording = True
        self.start_time = time.time()
        self.chunks_processed = 0
        
        # Open audio stream
        self.stream = self.audio_interface.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK_SIZE,
            stream_callback=self._audio_callback
        )
        
        # Start recording thread
        self.recording_thread = threading.Thread(target=self._recording_loop)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        self.stream.start_stream()
        print(f"🎤 Voice transcription started!")
        print(f"   - Chunk duration: {self.CHUNK_DURATION}s")
        print(f"   - Context window: {self.CONTEXT_DURATION}s")
        print(f"   - Sample rate: {self.RATE}Hz")
        
    def stop(self):
        """Stop recording and transcription."""
        if not self.is_recording:
            return
            
        self.is_recording = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            
        if self.recording_thread:
            self.recording_thread.join(timeout=2)
            
        elapsed = time.time() - self.start_time if self.start_time else 0
        print(f"\n🛑 Recording stopped. Duration: {elapsed:.1f}s, Chunks: {self.chunks_processed}")
        
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream - captures audio data."""
        if self.is_recording:
            self.audio_buffer.append(in_data)
        return (in_data, pyaudio.paContinue)
        
    def _recording_loop(self):
        """Main recording loop - processes 15s chunks."""
        while self.is_recording:
            # Wait for 15 seconds of audio
            time.sleep(self.CHUNK_DURATION)
            
            if not self.audio_buffer:
                continue
                
            # Get current audio chunk
            audio_data = b''.join(self.audio_buffer)
            self.audio_buffer = []
            
            # Transcribe the chunk
            transcript = self._transcribe_audio(audio_data)
            
            if transcript:
                self.chunks_processed += 1
                
                # Add to history
                self.transcript_history.append({
                    'timestamp': datetime.now(),
                    'text': transcript,
                    'chunk_number': self.chunks_processed
                })
                
                # Get full context (last 30 seconds)
                full_context = self._get_context()
                
                # Log
                elapsed = time.time() - self.start_time
                print(f"\n[{elapsed:.1f}s] Chunk #{self.chunks_processed}")
                print(f"📝 New transcript: {transcript}")
                print(f"📋 Full context ({len(self.transcript_history)} chunks): {full_context[:100]}...")
                
                # Call callback if provided
                if self.on_transcript:
                    try:
                        self.on_transcript(transcript, full_context)
                    except Exception as e:
                        print(f"❌ Error in transcript callback: {e}")
                        
    def _transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """
        Transcribe audio data to text using Google Speech Recognition.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Transcribed text or None if transcription failed
        """
        try:
            # Convert raw audio to AudioData object
            audio = sr.AudioData(audio_data, self.RATE, 2)
            
            # Recognize speech
            print("🔄 Transcribing audio...", end=" ")
            text = self.recognizer.recognize_google(audio)
            print("✅")
            
            return text
            
        except sr.UnknownValueError:
            print("⚠️  Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition service error: {e}")
            return None
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
            
    def _get_context(self) -> str:
        """
        Get the full context (last 30 seconds of transcripts).
        
        Returns:
            Combined transcript text from last 2 chunks
        """
        return " ".join([chunk['text'] for chunk in self.transcript_history])
        
    def get_stats(self) -> dict:
        """Get transcription statistics."""
        return {
            'is_recording': self.is_recording,
            'chunks_processed': self.chunks_processed,
            'elapsed_time': time.time() - self.start_time if self.start_time else 0,
            'context_size': len(self.transcript_history),
            'current_context': self._get_context()
        }
        
    def __del__(self):
        """Cleanup."""
        self.stop()
        if hasattr(self, 'audio_interface'):
            self.audio_interface.terminate()


def main():
    """Test the voice transcriber."""
    print("=" * 60)
    print("Voice Transcription Test")
    print("=" * 60)
    
    def on_new_transcript(new_chunk: str, full_context: str):
        """Callback for new transcripts."""
        print("\n" + "=" * 60)
        print("📨 NEW TRANSCRIPT READY FOR GEMINI API")
        print("=" * 60)
        print(f"New chunk: {new_chunk}")
        print(f"\nFull context (30s): {full_context}")
        print("=" * 60 + "\n")
        
    # Create transcriber
    transcriber = VoiceTranscriber(on_transcript=on_new_transcript)
    
    try:
        # Start transcription
        transcriber.start()
        
        # Record for 60 seconds (will process 4 chunks)
        print("\n🎤 Speak now! Recording for 60 seconds...")
        print("   (This will process 4x 15-second chunks)\n")
        time.sleep(60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    finally:
        transcriber.stop()
        
        # Show final stats
        stats = transcriber.get_stats()
        print("\n" + "=" * 60)
        print("📊 Final Statistics")
        print("=" * 60)
        print(f"Chunks processed: {stats['chunks_processed']}")
        print(f"Total time: {stats['elapsed_time']:.1f}s")
        print(f"Context buffer size: {stats['context_size']}")
        print("=" * 60)


if __name__ == "__main__":
    main()

