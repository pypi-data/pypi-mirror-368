from pacificpy.routing import route


@route("/ignored", methods=["GET"])
def ignored_endpoint():
    """This endpoint should be ignored."""
    return {"message": "This should not be discovered"}