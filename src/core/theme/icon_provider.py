from src.util.create_svg_icon import create_svg_icon
from .icons import SVG_ICONS

class IconProvider:
    _cache = {}

    @classmethod
    def get_icon(cls, icon_name, color):
        key = f"{icon_name}_{color}"
        if key not in cls._cache:
            cls._cache[key] = create_svg_icon(SVG_ICONS[icon_name], color).pixmap(14, 14)
        return cls._cache[key]
    

    @classmethod
    def clear_cache(cls):
        cls._cache.clear()