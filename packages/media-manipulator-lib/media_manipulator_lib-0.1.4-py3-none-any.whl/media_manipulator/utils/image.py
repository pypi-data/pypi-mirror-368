import io
import ffmpeg
import time
import tempfile
from media_manipulator.utils.logger import logger


def apply_text_on_image(image_bytes: bytes, text_node: dict) -> io.BytesIO | None:
    """
    Applies a text watermark to the input image using FFmpeg.

    Tries fast in-memory processing first (via stdin/stdout pipe). 
    If that fails, falls back to a tempfile-based approach.

    Parameters:
        image_bytes (bytes): The raw image data.
        text (str): Text to overlay as watermark.
        position (str): 'top' or 'bottom'. Defaults to 'bottom'.

    Returns:
        io.BytesIO | None: The final image buffer with watermark, or None on failure.
    """
    text = text_node.get("value")    
    text_style = text_node.get("style",{})
    position_x = text_style.get("position_x", "(w-text_w)/2")
    position_y = text_style.get("position_y", "h-30")
    font_style = text_style.get("style",'Barlow')
    font_size = text_style.get("size", "24")
    font_color = text_style.get("color", "white")
    font_path = ""

    if font_style == "Great Vibes":
        font_path = "media_manipulator/fonts/Great_Vibes/GreatVibes-Regular.ttf"

    if font_path != "":
        filter_expr = (
            f"drawtext=fontfile={font_path}:"
            f"text='{text}':fontcolor={font_color}:fontsize={font_size}:borderw=1:"
            "shadowcolor=black:shadowx=2:shadowy=2:"
            # "box=1:boxcolor=white@1.0:boxborderw=10:"
            f"x={position_x}:y={position_y}"
        )
    
    else:
        filter_expr = (
            f"drawtext=font={font_style}:"
            f"text='{text}':fontcolor={font_color}:fontsize={font_size}:borderw=1:"
            "shadowcolor=black:shadowx=2:shadowy=2:"
            f"x={position_x}:y={position_y}"
        )

    image_with_text= run_tempfile_ffmpeg_image(image_bytes, filter_expr)
    
    return image_with_text


def run_tempfile_ffmpeg_image(image_bytes: bytes, filter_expr: str) -> io.BytesIO | None:
    """
    Applies a drawtext filter to an image using FFmpeg with temporary files.

    Parameters:
        image_bytes (bytes): Raw image input (e.g. PNG or JPG).
        filter_expr (str): FFmpeg drawtext filter string.

    Returns:
        io.BytesIO | None: Processed image or None on failure.
    """
    try:
        start = time.time()

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as input_file, \
             tempfile.NamedTemporaryFile(suffix=".png", delete=False) as output_file:

            input_file.write(image_bytes)
            input_file.flush()

            

            (
                ffmpeg
                .input(input_file.name)
                .output(
                    output_file.name,
                    vf=filter_expr,
                    loglevel='error'
                )
                .overwrite_output()
                .run()
            )

            with open(output_file.name, "rb") as f:
                result = io.BytesIO(f.read())
                result.seek(0)
                print(f"Image processed via FFmpeg in {round(time.time() - start, 2)}s")
                return result

    except Exception as e:
        print(f"FFmpeg image processing failed: {e}")
        return None


def overlay_image_on_image(base_bytes: bytes,overlay_image_node: dict) -> io.BytesIO | None:
    """
    Overlays a resized image (e.g., signature) onto a base image using FFmpeg.

    Parameters:
        base_bytes (bytes): Background image in bytes.
        overlay_bytes (bytes): Overlay image in bytes.
        x, y (int): Coordinates for overlay placement.
        overlay_width (int): Resize width for the overlay image.

    Returns:
        io.BytesIO | None: Final overlaid image in memory.
    """
    try:
        start = time.time()

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as base_file, \
             tempfile.NamedTemporaryFile(suffix=".png", delete=False) as overlay_file, \
             tempfile.NamedTemporaryFile(suffix=".png", delete=False) as resized_overlay_file, \
             tempfile.NamedTemporaryFile(suffix=".png", delete=False) as output_file:

            overlay_bytes = overlay_image_node.get("bytes")    
            image_attributes = overlay_image_node.get("attributes",{})
            position_x = image_attributes.get("position_x", 100)
            position_y = image_attributes.get("position_y", 100)
            overlay_width = image_attributes.get("width",200)

            if isinstance(overlay_bytes, io.BytesIO):
                overlay_bytes = overlay_bytes.getvalue()


            base_file.write(base_bytes)
            base_file.flush()
            overlay_file.write(overlay_bytes)
            overlay_file.flush()


            (
                ffmpeg
                .input(overlay_file.name)
                .filter('scale', overlay_width, -1)
                .output(resized_overlay_file.name, format='image2', vcodec='png', loglevel='error')
                .overwrite_output()
                .run()
            )

            base_input = ffmpeg.input(base_file.name)
            overlay_input = ffmpeg.input(resized_overlay_file.name)
            
            
            (
                ffmpeg
                .filter([base_input, overlay_input], 'overlay', x=position_x, y=position_y)
                .output(output_file.name, format='image2', vcodec='png', loglevel='error')
                .overwrite_output()
                .run()
            )


            print("Done")


            with open(output_file.name, "rb") as f:
                result = io.BytesIO(f.read())
                result.seek(0)
                print(f"Overlay completed in {round(time.time() - start, 2)}s")
                return result

    except Exception as e:
        print(f"Overlay failed: {e}")
        return None