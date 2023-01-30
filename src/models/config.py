from __future__ import annotations

import logging
from dataclasses import dataclass
from dataclasses import field
from typing import List

from dataclasses_json import dataclass_json

logger = logging.getLogger("discord")


@dataclass(frozen=True)
class RedisConfig:
    host: str = ""
    port: int = 6379


@dataclass(frozen=True)
class MongoConfig:
    host: str = ""
    database: str = "sunny"
    timeout: int = 10000


@dataclass(frozen=True)
class PPConfig:
    host: str = "https://oldpp.aesth.dev"
    secret: str = "potato"


@dataclass(frozen=True)
class LavalinkConfig:
    host: str = "lavalink"
    port: int = 2333
    password: str = "youshallnotpass"
    region: str = "eu"
    name: str = "local"


@dataclass(frozen=True)
class Config:
    log_level: str = "WARNING"
    color: int = 0xD74613
    token: str = ""
    osuAPI: str = ""
    sentry: str = ""
    owners: List[int] = field(default_factory=lambda: [151670779782758400])
    command_prefixes: List[str] = field(default_factory=lambda: ["s."])
    redis: RedisConfig = field(default_factory=lambda: RedisConfig())
    mongo: MongoConfig = field(default_factory=lambda: MongoConfig())
    ppAPI: PPConfig = field(default_factory=lambda: PPConfig())
    lavalink: List[LavalinkConfig] = field(default_factory=lambda: [LavalinkConfig()])


@dataclass_json
@dataclass(frozen=True)
class ConfigList:
    __comment: str = "select -> index of config to use (starting from 0)"
    select: int = 0
    configs: List[Config] = field(default_factory=lambda: [Config()])

    def __get_selected_config(self) -> Config:
        return self.configs[self.select]

    @classmethod
    def _create_config(cls) -> None:
        with open("config.json", "a+") as config_file:
            fmt = cls().to_json(indent=4)  # type:ignore
            config_file.write(fmt)
            logger.warn(
                "A config file was not found! Please edit the newly created `config.json` and run again.",
            )
            config_file.close()

    @classmethod
    def get_config(cls) -> Config:
        with open("config.json") as config_file:
            config_file.seek(0)
            data = config_file.read()
            if data:
                config_file.close()
                return cls.from_json(data).__get_selected_config()  # type: ignore
            cls._create_config()
            exit()
