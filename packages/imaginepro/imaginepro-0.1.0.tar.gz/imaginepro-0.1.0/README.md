# imaginepro-python-sdk

[![PyPI version](https://img.shields.io/pypi/v/imaginepro.svg)](https://pypi.org/project/imaginepro/)
[![License](https://img.shields.io/pypi/l/imaginepro.svg)](https://github.com/imaginpro/imaginepro-python-sdk/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/imaginepro.svg)](https://pypi.org/project/imaginepro/)
[![Build Status](https://img.shields.io/github/workflow/status/imaginpro/imaginepro-python-sdk/CI)](https://github.com/imaginpro/imaginepro-python-sdk/actions)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/imaginpro/imaginepro-python-sdk/blob/main/CONTRIBUTING.md)

Official Python SDK of [Imaginepro](https://platform.imaginepro.ai/), your professional AI image generation platform with enterprise-grade stability and scalability.

Imaginepro offers state-of-the-art AI image generation capabilities with:

- 🚀 Enterprise-grade API with high availability
- 🎨 High-quality image generation with advanced AI models
- ⚡ Fast processing speed and optimized performance
- 🛠️ Rich image manipulation features including upscaling, variants and inpainting
- 🔒 Secure and stable service with professional support
- 💰 Flexible pricing plans for different business needs

## Key Features

- Text-to-Image Generation: Create stunning images from text descriptions
- Image Upscaling: Enhance image resolution while maintaining quality
- Image Variants: Generate alternative versions of existing images
- Inpainting: Selectively modify specific areas of an image
- Webhook Support: Integrate with your workflow using custom callbacks
- Progress Tracking: Monitor generation progress in real-time
- Enterprise Support: Professional technical support and SLA

## Get Started

```bash
pip install imaginepro
```

## Quick start

```python
import os
from imaginepro import ImagineProSDK, ImagineProSDKOptions

# Initialize the SDK
sdk = ImagineProSDK(ImagineProSDKOptions(
    api_key="sk-xxxx",
    base_url="https://api.imaginepro.ai",  # Optional, defaults to 'https://api.imaginepro.ai'
    default_timeout=300,  # Optional, defaults to 1800 seconds (30 minutes)
    fetch_interval=2,  # Optional, defaults to 2 seconds
))

# Generate an image
try:
    result = sdk.imagine({
        "prompt": "a pretty cat playing with a puppy"
    })
    print(f"Image generation initiated: {result}")

    # Wait for the generation to complete
    imagine = sdk.fetch_message(result["message_id"])
    print(f"Image generation result: {imagine}")
except Exception as error:
    print(f"Error: {error}")
```

## Imagine

The `imagine` method allows you to generate an image based on a text prompt.

```python
imagine_response = sdk.imagine({
    "prompt": "a futuristic cityscape at sunset"
})
print(f"Imagine response: {imagine_response}")
```

## Buttons

The `press_button` method allows you to interact with buttons associated with a message. You can specify the `message_id` and `button` identifier.

```python
button_response = sdk.press_button({
    "message_id": "your-message-id",
    "button": "U1"
})
print(f"Button press response: {button_response}")
```

## Upscale

The `upscale` method allows you to upscale an image by interacting with the button 'U1' using the provided `message_id` and `index`.

```python
upscale_response = sdk.upscale({
    "message_id": "your-message-id",
    "index": 1  # Corresponds to button 'U1'
})
print(f"Upscale response: {upscale_response}")
```

## Variant

The `variant` method allows you to generate a variant of an image by interacting with a variant button using the provided `message_id` and `index`.

```python
variant_response = sdk.variant({
    "message_id": "your-message-id",
    "index": 1  # Corresponds to button 'V1'
})
print(f"Variant response: {variant_response}")
```

## Reroll

The `reroll` method allows you to regenerate an image using the provided `message_id`.

```python
reroll_response = sdk.reroll({
    "message_id": "your-message-id"
})
print(f"Reroll response: {reroll_response}")
```

## Inpainting

The `inpainting` method allows you to vary a specific region of an image using the provided `message_id` and `mask`. You can create mask by this [tool](https://mask.imaginepro.ai/)

```python
inpainting_response = sdk.inpainting({
    "message_id": "your-message-id",
    "mask": "xxx"
})
print(f"Inpainting response: {inpainting_response}")
```

## Fetch Message

The `fetch_message` method allows you to retrieve the status and details of a specific message using its `message_id`. This method polls the message status until it is either `DONE` or `FAIL`.

```python
message_response = sdk.fetch_message("your-message-id")
print(f"Message response: {message_response}")
```

### Parameters

- `message_id` (string): The unique identifier for the message.
- `interval` (int, optional): The polling interval in seconds. Defaults to 2 seconds.
- `timeout` (int, optional): The maximum time to wait for the message status in seconds. Defaults to 30 minutes.

### Returns

A `MessageResponse` dictionary containing details such as the `status`, `progress`, and generated image URL (if successful).

### Example

```python
try:
    message_response = sdk.fetch_message("your-message-id")
    print(f"Message details: {message_response}")
except Exception as error:
    print(f"Error fetching message: {error}")
```

## With webhook

You can use the optional parameters `ref` and `webhook_override` to customize the behavior of the SDK when generating images.

- `ref`: A reference ID that will be sent to the webhook for tracking purposes.
- `webhook_override`: A custom webhook URL to receive callbacks for generation results.

Example:

```python
imagine_response = sdk.imagine({
    "prompt": "a serene mountain landscape",
    "ref": "custom-reference-id",  # Optional reference ID
    "webhook_override": "https://your-custom-webhook.url/callback"  # Optional custom webhook URL
})
print(f"Imagine response with webhook: {imagine_response}")
```

When using `webhook_override`, the generation result will be sent to the specified webhook URL instead of the default one configured in your account.

The webhook payload will include details exactly the same as the response of `fetch_message`.

## Init Options

The `ImagineProSDK` constructor accepts the following options via the `ImagineProSDKOptions` dataclass:

- `api_key` (string, required): Your API key for authentication.
- `base_url` (string, optional): The base URL for the API. Defaults to `https://api.imaginepro.ai`.
- `default_timeout` (int, optional): The default timeout for requests in seconds. Defaults to 1800 seconds (30 minutes).
- `fetch_interval` (int, optional): The interval for polling the message status in seconds. Defaults to 2 seconds.

### Example

```python:README.md
from imaginepro import ImagineProSDK, ImagineProSDKOptions

sdk = ImagineProSDK(ImagineProSDKOptions(
    api_key="your-api-key",
    base_url="https://api.imaginepro.ai`",  # Optional
    default_timeout=60,  # Optional, 1 minute
    fetch_interval=1  # Optional, 1 second
))
```

## Message Response

The `MessageResponse` dictionary contains details about the status and result of a message.

### Properties

- `message_id` (string): The unique identifier for the message.
- `prompt` (string): The prompt used for image generation.
- `original_url` (string, optional): The original image URL.
- `uri` (string, optional): The generated image URL.
- `progress` (int): The progress percentage of the task.
- `status` (string): The current status of the message. Possible values are:
  - `PROCESSING`
  - `QUEUED`
  - `DONE`
  - `FAIL`
- `created_at` (string, optional): The timestamp when the message was created.
- `updated_at` (string, optional): The timestamp when the message was last updated.
- `buttons` (list of strings, optional): The available action buttons for the message.
- `originating_message_id` (string, optional): The ID of the originating message, if applicable.
- `ref` (string, optional): Reference information provided during the request.
- `error` (string, optional): The error message, if the task fails.

### Example

```python:README.md
message_response = {
    "message_id": "abc123",
    "prompt": "a futuristic cityscape at sunset",
    "uri": "https://cdn.imaginepro.ai/generated-image.jpg",
    "progress": 100,
    "status": "DONE",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:05:00Z",
    "buttons": ["U1", "V1"],
    "ref": "custom-reference-id"
}
print(f"Message Response: {message_response}")
```
