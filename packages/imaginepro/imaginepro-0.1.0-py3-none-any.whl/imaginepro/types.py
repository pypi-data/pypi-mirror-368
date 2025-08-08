from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass


@dataclass
class BaseParams:
    """Base parameters for all API requests"""
    ref: Optional[str] = None
    webhook_override: Optional[str] = None
    timeout: Optional[int] = None
    disable_cdn: Optional[bool] = None


@dataclass
class ImagineParams(BaseParams):
    """Parameters for the imagine API endpoint"""
    prompt: str = ""
    negative_prompt: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    steps: Optional[int] = None
    seed: Optional[int] = None
    cfg_scale: Optional[float] = None
    style: Optional[str] = None
    model: Optional[str] = None


@dataclass
class ButtonPressParams(BaseParams):
    """Parameters for the button press API endpoint"""
    message_id: str = ""
    button: str = ""
    mask: Optional[str] = None
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None


@dataclass
class UpscaleParams(BaseParams):
    """Parameters for upscaling an image"""
    message_id: str = ""
    index: int = 1


@dataclass
class VariantParams(BaseParams):
    """Parameters for creating a variant of an image"""
    message_id: str = ""
    index: int = 1


@dataclass
class RerollParams(BaseParams):
    """Parameters for rerolling an image generation"""
    message_id: str = ""


@dataclass
class InpaintingParams(BaseParams):
    """Parameters for inpainting an image"""
    message_id: str = ""
    mask: str = ""
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None


@dataclass
class ImagineProSDKOptions:
    """Configuration options for the ImagineProSDK"""
    api_key: str
    base_url: str = "https://api.imaginepro.ai"
    default_timeout: int = 1800  # 30 minutes
    fetch_interval: int = 2  # 2 seconds


# Response types
ImagineResponse = Dict[str, Any]
MessageResponse = Dict[str, Any]
ErrorResponse = Dict[str, Any]