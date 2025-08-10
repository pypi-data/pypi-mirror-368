"""Audio recorder using sounddevice."""

import threading
import queue
import wave
import numpy as np
from pathlib import Path
from typing import Optional

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False


class AudioRecorder:
    """Audio recorder for capturing microphone input to WAV file."""
    
    # Target audio format for Groq Whisper
    SAMPLE_RATE = 16000  # 16 kHz
    CHANNELS = 1  # Mono
    DTYPE = 'float32'  # Internal processing format
    
    def __init__(self, config=None):
        if not SOUNDDEVICE_AVAILABLE:
            raise ImportError("sounddevice not available. Install with: pip install sounddevice")
        
        self.config = config or {}
        self.recording = False
        self.stream = None
        self.audio_queue = queue.Queue()
        self.current_file_path = None
        self.recording_thread = None
        
        # Audio buffers
        self.audio_buffers = []
        
        # Get recording timeout
        self.timeout = self.config.get("recording_timeout", 30)
    
    def start_recording(self, file_path: Path):
        """Start recording audio to file."""
        if self.recording:
            raise RuntimeError("Already recording")
        
        self.current_file_path = file_path
        self.audio_buffers = []
        self.recording = True
        
        try:
            # Try to open stream at target sample rate
            self.stream = sd.InputStream(
                samplerate=self.SAMPLE_RATE,
                channels=self.CHANNELS,
                dtype=self.DTYPE,
                callback=self._audio_callback,
                blocksize=2048
            )
            self.stream.start()
            
        except Exception as e:
            # If target sample rate not supported, use default and we'll resample later
            print(f"Could not open stream at 16kHz, using default: {e}")
            
            # Get default sample rate
            device_info = sd.query_devices(sd.default.device, 'input')
            default_samplerate = device_info['default_samplerate']
            
            self.stream = sd.InputStream(
                samplerate=default_samplerate,
                channels=self.CHANNELS,
                dtype=self.DTYPE,
                callback=self._audio_callback,
                blocksize=2048
            )
            self.stream.start()
            
            # We'll need to resample
            self.needs_resampling = True
            self.original_samplerate = default_samplerate
        else:
            self.needs_resampling = False
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream."""
        if status:
            print(f"Audio callback status: {status}")
        
        if self.recording:
            # Copy audio data to buffer
            audio_copy = indata.copy()
            
            # If stereo, mix down to mono
            if audio_copy.shape[1] > 1:
                audio_copy = np.mean(audio_copy, axis=1, keepdims=True)
            
            self.audio_buffers.append(audio_copy)
    
    def stop_recording(self):
        """Stop recording and save to file."""
        if not self.recording:
            return
        
        self.recording = False
        
        # Stop and close stream
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        # Process and save audio
        if self.audio_buffers and self.current_file_path:
            self._save_audio()
    
    def _save_audio(self):
        """Save recorded audio to WAV file."""
        try:
            # Concatenate all buffers
            audio_data = np.concatenate(self.audio_buffers, axis=0)
            
            # Resample if needed
            if hasattr(self, 'needs_resampling') and self.needs_resampling:
                audio_data = self._resample(audio_data, self.original_samplerate, self.SAMPLE_RATE)
            
            # Convert to 16-bit PCM
            audio_data = np.clip(audio_data * 32767, -32768, 32767).astype(np.int16)
            
            # Ensure mono
            if len(audio_data.shape) > 1:
                audio_data = audio_data[:, 0]
            
            # Save to WAV file
            with wave.open(str(self.current_file_path), 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(2)  # 16-bit = 2 bytes
                wf.setframerate(self.SAMPLE_RATE)
                wf.writeframes(audio_data.tobytes())
            
            print(f"Audio saved to {self.current_file_path}")
            
        except Exception as e:
            print(f"Error saving audio: {e}")
            raise
        finally:
            self.audio_buffers = []
            self.current_file_path = None
    
    def _resample(self, audio_data: np.ndarray, orig_sr: float, target_sr: float) -> np.ndarray:
        """Resample audio to target sample rate."""
        try:
            # Try using resampy if available
            import resampy
            return resampy.resample(audio_data[:, 0], orig_sr, target_sr).reshape(-1, 1)
        except ImportError:
            # Fallback to simple linear interpolation
            ratio = target_sr / orig_sr
            new_length = int(len(audio_data) * ratio)
            
            # Simple linear resampling
            old_indices = np.arange(len(audio_data))
            new_indices = np.linspace(0, len(audio_data) - 1, new_length)
            
            if len(audio_data.shape) > 1:
                audio_data = audio_data[:, 0]
            
            resampled = np.interp(new_indices, old_indices, audio_data)
            return resampled.reshape(-1, 1)
    
    def cleanup(self):
        """Clean up resources."""
        if self.recording:
            self.stop_recording()
        
        if self.stream:
            self.stream.close()
            self.stream = None
    
    def get_input_devices(self):
        """Get list of available input devices."""
        devices = []
        for i, device in enumerate(sd.query_devices()):
            if device['max_input_channels'] > 0:
                devices.append({
                    'index': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                })
        return devices
    
    def set_input_device(self, device_index: int):
        """Set the input device for recording."""
        sd.default.device = (device_index, None)