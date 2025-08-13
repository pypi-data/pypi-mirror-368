from bosa_server_plugins.github.requests.repositories import BasicRepositoryRequest as BasicRepositoryRequest

class GetCollaboratorsRequest(BasicRepositoryRequest):
    """Request model for getting repository collaborators."""
    affiliation: str | None
    permission: str | None
    per_page: int | None
    page: int | None
