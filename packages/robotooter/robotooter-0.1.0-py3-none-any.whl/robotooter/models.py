from pathlib import Path

from pydantic import BaseModel


class MastodonAppConfig(BaseModel):
    name: str
    mastodon_base_url: str
    client_key: str
    client_secret: str
    token: str

class BotConfig(BaseModel):
    bot_name: str
    bot_class: str
    mastodon_config: MastodonAppConfig | None
    working_directory: Path
    tags: list[str] | None = None
    toot_prepend: str | None = None
    toot_append: str | None = None
    filter_names: list[str] = []


class RoboTooterConfig(BaseModel):
    working_directory: Path
    filters: list[str] = []
    tooters: list[str] = []
