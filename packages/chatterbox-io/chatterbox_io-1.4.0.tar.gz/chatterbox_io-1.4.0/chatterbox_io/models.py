from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ChatterBoxAPIError(Exception):
    """Base exception class for ChatterBox API errors."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class ChatterBoxBadRequestError(ChatterBoxAPIError):
    """Exception raised for 400 Bad Request errors."""
    pass


class ChatterBoxUnauthorizedError(ChatterBoxAPIError):
    """Exception raised for 401 Unauthorized errors."""
    pass


class ChatterBoxForbiddenError(ChatterBoxAPIError):
    """Exception raised for 403 Forbidden errors."""
    pass


class ChatterBoxNotFoundError(ChatterBoxAPIError):
    """Exception raised for 404 Not Found errors."""
    pass


class ChatterBoxServerError(ChatterBoxAPIError):
    """Exception raised for 5xx server errors."""
    pass


class Session(BaseModel):
    """Represents a ChatterBox session."""
    id: str = Field(alias="sessionId")
    platform: Optional[str] = None
    meeting_id: Optional[str] = Field(None, alias="meetingId")
    meeting_password: Optional[str] = Field(None, alias="meetingPassword")
    bot_name: Optional[str] = Field(None, alias="botName")
    webhook_url: Optional[str] = Field(None, alias="webhookUrl")

    model_config = ConfigDict(populate_by_name=True)


class SendBotRequest(BaseModel):
    """Request model for sending a bot to a meeting."""
    platform: str = Field(..., description="The platform to send the bot to ('zoom', 'googlemeet', 'teams')")
    meeting_id: str = Field(..., description="The ID of the meeting", alias="meetingId")
    meeting_password: Optional[str] = Field(None, description="The meeting password", alias="meetingPassword")
    bot_name: Optional[str] = Field("ChatterBox", description="Custom name for the bot", alias="botName")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for meeting events", alias="webhookUrl")
    language: Optional[str] = Field("multi", description="The language for transcription", alias="language")
    model: Optional[str] = Field("nova-3", description="The Deepgram model to use for transcription", alias="model")
    custom_image: Optional[str] = Field(None, description="Base64-encoded image data for the bot's profile picture. Must start with 'data:image/[type];base64,'. Supported types: png, jpg, jpeg, gif, bmp, webp, tiff", alias="customImage")
    no_transcript_timeout_seconds: Optional[int] = Field(
        None,
        description="If set, the bot will leave the session after this many seconds without receiving any transcripts.",
        alias="noTranscriptTimeoutSeconds",
    )

    model_config = ConfigDict(populate_by_name=True)


class WebSocketEvent(BaseModel):
    """Base model for WebSocket events."""
    type: str
    data: dict


class MeetingStartedEvent(WebSocketEvent):
    """Event triggered when a meeting starts."""
    type: str = "meeting_started"


class MeetingFinishedEvent(WebSocketEvent):
    """Event triggered when a meeting ends."""
    type: str = "meeting_finished"


class TranscriptEvent(WebSocketEvent):
    """Event triggered when a transcript update is received."""
    type: str = "transcript_received"
    data: dict = Field(..., description="Contains 'speaker' and 'text' fields")


class TemporaryToken(BaseModel):
    """Response model for temporary token generation."""
    token: str = Field(..., description="The generated temporary JWT token")
    expires_in: int = Field(..., alias="expiresIn", description="The duration in seconds for which the token is valid")

    model_config = ConfigDict(populate_by_name=True) 