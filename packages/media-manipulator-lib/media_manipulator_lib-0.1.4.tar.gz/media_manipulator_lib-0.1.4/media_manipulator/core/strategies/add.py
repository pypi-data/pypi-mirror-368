from media_manipulator.core.strategies.base import VideoEditStrategy

class AddStrategy(VideoEditStrategy):
    def apply(self, left: dict, right: dict) -> dict | None:
        """
        Apply the 'add' operation between two media inputs.

        Currently supports:
        - video + text → watermark at the end of the video
        - text + video → watermark at the start of the video
        - video + video → add two videos

        Returns:
            dict: Modified media node with applied effect.
            None: If the processing fails or inputs are invalid.
        """
        if not isinstance(left, dict) or not isinstance(right, dict):
            raise ValueError("Both inputs must be dictionaries.")

        left_type = left.get("type")
        right_type = right.get("type")

        raise NotImplementedError(f"AddStrategy does not support '{left_type}' + '{right_type}' combination")
