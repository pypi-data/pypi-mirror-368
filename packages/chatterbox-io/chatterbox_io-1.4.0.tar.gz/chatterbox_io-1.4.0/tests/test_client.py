import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from chatterbox_io import (
    ChatterBox, 
    Session, 
    ChatterBoxAPIError,
    ChatterBoxBadRequestError,
    ChatterBoxUnauthorizedError,
    ChatterBoxForbiddenError,
    ChatterBoxNotFoundError,
    ChatterBoxServerError
)
from chatterbox_io.models import SendBotRequest, TemporaryToken


@pytest.fixture
def client():
    return ChatterBox(authorization_token="test_token")


@pytest.fixture
def mock_session():
    return Session(
        id="test_session_id",
        platform="zoom",
        meeting_id="1234567890",
        bot_name="TestBot"
    )


@pytest.mark.asyncio
async def test_send_bot(client, mock_session):
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = mock_session.model_dump(by_alias=True)
    mock_response.__aenter__.return_value = mock_response

    mock_session_instance = AsyncMock()
    mock_session_instance.post.return_value = mock_response

    with patch("aiohttp.ClientSession", return_value=mock_session_instance):
        result = await client.send_bot(
            platform="zoom",
            meeting_id="1234567890",
            bot_name="TestBot"
        )
        
        assert isinstance(result, Session)
        assert result.id == mock_session.id
        assert result.platform == mock_session.platform
        assert result.meeting_id == mock_session.meeting_id
        assert result.bot_name == mock_session.bot_name
        
        # Verify request URL and required fields; allow additional defaults (e.g., language/model)
        assert mock_session_instance.post.call_count == 1
        args, kwargs = mock_session_instance.post.call_args
        assert args[0] == "https://bot.chatter-box.io/join"
        body = kwargs.get("json", {})
        assert body.get("platform") == "zoom"
        assert body.get("meetingId") == "1234567890"
        assert body.get("botName") == "TestBot"


@pytest.mark.asyncio
async def test_send_bot_with_no_transcript_timeout(client, mock_session):
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = mock_session.model_dump(by_alias=True)
    mock_response.__aenter__.return_value = mock_response

    mock_session_instance = AsyncMock()
    mock_session_instance.post.return_value = mock_response

    with patch("aiohttp.ClientSession", return_value=mock_session_instance):
        result = await client.send_bot(
            platform="zoom",
            meeting_id="1234567890",
            bot_name="TestBot",
            no_transcript_timeout_seconds=180
        )

        assert isinstance(result, Session)

        # Verify request URL and required fields including timeout; allow additional defaults
        assert mock_session_instance.post.call_count == 1
        args, kwargs = mock_session_instance.post.call_args
        assert args[0] == "https://bot.chatter-box.io/join"
        body = kwargs.get("json", {})
        assert body.get("platform") == "zoom"
        assert body.get("meetingId") == "1234567890"
        assert body.get("botName") == "TestBot"
        assert body.get("noTranscriptTimeoutSeconds") == 180


@pytest.mark.asyncio
async def test_connect_socket(client):
    socket = client.connect_socket("test_session_id")
    assert socket.session_id == "test_session_id"
    assert socket.base_url == "wss://ws.chatter-box.io"


@pytest.mark.asyncio
async def test_close(client):
    mock_session_instance = AsyncMock()
    
    with patch("aiohttp.ClientSession", return_value=mock_session_instance):
        client._session = mock_session_instance
        await client.close()
        
        # Use await to properly check the async mock
        await mock_session_instance.close.aclose()


@pytest.mark.asyncio
async def test_get_temporary_token(client):
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {
        "token": "test_token",
        "expiresIn": 3600
    }
    mock_response.__aenter__.return_value = mock_response

    mock_session_instance = AsyncMock()
    mock_session_instance.post.return_value = mock_response

    with patch("aiohttp.ClientSession", return_value=mock_session_instance):
        result = await client.get_temporary_token(expires_in=3600)
        
        assert isinstance(result, TemporaryToken)
        assert result.token == "test_token"
        assert result.expires_in == 3600
        
        mock_session_instance.post.assert_called_once_with(
            "https://bot.chatter-box.io/token",
            json={"expiresIn": 3600}
        )


