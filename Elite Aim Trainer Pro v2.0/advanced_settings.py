import json
import os
import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

class SettingType(Enum):
    BOOLEAN = "boolean"
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    CHOICE = "choice"
    COLOR = "color"
    KEY_BINDING = "key_binding"

@dataclass
class Setting:
    """Individual setting definition"""
    name: str
    setting_type: SettingType
    default_value: Any
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    choices: Optional[list] = None
    description: str = ""
    category: str = "General"
    requires_restart: bool = False
    validation_func: Optional[Callable] = None

class AdvancedSettingsManager:
    """Advanced settings manager with categories, validation, and auto-save"""
    
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = settings_file
        self.settings_definitions = self._create_settings_definitions()
        self.current_settings = {}
        self.setting_categories = {}
        self.change_callbacks = {}
        
        self._organize_categories()
        self.load_settings()
    
    def _create_settings_definitions(self) -> Dict[str, Setting]:
        """Define all available settings"""
        return {
            # Display Settings
            "fullscreen": Setting(
                "fullscreen", SettingType.BOOLEAN, False,
                description="Run in fullscreen mode", category="Display", requires_restart=True
            ),
            "resolution_width": Setting(
                "resolution_width", SettingType.INTEGER, 1400,
                min_value=800, max_value=3840,
                description="Window width", category="Display", requires_restart=True
            ),
            "resolution_height": Setting(
                "resolution_height", SettingType.INTEGER, 900,
                min_value=600, max_value=2160,
                description="Window height", category="Display", requires_restart=True
            ),
            "target_fps": Setting(
                "target_fps", SettingType.CHOICE, 144,
                choices=[60, 120, 144, 240, 360],
                description="Target frame rate", category="Display"
            ),
            "vsync": Setting(
                "vsync", SettingType.BOOLEAN, False,
                description="Enable vertical sync", category="Display"
            ),
            
            # Graphics Settings
            "theme": Setting(
                "theme", SettingType.CHOICE, "dark",
                choices=["dark", "light", "neon", "retro"],
                description="UI theme", category="Graphics"
            ),
            "particles_enabled": Setting(
                "particles_enabled", SettingType.BOOLEAN, True,
                description="Enable particle effects", category="Graphics"
            ),
            "particle_quality": Setting(
                "particle_quality", SettingType.CHOICE, "high",
                choices=["low", "medium", "high", "ultra"],
                description="Particle effect quality", category="Graphics"
            ),
            "glow_effects": Setting(
                "glow_effects", SettingType.BOOLEAN, True,
                description="Enable glow effects", category="Graphics"
            ),
            "animations": Setting(
                "animations", SettingType.BOOLEAN, True,
                description="Enable UI animations", category="Graphics"
            ),
            "anti_aliasing": Setting(
                "anti_aliasing", SettingType.BOOLEAN, False,
                description="Enable anti-aliasing", category="Graphics"
            ),
            
            # Audio Settings
            "sound_enabled": Setting(
                "sound_enabled", SettingType.BOOLEAN, True,
                description="Enable sound effects", category="Audio"
            ),
            "master_volume": Setting(
                "master_volume", SettingType.FLOAT, 0.7,
                min_value=0.0, max_value=1.0,
                description="Master volume", category="Audio"
            ),
            "music_volume": Setting(
                "music_volume", SettingType.FLOAT, 0.3,
                min_value=0.0, max_value=1.0,
                description="Music volume", category="Audio"
            ),
            "sfx_volume": Setting(
                "sfx_volume", SettingType.FLOAT, 0.8,
                min_value=0.0, max_value=1.0,
                description="Sound effects volume", category="Audio"
            ),
            
            # Gameplay Settings
            "crosshair_style": Setting(
                "crosshair_style", SettingType.CHOICE, 0,
                choices=[0, 1, 2], description="Crosshair style", category="Gameplay"
            ),
            "crosshair_color": Setting(
                "crosshair_color", SettingType.COLOR, [64, 224, 160],
                description="Crosshair color", category="Gameplay"
            ),
            "mouse_sensitivity": Setting(
                "mouse_sensitivity", SettingType.FLOAT, 1.0,
                min_value=0.1, max_value=5.0,
                description="Mouse sensitivity", category="Gameplay"
            ),
            "show_trail": Setting(
                "show_trail", SettingType.BOOLEAN, True,
                description="Show mouse trail", category="Gameplay"
            ),
            "auto_pause": Setting(
                "auto_pause", SettingType.BOOLEAN, False,
                description="Auto pause when window loses focus", category="Gameplay"
            ),
            
            # Performance Settings
            "auto_optimize": Setting(
                "auto_optimize", SettingType.BOOLEAN, True,
                description="Automatically optimize performance", category="Performance"
            ),
            "max_particles": Setting(
                "max_particles", SettingType.INTEGER, 1000,
                min_value=100, max_value=5000,
                description="Maximum particle count", category="Performance"
            ),
            "target_optimization": Setting(
                "target_optimization", SettingType.CHOICE, "balanced",
                choices=["performance", "balanced", "quality"],
                description="Optimization target", category="Performance"
            ),
            
            # Analytics Settings
            "collect_analytics": Setting(
                "collect_analytics", SettingType.BOOLEAN, True,
                description="Collect performance analytics", category="Analytics"
            ),
            "export_data": Setting(
                "export_data", SettingType.BOOLEAN, False,
                description="Auto-export session data", category="Analytics"
            ),
            "analytics_detail": Setting(
                "analytics_detail", SettingType.CHOICE, "medium",
                choices=["minimal", "medium", "detailed"],
                description="Analytics detail level", category="Analytics"
            ),
        }
    
    def _organize_categories(self):
        """Organize settings by category"""
        for setting_name, setting in self.settings_definitions.items():
            category = setting.category
            if category not in self.setting_categories:
                self.setting_categories[category] = []
            self.setting_categories[category].append(setting_name)
    
    def load_settings(self):
        """Load settings from file"""
        # Initialize with defaults
        for name, setting in self.settings_definitions.items():
            self.current_settings[name] = setting.default_value
        
        # Load from file if it exists
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    
                for name, value in saved_settings.items():
                    if name in self.settings_definitions:
                        if self._validate_setting(name, value):
                            self.current_settings[name] = value
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.current_settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get_setting(self, name: str, default=None):
        """Get a setting value"""
        return self.current_settings.get(name, default)
    
    def set_setting(self, name: str, value: Any, save_immediately: bool = True) -> bool:
        """Set a setting value with validation"""
        if name not in self.settings_definitions:
            print(f"Unknown setting: {name}")
            return False
        
        if not self._validate_setting(name, value):
            print(f"Invalid value for setting {name}: {value}")
            return False
        
        old_value = self.current_settings.get(name)
        self.current_settings[name] = value
        
        # Call change callback if registered
        if name in self.change_callbacks:
            self.change_callbacks[name](old_value, value)
        
        if save_immediately:
            self.save_settings()
        
        return True
    
    def _validate_setting(self, name: str, value: Any) -> bool:
        """Validate a setting value"""
        setting = self.settings_definitions[name]
        
        # Type validation
        if setting.setting_type == SettingType.BOOLEAN and not isinstance(value, bool):
            return False
        elif setting.setting_type == SettingType.INTEGER and not isinstance(value, int):
            return False
        elif setting.setting_type == SettingType.FLOAT and not isinstance(value, (int, float)):
            return False
        elif setting.setting_type == SettingType.STRING and not isinstance(value, str):
            return False
        
        # Range validation
        if setting.min_value is not None and value < setting.min_value:
            return False
        if setting.max_value is not None and value > setting.max_value:
            return False
        
        # Choice validation
        if setting.choices is not None and value not in setting.choices:
            return False
        
        # Custom validation
        if setting.validation_func and not setting.validation_func(value):
            return False
        
        return True
    
    def register_change_callback(self, setting_name: str, callback: Callable):
        """Register a callback for when a setting changes"""
        self.change_callbacks[setting_name] = callback
    
    def get_settings_by_category(self, category: str) -> Dict[str, Any]:
        """Get all settings in a specific category"""
        if category not in self.setting_categories:
            return {}
        
        return {
            name: self.current_settings[name]
            for name in self.setting_categories[category]
        }
    
    def get_all_categories(self) -> list:
        """Get list of all setting categories"""
        return list(self.setting_categories.keys())
    
    def reset_category(self, category: str):
        """Reset all settings in a category to defaults"""
        if category not in self.setting_categories:
            return
        
        for setting_name in self.setting_categories[category]:
            default_value = self.settings_definitions[setting_name].default_value
            self.set_setting(setting_name, default_value, save_immediately=False)
        
        self.save_settings()
    
    def reset_all_settings(self):
        """Reset all settings to defaults"""
        for name, setting in self.settings_definitions.items():
            self.current_settings[name] = setting.default_value
        self.save_settings()
    
    def export_settings(self, filename: str):
        """Export settings to a file"""
        export_data = {
            'settings': self.current_settings,
            'definitions': {
                name: asdict(setting) for name, setting in self.settings_definitions.items()
            },
            'export_timestamp': time.time()
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
        except Exception as e:
            print(f"Error exporting settings: {e}")
    
    def import_settings(self, filename: str) -> bool:
        """Import settings from a file"""
        try:
            with open(filename, 'r') as f:
                import_data = json.load(f)
                
            imported_settings = import_data.get('settings', {})
            
            for name, value in imported_settings.items():
                if name in self.settings_definitions:
                    self.set_setting(name, value, save_immediately=False)
            
            self.save_settings()
            return True
            
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False
    
    def get_settings_requiring_restart(self) -> list:
        """Get list of settings that require restart when changed"""
        return [
            name for name, setting in self.settings_definitions.items()
            if setting.requires_restart
        ]
