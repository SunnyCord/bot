###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import List

import orjson
from aiosu.models import FrozenModel
from common.logging import logger
from pydantic import Field


class RedisConfig(FrozenModel):
    host: str = ""
    port: int = 6379


class MongoConfig(FrozenModel):
    host: str = ""
    database: str = "sunny"
    timeout: int = 10000


class LavalinkConfig(FrozenModel):
    name: str = "local"
    host: str = "lavalink"
    port: int = 2333
    password: str = "youshallnotpass"
    ssl_enabled: bool = False
    heartbeat: int = 50


class LavalinkConfigList(FrozenModel):
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    nodes: List[LavalinkConfig] = Field(default_factory=lambda: [LavalinkConfig()])


class OsuAPIConfig(FrozenModel):
    api_key: str = "key_here"
    client_id: str = 1
    client_secret: str = "secret_here"
    redirect_uri: str = "http://localhost:5000/callback"


class PremiumConfig(FrozenModel):
    boost_limit: int = 2
    support_guild_id: int = 0
    premium_role_id: int = 0
    premium_url: str = "http://ko-fi.com/niceaesth/tiers"


class Config(FrozenModel):
    log_level: str = "WARNING"
    environment: str = "production"
    color: int = 0xD74613
    token: str = ""
    osu_api: OsuAPIConfig = Field(default_factory=OsuAPIConfig)
    osu_daily_key: str = ""
    ordr_key: str = ""
    open_weather_key: str = ""
    sentry: str = ""
    support_invite: str = "https://discord.gg/ufHV3T3UPD"
    premium: PremiumConfig = Field(default_factory=PremiumConfig)
    owners: List[int] = Field(default_factory=lambda: [151670779782758400])
    command_prefixes: List[str] = Field(default_factory=lambda: ["s."])
    redis: RedisConfig = Field(default_factory=RedisConfig)
    mongo: MongoConfig = Field(default_factory=MongoConfig)
    lavalink: LavalinkConfigList = Field(default_factory=LavalinkConfigList)


class ConfigList(FrozenModel):
    select: int = 0
    configs: List[Config] = Field(default_factory=lambda: [Config()])

    def __get_selected_config(self) -> Config:
        return self.configs[self.select]

    @classmethod
    def _create_config(cls) -> None:
        with open("config.json", "a+") as config_file:
            base_config_dict = cls().dict()
            base_config_json = orjson.dumps(
                base_config_dict,
                option=orjson.OPT_INDENT_2,
            ).decode()
            config_file.write(base_config_json)
            logger.warning(
                "A config file was not found! Please edit the newly created `config.json` and run again.",
            )

    @classmethod
    def get_config(cls) -> Config:
        try:
            config_list = cls.parse_file("config.json")
            return config_list.__get_selected_config()
        except FileNotFoundError:
            cls._create_config()
            exit(1)
