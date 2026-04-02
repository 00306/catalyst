from dataclasses import dataclass
from src.model.project_config import ProjectMetadata

@dataclass
class ProjectListItem:
    file_path: str
    date_str: str
    metadata: ProjectMetadata