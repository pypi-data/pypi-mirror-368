class Node:
    """
    node of a an event flow graph. the nodes have an id and an event
    """
    node_id: str
    event: str
    children: set[Node]
    parents: set[Node]
    attributes: dict[str,object]
    def __init__(self, node_id: int, event: str): ...
