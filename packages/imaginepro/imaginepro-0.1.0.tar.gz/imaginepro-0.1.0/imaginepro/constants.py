from enum import Enum


class Button(str, Enum):
    U1 = 'U1'  # Upscale button 1
    U2 = 'U2'  # Upscale button 2
    U3 = 'U3'  # Upscale button 3
    U4 = 'U4'  # Upscale button 4
    V1 = 'V1'  # Variant button 1
    V2 = 'V2'  # Variant button 2
    V3 = 'V3'  # Variant button 3
    V4 = 'V4'  # Variant button 4
    REROLL = '🔄'  # Reroll button
    ZOOM_OUT_2X = 'Zoom Out 2x'  # Zoom Out button (2x)
    ZOOM_OUT_1_5X = 'Zoom Out 1.5x'  # Zoom Out button (1.5x)
    VARY_STRONG = 'Vary (Strong)'  # Strong variation button
    VARY_SUBTLE = 'Vary (Subtle)'  # Subtle variation button
    VARY_REGION = 'Vary (Region)'  # Region variation button
    PAN_LEFT = '⬅️'  # Left pan button
    PAN_RIGHT = '➡️'  # Right pan button
    PAN_UP = '⬆️'  # Up pan button
    PAN_DOWN = '⬇️'  # Down pan button
    MAKE_SQUARE = 'Make Square'  # Make square button
    UPSCALE_2X = 'Upscale (2x)'  # Upscale button (2x)
    UPSCALE_4X = 'Upscale (4x)'  # Upscale button (4x)
    CANCEL_JOB = 'Cancel Job'  # Cancel job button
    UPSCALE_CREATIVE = 'Upscale (Creative)'  # Upscale button (Creative)
    UPSCALE_SUBTLE = 'Upscale (Subtle)'  # Upscale button (Subtle)


class Button:
    """Button constants for the ImagineProSDK"""
    UPSCALE_1 = "U1"
    UPSCALE_2 = "U2"
    UPSCALE_3 = "U3"
    UPSCALE_4 = "U4"
    VARIANT_1 = "V1"
    VARIANT_2 = "V2"
    VARIANT_3 = "V3"
    VARIANT_4 = "V4"
    REROLL = "🔄"
    VARY_REGION = "Vary (Region)"