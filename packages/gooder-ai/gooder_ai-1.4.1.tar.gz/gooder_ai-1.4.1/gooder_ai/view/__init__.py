from aiohttp import ClientSession
from gooder_ai.view.types import ExecuteGraphQLParams


Create_Shared_View = """
mutation CreateSharedView(
    $input: CreateSharedViewInput!
    $condition: ModelSharedViewConditionInput
) {
    createSharedView(input: $input, condition: $condition) {
        id
        datasetPath
        configPath
        owner
        accessibleTo
        createdAt
        updatedAt
        __typename
    }
}"""

Update_Shared_View = """
mutation UpdateSharedView(
    $input: UpdateSharedViewInput!
    $condition: ModelSharedViewConditionInput
) {
    updateSharedView(input: $input, condition: $condition) {
        id
        datasetPath
        configPath
        owner
        accessibleTo
        createdAt
        updatedAt
        __typename
    }
}"""


async def execute_graphql_query(input: ExecuteGraphQLParams) -> dict:
    token = input["token"]
    api_url = input["api_url"]
    variables = input["variables"]
    mutation_type = input["mutation"]
    query = (
        Create_Shared_View
        if mutation_type == "createSharedView"
        else Update_Shared_View
    )

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    async with ClientSession() as session:
        output = None
        async with session.post(
            api_url, json={"query": query, "variables": variables}, headers=headers
        ) as response:
            output = await response.json()
            if (output["data"][mutation_type]) is None:
                raise Exception(f"GraphQL query failed: {output}")
        return output
