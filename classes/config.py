import logging
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import List

logger = logging.getLogger("discord")


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
    redis: bool = True
    log_level: str = "WARNING"
    color: int = 0xD74613
    token: str = ""
    osuAPI: str = ""
    sentry: str = ""
    owners: List[int] = field(default_factory=lambda: [151670779782758400])
    command_prefixes: List[str] = field(default_factory=lambda: ["s."])
    mongo: MongoConfig = field(default_factory=lambda: MongoConfig())
    ppAPI: PPConfig = field(default_factory=lambda: PPConfig())
    lavalink: List[LavalinkConfig] = field(default_factory=lambda: [LavalinkConfig()])


@dataclass_json
@dataclass(frozen=True)
class ConfigList:
    __comment: str = "select -> index of config to use (starting from 0)"
    select: int = 0
    configs: List[Config] = field(default_factory=lambda: [Config()])

    def __get_selected_config(self):
        return self.configs[self.select]

    @classmethod
    def get_config(cls) -> "Config":
        with open("config.json", "a+") as config_file:
            config_file.seek(0)
            data = config_file.read()
            if data:
                config_file.close()
                return cls.from_json(data).__get_selected_config()
            fmt = cls().to_json(indent=4)
            config_file.write(fmt)
            logger.warn(
                "A config file was not found! Please edit the newly created `config.json` and run again."
            )
            config_file.close()
            exit()
