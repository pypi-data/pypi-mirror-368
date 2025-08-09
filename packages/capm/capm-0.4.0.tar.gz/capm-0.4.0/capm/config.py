from dataclasses import asdict
from pathlib import Path

import yaml

from capm.entities.Config import Config
from capm.entities.PackageConfig import PackageConfig


def load_config(data: str) -> Config:
    config_dict = yaml.safe_load(data)
    if not config_dict:
        return Config()
    package_configs_list = config_dict.get('packages', [])
    package_configs = [PackageConfig(**pc) for pc in package_configs_list]
    return Config(packages=package_configs)


def load_config_from_file(path: Path) -> Config:
    if not path.exists():
        return Config()
    else:
        with open(path, 'r') as file:
            return load_config(file.read())


def save_config_to_file(config: Config, path: Path):
    dict_factory = lambda x: {k: v for (k, v) in x if v is not None}
    with open(path, 'w') as file:
        yaml.dump(asdict(config, dict_factory=dict_factory), file)


class Settings:
    workspace_dir: Path = Path('/capm/workspace')
    reports_dir: Path = Path('/capm/reports')


run_commands = Settings()
