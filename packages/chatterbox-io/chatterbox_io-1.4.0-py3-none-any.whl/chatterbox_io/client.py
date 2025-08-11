import aiohttp
from typing import Optional
from .models import (
    Session, 
    SendBotRequest, 
    TemporaryToken,
    ChatterBoxAPIError,
    ChatterBoxBadRequestError,
    ChatterBoxUnauthorizedError,
    ChatterBoxForbiddenError,
    ChatterBoxNotFoundError,
    ChatterBoxServerError
)
from .websocket import WebSocketClient


class ChatterBox:
    """Main client for interacting with the ChatterBox API."""

    def __init__(
        self,
        authorization_token: str,
        base_url: str = "https://bot.chatter-box.io",
        websocket_base_url: str = "wss://ws.chatter-box.io",
    ):
        self.authorization_token = authorization_token
        self.base_url = base_url
        self.websocket_base_url = websocket_base_url
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp ClientSession."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.authorization_token}"}
            )
        return self._session

    async def close(self) -> None:
        """Close the client session."""
        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._session = None

    async def _handle_response_error(self, response: aiohttp.ClientResponse) -> None:
        """Handle HTTP error responses and raise appropriate exceptions with server error messages."""
        if response.status < 400:
            return  # No error
            
        # Try to get the error message from the response body
        try:
            error_data = await response.json()
            error_message = error_data.get('message', error_data.get('error', f'HTTP {response.status}'))
        except:
            # If we can't parse JSON, try to get text response
            try:
                error_text = await response.text()
                error_message = error_text if error_text else f'HTTP {response.status}'
            except:
                error_message = f'HTTP {response.status}'
        
        # Raise specific exception based on status code
        if response.status == 400:
            raise ChatterBoxBadRequestError(error_message, response.status, error_data if 'error_data' in locals() else None)
        elif response.status == 401:
            raise ChatterBoxUnauthorizedError(error_message, response.status, error_data if 'error_data' in locals() else None)
        elif response.status == 403:
            raise ChatterBoxForbiddenError(error_message, response.status, error_data if 'error_data' in locals() else None)
        elif response.status == 404:
            raise ChatterBoxNotFoundError(error_message, response.status, error_data if 'error_data' in locals() else None)
        elif response.status >= 500:
            raise ChatterBoxServerError(error_message, response.status, error_data if 'error_data' in locals() else None)
        else:
            raise ChatterBoxAPIError(error_message, response.status, error_data if 'error_data' in locals() else None)

    async def get_temporary_token(self, expires_in: int = 3600) -> TemporaryToken:
        """
        Generate a temporary token for enhanced security.
        
        Args:
            expires_in: The duration in seconds for which the token should be valid.
                       Must be between 60 and 86400 seconds (1 minute to 24 hours).
                       Defaults to 3600 seconds (1 hour).
            
        Returns:
            TemporaryToken: Contains the temporary token and its expiration time
            
        Raises:
            ValueError: If expires_in is not between 60 and 86400 seconds
        """
        if not 60 <= expires_in <= 86400:
            raise ValueError("expires_in must be between 60 and 86400 seconds")
            
        session = await self._get_session()
        response = await session.post(
            f"{self.base_url}/token",
            json={"expiresIn": expires_in}
        )
        await self._handle_response_error(response)
        data = await response.json()
        return TemporaryToken(**data)

    async def send_bot(self, **kwargs) -> Session:
        """
        Send a bot to a meeting.
        
        Args:
            platform: The platform to send the bot to ('zoom', 'googlemeet', 'teams')
            meeting_id: The ID of the meeting
            meeting_password: (Optional) The meeting password or passcode
            bot_name: (Optional) Custom name for the bot
            webhook_url: (Optional) Webhook URL for meeting events
            language: (Optional) The language for transcription. Defaults to 'multi'
            model: (Optional) The Deepgram model to use for transcription. Defaults to 'nova-3'
            custom_image: (Optional) Base64-encoded image data for the bot's profile picture.
                         Must start with 'data:image/[type];base64,'. Supported types: png, jpg, jpeg, gif, bmp, webp, tiff.
                         For best results, use 4:3 aspect ratio images like 640×480 pixels, 1024×768, or 1400×1050
            
        Returns:
            Session: The created session
        """
        # Create the request with proper field mapping
        request = SendBotRequest(**kwargs)
        
        session = await self._get_session()
        
        # Convert to camelCase for API call
        request_data = request.model_dump(by_alias=True, exclude_none=True)
        
        response = await session.post(
            f"{self.base_url}/join",
            json=request_data
        )
        await self._handle_response_error(response)
        data = await response.json()
        
        # Add the request data to the response for context
        data.update({
            'platform': kwargs.get('platform'),
            'meetingId': kwargs.get('meeting_id'),
            'meetingPassword': kwargs.get('meeting_password'),
            'botName': kwargs.get('bot_name'),
            'webhookUrl': kwargs.get('webhook_url'),
            'customImage': kwargs.get('custom_image')
        })
            
        return Session(**data)

    def connect_socket(self, session_id: str) -> WebSocketClient:
        """
        Create a WebSocket connection for real-time events.
        
        Args:
            session_id: The ID of the session to connect to
            
        Returns:
            WebSocketClient: The WebSocket client instance
        """
        return WebSocketClient(session_id, self.authorization_token, self.websocket_base_url)