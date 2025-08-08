# Betatel SDK

Official Python SDK for Betatel telecommunications services.

## Installation

```bash
pip install betatelsdk
```

## Features

- **SMS**: Send and manage SMS messages
- **Voice**: Text-to-speech and voice services  
- **Call**: Voice call management and control
- **Carrier**: Carrier information and routing
- **Network**: Network status and connectivity
- **Billing**: Usage tracking and billing management

## Quick Start

```python
from betatelsdk import BetatelSDK

sdk = BetatelSDK(
    api_key='your_api_key_here',
    user_id='your_user_id_here'
)

# Send SMS
sdk.sms.send(
    from_='ExampleSender',
    to='ExampleRecipient',
    message='Hello from Betatel!'
)

# Make voice call
sdk.voice.text_to_speech(
    text='Hello world',
    voice='en-US'
)
```

## Documentation

For detailed API documentation and examples, visit [api.betatel.com/docs/category/api-documentation](https://api.betatel.com/docs/category/api-documentation)

## Support

For support and questions, contact us at support@betatel.com