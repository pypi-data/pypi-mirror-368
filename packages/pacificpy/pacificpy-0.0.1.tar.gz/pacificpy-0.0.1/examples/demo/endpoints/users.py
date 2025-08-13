from pacificpy.routing import route


@route("/users", methods=["GET"])
def get_users():
    """Get list of users."""
    return {"users": ["Alice", "Bob", "Charlie"]}


@route("/users", methods=["POST"])
def create_user():
    """Create a new user."""
    return {"message": "User created"}


@route("/users/{user_id}", methods=["GET"])
def get_user(user_id: str):
    """Get a specific user by ID."""
    return {"user_id": user_id, "name": f"User {user_id}"}