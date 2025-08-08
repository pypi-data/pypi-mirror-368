from bosa_server_plugins.github.requests.repositories import BasicRepositoryRequest as BasicRepositoryRequest
from bosa_server_plugins.handler import BaseRequestModel as BaseRequestModel

class GetCommitsRequest(BasicRepositoryRequest):
    """Request model for getting repository commits."""
    sha: str | None
    path: str | None
    author: str | None
    since: str | None
    until: str | None
    per_page: int | None
    page: int | None

class SearchCommitsRequest(BaseRequestModel):
    """Request model for searching repository commits."""
    repositories: list[str] | None
    since: str | None
    until: str | None
    author: str | None
    fields: list[str] | None
    summarize: bool | None
    callback_urls: list[str] | None
