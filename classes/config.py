import os
import json
from typing import List, Dict


class Config:
    def __init__(
        self,
        redis: bool,
        mongo: Dict,
        lavalink: List[Dict],
        sentry: str,
        command_prefixes: List,
        token: str,
        osuAPI: str,
        ppAPI: Dict,
        owners: List[int],
        color: int,
    ):
        self.redis = redis
        self.mongo = mongo
        self.lavalink = lavalink
        self.sentry = sentry
        self.command_prefixes = command_prefixes
        self.token = token
        self.osuAPI = osuAPI
        self.ppAPI = ppAPI
        self.owners = owners
        self.color = color

    @classmethod
    def fromJSON(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError("Provided path is invalid!")
        else:
            with open(path, "r") as configJSON:
                configData = configJSON.read()

            # Parse JSON file
            configDict = json.loads(configData)
            selectedConfig = configDict["configs"][configDict["select"]]
            configJSON.close()
            return self(
                configDict["redis"],
                selectedConfig["mongo"],
                list(selectedConfig["lavalink"]),
                selectedConfig["sentry"],
                selectedConfig["command_prefixes"],
                str(selectedConfig["token"]),
                str(selectedConfig["osuAPI"]),
                selectedConfig["ppAPI"],
                list(selectedConfig["owners"]),
                int(selectedConfig["color"], 16),
            )
