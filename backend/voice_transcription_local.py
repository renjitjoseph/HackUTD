"""
Real-time voice transcription system using LOCAL Whisper (FREE, no API costs).
Runs entirely on your Mac - no internet required after initial model download.
"""

import pyaudio
import wave
import threading
import time
from datetime import datetime
from collections import deque
from typing import Optional, Callable
import numpy as np
import whisper
import tempfile
import os


class LocalVoiceTranscriber:
    """
    Handles real-time audio capture and transcription using local Whisper model.
    100% FREE - runs entirely on your Mac!
    """
    
    # Audio configuration
    CHUNK_SIZE = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000  # 16kHz is optimal for Whisper
    
    # Time windows
    CHUNK_DURATION = 10  # seconds - send new transcript every 10s
    CONTEXT_DURATION = None  # Keep ALL conversation history (unlimited)
    
    def __init__(self, on_transcript: Optional[Callable] = None, model_size: str = "base"):
        """
        Initialize the voice transcriber with local Whisper.
        
        Args:
            on_transcript: Callback function called when new transcript is ready.
                          Receives (new_chunk: str, full_context: str)
            model_size: Whisper model size. Options:
                       - "tiny": Fastest, least accurate (~1GB RAM)
                       - "base": Good balance (default, ~1GB RAM)  
                       - "small": Better accuracy (~2GB RAM)
                       - "medium": Very good (~5GB RAM)
                       - "large": Best accuracy (~10GB RAM)
        """
        self.on_transcript = on_transcript
        self.model_size = model_size
        
        # Load Whisper model (downloads first time only, then cached)
        print(f"🔄 Loading Whisper '{model_size}' model (first time downloads ~{self._get_model_size(model_size)})...")
        self.whisper_model = whisper.load_model(model_size)
        print("✅ Whisper model loaded!")
        
        self.audio_interface = pyaudio.PyAudio()
        
        # Buffers
        self.audio_buffer = []  # Current 15s chunk
        self.transcript_history = deque()  # All conversation history (no limit)
        
        # Control flags
        self.is_recording = False
        self.stream = None
        self.recording_thread = None
        
        # Stats
        self.chunks_processed = 0
        self.start_time = None
        
    def _get_model_size(self, model: str) -> str:
        """Get approximate model download size."""
        sizes = {
            "tiny": "75MB",
            "base": "140MB", 
            "small": "460MB",
            "medium": "1.5GB",
            "large": "3GB"
        }
        return sizes.get(model, "unknown")
        
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
        print(f"\n🎤 Voice transcription started!")
        print(f"   - Model: Whisper '{self.model_size}' (running locally)")
        print(f"   - Chunk duration: {self.CHUNK_DURATION}s")
        print(f"   - Context window: FULL CONVERSATION (unlimited)")
        print(f"   - Sample rate: {self.RATE}Hz")
        print(f"   - 100% FREE, no API costs!\n")
        
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
                
                # Get full context (entire conversation)
                full_context = self._get_context()
                
                # Log
                elapsed = time.time() - self.start_time
                print(f"\n{'='*60}")
                print(f"[{elapsed:.1f}s] Chunk #{self.chunks_processed}")
                print(f"{'='*60}")
                print(f"📝 New transcript: {transcript}")
                print(f"📋 Full conversation context ({len(self.transcript_history)} chunks total):")
                print(f"   ...{full_context[-200:]}" if len(full_context) > 200 else f"   {full_context}")
                print('='*60 + '\n')
                
                # Call callback if provided
                if self.on_transcript:
                    try:
                        self.on_transcript(transcript, full_context)
                    except Exception as e:
                        print(f"❌ Error in transcript callback: {e}")
                        
    def _transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """
        Transcribe audio data to text using local Whisper model.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Transcribed text or None if transcription failed
        """
        try:
            # Convert bytes to numpy array
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Whisper expects audio at 16kHz (which we're already using)
            print("🔄 Transcribing with Whisper (local)...", end=" ")
            start = time.time()
            
            # Transcribe using Whisper
            result = self.whisper_model.transcribe(
                audio_np,
                language="en",  # Set to English for sales calls
                fp16=False  # Use FP32 for better Mac compatibility
            )
            
            elapsed = time.time() - start
            text = result["text"].strip()
            
            if text:
                print(f"✅ ({elapsed:.1f}s)")
                return text
            else:
                print("⚠️  No speech detected")
                return None
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
            
    def _get_context(self) -> str:
        """
        Get the full context (entire conversation history).
        
        Returns:
            Combined transcript text from ALL chunks
        """
        return " ".join([chunk['text'] for chunk in self.transcript_history])
        
    def get_stats(self) -> dict:
        """Get transcription statistics."""
        return {
            'is_recording': self.is_recording,
            'chunks_processed': self.chunks_processed,
            'elapsed_time': time.time() - self.start_time if self.start_time else 0,
            'context_size': len(self.transcript_history),
            'current_context': self._get_context(),
            'model': self.model_size
        }
        
    def __del__(self):
        """Cleanup."""
        self.stop()
        if hasattr(self, 'audio_interface'):
            self.audio_interface.terminate()


def main():
    """Test the local voice transcriber."""
    print("=" * 60)
    print("Local Voice Transcription Test (FREE, runs on your Mac!)")
    print("=" * 60)
    
    def on_new_transcript(new_chunk: str, full_context: str):
        """Callback for new transcripts - ready to send to Gemini API."""
        print("\n" + "🔥" * 30)
        print("📨 NEW TRANSCRIPT READY FOR GEMINI API")
        print("🔥" * 30)
        print(f"\n📌 Latest 15s chunk:\n{new_chunk}")
        print(f"\n📌 Full 30s context:\n{full_context}")
        print("\n" + "🔥" * 30 + "\n")
        
    # Create transcriber with 'base' model (good balance of speed/accuracy)
    # You can change to 'tiny' for faster, or 'small'/'medium' for more accuracy
    transcriber = LocalVoiceTranscriber(
        on_transcript=on_new_transcript,
        model_size="base"  # Change to "tiny" for faster processing
    )
    
    try:
        # Start transcription
        transcriber.start()
        
        # Record for 60 seconds (will process 4 chunks)
        print("🎤 Speak now! Recording for 60 seconds...")
        print("   (This will process 4x 15-second chunks)")
        print("   Press Ctrl+C to stop early\n")
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
        print(f"Model: Whisper '{stats['model']}'")
        print(f"Chunks processed: {stats['chunks_processed']}")
        print(f"Total time: {stats['elapsed_time']:.1f}s")
        print(f"Context buffer size: {stats['context_size']}")
        print("=" * 60)


if __name__ == "__main__":
    main()

