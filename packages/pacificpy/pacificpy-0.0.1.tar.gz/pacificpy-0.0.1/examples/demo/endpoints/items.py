from pacificpy.routing import get, post, put, delete, patch


@get("/items")
def list_items():
    """Get list of items."""
    return {"items": ["Item 1", "Item 2", "Item 3"]}


@post("/items")
def create_item():
    """Create a new item."""
    return {"message": "Item created"}


@get("/items/{item_id}")
def get_item(item_id: str):
    """Get a specific item by ID."""
    return {"item_id": item_id, "name": f"Item {item_id}"}


@put("/items/{item_id}")
def update_item(item_id: str):
    """Update a specific item by ID."""
    return {"message": f"Item {item_id} updated"}


@patch("/items/{item_id}")
def partial_update_item(item_id: str):
    """Partially update a specific item by ID."""
    return {"message": f"Item {item_id} partially updated"}


@delete("/items/{item_id}")
def delete_item(item_id: str):
    """Delete a specific item by ID."""
    return {"message": f"Item {item_id} deleted"}