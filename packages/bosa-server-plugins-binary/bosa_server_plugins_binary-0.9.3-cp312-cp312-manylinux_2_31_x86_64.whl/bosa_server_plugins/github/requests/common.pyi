class GithubCursorListRequest:
    """Request model for listing items with pagination."""
    per_page: int | None
    cursor: str | None
    from_last: bool | None
