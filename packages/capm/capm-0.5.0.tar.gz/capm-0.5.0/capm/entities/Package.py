from dataclasses import dataclass


@dataclass
class Package:
    image: str
    args: str
    workspace_mode: str = 'ro'
