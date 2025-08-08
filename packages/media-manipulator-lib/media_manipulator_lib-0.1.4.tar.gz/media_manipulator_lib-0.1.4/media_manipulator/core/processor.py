from media_manipulator.core.strategy_registry import STRATEGY_MAP
from media_manipulator.utils.logger import logger

class Processor:
    def __init__(self):
        self.strategy_map = STRATEGY_MAP

    def process_command(self, command):
        """
        Recursively processes a nested video editing command tree based on the operation types.

        Parameters:
        - command (dict): A JSON-like dictionary representing either:
            - a media node (e.g., video, audio, text), or
            - an operation node with 'operation', 'left', and 'right' keys.

        Returns:
        - dict: The result of applying the operation strategy on left and right subtrees.
        - dict: The base media node if no operation is present.

        Raises:
        - ValueError: If the command is not valid or contains unsupported operations.
        """
        
        if "operation" in command:
            operation = command["operation"]
            strategy = self.strategy_map.get(operation)
            if not strategy:
                raise ValueError(f"Unsupported operation: {operation}")

            left = self.process_command(command["left"])
            right = self.process_command(command["right"])

            return strategy.apply(left, right)

        elif "type" in command:
            return command

        raise ValueError("Invalid command structure")
