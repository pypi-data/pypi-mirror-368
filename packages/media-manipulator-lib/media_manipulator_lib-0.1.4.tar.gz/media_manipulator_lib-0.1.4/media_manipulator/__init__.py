import time
from media_manipulator.core.interpreter import Interpreter
from media_manipulator.core.processor import Processor
from media_manipulator.utils.logger import logger

__version__ = "0.1.0"

def process_video_request(request: dict) -> dict | None:
    """
    Public API function to process media manipulation instructions.

    Args:
        request (dict): The structured JSON payload.

    Returns:
        dict | None: Dictionary with 'type' and 'bytes', or None on failure.
    """
    try:
        start = time.time()
        interpreter = Interpreter()
        command = interpreter.interpret(request)

        if command is None:
            logger.error("Invalid request.")
            return None

        logger.info("Calling processor with interpreted command")
        processor = Processor()
        result = processor.process_command(command)

        if result is None:
            logger.error("Media Manipulation failed")
        else:
            logger.success(f"Processing completed in {round(time.time() - start, 2)}s")
            return result

    except Exception as e:
        logger.error(f"Fatal error during processing: {e}")
        return None
