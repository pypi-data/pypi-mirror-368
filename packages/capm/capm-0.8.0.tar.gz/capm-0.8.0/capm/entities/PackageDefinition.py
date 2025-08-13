from dataclasses import dataclass


@dataclass
class PackageDefinition:
    image: str
    args: str
    install_command: str | None = None
    entrypoint: str | None = None
    workspace_mode: str = 'ro'
