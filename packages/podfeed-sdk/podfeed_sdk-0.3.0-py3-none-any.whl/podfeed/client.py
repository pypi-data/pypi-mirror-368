"""Podfeed API Client."""

import os
import time
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from pydantic import ValidationError

from .exceptions import PodfeedError, PodfeedAuthError, PodfeedAPIError
from .types import (
    AudioGenerationRequest,
    InputContent,
    VoiceConfig,
    ContentConfig,
    TaskProgress,
    AudioDetails,
)


class PodfeedClient:
    """
    A minimal client for the Podfeed API.

    This client provides methods to interact with the Podfeed API for generating
    audio content from various input sources.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.podfeed.ai",
    ):
        """
        Initialize the Podfeed client.

        Args:
            api_key: API key for authentication. If not provided, will look for PODFEED_API_KEY env var.
            base_url: Base URL for the API. Defaults to the TST environment.
        """
        self.api_key = api_key or os.getenv("PODFEED_API_KEY")
        if not self.api_key:
            raise PodfeedAuthError(
                "API key is required. Provide it directly or set PODFEED_API_KEY environment variable."
            )

        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {"x-api-key": self.api_key, "User-Agent": "Podfeed-SDK/0.1.0"}
        )

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make a request to the API.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for the request

        Returns:
            Response data as dictionary

        Raises:
            PodfeedAPIError: If the API returns an error response
        """
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.request(method, url, **kwargs)

            if response.status_code == 401:
                raise PodfeedAuthError("Invalid API key or authentication failed")

            if not response.ok:
                error_data = response.json() if response.content else {}
                error_message = error_data.get("error", f"HTTP {response.status_code}")
                error_code = error_data.get("error_code")
                raise PodfeedAPIError(error_message, response.status_code, error_code)

            return response.json()

        except requests.exceptions.RequestException as e:
            raise PodfeedError(f"Request failed: {str(e)}")

    def generate_audio(self, request: AudioGenerationRequest) -> Dict[str, Any]:
        """
        Generate audio content using structured request model.

        This method provides a type-safe way to generate audio content with
        automatic validation and file upload handling.

        Args:
            request: AudioGenerationRequest containing all generation parameters

        Returns:
            Dictionary containing task_id and status information

        Raises:
            PodfeedError: If validation fails or request processing encounters an error
            ValidationError: If the request model validation fails

        Example:
            >>> from podfeed import PodfeedClient, AudioGenerationRequest, InputContent, VoiceConfig
            >>> client = PodfeedClient(api_key="your-key")
            >>>
            >>> # For text input
            >>> request = AudioGenerationRequest(
            ...     input_type="text",
            ...     mode="monologue",
            ...     input_content=InputContent(text="Your text content here"),
            ...     voice_config=VoiceConfig(voice="google-male-puck")
            ... )
            >>> result = client.generate_audio(request)
            >>>
            >>> # For file input
            >>> request = AudioGenerationRequest(
            ...     input_type="file",
            ...     mode="dialogue",
            ...     input_content=InputContent(files=["document.pdf", "recording.mp3"]),
            ...     voice_config=VoiceConfig(
            ...         host_voice="gemini-achird",
            ...         cohost_voice="gemini-achernar"
            ...     ),
            ...     progress_callback=lambda current, total: print(f"Uploaded {current}/{total}")
            ... )
            >>> result = client.generate_audio(request)
        """
        try:
            # Validate the request
            request.model_dump()  # This will trigger Pydantic validation
        except ValidationError as e:
            raise PodfeedError(f"Request validation failed: {str(e)}")

        # Handle file uploads if needed
        gcs_uris = None
        if request.input_type == "file" and request.input_content.files:
            # Check if files are file paths (str) that need uploading
            file_paths = [f for f in request.input_content.files if isinstance(f, str)]
            if file_paths:
                gcs_uris = self.upload_files(
                    file_paths=file_paths,
                    progress_callback=request.progress_callback,
                    max_workers=request.max_workers,
                    max_retries=request.max_retries,
                )

        # Build API request payload
        data = {
            "inputType": request.input_type,
            "mode": request.mode,
            "language": request.content_config.language,
            "level": request.content_config.level,
            "length": request.content_config.length,
        }

        # Add voice configuration
        if request.voice_config.voice:
            data["voice"] = request.voice_config.voice
        if request.voice_config.host_voice:
            data["hostVoice"] = request.voice_config.host_voice
        if request.voice_config.cohost_voice:
            data["coHostVoice"] = request.voice_config.cohost_voice
        if request.voice_config.voice_instructions:
            data["voiceInstructions"] = request.voice_config.voice_instructions
        if request.voice_config.host_voice_instructions:
            data["hostVoiceInstructions"] = request.voice_config.host_voice_instructions
        if request.voice_config.cohost_voice_instructions:
            data["cohostVoiceInstructions"] = (
                request.voice_config.cohost_voice_instructions
            )

        # Add content configuration
        if request.content_config.emphasis:
            data["emphasis"] = request.content_config.emphasis
        if request.content_config.questions:
            data["questions"] = request.content_config.questions
        if request.content_config.user_instructions:
            data["userInstructions"] = request.content_config.user_instructions
        if request.content_config.read_mode:
            data["readMode"] = request.content_config.read_mode

        # Add input content based on type
        if request.input_type == "text" and request.input_content.text:
            data["textContent"] = request.input_content.text
        elif request.input_type == "url" and request.input_content.url:
            data["websiteUrl"] = request.input_content.url
        elif request.input_type == "topic" and request.input_content.topic:
            data["topic"] = request.input_content.topic
        elif request.input_type == "script" and request.input_content.script:
            data["scriptContent"] = request.input_content.script
        elif request.input_type == "file":
            if gcs_uris:
                data["gcsUris"] = gcs_uris
            elif request.input_content.files:
                # Handle pre-uploaded GCS URIs (strings starting with gs://)
                gcs_uri_strings = [
                    f
                    for f in request.input_content.files
                    if isinstance(f, str) and f.startswith("gs://")
                ]
                if gcs_uri_strings:
                    data["gcsUris"] = gcs_uri_strings
                else:
                    raise PodfeedError(
                        "No valid files or GCS URIs found for file input type"
                    )

        return self._request("POST", "/api/audios", json=data)

    def get_task_progress(self, task_id: str) -> Dict[str, Any]:
        """
        Check the progress of an audio generation task.

        Args:
            task_id: The unique identifier of the task

        Returns:
            Dictionary containing task status and progress information
        """
        return self._request("GET", f"/api/audios/tasks/{task_id}")

    def get_audio_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of an audio generation task.

        Args:
            task_id: The task ID returned from generate_audio

        Returns:
            Dictionary containing task status information
        """
        return self._request("GET", f"/api/audios/requests?task_id={task_id}")

    def list_audios(
        self, limit: int = 20, offset: int = 0, status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List generated audio files.

        Args:
            limit: Maximum number of audios to return (1-100)
            offset: Number of audios to skip
            status: Filter by status ('processing', 'completed', 'failed')

        Returns:
            Dictionary containing list of audio files and pagination info
        """
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status

        return self._request("GET", "/api/audios", params=params)

    def get_audio(self, audio_id: str) -> Dict[str, Any]:
        """
        Get details for a specific audio file.

        Args:
            audio_id: The unique identifier of the audio

        Returns:
            Dictionary containing audio details and download link
        """
        return self._request("GET", f"/api/audios/{audio_id}")

    def delete_audio(self, audio_id: str) -> Dict[str, Any]:
        """
        Delete an audio file.

        Args:
            audio_id: The unique identifier of the audio to delete

        Returns:
            Dictionary containing success confirmation
        """
        return self._request("DELETE", f"/api/audios/{audio_id}")

    def get_upload_urls(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get signed URLs for uploading large files.

        Args:
            files: List of file info dictionaries with 'filename', 'contentType', and 'size'

        Returns:
            Dictionary containing signed URLs and GCS URIs
        """
        return self._request("POST", "/api/audios/upload-urls", json={"files": files})

    def create_share_link(self, audio_id: str) -> Dict[str, Any]:
        """
        Create a shareable link for an audio file.

        Args:
            audio_id: The ID of the audio to share

        Returns:
            Dictionary containing shareable URL and expiration info
        """
        return self._request("POST", "/api/audios/share", json={"audio_id": audio_id})

    def list_available_voices(self) -> Dict[str, Any]:
        """
        Retrieve all available voices organized by language code.

        This method returns the complete voice configuration including voice names,
        TTS providers, credits multipliers, and language support. The response is
        structured by language codes (e.g., 'en', 'es', 'fr') and includes detailed
        information about each voice.

        Returns:
            Dictionary containing voice configuration organized by language:
            {
                "en": {
                    "language_name": "English",
                    "voices": {
                        "google-neural-en-US-Neural2-A": {
                            "tts": "google",
                            "credits_multiplier": 1.0,
                            "display_name": "Google Neural2 A (English)",
                            "gender": "female"
                        },
                        "elevenlabs-rachel": {
                            "tts": "elevenlabs",
                            "credits_multiplier": 3.0,
                            "display_name": "Rachel (ElevenLabs)",
                            "gender": "female"
                        }
                    }
                },
                "es": {
                    "language_name": "Spanish",
                    "voices": { ... }
                }
            }

        Raises:
            PodfeedAuthError: If authentication fails
            PodfeedAPIError: If the API returns an error response
            PodfeedError: If the request fails
        """
        return self._request("GET", "/api/voices")

    def upload_files(
        self,
        file_paths: List[str],
        progress_callback: Optional[Callable[[int, int], None]] = None,
        max_workers: int = 3,
        max_retries: int = 3,
    ) -> List[str]:
        """
        Upload multiple files to GCS and return their URIs.

        Args:
            file_paths: List of local file paths to upload
            progress_callback: Optional callback function called with (current, total) for upload progress
            max_workers: Maximum number of concurrent uploads (default: 3)
            max_retries: Maximum number of retry attempts per file (default: 3)

        Returns:
            List of GCS URIs for the uploaded files

        Raises:
            PodfeedError: If file validation or upload fails
        """
        if not file_paths:
            return []

        # Validate all files first
        validated_files = []
        for file_path in file_paths:
            validated_files.append(self._validate_file(file_path))

        # Get signed URLs for all files
        files_metadata = [file_data for _, file_data in validated_files]
        upload_response = self.get_upload_urls(files_metadata)
        urls_data = upload_response.get("urls", [])

        if len(urls_data) != len(validated_files):
            raise PodfeedError(
                f"Mismatch between requested files ({len(validated_files)}) and received URLs ({len(urls_data)})"
            )

        # Upload files concurrently
        gcs_uris = []
        completed_uploads = 0

        def upload_single_file(file_info, url_data):
            """Upload a single file with retry logic."""
            file_path, file_data = file_info
            signed_url = url_data["signedUrl"]
            gcs_uri = url_data["gcsUri"]

            for attempt in range(max_retries):
                try:
                    self._upload_to_signed_url(
                        file_path, signed_url, file_data["contentType"]
                    )
                    return gcs_uri
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise PodfeedError(
                            f"Failed to upload {file_path} after {max_retries} attempts: {str(e)}"
                        )
                    time.sleep(2**attempt)  # Exponential backoff

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all upload tasks
            future_to_file = {
                executor.submit(upload_single_file, file_info, url_data): (
                    file_info[0],
                    url_data["gcsUri"],
                )
                for file_info, url_data in zip(validated_files, urls_data)
            }

            # Process completed uploads
            for future in as_completed(future_to_file):
                file_path, expected_uri = future_to_file[future]
                try:
                    gcs_uri = future.result()
                    gcs_uris.append(gcs_uri)
                    completed_uploads += 1

                    if progress_callback:
                        progress_callback(completed_uploads, len(validated_files))

                except Exception as e:
                    raise PodfeedError(f"Upload failed for {file_path}: {str(e)}")

        return gcs_uris

    def _validate_file(self, file_path: str) -> tuple[str, Dict[str, Any]]:
        """
        Validate a file and return file info.

        Args:
            file_path: Path to the file to validate

        Returns:
            Tuple of (file_path, file_metadata)

        Raises:
            PodfeedError: If file validation fails
        """
        path = Path(file_path)

        if not path.exists():
            raise PodfeedError(f"File not found: {file_path}")

        if not path.is_file():
            raise PodfeedError(f"Path is not a file: {file_path}")

        # Get file info
        file_size = path.stat().st_size

        # Check file size (500MB limit as per backend)
        max_size_bytes = 500 * 1024 * 1024  # 500MB
        if file_size > max_size_bytes:
            raise PodfeedError(
                f"File {file_path} is too large ({file_size / (1024*1024):.1f}MB). Maximum size is 500MB."
            )

        # Determine content type
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            # Default content type for unknown files
            content_type = "application/octet-stream"

        file_data = {
            "filename": path.name,
            "contentType": content_type,
            "size": file_size,
        }

        return file_path, file_data

    def _upload_to_signed_url(
        self, file_path: str, signed_url: str, content_type: str
    ) -> None:
        """
        Upload a file to a GCS signed URL.

        Args:
            file_path: Local path to the file
            signed_url: GCS signed URL for upload
            content_type: MIME content type of the file

        Raises:
            PodfeedError: If upload fails
        """
        try:
            with open(file_path, "rb") as file:
                headers = {
                    "Content-Type": content_type,
                }

                response = requests.put(
                    signed_url,
                    data=file,
                    headers=headers,
                    timeout=300,  # 5 minute timeout for large files
                )

                if not response.ok:
                    raise PodfeedError(
                        f"Upload failed with status {response.status_code}: {response.text}"
                    )

        except requests.exceptions.RequestException as e:
            raise PodfeedError(f"Network error during upload: {str(e)}")
        except IOError as e:
            raise PodfeedError(f"File I/O error: {str(e)}")

    def wait_for_completion(
        self, task_id: str, timeout: int = 3600, poll_interval: int = 30
    ) -> Dict[str, Any]:
        """
        Wait for an audio generation task to complete.

        Args:
            task_id: The task ID to monitor
            timeout: Maximum time to wait in seconds (default: 30 minutes)
            poll_interval: Time between status checks in seconds (default: 5)

        Returns:
            Dictionary containing the final task status

        Raises:
            PodfeedError: If task fails or times out
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            time.sleep(poll_interval)

            status = self.get_task_progress(task_id)

            if status["status"] == "completed":
                return status
            elif status["status"] == "failed":
                error_msg = status.get("error", "Task failed")
                raise PodfeedError(f"Audio generation failed: {error_msg}")

        raise PodfeedError(f"Task timed out after {timeout} seconds")
