# ChatterBox Python Client

The **ChatterBox Python Client** is an easy-to-use Python package that allows you to integrate your applications with popular video conferencing platforms. With this package, you can deploy bots to meetings, retrieve real-time meeting events, and access live transcripts with just a few lines of code.

## Features

- **Send Bots to Meetings**: Easily deploy a bot to your video conferencing meetings. Currently, Zoom, Google Meet and Microsoft Teams are supported.
- **Real-Time Transcription**: Receive live transcripts of ongoing meetings.
- **WebSocket Integration**: Get real-time meeting events such as meeting start, finish, and transcript updates.
- **Customizable**: Set your own bot names and optionally customize API and WebSocket base URLs.

## Installation

You can install the ChatterBox Client via pip:

```bash
pip install chatterbox-io
```

## Usage

### Basic Example

To use the ChatterBox client, initialize it with your authorization token and deploy a bot to a meeting:

> **Note**: The ChatterBox client now provides detailed error messages from the server. Make sure to handle exceptions properly to get specific error information.

```python
import asyncio
import os
from chatterbox_io import ChatterBox

# Initialize the client with your authorization token
client = ChatterBox(
    authorization_token=os.getenv("CHATTERBOX_TOKEN")
)

async def handle_meeting_started(data):
    print(f"Meeting started: {data}")

async def handle_meeting_finished(data):
    print(f"Meeting finished: {data}")

async def handle_transcript(data):
    print(f"Transcript: {data['text']} (Speaker: {data['speaker']})")

async def main():
    try:
        # Send a bot to a Zoom meeting
        session = await client.send_bot(
            platform="zoom",
            meeting_id="1234567890",
            meeting_password="your_meeting_password_if_used",  # Optional
            bot_name="Test Bot",  # Optional
            language="multi",  # Optional
            model="nova-3",  # Optional
            no_transcript_timeout_seconds=300  # Optional: leave after 5 minutes of no transcripts
        )
        print(f"Bot started with session ID: {session.id}")

        # Connect to WebSocket for real-time events
        socket = client.connect_socket(session.id)

        # Register event handlers
        socket.on_meeting_started(handle_meeting_started)
        socket.on_meeting_finished(handle_meeting_finished)
        socket.on_transcript_received(handle_transcript)

        print("Connecting to WebSocket...")
        await socket.connect()
        print("Connected to WebSocket")

        # Keep the connection alive until interrupted
        try:
            await socket.wait_closed()
        except KeyboardInterrupt:
            print("\nShutting down...")
            await socket.disconnect()
            print("Disconnected from WebSocket")

    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Parameters for send_bot

- `platform`: The platform to send the bot to ('zoom', 'googlemeet', 'teams')
- `meeting_id`: The ID of the meeting (numeric ID for Zoom and Microsoft Teams, 'xxx-xxx-xxx' for Google Meet)
- `meeting_password`: (Optional) The meeting password
- `bot_name`: (Optional) Customize the name of the bot. Default is 'ChatterBox'
- `webhook_url`: (Optional) The webhook URL to send the meeting events to
- `language`: (Optional) The language for transcription. Default is 'multi' for multi-language support
- `model`: (Optional) The Deepgram model to use for transcription. Default is 'nova-3'
- `custom_image`: (Optional) Base64-encoded image data for the bot's profile picture. Must start with 'data:image/[type];base64,'. Supported types: png, jpg, jpeg, gif, bmp, webp, tiff. For best results, use 4:3 aspect ratio images like 640×480 pixels, 1024×768, or 1400×1050
- `no_transcript_timeout_seconds`: (Optional) Numeric. If provided, the bot will automatically leave the session after this many seconds without receiving transcripts.

### WebSocket Event Handlers

The WebSocket client provides the following event handlers:

- `on_meeting_started`: Triggered when the meeting starts
- `on_meeting_finished`: Triggered when the meeting ends
- `on_transcript_received`: Triggered when a transcript update is received

Each event handler receives a data dictionary containing the relevant information:

- Meeting events contain meeting-specific data
- Transcript events contain 'text' and 'speaker' fields

## Error Handling

The ChatterBox client provides detailed error handling with specific exception types that include the actual server error messages. This allows you to handle different types of errors appropriately and get meaningful error information from the server.

### Exception Types

- `ChatterBoxAPIError`: Base exception class for all API errors
- `ChatterBoxBadRequestError`: Raised for 400 Bad Request errors (invalid parameters, etc.)
- `ChatterBoxUnauthorizedError`: Raised for 401 Unauthorized errors (invalid token)
- `ChatterBoxForbiddenError`: Raised for 403 Forbidden errors (insufficient permissions)
- `ChatterBoxNotFoundError`: Raised for 404 Not Found errors (resource not found)
- `ChatterBoxServerError`: Raised for 5xx server errors

### Exception Properties

All exceptions have the following properties:

- `message`: The error message from the server
- `status_code`: The HTTP status code
- `response_data`: The full response data from the server (if available)

### Example Error Handling

```python
import asyncio
from chatterbox_io import (
    ChatterBox,
    ChatterBoxBadRequestError,
    ChatterBoxUnauthorizedError,
    ChatterBoxAPIError
)

async def main():
    client = ChatterBox(authorization_token="your_token")

    try:
        session = await client.send_bot(
            platform="zoom",
            meeting_id="invalid_meeting_id",
        )
    except ChatterBoxBadRequestError as e:
        print(f"Bad request: {e.message}")
        print(f"Status code: {e.status_code}")
        if e.response_data:
            print(f"Server response: {e.response_data}")
    except ChatterBoxUnauthorizedError as e:
        print(f"Authentication failed: {e.message}")
    except ChatterBoxAPIError as e:
        print(f"API error: {e.message} (Status: {e.status_code})")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### WebSocket Connection Management

The WebSocket client provides methods for managing the connection:

- `connect()`: Establishes the WebSocket connection
- `disconnect()`: Closes the WebSocket connection
- `wait_closed()`: Waits for the connection to close
- `on_meeting_started()`, `on_meeting_finished()`, `on_transcript_received()`: Register event handlers

## Getting Your Access Token

To use the ChatterBox client, you need an authorization token. You can request your token by signing up at our website: https://chatter-box.io/

Once you have your token, you can use it to initialize the ChatterBox client as shown in the examples above.

### Temporary Tokens

For enhanced security, you can generate temporary tokens that expire after a specified duration. This is particularly useful for client-side applications where you don't want to expose your permanent API token.

```python
import asyncio
from chatterbox_io import ChatterBox

async def main():
    # Initialize with your permanent API token
    client = ChatterBox(authorization_token="your_permanent_token")

    # Generate a temporary token that expires in 1 hour (3600 seconds)
    token_data = await client.get_temporary_token(expires_in=3600)
    print(f"Temporary token: {token_data['token']}")
    print(f"Expires in: {token_data['expiresIn']} seconds")

    # Use the temporary token for client operations
    temp_client = ChatterBox(authorization_token=token_data['token'])
    # ... use temp_client for your operations ...

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

Temporary tokens can be configured to expire between 60 seconds (1 minute) and 86400 seconds (24 hours). The default expiration time is 3600 seconds (1 hour).

## Development

To set up the development environment:

1. Clone the repository:

```bash
git clone https://github.com/OverQuotaAI/chatterbox-python.git
cd chatterbox-python
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:

```bash
pip install -r requirements.txt
```

4. Run tests:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
