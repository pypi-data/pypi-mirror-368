import httpx
from veri_agents_aiware.aiware_client.search.models import VectorSearchRequest, VectorSearchResults

class AiwareSearch(httpx.Client):
    def vector_search(self, request: VectorSearchRequest) -> VectorSearchResults:
        data = request.model_dump(mode='json', exclude_unset=True)
        response = self.post("/vector", json=data)
        response.raise_for_status()

        return VectorSearchResults.model_validate_json(response.text)
