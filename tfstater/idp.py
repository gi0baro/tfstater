import asyncio

from typing import Any, Callable, Dict, List, Optional, Tuple, Type
from urllib.parse import urlencode

from emmett import Pipe, request, redirect, abort, sdict
from httpx import AsyncClient


class IdentityProvider:
    url_authorize: str
    url_exchange: str

    def __init__(self, client_id: str, client_secret: str, **kwargs: Any):
        self.client_id = client_id
        self.client_secret = client_secret

    def authorize_params(self, redirect_url: str) -> Dict[str, str]:
        raise NotImplementedError

    def authorize(self, redirect_url: str):
        redirect(
            f"{self.url_authorize}?{urlencode(self.authorize_params(redirect_url))}"
        )

    async def exchange(self, client: AsyncClient) -> Optional[str]:
        raise NotImplementedError

    async def fetch(self, client: AsyncClient, token: str) -> Any:
        raise NotImplementedError


class Providers:
    registry: Dict[str, Type[IdentityProvider]] = {}

    @classmethod
    def register(
        cls,
        key: str
    ) -> Callable[[Type[IdentityProvider]], Type[IdentityProvider]]:
        def deco(obj: Type[IdentityProvider]) -> Type[IdentityProvider]:
            cls.registry[key] = obj
            return obj
        return deco

    def __init__(self, config):
        self.idps: Dict[str, IdentityProvider] = {}
        for key in set(config.keys()) & set(self.registry.keys()):
            self.idps[key] = self.registry[key](**config[key])

    def get(self, key: str) -> Optional[IdentityProvider]:
        return self.idps.get(key)

    def available(self) -> List[str]:
        return list(self.idps.keys())


class ExchangePipe(Pipe):
    def __init__(self, provider: IdentityProvider):
        self.provider = provider

    async def pipe(self, next_pipe, **kwargs):
        async with AsyncClient() as client:
            token = await self.provider.exchange(client)
            if not token:
                abort(401)
            data = await self.provider.fetch(client, token)
            if not data.get("user"):
                abort(401)
            if not data.get("role"):
                abort(401)
            kwargs.update(**data)
        return await next_pipe(**kwargs)


@Providers.register("github")
class GithubProvider(IdentityProvider):
    url_authorize = "https://github.com/login/oauth/authorize"
    url_exchange = "https://github.com/login/oauth/access_token"

    def __init__(self, client_id: str, client_secret: str, **kwargs: Any):
        super().__init__(client_id, client_secret, **kwargs)
        self.config = sdict(
            scopes = ["user:email", "read:org"]
        )
        self.config.update(kwargs)
        assert self.config.organization, 'Missing organization in github config'

    def authorize_params(self, redirect_url: str) -> Dict[str, str]:
        return {
            "client_id": self.client_id,
            "redirect_uri": redirect_url,
            "scope": ",".join(self.config.scopes)
        }

    async def exchange(self, client: AsyncClient) -> Optional[str]:
        try:
            res = await client.post(
                self.url_exchange,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": request.query_params.code
                },
                headers={
                    "accept": "application/json"
                }
            )
            token = res.json()["access_token"]
        except Exception:
            token = None
        return token

    async def fetch(
        self, client: AsyncClient, token: str
    ) -> Tuple[Dict[str, Any], Optional[str], List[str]]:
        use_teams = bool(self.config.claim_teams or self.config.match_teams)
        reqs = [
            "https://api.github.com/user/emails",
            f"https://api.github.com/user/memberships/orgs/{self.config.organization}"
        ]
        if use_teams:
            reqs.append("https://api.github.com/user/teams?per_page=100")
        udata, orole, troles = {}, None, []
        try:
            res = await asyncio.gather(*[
                client.get(url, headers={
                    "Authorization": f"token {token}"
                }) for url in reqs
            ])
            for element in res[0].json():
                if element["verified"] and element["primary"]:
                    udata = {"email": element["email"]}
                    break
            if res[1].status_code == 200:
                odata = res[1].json()
                if odata["state"] == "active":
                    orole = odata["role"]
            if use_teams:
                tlist = res[2].json()
                for element in filter(
                    lambda v: v["organization"]["login"] == self.config.organization,
                    tlist
                ):
                    troles.append(element["slug"])
        except Exception:
            pass
        return {"user": udata, "role": orole, "teams": troles}
