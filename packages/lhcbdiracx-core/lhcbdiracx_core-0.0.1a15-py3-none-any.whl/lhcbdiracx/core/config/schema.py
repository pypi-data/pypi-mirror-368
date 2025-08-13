from __future__ import annotations

# mypy: disable-error-code="assignment"
from typing import MutableMapping

from diracx.core.config.schema import BaseModel
from diracx.core.config.schema import Config as _Config
from diracx.core.config.schema import OperationsConfig as _OperationsConfig

"""
In order to add extra config, you need to redefine
the whole tree down to the point you are interested in changing
"""


class AnalysisProductionsConfig(BaseModel):
    ForceActiveInput: list[str] = []


class OperationsConfig(_OperationsConfig):
    AnalysisProductions: AnalysisProductionsConfig = AnalysisProductionsConfig()


class Config(_Config):

    Operations: MutableMapping[str, OperationsConfig]
