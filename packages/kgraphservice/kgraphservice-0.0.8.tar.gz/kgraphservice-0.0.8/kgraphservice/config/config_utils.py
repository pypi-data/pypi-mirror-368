import os

import yaml


class ConfigUtils:

    @classmethod
    def load_config(cls, vitalhome) -> dict:

        config_path = os.path.join(vitalhome, "vital-config", "kgraphservice", "kgraphservice_config.yaml")

        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
            return config
