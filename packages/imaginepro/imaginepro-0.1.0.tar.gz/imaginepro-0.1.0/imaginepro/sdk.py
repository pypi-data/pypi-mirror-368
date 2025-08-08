import time
import json
import requests
from typing import Dict, Any, Optional, TypeVar, cast, Type, Generic

from .types import (
    ImagineProSDKOptions, ImagineParams, ButtonPressParams, UpscaleParams,
    VariantParams, RerollParams, InpaintingParams, BaseParams,
    ImagineResponse, MessageResponse, ErrorResponse
)
from .constants import Button

T = TypeVar('T')


class ImagineProSDK:
    """
    ImagineProSDK class for interacting with the Imagine Pro AI image generation API
    """
    
    def __init__(self, options: ImagineProSDKOptions):
        """
        Initialize the SDK with configuration options
        """
        self.api_key = options.api_key
        self.base_url = options.base_url
        self.default_timeout = options.default_timeout  # in seconds
        self.fetch_interval = options.fetch_interval  # in seconds

    def imagine(self, params: ImagineParams) -> ImagineResponse:
        """
        Generate an image with the given prompt
        """
        response = self._post_request('/api/v1/nova/imagine', self._convert_params(params))
        # If the response has 'message_id' but not 'id', add 'id' for compatibility
        if 'message_id' in response and 'id' not in response:
            response['id'] = response['message_id']
        return response

    def fetch_message_once(self, message_id: str) -> MessageResponse:
        """
        Fetch the status of a message once
        """
        endpoint = f'/api/v1/message/fetch/{message_id}'
        message_status = self._get_request(endpoint)
        # Remove or comment out this print statement for tests
        # print(f"Message status: {message_status['status']}, progress: {message_status['progress']}")
        return cast(MessageResponse, message_status)

    def fetch_message(
        self, 
        message_id: str, 
        interval: Optional[int] = None, 
        timeout: Optional[int] = None
    ) -> MessageResponse:
        """
        Poll for message status until completion or timeout
        """
        if interval is None:
            interval = self.fetch_interval
        if timeout is None:
            timeout = self.default_timeout
            
        start_time = time.time()
        
        while True:
            message_status = self.fetch_message_once(message_id)
            
            if message_status['status'] in ['DONE', 'FAIL']:
                return message_status
                
            if time.time() - start_time > timeout:
                raise TimeoutError('Timeout exceeded while waiting for message status.')
                
            time.sleep(interval)

    def press_button(self, params: ButtonPressParams) -> ImagineResponse:
        """
        Press a button on an existing image generation
        """
        return self._post_request('/api/v1/nova/button', self._convert_params(params))

    def upscale(self, params: UpscaleParams) -> ImagineResponse:
        """
        Upscale a generated image
        """
        button = f"U{params.index}"
        
        button_params = ButtonPressParams(
            message_id=params.message_id,
            button=button,
            ref=params.ref,
            webhook_override=params.webhook_override,
            timeout=params.timeout,
            disable_cdn=params.disable_cdn
        )
        
        return self.press_button(button_params)

    def variant(self, params: VariantParams) -> ImagineResponse:
        """
        Create a variant of a generated image
        """
        button = f"V{params.index}"
        
        button_params = ButtonPressParams(
            message_id=params.message_id,
            button=button,
            ref=params.ref,
            webhook_override=params.webhook_override,
            timeout=params.timeout,
            disable_cdn=params.disable_cdn
        )
        
        return self.press_button(button_params)

    def reroll(self, params: RerollParams) -> ImagineResponse:
        """
        Regenerate an image with the same prompt
        """
        button_params = ButtonPressParams(
            message_id=params.message_id,
            button=Button.REROLL,
            ref=params.ref,
            webhook_override=params.webhook_override,
            timeout=params.timeout,
            disable_cdn=params.disable_cdn
        )
        
        return self.press_button(button_params)

    def inpainting(self, params: InpaintingParams) -> ImagineResponse:
        """
        Apply inpainting to modify a specific region of an image
        """
        button_params = ButtonPressParams(
            message_id=params.message_id,
            button=Button.VARY_REGION,
            mask=params.mask,
            prompt=params.prompt,
            ref=params.ref,
            webhook_override=params.webhook_override,
            timeout=params.timeout,
            disable_cdn=params.disable_cdn
        )
        
        return self.press_button(button_params)

    def _extract_base_params(self, params: BaseParams) -> Dict[str, Any]:
        """
        Extract base parameters from a params object
        """
        result = {}
        if params.ref is not None:
            result['ref'] = params.ref
        if params.webhook_override is not None:
            result['webhookOverride'] = params.webhook_override
        if params.timeout is not None:
            result['timeout'] = params.timeout
        if params.disable_cdn is not None:
            result['disableCdn'] = params.disable_cdn
        return result

    def _convert_params(self, params: Any) -> Dict[str, Any]:
        """
        Convert snake_case parameter names to camelCase for API requests
        """
        if not hasattr(params, '__dict__'):
            return params
            
        result = {}
        for key, value in params.__dict__.items():
            if value is not None:
                # Convert snake_case to camelCase
                parts = key.split('_')
                camel_key = parts[0] + ''.join(part.capitalize() for part in parts[1:])
                result[camel_key] = value
                
        return result

    def _get_request(self, endpoint: str) -> Dict[str, Any]:
        """
        Make a GET request to the API
        """
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )

            if not response.ok:
                error_response = response.json()
                raise Exception(error_response.get('error') or f"Error fetching data: {response.reason}")

            return response.json()
        except Exception as error:
            print(f"Error fetching data: {error}")
            raise

    def _post_request(self, endpoint: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a POST request to the API
        """
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
            )

            if not response.ok:
                error_response = response.json()
                raise Exception(error_response.get('error') or f"Error posting data: {response.reason}")

            return response.json()
        except Exception as error:
            print(f"Error posting data: {error}")
            raise