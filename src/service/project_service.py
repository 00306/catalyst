import datetime
import zipfile
import json
from src.config.app_config import AppConfig
from pathlib import Path
from src.model import ProjectMetadata
from src.ui.model import ProjectListItem
from functools import lru_cache
import io
import numpy as np
import shutil
from dataclasses import fields

class ProjectService:
    
    @staticmethod
    def get_recent_projects():
        if not AppConfig.PROJECT_DIR.exists():
            AppConfig.PROJECT_DIR.mkdir(parents=True, exist_ok=True)
            return []
        
        pkz_files = list(AppConfig.PROJECT_DIR.glob("*.pkz"))
        mdz_files = list(AppConfig.PROJECT_DIR.glob("*.mdz"))
        all_files = pkz_files + mdz_files
        all_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        results = []
        for path in all_files:
            mtime = path.stat().st_mtime
            date_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
            
            metadata = ProjectService.parse_metadata(path)
            item_data = ProjectListItem(file_path=str(path), date_str=date_str, metadata=metadata)
            
            results.append(item_data)

        return results

    @staticmethod
    def parse_metadata(file_path: Path) -> ProjectMetadata:
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                if 'metadata.json' in zf.namelist():
                    with zf.open('metadata.json') as f:
                        meta_dict = json.load(f)

                        class_keys = {f.name for f in fields(ProjectMetadata)}
                        filtered_data = {k: v for k, v in meta_dict.items() if k in class_keys}

                        return ProjectMetadata(**filtered_data)
        except Exception as e:
            print(f"⚠️ [ProjectService] Metadata parse error ({file_path.name}): {e}")
        
        return ProjectMetadata(
            project_name=file_path.stem, 
            description="", 
            mode="Overlay", 
            sample_names=[], 
            detectors=[],
            default_detector="",
            z_unit_dict={}
        )
    
    @staticmethod
    @lru_cache(maxsize=7)
    def load_project_data(file_path):
        with zipfile.ZipFile(file_path, 'r') as zf:
            with zf.open('metadata.json') as f:
                metadata_dict = json.load(f)
                class_fields = {f.name for f in fields(ProjectMetadata)}
                filtered_data = {k: v for k, v in metadata_dict.items() if k in class_fields}
                
                metadata = ProjectMetadata(**filtered_data)

            with zf.open('data.npz') as f:
                data_bytes = f.read()
                npz_data = np.load(io.BytesIO(data_bytes), allow_pickle=False)
                
                data_dict = {key: npz_data[key] for key in npz_data.files}

        return metadata, data_dict
    
    
    @staticmethod
    def update_metadata_in_zip(file_path: str, new_meta_dict: dict):
        temp_path = file_path + ".tmp"

        try:
            with zipfile.ZipFile(file_path, 'r') as zin, zipfile.ZipFile(temp_path, 'w') as zout:
                for item in zin.infolist():
                    if item.filename == 'metadata.json':
                        new_json_str = json.dumps(new_meta_dict, indent=4)
                        zout.writestr('metadata.json', new_json_str)
                    else:
                        zout.writestr(item, zin.read(item.filename))
            
            shutil.move(temp_path, file_path)
            
            ProjectService.load_project_data.cache_clear()
            

        except Exception as e:
            if Path(temp_path).exists():
                Path(temp_path).unlink()
            print(f"❌ [ProjectService] 저장 실패: {e}")
            raise e
        
    @staticmethod
    def delete_project(file_path: str) -> bool:
        try:
            target_path = Path(file_path)
            if target_path.exists():
                target_path.unlink()
                ProjectService.load_project_data.cache_clear()
                return True
            else:
                return False
        except Exception as e:
            print(f"❌ [ProjectService] 프로젝트 삭제 실패: {e}")
            return False

