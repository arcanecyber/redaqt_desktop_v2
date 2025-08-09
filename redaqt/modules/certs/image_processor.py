"""
File: code/modules/certs/image_processor.py
Author: Jonathan Carr
Arcane Cyber, LLC
https://arcanecyber.net
contact@arcanecyber.net
Copyright 2025 - All rights reserved

Date: August 2025
Description: Process the certificate image and normalizes it
"""

import os
import platform
from typing import Tuple, Optional
import numpy as np

def is_gpu_available() -> bool:
    """Check if CUDA-enabled GPU is available (Windows/Linux only)."""
    try:
        if platform.system() != "Darwin":
            import cupy as cp
            return cp.cuda.runtime.getDeviceCount() > 0
    except Exception:
        return False
    return False

# Allow environment override, default True
USE_GPU = os.getenv("USE_GPU", "1") == "1" and is_gpu_available()

if USE_GPU:
    import cupy as cp


def process_image(image_array: np.ndarray) -> Tuple[bool, Optional[np.ndarray]]:
    """
    Normalize the blue channel in a steganographic-compatible format.

    Args:
        image_array (np.ndarray): 3D uint8 image array (H x W x 3).

    Returns:
        success: bool -- True for success, False for failure.
        np.ndarray -- Modified image array.
    """

    """
    The stegonographic algorithm must process the image array and normalize the blue color channel
        so the data/information can be embedded and extracted from it. However, in the normalization
        process, any value at Blue=255 must be changed to Blue=254 to avoid having an overflow.

    Algorithm Note: The Red and Green channel act as a carrier for the Blue channel.  The Blue channel
        is normalized to Red and Green, so that when the Blue channel is modified with data, the data
        can be extracted.

    Equation 1: binaryBlue = (Red%2 ^ Green%2) ^ (Blue + (Red%2 ^ Green%2))%2
    Equation 2: normalizedBlue = Blue + binaryBlue
    """

    if image_array.dtype != np.uint8:
        return False, None
    if image_array.ndim != 3 or image_array.shape[2] != 3:
        return False, None

    if USE_GPU:
        try:
            img = cp.asarray(image_array)

            red = img[:, :, 0]
            green = img[:, :, 1]
            blue = cp.clip(img[:, :, 2], 1, 254)

            rg_mask = (red & 1) ^ (green & 1)
            binary_blue = rg_mask ^ ((blue + rg_mask) & 1)
            img[:, :, 2] = blue + binary_blue

            print(f"[DEBUG] Running on GPU: {cp.cuda.Device().name}")
            return True, cp.asnumpy(img)
        except Exception as e:
            print(f"[DEBUG] GPU processing failed, falling back to CPU. Error: {e}")

        # CPU fallback
    img = image_array.copy()
    red = img[:, :, 0]
    green = img[:, :, 1]
    blue = np.clip(img[:, :, 2], 1, 254)

    rg_mask = (red & 1) ^ (green & 1)
    binary_blue = rg_mask ^ ((blue + rg_mask) & 1)
    img[:, :, 2] = blue + binary_blue

    return True, img