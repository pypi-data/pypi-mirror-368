import json
import os
from pathlib import Path

from robotooter.bots.base_bot import BaseBot
from robotooter.filters.base_filter import BaseFilter
from robotooter.models import BotConfig, MastodonAppConfig, RoboTooterConfig
from robotooter.util import load_included


class RoboTooter:
    __version__ = "0.1.0"
    def __init__(self, config: RoboTooterConfig) -> None:
        if config is None:
            config = RoboTooterConfig(
                working_directory=Path(os.path.expanduser("~/.robotooter")),
            )
        self.config = config
        self._filters: dict[str, type[BaseFilter]] = {}
        self._bots: dict[str, type[BaseBot]] = {}

        self._import_filters()
        self._import_bots()

    @property
    def is_configured(self) -> bool:
        return os.path.exists(self.config.working_directory / "config.json")

    def save_configuration(self) -> None:
        if not os.path.exists(self.config.working_directory):
            os.makedirs(self.config.working_directory)

        with open(self.config.working_directory / "config.json", "w") as config_file:
            config_file.write(self.config.model_dump_json(indent=2))

    def create_new_bot(
        self,
        bot_name: str,
        bot_class: str,
        filter_names: list[str],
        mastodon_config: MastodonAppConfig | None = None,
        tags: list[str] | None = None,
        toot_prepend: str | None = None,
        toot_append: str | None = None,
    ) -> None:
        if bot_class not in self._bots.keys():
            raise ValueError(f"Invalid bot class {bot_class}")
        for filter_name in filter_names:
            if filter_name not in self._filters.keys():
                raise ValueError(f"Invalid filter name {filter_name}")

        bot_working_directory = self.config.working_directory / bot_name
        os.makedirs(bot_working_directory, exist_ok=True)

        if tags is None:
            tags = []

        bot_config = BotConfig(
            bot_name=bot_name,
            bot_class=bot_class,
            filter_names=filter_names,
            mastodon_config=mastodon_config,
            working_directory=bot_working_directory,
            tags=tags,
            toot_prepend=toot_prepend,
            toot_append=toot_append,
        )
        self._save_bot_config(bot_config)

    def load_bot(self, bot_name: str) -> BaseBot:
        bot_config = self._load_bot_config(bot_name)
        bot_class = self._bots[bot_config.bot_class]
        bot_filters: list[BaseFilter] = []
        for filter_name in bot_config.filter_names:
            bot_filters.append(self._filters[filter_name]())

        return bot_class(bot_config, bot_filters)

    def _import_filters(self) -> None:
        self._filters = load_included('robotooter.filters', BaseFilter, 'Filter')

    def _import_bots(self) -> None:
        self._bots = load_included('robotooter.bots', BaseBot, 'Bot')

    def _save_bot_config(self, bot_config: BotConfig) -> None:
        with open(self.config.working_directory / f"{bot_config.bot_name}.json", "w") as config_file:
            config_file.write(bot_config.model_dump_json(indent=2))

    def _load_bot_config(self, bot_name: str) -> BotConfig:
        with open(self.config.working_directory / f"{bot_name}.json", "r") as config_file:
            json_config = json.load(config_file)
            return BotConfig(**json_config)


def load_robo_tooter() -> RoboTooter:
    config_path = Path(os.path.expanduser('~/.robotooter'))

    config = RoboTooterConfig(working_directory=config_path)
    return RoboTooter(config)
