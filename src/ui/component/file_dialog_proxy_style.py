from PyQt5.QtWidgets import QProxyStyle, QStyle
from src.util.create_svg_icon import create_svg_icon
from src.core.theme.icons import SVG_ICONS

class FileDialogIconProxyStyle(QProxyStyle):

    def __init__(self, icon_color, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon_color = icon_color

        self._icon_cache = {}
        icon_mapping = {
            QStyle.SP_ArrowBack: SVG_ICONS["arrow_left"],
            QStyle.SP_ArrowForward: SVG_ICONS["arrow_right"],
            QStyle.SP_FileDialogToParent: SVG_ICONS["arrow_up"],
            QStyle.SP_FileDialogNewFolder: SVG_ICONS["folder_plus"],
            QStyle.SP_FileDialogListView: SVG_ICONS["list"],
            QStyle.SP_FileDialogDetailedView: SVG_ICONS["list_collapse"]
        }

        for standard_icon, svg_string in icon_mapping.items():
                
                self._icon_cache[standard_icon] = create_svg_icon(svg_string, self.icon_color)

    
    def standardIcon(self, standardIcon, option=None, widget=None):
        if standardIcon in self._icon_cache:
            return self._icon_cache[standardIcon]

        return super().standardIcon(standardIcon, option, widget)