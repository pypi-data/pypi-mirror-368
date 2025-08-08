import io

from media_manipulator.core.strategies.base import VideoEditStrategy
from media_manipulator.utils.video import apply_watermark_ffmpeg
from media_manipulator.utils.audio import overlay_audio_ffmpeg
from media_manipulator.utils.image import apply_text_on_image, overlay_image_on_image
from media_manipulator.utils.helpers import get_node_by_type
from media_manipulator.utils.logger import logger


class OverlayStrategy(VideoEditStrategy):
    def apply(self, left: dict, right: dict) -> dict | None:
        """
        Applies a overlay(audio or text) on the video input using FFmpeg.

        Parameters:
        - left (dict): One of the input nodes, expected to be video or text or audio.
        - right (dict): The other input node, expected to be video or text or audio.

        Returns:
        - dict: A dictionary containing the processed video with overlay.
        - None: If processing fails or input is invalid.
        """

        # Ensure both inputs are valid dictionaries
        if not isinstance(left, dict) or not isinstance(right, dict):
            logger.error("Invalid input types. Expected dicts.")
            return None

        left_type = left.get("type")
        right_type = right.get("type")
        type_pair = {left_type, right_type}

        if type_pair == {"video", "text"}:
            return self.handle_video_text_overlay(left, right)

        elif type_pair == {"video", "audio"}:
            return self.handle_video_audio_overlay(left, right)
        
        elif type_pair == {"image","text"}:
            return self.handle_image_text_overlay(left,right)

        elif type_pair == {"image","image"}:
            return self.handle_image_over_image_overlay(left,right)
        
    
    def handle_video_text_overlay(self, left: dict, right: dict) -> dict | None:
        """Handles video + text → watermark overlay"""
        logger.info("AddStrategy: Applying text overlay to video")

        # Extract the video and text nodes from left/right
        video_node = get_node_by_type(left, right, "video")
        text_node =  get_node_by_type(left, right, "text")

        if not video_node or not text_node:
            logger.error("Both video and text inputs are required.")
            return None

        video_bytes = video_node.get("bytes")
        text = text_node.get("value")        

        # Validate required content
        if not video_bytes:
            logger.error("Missing video bytes.")
            return None

        if not text:
            logger.error("Missing watermark text.")
            return None

        video_bytes = video_node.get("bytes")
        if isinstance(video_bytes, io.BytesIO):
            video_bytes = video_bytes.getvalue()

        result = apply_watermark_ffmpeg(video_bytes, text_node)
        if result is None:
            logger.error("Watermarking failed")
            return None

        logger.success("Successfully completed Watermarking")
        return {
            "type": "video",
            "bytes": result
        }
    
    def handle_video_audio_overlay(self, left: dict, right: dict) -> dict | None:
        """
        Overlays an audio stream onto a video.
        Accepts input on either side (left/right) to allow flexible JSON structure.
        """

        if not isinstance(left, dict) or not isinstance(right, dict):
            logger.error("Invalid input types, Expected bytes")
            return None

        video = get_node_by_type(left, right, "video")
        audio = get_node_by_type(left, right, "audio")

        video_bytes = video.get("bytes")
        audio_bytes = audio.get("bytes")

        if not video_bytes or not audio_bytes:
            logger.error("Missing video or audio bytes")
            return None

        result = overlay_audio_ffmpeg(video_bytes, audio_bytes)

        if result is None:
            logger.error("Audio overlay failed")
            return None

        logger.success("Successfully completed Audio overlay")
        return {
            "type": "video",
            "bytes": result
        }
    

    def handle_image_text_overlay(self, left: dict, right: dict) -> dict | None:
        """Handles image + text → watermark overlay"""
        logger.info("AddStrategy: Applying text overlay to image")

        # Extract the video and text nodes from left/right
        image_node = get_node_by_type(left, right, "image")
        text_node =  get_node_by_type(left, right, "text")

        if not image_node or not text_node:
            logger.error("Both image and text inputs are required.")
            return None

        image_bytes = image_node.get("bytes")
        text = text_node.get("value")        

        # Validate required content
        if not image_bytes:
            logger.error("Missing image bytes.")
            return None

        if not text:
            logger.error("Missing watermark text.")
            return None

        image_bytes = image_node.get("bytes")
        if isinstance(image_bytes, io.BytesIO):
            image_bytes = image_bytes.getvalue()

        result = apply_text_on_image(image_bytes, text_node)
        if result is None:
            logger.error("Image overlay failed")
            return None

        logger.success("Successfully completed image overlay")
        return {
            "type": "image",
            "bytes": result
        }
    
    
    def handle_image_over_image_overlay(self, left: dict, right: dict) -> dict | None:
        """Handles image + image → overlay"""
        logger.info("AddStrategy: Applying image overlay to image")

        # Extract the video and text nodes from left/right
        base_image_node = left
        overlay_image_node = right

        if not base_image_node or not overlay_image_node:
            logger.error("Both images are required.")
            return None

        base_image_bytes = base_image_node.get("bytes")
        overlay_image_bytes = overlay_image_node.get("bytes")        

        # Validate required content
        if not base_image_bytes:
            logger.error("Missing base image bytes.")
            return None

        if not overlay_image_bytes:
            logger.error("Missing overlay image bytes")
            return None

        if isinstance(base_image_bytes, io.BytesIO):
            base_image_bytes = base_image_bytes.getvalue()
            
        print("calling helper func")
        result = overlay_image_on_image(base_image_bytes, overlay_image_node)
        if result is None:
            logger.error("Image overlay failed")
            return None

        logger.success("Successfully completed image overlay")
        return {
            "type": "image",
            "bytes": result
        }
