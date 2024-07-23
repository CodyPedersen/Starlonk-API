import os
from typing import Optional

import yaml

class Config:
    """Base configuration class"""

    cfg_file = "config/config.yaml"

    # Configs. Overridden by cfg yaml
    DB_HOST: str = os.getenv("DB_HOST", "0.0.0.0")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_NAME: str = os.getenv("DB_NAME", "postgres")
    DB_PORT: int = int(os.getenv("DB_PORT", '5432'))
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    API_KEY: str = os.getenv("API_KEY", "fill_me_in")

    TEST_CFG: Optional[str] = None

    def __init__(self):
        self.ingest_cfg_from_file()

    def ingest_cfg_from_file(self):
        """Bare-bones config ingestion"""
        with open(self.cfg_file, encoding='utf8') as stream:
            cfg = yaml.safe_load(stream)

        if not isinstance(cfg, dict):
            err = "Unsupported config format"
            raise TypeError(err)

        for key, value in cfg.items():
            setattr(self, key, value)

        assert self.TEST_CFG, "failed to initialize configs"

# hacky singleton enforce
Config = Config()  # type: ignore