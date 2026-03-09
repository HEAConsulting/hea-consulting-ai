"""
Content Domain — AI Image Generation
======================================

Generate images for blogs, social media, and marketing
using OpenAI's gpt-image-1 model.
"""

import os
import base64
from typing import Optional
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import format_response, error_response

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def register_tools(mcp):

    @mcp.tool()
    def generate_image(
        prompt: str,
        style: str = "professional",
        size: str = "1024x1024",
        save_path: Optional[str] = None,
    ) -> dict:
        """
        Generate an image using AI.

        Args:
            prompt: Image description
            style: Style hint (professional, creative, minimal, bold)
            size: Image size (1024x1024, 1792x1024, 1024x1792)
            save_path: Optional local path to save the image
        """
        try:
            if not OPENAI_API_KEY:
                return error_response("OPENAI_API_KEY not configured")

            import requests

            full_prompt = f"{style} style: {prompt}"

            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-image-1",
                    "prompt": full_prompt,
                    "n": 1,
                    "size": size,
                    "response_format": "b64_json",
                },
                timeout=60,
            )

            if response.status_code != 200:
                return error_response(f"API error: {response.status_code}")

            data = response.json()
            b64 = data["data"][0]["b64_json"]

            if save_path:
                with open(save_path, "wb") as f:
                    f.write(base64.b64decode(b64))

            return format_response({
                "prompt": full_prompt,
                "size": size,
                "saved_to": save_path,
                "b64_length": len(b64),
            }, "Image generated")
        except Exception as e:
            return error_response(str(e))
