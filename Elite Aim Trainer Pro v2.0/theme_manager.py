from typing import Dict, Tuple
import json

class Theme:
    """Color theme for the UI"""
    
    def __init__(self, name: str, colors: Dict[str, Tuple[int, int, int]]):
        self.name = name
        self.colors = colors
    
    def get_color(self, element: str) -> Tuple[int, int, int]:
        """Get color for a UI element"""
        return self.colors.get(element, (255, 255, 255))

class ThemeManager:
    """Manages different UI themes"""
    
    def __init__(self):
        self.themes = {
            "default": Theme("Default", {
                "background": (8, 12, 20),
                "ui": (20, 25, 35),
                "accent": (64, 224, 160),
                "secondary_accent": (255, 107, 107),
                "text": (220, 230, 240),
                "text_secondary": (180, 190, 200),
                "error": (255, 100, 100),
                "target": (255, 70, 70),
                "hit": (100, 255, 150),
                "gold": (255, 215, 0),
                "silver": (192, 192, 192),
                "bronze": (205, 127, 50)
            }),
            
            "dark": Theme("Dark", {
                "background": (8, 12, 20),
                "ui": (20, 25, 35),
                "accent": (64, 224, 160),
                "secondary_accent": (255, 107, 107),
                "text": (220, 230, 240),
                "text_secondary": (180, 190, 200),
                "error": (255, 100, 100),
                "target": (255, 70, 70),
                "hit": (100, 255, 150),
                "gold": (255, 215, 0),
                "silver": (192, 192, 192),
                "bronze": (205, 127, 50)
            }),
            
            "cyberpunk": Theme("Cyberpunk", {
                "background": (10, 0, 20),
                "ui": (25, 5, 35),
                "accent": (255, 0, 150),
                "secondary_accent": (0, 255, 255),
                "text": (255, 255, 255),
                "text_secondary": (200, 180, 255),
                "error": (255, 20, 80),
                "target": (255, 20, 80),
                "hit": (0, 255, 200),
                "gold": (255, 255, 0),
                "silver": (180, 180, 255),
                "bronze": (255, 100, 0)
            }),
            
            "neon": Theme("Neon", {
                "background": (0, 0, 20),
                "ui": (10, 10, 40),
                "accent": (0, 255, 255),
                "secondary_accent": (255, 0, 255),
                "text": (255, 255, 255),
                "text_secondary": (200, 200, 255),
                "error": (255, 50, 100),
                "target": (255, 50, 100),
                "hit": (50, 255, 150),
                "gold": (255, 255, 0),
                "silver": (200, 200, 255),
                "bronze": (255, 150, 50)
            }),
            
            "retro": Theme("Retro", {
                "background": (20, 12, 8),
                "ui": (40, 25, 15),
                "accent": (255, 165, 0),
                "secondary_accent": (255, 69, 0),
                "text": (255, 248, 220),
                "text_secondary": (205, 198, 180),
                "error": (220, 20, 60),
                "target": (220, 20, 60),
                "hit": (154, 205, 50),
                "gold": (255, 215, 0),
                "silver": (192, 192, 192),
                "bronze": (205, 127, 50)
            }),
            
            "ocean": Theme("Ocean", {
                "background": (5, 15, 35),
                "ui": (15, 30, 55),
                "accent": (0, 191, 255),
                "secondary_accent": (30, 144, 255),
                "text": (240, 248, 255),
                "text_secondary": (176, 196, 222),
                "error": (255, 69, 0),
                "target": (255, 69, 0),
                "hit": (0, 255, 127),
                "gold": (255, 215, 0),
                "silver": (192, 192, 192),
                "bronze": (205, 127, 50)
            })
        }
        
        self.current_theme_name = "default"
        self.current_theme = self.themes[self.current_theme_name]
    
    def set_theme(self, theme_name: str):
        """Switch to a different theme"""
        if theme_name in self.themes:
            self.current_theme_name = theme_name
            self.current_theme = self.themes[theme_name]
    
    def get_color(self, element: str) -> Tuple[int, int, int]:
        """Get color for a UI element from current theme"""
        return self.current_theme.get_color(element)
    
    def get_available_themes(self) -> list:
        """Get list of available theme names"""
        return list(self.themes.keys())
    
    def add_custom_theme(self, name: str, colors: Dict[str, Tuple[int, int, int]]):
        """Add a custom theme"""
        self.themes[name] = Theme(name, colors)
    
    def save_theme_preference(self, filename: str = "theme_settings.json"):
        """Save current theme preference"""
        try:
            with open(filename, 'w') as f:
                json.dump({"current_theme": self.current_theme_name}, f)
        except Exception:
            pass
    
    def load_theme_preference(self, filename: str = "theme_settings.json"):
        """Load saved theme preference"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                theme_name = data.get("current_theme", "default")
                self.set_theme(theme_name)
        except Exception:
            pass
