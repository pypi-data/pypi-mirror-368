from pacificpy.routing import get


@get("/posts")
def get_posts():
    """Get list of posts."""
    return {"posts": ["Post 1", "Post 2", "Post 3"]}


@get("/posts/{post_id}")
def get_post(post_id: str):
    """Get a specific post by ID."""
    return {"post_id": post_id, "title": f"Post {post_id}"}