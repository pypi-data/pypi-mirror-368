def get_node_by_type(node1: dict, node2: dict, media_type: str) -> dict | None:
    """
    Utility to extract a specific media type (e.g., 'video', 'text') from two candidate nodes.

    Parameters:
    - node1 (dict): First candidate node.
    - node2 (dict): Second candidate node.
    - media_type (str): The desired media type to look for.

    Returns:
    - dict: The matching node if found.
    - None: If no matching type is found.
    """
     
    if node1.get("type") == media_type:
        return node1
    if node2.get("type") == media_type:
        return node2
    return None
