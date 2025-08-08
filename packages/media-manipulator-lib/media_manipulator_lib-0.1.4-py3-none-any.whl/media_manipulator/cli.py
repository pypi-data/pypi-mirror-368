import sys
import json
import io
import base64
from media_manipulator import process_video_request
from media_manipulator.utils.logger import logger

def main():
    # if len(sys.argv) != 2:
    #     print("Usage: python -m media_manipulator.cli input.json")
    #     sys.exit(1)

    try:
        base_image_bytes = open("sample.png", "rb").read()
        overlay_image_bytes = open("signature.png", "rb").read()
        encrypted_base_bytes = base64.b64encode(base_image_bytes)
        encrypted_overlay_bytes = base64.b64encode(overlay_image_bytes)
        request = {
                "operation": "overlay",
                    "left": {
                        "operation": "overlay",
                            "left": {
                                "operation": "overlay",
                                "left": {
                                    "type": "image",
                                    "value": encrypted_base_bytes
                                },
                                "right": {
                                    "type": "text",
                                    "value": "Aditya Sharma",
                                    "style": {
                                        "position_x":380,
                                        "position_y":350,
                                        "size": 76,
                                        "style": "Great Vibes"
                                    }
                                }
                            },
                            "right": {
                                "type": "image",
                                "value": encrypted_overlay_bytes,
                                "attributes": {
                                    "position_x":250,
                                    "position_y":570,
                                    "width": 200,
                                }
                            }
                    },
                    "right": {
                        "type": "image",
                        "value": encrypted_overlay_bytes,
                        "attributes": {
                            "position_x":800,
                            "position_y":570,
                            "width": 200,
                        }
                    }
    }
        # with open(sys.argv[1], 'r') as f:
        #     request = json.load(f)

        result = process_video_request(request)

        if result:
            data = result["bytes"]
            if isinstance(data, io.BytesIO):
                data = data.getvalue()

            with open("output.png", "wb") as f:
                f.write(data)

            logger.success("Image saved to output.png")
        else:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error while running CLI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
