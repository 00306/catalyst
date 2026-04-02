import json
from PyQt5.QtCore import QObject, pyqtSignal
from src.core.theme.tokens import UI_TAG
from src.util.resource_path import resource_path
import os

class ThemeManager(QObject):
    theme_changed = pyqtSignal(str)
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ThemeManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if ThemeManager._initialized:
            return
            
        super().__init__()
        
        self.current_mode = "dark"
        self.json_path = resource_path("asset/theme/tokens.json")

        self.load_data()

        ThemeManager._initialized = True
    
    def load_data(self):

        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.palette = data["global"]["colors"]
            self.semantics = data["semantic"]
            self.font_palette = data["global"].get("fonts", {})

        except FileNotFoundError:
            self.font_palette = {}
            self.palette = {}
            self.semantics = {"dark": {}, "paper": {}}

    
    def get_resolved_theme(self):
        mode_data = self.semantics.get(self.current_mode, {})

        resolved = {}
        
        colors_data = mode_data.get("colors", {})
        for key, color_name in colors_data.items():
            resolved[key] = self.palette.get(color_name, color_name)
            
        typo_data = mode_data.get("typography", {})
        for key, typo_val in typo_data.items():
            if key == "font_family_main":
                resolved[key] = self.font_palette.get(typo_val, typo_val)
            else:
                resolved[key] = typo_val
        
        return resolved
    
    def get_graph_theme(self):
        t = self.get_resolved_theme()

        def c(key, default="#ffffff"): return t.get(key, default)

        return {
            "bg_base": c(UI_TAG.BG_CARD_SECONDARY, "#323232"),
            "bg_card": c(UI_TAG.BG_GRAPH_AREA, "#2B2B2B"),
            "border": c(UI_TAG.BORDER_BASE, "#404040"),
            "title_text": c(UI_TAG.TEXT_ACTION, "#64D2FF"),
            "text": c(UI_TAG.TEXT_PRIMARY, "#A0A0A0"),
            "text_accent": c(UI_TAG.TEXT_ACCENT, "#64D2FF"),
            "bg_paper": c(UI_TAG.BG_GRAPH_AREA, "#2B2B2B"),
            "plot_line": c(UI_TAG.PLOT_LINE, "ffffff"),
            "grid_line": c(UI_TAG.PLOT_GRID, "#454545"),
            "axis_line": c(UI_TAG.BORDER_BASE, "#404040"),
            "axis_title": c(UI_TAG.TEXT_SECONDARY, "#A0A0A0"),
            "guide_line": "rgba(255, 255, 255, 0.4)",
            "slice_line": c(UI_TAG.SLICE_LINE, "#E0E0E0")
        }

    def get_qss(self):
        t = self.get_resolved_theme()

        font_main = t.get("font_family_main", "Arial")
        font_size = t.get("font_size_body", "14px")

        def c(key): return t.get(key, "#ffffff")

        return f"""
            * {{
                font-family: "{font_main}";
            }}

            QWidget[class~="{UI_TAG.BG_BASE}"] {{
                background-color: {c(UI_TAG.BG_BASE)};
            }}

            #transparent_scroll_area, 
            #transparent_viewport, 
            #transparent_content_widget {{
                background-color: transparent;
                border: none;
            }}

            QWidget[class~="{UI_TAG.BG_HEADER}"] {{
                background-color: {c(UI_TAG.BG_HEADER)};
                border: 1px solid {c(UI_TAG.BORDER_BASE)};
            }}

            QWidget[class~="{UI_TAG.BG_ITEM}"] {{
                background-color: {c(UI_TAG.BG_ITEM)};
                border: 1px solid {c(UI_TAG.BORDER_BASE)};

            }}

            QWidget[class~="{UI_TAG.BG_CARD_SECONDARY}"][isSelected="true"] {{
                border: 2px solid {c(UI_TAG.BORDER_FOCUS)}; 
            }}

            QWidget[class~="{UI_TAG.BG_GRAPH_AREA}"] {{
                background-color: {c(UI_TAG.BG_GRAPH_AREA)};
                border-radius: 20px;
                border: 1px solid {c(UI_TAG.BORDER_BASE)};
            }}

            QCheckBox[class~="{UI_TAG.TEXT_SECONDARY}"] {{
                color: {c(UI_TAG.TEXT_SECONDARY)};
                outline: none;
            }}

            QCheckBox::indicator {{
                border-radius: 4px;
                border: 1.2px solid {c(UI_TAG.BORDER_BASE)};
                background-color: {c(UI_TAG.BG_INPUT)};
            }}

            QCheckBox::indicator:checked {{
                background-color: {c(UI_TAG.BG_SELECTED)};
                border: 1.2px solid {c(UI_TAG.TEXT_SECONDARY)};
                
            }}

            QDialog[class~="{UI_TAG.BG_ALERT}"] {{
                background-color: {c(UI_TAG.BG_ALERT)};

            }}

            QTextEdit[class~="{UI_TAG.BG_INPUT}"],
            QComboBox[class~="{UI_TAG.BG_INPUT}"], 
            QLineEdit[class~="{UI_TAG.BG_INPUT}"] {{
                background-color: {c(UI_TAG.BG_INPUT)};
                color: {c(UI_TAG.TEXT_PRIMARY)};
                border: 1px solid {c(UI_TAG.BORDER_BASE)};
                border-radius: 6px;
                padding: 5px;
            }}

            QComboBox[class~="{UI_TAG.BG_INPUT}"]:hover {{
                border: 1px solid {c(UI_TAG.BORDER_FOCUS)}; 
            }}

            QComboBox[class~="{UI_TAG.BG_INPUT}"]::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;         
                border-left: none;   
            }}

            QComboBox[class~="{UI_TAG.BG_INPUT}"] QAbstractItemView {{
                background-color: {c(UI_TAG.BG_CARD_SECONDARY)}; /* 원래 #2C2C2E 대응 */
                border: 1px solid {c(UI_TAG.BORDER_BASE)};
                selection-background-color: {c(UI_TAG.BG_SELECTED)};
                color: {c(UI_TAG.TEXT_PRIMARY)};
                outline: none;
            }}

            QComboBox[class~="{UI_TAG.BG_INPUT}"]:disabled,
            QLineEdit[class~="{UI_TAG.BG_INPUT}"]:disabled {{
                background-color: {c(UI_TAG.BG_BASE)}; 
                color: {c(UI_TAG.ACTION_DISABLED)}; 
                border: 1px solid {c(UI_TAG.BG_BASE)}; 
            }}



            QComboBox[class~="{UI_TAG.BG_INPUT}"]::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;         
                border-left: none;   
            }}

            QLineEdit[class~="{UI_TAG.BG_INPUT}"]:read-only {{
                background-color: {c(UI_TAG.BG_BASE)};
                color: {c(UI_TAG.TEXT_SECONDARY)};
            }}

            QLabel {{
                background-color: transparent;
                border: none;
            }}

            QLabel[class~="{UI_TAG.TEXT_DANGER}"] {{
                color: {c(UI_TAG.TEXT_DANGER)};
                font-size: 10px;
                font-weight: bold;
            }}

            QLabel[class~="{UI_TAG.BG_QUOTE}"] {{
                border-left: 3px solid {c(UI_TAG.TEXT_ACCENT)}; 
                color: {c(UI_TAG.TEXT_SECONDARY)};
                padding-left: 15px;
                padding-top: 5px;
                padding-bottom: 5px;
            }}

            QLabel[class~="{UI_TAG.TEXT_ITEM_TITLE}"] {{
                color: {c(UI_TAG.TEXT_ITEM_TITLE)};
                font-size: 12px;
            }}

            QLabel[class~="{UI_TAG.TEXT_ITEM_SUBTITLE}"] {{
                color: {c(UI_TAG.TEXT_ITEM_SUBTITLE)};
                font-size: 10px;
            }}

            QTableWidget[class~="{UI_TAG.TEXT_PRIMARY}"] {{
                color: {c(UI_TAG.TEXT_PRIMARY)};
                outline: none;
            }}
            
            QTableWidget[class~="{UI_TAG.BG_PANEL}"] {{
                background-color: {c(UI_TAG.BG_PANEL)};
                gridline-color: {c(UI_TAG.BORDER_BASE)}; 
                border: 1px solid {c(UI_TAG.BORDER_BASE)};
                border-radius: 4px;
                
            }}

            QTableWidget::item:selected {{
                background-color: {c(UI_TAG.BG_SELECTED)};
                color: {c(UI_TAG.TEXT_ACTION)};
                outline: none;
            }}

            QTableWidget::item:focus {{
                outline: none;
                border: none;

            }}

            QWidget[class~="{UI_TAG.BG_CARD_PRIMARY}"] {{
                background-color: {c(UI_TAG.BG_CARD_PRIMARY)};
                border: 1px solid {c(UI_TAG.BORDER_BASE)};
                border-radius: 12px;
            }}

            QWidget[class~="{UI_TAG.BG_CARD_SECONDARY}"] {{
                background-color: {c(UI_TAG.BG_CARD_SECONDARY)};
                border: 1px solid {c(UI_TAG.BORDER_BASE)};
                border-radius: 12px;
            }}

            QLabel[class~="{UI_TAG.TEXT_ACCENT}"] {{
                color: {c(UI_TAG.TEXT_ACCENT)};
                font-size: 14px;
                font-weight: bold;
            }}

            QFrame[class~="{UI_TAG.BG_CARD_SECONDARY}"] {{
                background-color: {c(UI_TAG.BG_CARD_SECONDARY)};
                border: 1px solid {c(UI_TAG.BORDER_BASE)};
                border-radius: 10px;
            }}

            QFrame[class~="{UI_TAG.BORDER_BASE}"] {{
                background-color: {c(UI_TAG.BORDER_BASE)};
            }}

            QFrame[class~="{UI_TAG.BG_BADGE}"] {{
                background-color: {c(UI_TAG.BG_BADGE)};
                border: 1px solid {c(UI_TAG.BORDER_BASE)};
                border-radius: 8px;
            }}

            QHeaderView[class~="{UI_TAG.BG_PANEL}"]::section {{
                background-color: {c(UI_TAG.BG_BASE)};
                color: {c(UI_TAG.TEXT_ACCENT)};
                font-weight: bold;
                border: none;
                border-right: 1px solid {c(UI_TAG.BORDER_BASE)};
                border-bottom: 1px solid {c(UI_TAG.BORDER_BASE)};
                padding: 4px;
            }}

            QFrame[class~="{UI_TAG.BG_ALERT}"] {{
                background-color: {c(UI_TAG.BG_ALERT)};
                border-radius: 16px;
                border: 1px solid {c(UI_TAG.BORDER_BASE)};

            }}

            QFrame[class~="{UI_TAG.BG_SELECTED}"] {{
                border: 1px solid {c(UI_TAG.BORDER_FOCUS)};
            }}

            QLabel[class~="{UI_TAG.TEXT_PANEL_HEADER}"] {{
                color: {c(UI_TAG.TEXT_PANEL_HEADER)};
                font-size: 12px;     
                font-weight: bold;
                padding-top: 2px;   
                padding-bottom: 2px; 
                padding-left: 2px;
            }}

            QLabel[class~="{UI_TAG.TEXT_VIEW_TITLE}"] {{
                color: {c(UI_TAG.TEXT_VIEW_TITLE)};
                font-size: 16px; 
                font-weight: bold;
            }}

            QLabel[class~="{UI_TAG.TEXT_VIEW_SUBTITLE}"] {{
                color: {c(UI_TAG.TEXT_VIEW_SUBTITLE)};
                font-size: 14px; 
            }}

            QPushButton[class~="{UI_TAG.BTN_PANEL_ADD}"] {{
                background-color: transparent;
                color: #8E8E93;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                outline: none;
            }}

            QPushButton[class~="{UI_TAG.BTN_PANEL_ADD}"]:hover {{
                background-color: {c(UI_TAG.BG_BTN_PANEL_FOCUS)};
                color: {c(UI_TAG.BTN_PANEL_ADD_HOVER)};
            }}

            QPushButton[class~="{UI_TAG.BTN_PRIMARY}"] {{
                background-color: {c(UI_TAG.ACTION_PRIMARY)};
                color: {c(UI_TAG.TEXT_ACTION)};
                border: none;
                border-radius: 6px;
                padding: 6px 15px;
                font-weight: bold;
                outline: none;
            }}

            QPushButton[class~="{UI_TAG.BTN_PRIMARY}"]:disabled {{
                background-color: {c(UI_TAG.ACTION_DISABLED)}; 
                color: {c(UI_TAG.TEXT_DISABLED)};
            }}

            QPushButton[class~="{UI_TAG.BTN_PRIMARY}"]:hover {{
                background-color: {c(UI_TAG.ACTION_HOVER)};
                color: {c(UI_TAG.TEXT_ACTION)};
            }}

            QPushButton[class~="{UI_TAG.BTN_SECONDARY}"] {{
                background-color: transparent;
                color: {c(UI_TAG.TEXT_SECONDARY)};
                border: 1px solid {c(UI_TAG.BORDER_BASE)};
                border-radius: 6px;
                padding: 6px 15px;
                font-weight: bold;
                outline: none;
            }}

            QPushButton[class~="{UI_TAG.BTN_SECONDARY}"]:hover {{
                background-color: {c(UI_TAG.BG_BTN_PANEL_FOCUS)};
                color: {c(UI_TAG.TEXT_PRIMARY)};
            }}

            QPushButton[class~="{UI_TAG.BTN_DANGER}"] {{
                background-color: {c(UI_TAG.BG_DANGER)};
                color: {c(UI_TAG.ACTION_DANGER)};
                border: 1px solid {c(UI_TAG.ACTION_DANGER)};
                border-radius: 6px;
                padding: 6px 15px;
                font-weight: bold;
            }}
            
            QPushButton[class~="{UI_TAG.BTN_DANGER}"]:hover {{
                background-color: {c(UI_TAG.ACTION_DANGER)};
                color: white;
            }}

            QPushButton[class="segment-button"] {{
            padding: 8px 16px;
            background-color: {c(UI_TAG.BG_CARD_SECONDARY)};
            border: 1px solid {c(UI_TAG.BORDER_BASE)};
            color: {c(UI_TAG.TEXT_SECONDARY)};
            }}

            QPushButton[class="segment-button"] {{
                padding: 8px 16px;
                background-color: {c(UI_TAG.BG_CARD_SECONDARY)}; /* 기본 배경 */
                border: 1px solid {c(UI_TAG.BORDER_BASE)};
                color: {c(UI_TAG.TEXT_SECONDARY)};
            }}

            QPushButton[class="segment-button"]:focus {{
                outline: none;
            }}

            /* 2. 위치별 라운드 (여기서 배경색을 건드리지 마세요) */
            QPushButton[class="segment-button"][position="first"]  {{ border-top-left-radius: 6px; border-bottom-left-radius: 6px; }}
            QPushButton[class="segment-button"][position="middle"] {{ border-radius: 0px; }}
            QPushButton[class="segment-button"][position="last"]   {{ border-top-right-radius: 6px; border-bottom-right-radius: 6px; }}

            /* 3. 호버 상태 */
            QPushButton[class="segment-button"]:hover {{
                background-color: {c(UI_TAG.BG_BTN_PANEL_FOCUS)};
            }}

            /* 4. 체크 상태 (여기가 중요! !important 급으로 명시) */
            QPushButton[class="segment-button"]:checked {{
                background-color: {c(UI_TAG.BG_SELECTED)}; /* 또는 ACTION_PRIMARY */
                border: 1px solid {c(UI_TAG.BORDER_FOCUS)}; /* 테두리도 하이라이트 */
            }}

            QLabel[class~="{UI_TAG.TEXT_BADGE}"] {{
                color: {c(UI_TAG.TEXT_BADGE)};
                font-size: 10px;
                font-weight: bold;

            }}

            QLabel[class~="{UI_TAG.TEXT_PRIMARY}"] {{
                color: {c(UI_TAG.TEXT_PRIMARY)};
                font-size: 16px;
                font-weight: bold;
            }}
            
            QLabel[class~="{UI_TAG.TEXT_SECONDARY}"] {{
                color: {c(UI_TAG.TEXT_SECONDARY)};
                font-size: 10px;
            }}

            QLabel[class~="{UI_TAG.TEXT_ALERT_BODY}"] {{
                color: {c(UI_TAG.TEXT_PRIMARY)};
                font-size: 14px;
                font-weight: bold;

            }}

            QListWidget[class~="{UI_TAG.BG_PANEL}"] {{
                outline: none;
                border: none;
                padding-top: 8px;
                padding-bottom: 8px;
                padding-right: 8px;
                border-radius: 10px;
                background-color: {c(UI_TAG.BG_PANEL)};
            }}

            QListWidget[class~="{UI_TAG.BG_PANEL}"]::item {{
                padding-left: 6px;
                background: transparent;
                border: none;
            }}

            QListWidget[class~="{UI_TAG.BG_PANEL}"]::item:selected,
            QListWidget[class~="{UI_TAG.BG_PANEL}"]::item:focus {{
                background: transparent;
                border: none;
                outline: none;
            }}
        
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 8px;
                margin: 0px;
            }}

            /* 스크롤바 손잡이 (기본) */
            QScrollBar::handle:vertical {{
                background-color: {c(UI_TAG.BORDER_BASE)}; /* 기존 #4A4A4C 대신 테두리색 활용 */
                min-height: 30px;
                border-radius: 4px;
            }}

            /* 스크롤바 손잡이 (마우스 올렸을 때) */
            QScrollBar::handle:vertical:hover {{
                background-color: {c(UI_TAG.TEXT_SECONDARY)}; /* 기존 #6A6A6C 대신 보조 텍스트색 활용 */
            }}

            /* 위아래 화살표 및 빈 공간(페이지) 배경 투명하게 날리기 */
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                height: 0px;
                border: none;
                background: none;
            }}

            #DropZone[dropState="normal"] {{
                background-color: {c(UI_TAG.BG_BASE)};
                border: 1px solid {c(UI_TAG.BORDER_BASE)};
                border-radius: 15px;
            }}
            #DropZone[dropState="normal"] QLabel {{
                color: {c(UI_TAG.TEXT_PRIMARY)};
            }}

            /* 2. 호버 상태 (Hover) - 마우스 올라갔을 때 */
            #DropZone[dropState="hover"] {{
                background-color: {c(UI_TAG.BG_CARD_PRIMARY)};
                border: 1.5px dashed {c(UI_TAG.BORDER_FOCUS)}; /* 파란색 계열 테마 */
                border-radius: 15px;
            }}
            #DropZone[dropState="hover"] QLabel {{
                color: {c(UI_TAG.TEXT_PRIMARY)};
            }}

            /* 3. 드래그 상태 (Drag) - 파일을 쥐고 들어왔을 때 */
            #DropZone[dropState="drag"] {{
                background-color: {c(UI_TAG.BG_SELECTED)}; 
                border: 1.5px dashed {c(UI_TAG.BORDER_FOCUS)}; 
                border-radius: 15px;
            }}
            #DropZone[dropState="drag"] QLabel {{
                color: {c(UI_TAG.TEXT_ACCENT)};
            }}

            QFileDialog {{
                background-color: {c(UI_TAG.BG_BASE)};
            }}

            QFileDialog #fileNameEdit,
            QFileDialog #fileTypeCombo,
            QFileDialog #lookInCombo {{
                background-color: {c(UI_TAG.BG_BASE)};
                border: 1px solid {c(UI_TAG.BORDER_BASE)};
                color: {c(UI_TAG.TEXT_PRIMARY)};
                padding: 6px;
                border-radius: 6px;
                margin: 0px;
            }}


            QFileDialog #fileTypeCombo::drop-down,
            QFileDialog #lookInCombo::drop-down {{
                width: 0px;
                border: none;
            }}

            QFileDialog #sidebar,
            QFileDialog #treeView {{
                background-color: {c(UI_TAG.BG_PANEL)};
                border: 1px solid {c(UI_TAG.BORDER_BASE)};
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
                color: {c(UI_TAG.TEXT_PRIMARY)};
            }}

            QFileDialog QPushButton {{
                background-color: transparent;
                border: 1px solid {c(UI_TAG.BORDER_BASE)};
                color: {c(UI_TAG.TEXT_PRIMARY)};
                padding-top: 6px;
                padding-bottom: 6px;
                padding-left: 8px;
                padding-right: 8px;
                border-radius: 8px;
                font-weight: bold;
            }}

            QFileDialog QPushButton:hover {{
                background-color: {c(UI_TAG.BG_BTN_PANEL_FOCUS)};
            }}

            QFileDialog QLabel {{
                color: {c(UI_TAG.TEXT_PRIMARY)};
                font-weight: bold;

            }}

            QFileDialog QHeaderView {{
                background-color: {c(UI_TAG.BG_PANEL)};
                color: {c(UI_TAG.TEXT_PRIMARY)};
                font-weight: bold;
                border: none;
                outline: none;
                border-bottom: 1px solid {c(UI_TAG.BORDER_BASE)};

            }}

            QFileDialog QComboBox {{
                background-color: {c(UI_TAG.BG_BASE)};
                border: 1px solid {c(UI_TAG.BORDER_BASE)};
                color: {c(UI_TAG.TEXT_PRIMARY)};
                combobox-popup: 0;
            }}

            QFileDialog QComboBox QAbstractItemView {{
                background-color: {c(UI_TAG.BG_BASE)};
                color: {c(UI_TAG.TEXT_PRIMARY)};
                padding: 0px;
            }}
            
            QFileDialog QComboBox QAbstractItemView::item {{
                background-color: transparent;
                color: {c(UI_TAG.TEXT_PRIMARY)};
            }}

            QFileDialog QToolButton {{
                background-color: {c(UI_TAG.BG_BASE)};
                border: 1px solid {c(UI_TAG.BORDER_BASE)};
            }}

            QFileDialog QToolButton:hover {{
                background-color: {c(UI_TAG.BG_BTN_PANEL_FOCUS)};
            }}

        """
        
