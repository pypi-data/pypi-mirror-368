from _typeshed import Incomplete
from bosa_server_plugins.github.gql.issue import GQLIssueFilter as GQLIssueFilter, GQLIssueOrderBy as GQLIssueOrderBy
from bosa_server_plugins.github.requests.common import GithubCursorListRequest as GithubCursorListRequest
from bosa_server_plugins.github.requests.repositories import BasicRepositoryRequest as BasicRepositoryRequest
from bosa_server_plugins.handler import BaseRequestModel as BaseRequestModel
from enum import Enum
from typing import Literal

class CreateIssueRequest(BasicRepositoryRequest):
    """Request model for creating an issue."""
    title: str
    body: str | None
    assignees: list[str] | None
    labels: list[str] | None
    milestone: int | None

class ListIssuesRequest(BasicRepositoryRequest):
    """Request model for listing issues."""
    milestone: str | None
    state: str | None
    assignee: str | None
    creator: str | None
    mentioned: str | None
    labels: str | None
    sort: str | None
    direction: str | None
    since: str | None
    per_page: int | None
    page: int | None

class GQLDirection(str, Enum):
    """Direction for ordering results."""
    ASC = 'ASC'
    DESC = 'DESC'

class GQLListIssuesRequest(GithubCursorListRequest, BasicRepositoryRequest):
    """Request model for listing issues."""
    order_by: GQLIssueOrderBy | None
    direction: GQLDirection | None
    filter_by: GQLIssueFilter | None

class GetIssueRequest(BasicRepositoryRequest):
    """Request model for getting an issue."""
    issue_number: int

class GetIssueCommentsRequest(GetIssueRequest):
    """Request model for getting an issue."""
    force_new: bool | None
    created_at_from: str | None
    created_at_to: str | None
    updated_at_from: str | None
    updated_at_to: str | None
    per_page: int | None
    page: int | None

class SearchIssuesRequest(BaseRequestModel):
    """Request model for searching issues."""
    repositories: list[str] | None
    since: str | None
    until: str | None
    state: str | None
    creator: str | None
    fields: list[str] | None
    summarize: bool | None
    sort: str | None
    direction: str | None
    labels: list[str] | None
    assignee: str | None
    milestone: int | None

SearchSortOptions: Incomplete

class GithubSearchIssuePrRequest(BaseRequestModel):
    """Request model for github search issues and pull request."""
    query: str
    sort: SearchSortOptions | None
    order: Literal['asc', 'desc'] | None
    page: int | None
    per_page: int | None
