from pathlib import Path
import json

class AppConfig:
    APP_NAME = 'Catalyst'
    BASE_DIR = Path.home() / "Documents" / APP_NAME
    PROJECT_DIR = BASE_DIR / "Projects"
    CALIBRATION_DIR = BASE_DIR / "Calibrations"
    PRESET_FILE = CALIBRATION_DIR / "presets.json"
    
    _current_theme_name = "for_human"

    @classmethod
    def initialize(cls):
        cls.PROJECT_DIR.mkdir(parents=True, exist_ok=True)
        cls.CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_project_files(cls):
        if not cls.PROJECT_DIR.exists():
            return []
        
        files = list(cls.PROJECT_DIR.glob("*.pkz")) + list(cls.PROJECT_DIR.glob("*.xpz"))
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return files
    
    @classmethod
    def get_calibration_presets(cls):
        if not cls.PRESET_FILE.exists():
            return {}
        
        try:
            with open(cls.PRESET_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
            
        except (json.JSONDecodeError, IOError):
            return {}
        
    @classmethod
    def _write_presets(cls, presets):
        with open(cls.PRESET_FILE, 'w', encoding='utf-8') as f:
            json.dump(presets, f, indent=4, ensure_ascii=False)
        
    @classmethod 
    def save_calibration_preset(cls, name, data):
        cls.CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)

        presets = cls.get_calibration_presets()
        presets[name] = data
        cls._write_presets(presets)

    @classmethod
    def delete_calibration_preset(cls, name):
        presets = cls.get_calibration_presets()
        cls._write_presets(presets)


