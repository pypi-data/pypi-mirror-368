import os
from pathlib import Path

from mastodon import Mastodon


class MastodonManager:
    def __init__(self, bot_working_directory: Path) -> None:
        self.bot_working_directory = bot_working_directory
        self._client: Mastodon | None = None

    @property
    def client(self) -> Mastodon:
        if not self._client:
            if self.access_token is None:
                raise RuntimeError("no access token")

            self._client = Mastodon(access_token=self.access_token)
        return self._client

    def toot(self, text: str) -> None:
        self.client.toot(text)

    @property
    def access_token(self) -> Path:
        return self.bot_working_directory / "access_token"

    @property
    def access_token_exists(self) -> bool:
        return self.access_token is not None and os.path.exists(self.access_token)

    def get_auth_url(self, client_key: str, client_secret: str, api_base_url: str) -> str:
        self._client = Mastodon(client_id=client_key, client_secret=client_secret, api_base_url=api_base_url)
        return self._client.auth_request_url()

    def log_in(self, code: str) -> None:
        if not self._client:
            raise RuntimeError("no access token")
        self._client.log_in(code=code, to_file=self.access_token)
