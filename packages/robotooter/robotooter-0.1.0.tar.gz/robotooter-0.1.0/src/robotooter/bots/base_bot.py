import os
from abc import ABC, abstractmethod
from pathlib import Path

from robotooter.filters.base_filter import BaseFilter
from robotooter.mastodon_manager import MastodonManager
from robotooter.models import BotConfig


class BaseBot(ABC):
    NAME = "BaseTooter"

    @staticmethod
    def new_bot_info() -> str | None:
        return None

    def __init__(self, config: BotConfig, filters: list[BaseFilter]) -> None:
        self.config = config
        self.working_directory = config.working_directory
        self.data_root = Path(os.path.join(self.working_directory, "data"))
        self.filters = filters
        self.mastodon_manager = MastodonManager(self.working_directory)

    @abstractmethod
    def generate_content(self) -> list[str]:
        pass

    @abstractmethod
    def generate_toots(self) -> list[str]:
        pass

    @abstractmethod
    def setup_data(self) -> None:
        pass

    def get_auth_url(self, client_key: str, client_secret: str, api_base_url: str) -> str:
        return self.mastodon_manager.get_auth_url(client_key, client_secret, api_base_url)

    def log_in(self, code: str) -> None:
        return self.mastodon_manager.log_in(code)

    def toot(self) -> None:
        for text in self.generate_toots():
            self.mastodon_manager.toot(text)
