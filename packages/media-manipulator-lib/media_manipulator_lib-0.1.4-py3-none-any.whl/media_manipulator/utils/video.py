import io
import ffmpeg
import time
import tempfile
from media_manipulator.utils.logger import logger


def apply_watermark_ffmpeg(video_bytes: bytes, text_node: dict) -> io.BytesIO | None:
    """
    Applies a text watermark to the input video using FFmpeg.

    Tries fast in-memory processing first (via stdin/stdout pipe). 
    If that fails, falls back to a tempfile-based approach.

    Parameters:
        video_bytes (bytes): The raw video data.
        text (str): Text to overlay as watermark.
        position (str): 'top' or 'bottom'. Defaults to 'bottom'.

    Returns:
        io.BytesIO | None: The final video buffer with watermark, or None on failure.
    """
    text = text_node.get("value")    
    text_style = text_node.get("style",{})
    position_x = text_style.get("position_x", "(w-text_w)/2")
    position_y = text_style.get("position_y", "h-30")
    font_style = text_style.get("style",'Barlow')
    font_size = text_style.get("size", "24")
    font_color = text_style.get("color", "white")

    filter_expr = (
        f"drawtext=font={font_style}:"
        f"text='{text}':fontcolor={font_color}:fontsize={font_size}:borderw=1:"
        "shadowcolor=black:shadowx=2:shadowy=2:"
        f"x={position_x}:y={position_y}"
    )

    video_with_watermark = run_tempfile_ffmpeg(video_bytes, filter_expr)
    
    return video_with_watermark


def run_tempfile_ffmpeg(video_bytes: bytes, filter_expr: str) -> io.BytesIO | None:
    """
    Applies a watermark using FFmpeg with temporary input/output files.

    Parameters:
        video_bytes (bytes): Raw video input.
        filter_expr (str): FFmpeg drawtext filter string.

    Returns:
        io.BytesIO | None: Processed video or None on failure.
    """
    try:
        start = time.time()

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=True) as input_file, \
             tempfile.NamedTemporaryFile(suffix=".mp4", delete=True) as output_file:

            # Write video bytes to input tempfile
            input_file.write(video_bytes)
            input_file.flush()

            # Run FFmpeg with input/output file paths
            (
                ffmpeg
                .input(input_file.name)
                .output(output_file.name, vf=filter_expr,
                        vcodec='libx264', 
                        acodec='aac',
                        preset='medium', 
                        crf=23,
                        movflags='frag_keyframe+empty_moov',
                        loglevel='error')
                .overwrite_output()
                .run()
            )

            # Read back the result into memory
            with open(output_file.name, "rb") as f:
                result = io.BytesIO(f.read())
                result.seek(0)
                logger.success(f"Watermark added via temp file in {round(time.time() - start, 2)}s")
                return result

    except Exception as e:
        logger.error(f"FFmpeg fallback failed: {e}")
        return None
