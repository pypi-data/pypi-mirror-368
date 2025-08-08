from abc import ABC, abstractmethod
from typing import Optional


class VideoEditStrategy(ABC):
    """
    Base class for single-input video editing strategies like watermark, trim, etc.
    """

    @abstractmethod
    def apply(self, video_bytes: bytes, params: dict) -> Optional[bytes]:
        """
        Apply the strategy to the video.

        Args:
            video_bytes (bytes): Raw video content.
            params (dict): Operation-specific parameters.

        Returns:
            Optional[bytes]: Modified video bytes or None if processing fails.
        """
        pass
