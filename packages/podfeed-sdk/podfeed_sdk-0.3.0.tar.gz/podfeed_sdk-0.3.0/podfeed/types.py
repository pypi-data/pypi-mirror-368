"""Pydantic models for the Podfeed SDK."""

from typing import List, Optional, Union, Literal, Callable
from pydantic import BaseModel, Field, field_validator
from pathlib import Path


class InputContent(BaseModel):
    """
    Input content for audio generation.

    Exactly one of the input fields must be provided based on the input_type.
    """

    files: Optional[List[Union[str, bytes]]] = Field(
        None,
        description="List of file paths (str) or file contents (bytes) for 'file' input type",
    )
    url: Optional[str] = Field(None, description="Website URL for 'url' input type")
    text: Optional[str] = Field(None, description="Text content for 'text' input type")
    topic: Optional[str] = Field(
        None, description="Topic for research-based generation for 'topic' input type"
    )
    script: Optional[str] = Field(
        None, description="Pre-written script content for 'script' input type"
    )

    @field_validator("files")
    def validate_files(cls, v):
        """Validate files input."""
        if v is not None:
            if not isinstance(v, list) or len(v) == 0:
                raise ValueError("files must be a non-empty list")

            for item in v:
                if isinstance(item, str):
                    # Validate file path exists if it's a string
                    if not Path(item).exists():
                        raise ValueError(f"File not found: {item}")
                elif not isinstance(item, bytes):
                    raise ValueError(
                        "files must contain only str (file paths) or bytes (file contents)"
                    )
        return v

    @field_validator("url")
    def validate_url(cls, v):
        """Validate URL format."""
        if v is not None:
            if not v.startswith(("http://", "https://")):
                raise ValueError("url must start with http:// or https://")
        return v

    def count_provided_inputs(self) -> int:
        """Count how many input fields are provided."""
        inputs = [self.files, self.url, self.text, self.topic, self.script]
        return sum(1 for input_val in inputs if input_val is not None)


class VoiceConfig(BaseModel):
    """Voice configuration for audio generation."""

    voice: Optional[str] = Field(None, description="Primary voice for monologue mode")
    host_voice: Optional[str] = Field(None, description="Host voice for dialogue mode")
    cohost_voice: Optional[str] = Field(
        None, description="Co-host voice for dialogue mode"
    )
    voice_instructions: Optional[str] = Field(
        None, description="Custom instructions for voice synthesis"
    )
    host_voice_instructions: Optional[str] = Field(
        None, description="Custom instructions for host voice"
    )
    cohost_voice_instructions: Optional[str] = Field(
        None, description="Custom instructions for co-host voice"
    )

    @field_validator("voice")
    def validate_monologue_voice(cls, v):
        """Ensure voice is provided for monologue mode if specified."""
        return v

    def validate_for_mode(self, mode: str) -> None:
        """Validate voice configuration for the specified mode."""
        if mode == "monologue":
            if not self.voice:
                raise ValueError("voice is required for monologue mode")
        elif mode == "dialogue":
            if not self.host_voice or not self.cohost_voice:
                raise ValueError(
                    "host_voice and cohost_voice are required for dialogue mode"
                )


class ContentConfig(BaseModel):
    """Content configuration for audio generation."""

    level: Literal["beginner", "intermediate", "expert"] = Field(
        "intermediate", description="Content complexity level"
    )
    length: Literal["short", "medium", "long"] = Field(
        "medium", description="Content length preference"
    )
    language: str = Field("en-US", description="Content language code")
    emphasis: Optional[str] = Field(None, description="Content emphasis or focus area")
    questions: Optional[str] = Field(None, description="Include Q&A segments")
    user_instructions: Optional[str] = Field(
        None, description="Custom instructions for content generation"
    )
    read_mode: bool = Field(
        False, description="Direct text reading mode (monologue only)"
    )


class AudioGenerationRequest(BaseModel):
    """Complete audio generation request."""

    input_type: Literal["text", "url", "topic", "script", "file"] = Field(
        description="Type of input content"
    )
    mode: Literal["monologue", "dialogue"] = Field(description="Generation mode")
    input_content: InputContent = Field(description="The content to process")
    voice_config: VoiceConfig = Field(description="Voice configuration")
    content_config: ContentConfig = Field(
        default_factory=ContentConfig, description="Content generation configuration"
    )

    # Upload configuration
    progress_callback: Optional[Callable[[int, int], None]] = Field(
        None, description="Progress callback for file uploads"
    )
    max_workers: int = Field(
        3, ge=1, le=10, description="Maximum concurrent upload workers"
    )
    max_retries: int = Field(
        3, ge=1, le=10, description="Maximum retry attempts per file upload"
    )

    class Config:
        arbitrary_types_allowed = True  # Allow Callable type

    @field_validator("input_content")
    def validate_input_content(cls, v, info):
        """Validate input content matches input type."""
        input_type = info.data.get("input_type")
        if not input_type:
            return v

        provided_count = v.count_provided_inputs()
        if provided_count != 1:
            raise ValueError(
                f"Exactly one input field must be provided, got {provided_count}"
            )

        # Validate correct input is provided for input_type
        input_mapping = {
            "file": v.files,
            "url": v.url,
            "text": v.text,
            "topic": v.topic,
            "script": v.script,
        }

        expected_input = input_mapping.get(input_type)
        if expected_input is None:
            raise ValueError(
                f"input_type '{input_type}' requires corresponding input content"
            )

        return v

    @field_validator("voice_config")
    def validate_voice_config(cls, v, info):
        """Validate voice configuration for the specified mode."""
        mode = info.data.get("mode")
        if mode:
            v.validate_for_mode(mode)
        return v

    @field_validator("content_config")
    def validate_read_mode(cls, v, info):
        """Validate read mode restrictions."""
        if v.read_mode:
            mode = info.data.get("mode")
            if mode != "monologue":
                raise ValueError("read_mode is only available for monologue mode")
        return v


class TaskProgress(BaseModel):
    """Task progress response model."""

    task_id: str
    status: Literal["processing", "completed", "failed", "not_found"]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    error: Optional[str] = None
    result: Optional[dict] = None


class AudioDetails(BaseModel):
    """Audio details response model."""

    audio_id: str
    audio_url: str
    title: Optional[str] = None
    description: Optional[str] = None
    transcript: Optional[str] = None
    created_at: str
    metadata: Optional[dict] = None
    voice_config: Optional[dict] = None
    content_config: Optional[dict] = None