@pytest.mark.asyncio
async def test_get_temporary_token_invalid_expiration(client):
    with pytest.raises(ValueError, match="expires_in must be between 60 and 86400 seconds"):
        await client.get_temporary_token(expires_in=30)


@pytest.mark.asyncio
async def test_send_bot_bad_request_error(client):
    """Test handling of 400 Bad Request with server error message."""
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_response.json.return_value = {
        "message": "Invalid meeting ID format",
        "error": "INVALID_MEETING_ID"
    }

    mock_session_instance = AsyncMock()
    mock_session_instance.post.return_value = mock_response

    with patch("aiohttp.ClientSession", return_value=mock_session_instance):
        with pytest.raises(ChatterBoxBadRequestError) as exc_info:
            await client.send_bot(
                platform="zoom",
                meeting_id="invalid_id"
            )
        
        assert exc_info.value.message == "Invalid meeting ID format"
        assert exc_info.value.status_code == 400
        assert exc_info.value.response_data == {
            "message": "Invalid meeting ID format",
            "error": "INVALID_MEETING_ID"
        }


@pytest.mark.asyncio
async def test_send_bot_unauthorized_error(client):
    """Test handling of 401 Unauthorized error."""
    mock_response = AsyncMock()
    mock_response.status = 401
    mock_response.json.return_value = {
        "message": "Invalid or expired authorization token"
    }

    mock_session_instance = AsyncMock()
    mock_session_instance.post.return_value = mock_response

    with patch("aiohttp.ClientSession", return_value=mock_session_instance):
        with pytest.raises(ChatterBoxUnauthorizedError) as exc_info:
            await client.send_bot(platform="zoom", meeting_id="123")
        
        assert exc_info.value.message == "Invalid or expired authorization token"
        assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_send_bot_server_error(client):
    """Test handling of 500 server error."""
    mock_response = AsyncMock()
    mock_response.status = 500
    mock_response.json.return_value = {
        "message": "Internal server error occurred"
    }

    mock_session_instance = AsyncMock()
    mock_session_instance.post.return_value = mock_response

    with patch("aiohttp.ClientSession", return_value=mock_session_instance):
        with pytest.raises(ChatterBoxServerError) as exc_info:
            await client.send_bot(platform="zoom", meeting_id="123")
        
        assert exc_info.value.message == "Internal server error occurred"
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_send_bot_error_with_text_response(client):
    """Test handling of error when response is not JSON."""
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_response.json.side_effect = Exception("Not JSON")
    mock_response.text.return_value = "Bad Request: Invalid parameter"

    mock_session_instance = AsyncMock()
    mock_session_instance.post.return_value = mock_response

    with patch("aiohttp.ClientSession", return_value=mock_session_instance):
        with pytest.raises(ChatterBoxBadRequestError) as exc_info:
            await client.send_bot(platform="zoom", meeting_id="123")
        
        assert exc_info.value.message == "Bad Request: Invalid parameter"
        assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_get_temporary_token_forbidden_error(client):
    """Test handling of 403 Forbidden error."""
    mock_response = AsyncMock()
    mock_response.status = 403
    mock_response.json.return_value = {
        "message": "Token generation not allowed for this account"
    }

    mock_session_instance = AsyncMock()
    mock_session_instance.post.return_value = mock_response

    with patch("aiohttp.ClientSession", return_value=mock_session_instance):
        with pytest.raises(ChatterBoxForbiddenError) as exc_info:
            await client.get_temporary_token()
        
        assert exc_info.value.message == "Token generation not allowed for this account"
        assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_error_handling_no_response_body(client):
    """Test error handling when response body is empty."""
    mock_response = AsyncMock()
    mock_response.status = 404
    mock_response.json.side_effect = Exception("No JSON")
    mock_response.text.return_value = ""

    mock_session_instance = AsyncMock()
    mock_session_instance.post.return_value = mock_response

    with patch("aiohttp.ClientSession", return_value=mock_session_instance):
        with pytest.raises(ChatterBoxNotFoundError) as exc_info:
            await client.send_bot(platform="zoom", meeting_id="123")
        
        assert exc_info.value.message == "HTTP 404"
        assert exc_info.value.status_code == 404 