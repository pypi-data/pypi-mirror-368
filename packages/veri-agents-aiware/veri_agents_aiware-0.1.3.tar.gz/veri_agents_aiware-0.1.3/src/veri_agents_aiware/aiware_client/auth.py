import os
import httpx
from abc import ABC, abstractmethod

class AbstractTokenAuth(httpx.Auth, ABC):
    @abstractmethod
    def get_token(self) -> str:
        pass

    def sync_auth_flow(self, request):
        token = self.get_token()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request

    async def async_auth_flow(self, request):
        token = self.get_token()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request

class EnvAuth(AbstractTokenAuth):
    def get_token(self):
        token = os.environ.get("VERITONE_SESSION_ID")
        if token is None:
            raise Exception("No VERITONE_SESSION_ID env variable found")
        return token
    
class TokenAuth(AbstractTokenAuth):
    def __init__(self, token: str):
        super().__init__()
        self.token = token

    def get_token(self):
        return self.token
