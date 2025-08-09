from dataclasses import dataclass, field

from capm.entities.PackageConfig import PackageConfig


@dataclass
class Config:
    packages: list[PackageConfig] = field(default_factory=list)
