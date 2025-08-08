import base64
from media_manipulator.core.strategy_registry import STRATEGY_MAP


class Interpreter:
    def __init__(self):
        self.strategy_map = STRATEGY_MAP

    def interpret(self, node):
        """
        Recursively builds a command tree from the input JSON, without executing any processing.
        """
        if "operation" in node:
            operation = node["operation"]
            if operation not in self.strategy_map:
                raise ValueError(f"Unsupported operation: {operation}")
            
            return {
                "operation": operation,
                "left": self.interpret(node["left"]),
                "right": self.interpret(node["right"])
            }

        elif "type" in node:
            return self.handle_leaf(node)

        raise ValueError("Invalid node in request.")

    def handle_leaf(self, node):
        """
        Handles base media types: video, audio, text.

        For video/audio:
            - Expects base64-encoded "value" key.
            - Returns decoded bytes under "bytes" key.

        For text:
            - Returns full text dictionary unchanged.
        """
        media_type = node.get("type")

        if media_type in ("video", "audio","image"):
            raw_value = node.get("value")
            if not raw_value:
                raise ValueError(f"{media_type.capitalize()} must be provided as base64-encoded 'value'.")

            try:
                media_bytes = base64.b64decode(raw_value)
            except Exception as e:
                raise ValueError(f"Failed to decode base64 {media_type}: {e}")

            return {
                "type": media_type,
                "bytes": media_bytes,
                "operations": node.get("operations", []),
                "attributes": node.get("attributes", {}),
            }

        elif media_type == "text":
            return {
                "type": "text",
                "value": node.get("value"),
                "duration": node.get("duration"),
                "style": node.get("style", {}),
                "operations": node.get("operations", [])
            }

        else:
            raise ValueError(f"Unknown media type: {media_type}")

    def build_expression(self, node):
        """
        Returns a human-readable symbolic string expression, used to check if request is getting interpreted successfully e.g., add(video, overlay(text, audio))
        """
        if "operation" in node:
            op = node["operation"]
            if op not in self.strategy_map:
                raise ValueError(f"Unsupported operation: {op}")
            left_expr = self.build_expression(node["left"])
            right_expr = self.build_expression(node["right"])
            return f"{op}({left_expr}, {right_expr})"

        elif "type" in node:
            return node["type"]

        raise ValueError("Invalid node in expression builder.")
