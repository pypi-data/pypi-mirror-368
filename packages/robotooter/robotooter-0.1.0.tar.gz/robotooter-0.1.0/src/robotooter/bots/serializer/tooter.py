import os

from robotooter.models import BotConfig


class SerializerTooter:
    def __init__(self, config: BotConfig) -> None:
        self.working_directory = config.working_directory
        self.data_root = os.path.join(self.working_directory, "data")
        self.filters = config.filter_names

    def generate_content(self) -> str:
        return ''

    def generate_toot(self, hashtags: list[str] | None = None) -> None:
        pass
