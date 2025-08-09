import base64
import io
from typing import Literal

from pydantic import BaseModel

ImagePromptQuality = Literal["auto", "high", "low"]

# `ImagePrompt` is only available if PIL is installed
try:
    from PIL import Image  # type: ignore

    class ImagePrompt(BaseModel):
        image: Image.Image
        quality: ImagePromptQuality = "auto"

        def _encode_image(self, image: Image.Image) -> str:
            with io.BytesIO() as output:
                image.save(output, format="PNG")
                return base64.b64encode(output.getvalue()).decode("utf-8")

        class Config:
            arbitrary_types_allowed = True

except ImportError:
    ImagePrompt = None  # type: ignore


class ImageURLPrompt(BaseModel):
    """only for remote urls"""

    image_url: str
    quality: ImagePromptQuality = "auto"
