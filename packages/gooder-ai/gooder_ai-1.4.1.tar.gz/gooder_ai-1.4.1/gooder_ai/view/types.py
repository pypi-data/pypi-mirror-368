from typing import TypedDict, Literal


class MutationVariables(TypedDict):
    datasetPath: str | None
    configPath: str | None
    id: str


class ExecuteGraphQLParams(TypedDict):
    mutation: Literal["createSharedView", "updateSharedView"]
    variables: dict[Literal["input"], MutationVariables]
    token: str
    api_url: str
