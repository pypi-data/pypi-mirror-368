from types import TracebackType
from typing import Optional, Self

import httpx
from veri_agents_aiware.aiware_client.auth import EnvAuth
from veri_agents_aiware.aiware_client.graphql.client.client import AiwareGraphQL
from veri_agents_aiware.aiware_client.search.client import AiwareSearch

class Aiware:
    def __init__(
        self,
        graphql_endpoint="https://api.us-1.veritone.com/v3/graphql",
        search_endpoint="https://api.us-1.veritone.com/v1/search",
        auth: Optional[httpx.Auth] = EnvAuth(),
    ):
        self.graphql_endpoint = graphql_endpoint
        self.search_endpoint = search_endpoint

        self.graphql: AiwareGraphQL = AiwareGraphQL(url=self.graphql_endpoint, http_client=httpx.Client(auth=auth))
        self.search: AiwareSearch = AiwareSearch(base_url=self.search_endpoint, auth=auth)

    def __enter__(self: Self) -> Self:
        self.graphql.__enter__()
        self.search.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ) -> None:
        self.graphql.__exit__(exc_type=exc_type, exc_val=exc_value, exc_tb=traceback)
        self.search.__exit__(exc_type=exc_type, exc_value=exc_value, traceback=traceback)

    def with_auth(self, auth: httpx.Auth) -> "Aiware":
        return Aiware(
            graphql_endpoint=self.graphql_endpoint,
            search_endpoint=self.search_endpoint,
            auth=auth
        )
