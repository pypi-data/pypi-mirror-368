from bosa_server_plugins.github.gql.issue import GQLIssueOrderBy as GQLIssueOrderBy
from bosa_server_plugins.github.gql.pull_request import GQLPullRequestState as GQLPullRequestState
from bosa_server_plugins.github.requests.repositories import BasicRepositoryRequest as BasicRepositoryRequest
from bosa_server_plugins.handler import BaseRequestModel as BaseRequestModel

class PullRequestsRequest(BasicRepositoryRequest):
    """Pull Requests Request."""
    state: str | None
    head: str | None
    base: str | None
    sort: str | None
    direction: str | None
    per_page: int | None
    page: int | None

class SearchPullRequestsRequest(BaseRequestModel):
    """Search Pull Requests Request."""
    repositories: list[str] | None
    merged: bool | None
    draft: bool | None
    author: str | None
    labels: list[str] | None
    since: str | None
    until: str | None
    state: str | None
    sort: str | None
    direction: str | None
    fields: list[str] | None
    summarize: bool | None

class GetPullRequestRequest(BasicRepositoryRequest):
    """Request model for getting a single pull request."""
    pull_number: int

class GQLListPullRequestsRequest(BasicRepositoryRequest):
    """Request model for listing pull requests."""
    order_by: GQLIssueOrderBy | None
    direction: str | None
    per_page: int | None
    states: list[GQLPullRequestState] | None
    labels: list[str] | None
    head: str | None
    base: str | None
    cursor: str | None
    from_last: bool | None
