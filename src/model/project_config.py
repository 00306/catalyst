from dataclasses import dataclass, asdict, field
from typing import List, Dict
from pathlib import Path

@dataclass
class ProjectConfig:
    project_name: str
    description: str
    mode: str
    folder_paths: List[str]
    target_detector: str
    common_detectors: List[str]
    save_path: Path


@dataclass
class ProjectMetadata:
    project_name: str
    description: str
    mode: str
    sample_names: List[str]
    detectors: List[str]
    default_detector: str
    z_unit_dict: Dict[str, str]
    methods: Dict[str, str] = field(default_factory=dict)
    instruments: Dict[str, str] = field(default_factory=dict)
    analysis_dates: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)