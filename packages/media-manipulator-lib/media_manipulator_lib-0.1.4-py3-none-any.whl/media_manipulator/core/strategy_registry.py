from media_manipulator.core.strategies import add, overlay

# Centralized registry of all supported strategies
STRATEGY_MAP = {
    "add": add.AddStrategy(),
    "overlay": overlay.OverlayStrategy(),
    # Add more strategies here as needed
}
