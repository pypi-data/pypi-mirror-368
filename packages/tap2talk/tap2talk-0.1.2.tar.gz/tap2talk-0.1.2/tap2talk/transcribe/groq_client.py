"""Groq API client for audio transcription."""

import asyncio
import time
from pathlib import Path
from typing import Optional

try:
    from groq import AsyncGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class GroqTranscriber:
    """Groq API client for transcribing audio using Whisper."""
    
    def __init__(self, api_key: str, config=None):
        if not GROQ_AVAILABLE:
            raise ImportError("groq not available. Install with: pip install groq")
        
        if not api_key:
            raise ValueError("Groq API key is required")
        
        self.api_key = api_key
        self.config = config or {}
        
        # Initialize async client
        self.client = AsyncGroq(
            api_key=api_key,
            timeout=self.config.get("timeout", 30.0),
            max_retries=self.config.get("max_retries", 3)
        )
        
        # Model configuration
        self.model = self.config.get("model", "whisper-large-v3-turbo")
        self.temperature = 0  # For consistent results
    
    async def transcribe(self, audio_path: Path) -> str:
        """Transcribe audio file to text."""
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Check file size
        file_size = audio_path.stat().st_size
        max_size = 25 * 1024 * 1024  # 25 MB for free tier
        
        if file_size > max_size:
            raise ValueError(f"Audio file too large: {file_size / 1024 / 1024:.1f} MB (max: 25 MB)")
        
        try:
            # Open audio file
            with open(audio_path, 'rb') as audio_file:
                # Create transcription request
                response = await self.client.audio.transcriptions.create(
                    file=audio_file,
                    model=self.model,
                    temperature=self.temperature,
                    response_format="json"
                )
            
            # Extract text from response
            if hasattr(response, 'text'):
                return response.text
            else:
                return str(response)
        
        except asyncio.CancelledError:
            # Handle cancellation
            raise
        
        except Exception as e:
            # Handle specific error types
            error_str = str(e)
            
            if "401" in error_str or "authentication" in error_str.lower():
                raise ValueError("Invalid API key")
            elif "413" in error_str:
                raise ValueError("Audio file too large")
            elif "429" in error_str:
                # Rate limit - implement backoff
                await self._handle_rate_limit()
                # Retry once
                return await self.transcribe(audio_path)
            elif "500" in error_str or "502" in error_str or "503" in error_str:
                # Server error - retry with backoff
                await asyncio.sleep(1)
                raise
            else:
                raise
    
    async def _handle_rate_limit(self):
        """Handle rate limit with exponential backoff."""
        backoff_times = [0.5, 1.0, 2.0]
        for backoff in backoff_times:
            await asyncio.sleep(backoff)
            # Add jitter
            import random
            await asyncio.sleep(random.uniform(0, 0.5))
    
    async def validate_api_key(self) -> bool:
        """Validate API key by checking models endpoint."""
        try:
            # Try to list models
            models = await self.client.models.list()
            return True
        except Exception as e:
            print(f"API key validation failed: {e}")
            return False
    
    def close(self):
        """Close the client."""
        if hasattr(self.client, 'close'):
            self.client.close()


class MockTranscriber:
    """Mock transcriber for testing without API."""
    
    def __init__(self, api_key: str = None, config=None):
        self.config = config or {}
    
    async def transcribe(self, audio_path: Path) -> str:
        """Mock transcription - returns test text."""
        # Simulate processing delay
        await asyncio.sleep(1)
        return "This is a test transcription from the mock transcriber."
    
    async def validate_api_key(self) -> bool:
        """Mock validation - always returns True."""
        return True
    
    def close(self):
        """Mock close."""
        pass