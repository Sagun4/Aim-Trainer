import pygame
import random
import math
import time
import json
import os
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
import colorsys

# Import our new systems with better error handling
try:
    from object_pools import TargetPool, ParticlePool
    OBJECT_POOLS_AVAILABLE = True
except ImportError:
    print("Object pools not available")
    OBJECT_POOLS_AVAILABLE = False

try:
    from performance_optimization import AdaptiveQualitySystem
    PERFORMANCE_OPTIMIZATION_AVAILABLE = True
except ImportError:
    print("Performance optimization not available")
    PERFORMANCE_OPTIMIZATION_AVAILABLE = False

try:
    from advanced_settings import AdvancedSettingsManager
    ADVANCED_SETTINGS_AVAILABLE = True
except ImportError:
    print("Advanced settings not available")
    ADVANCED_SETTINGS_AVAILABLE = False

try:
    from sound_manager import SoundManager, SoundEffect
    SOUND_MANAGER_AVAILABLE = True
except ImportError:
    print("Sound manager not available")
    SOUND_MANAGER_AVAILABLE = False

try:
    from theme_manager import ThemeManager
    THEME_MANAGER_AVAILABLE = True
except ImportError:
    print("Theme manager not available")
    THEME_MANAGER_AVAILABLE = False

try:
    from analytics import AdvancedAnalytics
    ANALYTICS_AVAILABLE = True
except ImportError:
    print("Analytics not available")
    ANALYTICS_AVAILABLE = False

try:
    from render_cache import RenderCache
    RENDER_CACHE_AVAILABLE = True
except ImportError:
    print("Render cache not available")
    RENDER_CACHE_AVAILABLE = False

# Check if all advanced features are available
ADVANCED_FEATURES_AVAILABLE = all([
    OBJECT_POOLS_AVAILABLE,
    PERFORMANCE_OPTIMIZATION_AVAILABLE, 
    ADVANCED_SETTINGS_AVAILABLE,
    SOUND_MANAGER_AVAILABLE,
    THEME_MANAGER_AVAILABLE,
    ANALYTICS_AVAILABLE,
    RENDER_CACHE_AVAILABLE
])

if not ADVANCED_FEATURES_AVAILABLE:
    print("Running in compatibility mode - some features may be limited")

# Initialize Pygame with error handling
try:
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
except Exception as e:
    print(f"Warning: Pygame initialization issue: {e}")
    pygame.init()  # Fallback initialization

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        default_config = {
            "display": {
                "default_width": 1400,
                "default_height": 900,
                "fps": 144,
                "fullscreen": False
            },
            "colors": {
                "background": [8, 12, 20],
                "ui": [20, 25, 35],
                "accent": [64, 224, 160],
                "text": [220, 230, 240],
                "target": [255, 70, 70],
                "gold": [255, 215, 0]
            },
            "default_settings": {
                "crosshair_style": 0,
                "sound_enabled": True,
                "particles_enabled": True,
                "show_trail": True,
                "mouse_sensitivity": 1.0
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    return {**default_config, **loaded_config}
        except Exception as e:
            print(f"Error loading config: {e}")
        
        return default_config
    
    def save_config(self):
        """Save current configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'display.fps')"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value

# Initialize configuration
config_manager = ConfigManager()

# Get display info for proper resolution
display_info = pygame.display.Info()
SCREEN_WIDTH = min(config_manager.get('display.default_width', 1400), display_info.current_w - 100)
SCREEN_HEIGHT = min(config_manager.get('display.default_height', 900), display_info.current_h - 100)

# Constants
WINDOW_WIDTH = SCREEN_WIDTH
WINDOW_HEIGHT = SCREEN_HEIGHT
FPS = config_manager.get('display.fps', 144)
BACKGROUND_COLOR = tuple(config_manager.get('colors.background', [8, 12, 20]))
UI_COLOR = tuple(config_manager.get('colors.ui', [20, 25, 35]))
ACCENT_COLOR = tuple(config_manager.get('colors.accent', [64, 224, 160]))
SECONDARY_ACCENT = (255, 107, 107)
TEXT_COLOR = tuple(config_manager.get('colors.text', [220, 230, 240]))
ERROR_COLOR = (255, 100, 100)
TARGET_COLOR = tuple(config_manager.get('colors.target', [255, 70, 70]))
HIT_COLOR = (100, 255, 150)
GOLD_COLOR = tuple(config_manager.get('colors.gold', [255, 215, 0]))
SILVER_COLOR = (192, 192, 192)
BRONZE_COLOR = (205, 127, 50)

# File paths
STATS_FILE = "aim_stats.json"
SETTINGS_FILE = "settings.json"
ACHIEVEMENTS_FILE = "achievements.json"

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    RESULTS = 3
    SETTINGS = 4
    STATISTICS = 5
    ACHIEVEMENTS = 6
    LEADERBOARD = 7

@dataclass
class Target:
    x: float
    y: float
    radius: float
    spawn_time: float
    hit: bool = False
    target_type: str = "normal"  # normal, bonus, moving
    velocity: Tuple[float, float] = (0, 0)
    color: Tuple[int, int, int] = TARGET_COLOR
    points: int = 1
    
class GameMode:
    def __init__(self, name: str, duration: int, target_size: int, spawn_rate: float, 
                 max_targets: int, target_lifetime: float, description: str, difficulty: str):
        self.name = name
        self.duration = duration
        self.target_size = target_size
        self.spawn_rate = spawn_rate
        self.max_targets = max_targets
        self.target_lifetime = target_lifetime
        self.description = description
        self.difficulty = difficulty

class Achievement:
    def __init__(self, name: str, description: str, condition_func, unlocked: bool = False):
        self.name = name
        self.description = description
        self.condition_func = condition_func
        self.unlocked = unlocked
        self.unlock_time = None

class StatsManager:
    def __init__(self):
        self.stats = self.load_stats()
        self.session_stats = {
            "games_played": 0,
            "shots_fired": 0,
            "hits": 0,
            "best_streak": 0
        }
    
    def load_stats(self) -> Dict[str, Any]:
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError, OSError):
                pass
        return {
            "games_played": 0,
            "total_shots": 0,
            "total_hits": 0,
            "best_accuracy": 0.0,
            "best_targets_per_second": 0.0,
            "best_reaction_time": float('inf'),
            "total_playtime": 0.0,
            "highest_score": 0,
            "longest_streak": 0,
            "mode_records": {},
            "daily_stats": {}
        }
    
    def save_stats(self):
        with open(STATS_FILE, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def update_stats(self, shots: int, hits: int, accuracy: float, 
                    targets_per_second: float, avg_reaction_time: float, 
                    playtime: float, score: int, streak: int, mode_name: str):
        self.stats["games_played"] += 1
        self.stats["total_shots"] += shots
        self.stats["total_hits"] += hits
        self.stats["total_playtime"] += playtime
        
        if accuracy > self.stats["best_accuracy"]:
            self.stats["best_accuracy"] = accuracy
        
        if targets_per_second > self.stats["best_targets_per_second"]:
            self.stats["best_targets_per_second"] = targets_per_second
        
        if avg_reaction_time < self.stats["best_reaction_time"]:
            self.stats["best_reaction_time"] = avg_reaction_time
            
        if score > self.stats["highest_score"]:
            self.stats["highest_score"] = score
            
        if streak > self.stats["longest_streak"]:
            self.stats["longest_streak"] = streak
        
        # Mode-specific records
        if mode_name not in self.stats["mode_records"]:
            self.stats["mode_records"][mode_name] = {
                "best_score": 0,
                "best_accuracy": 0.0,
                "games_played": 0
            }
        
        mode_record = self.stats["mode_records"][mode_name]
        mode_record["games_played"] += 1
        if score > mode_record["best_score"]:
            mode_record["best_score"] = score
        if accuracy > mode_record["best_accuracy"]:
            mode_record["best_accuracy"] = accuracy
        
        self.save_stats()

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_hit_effect(self, x: float, y: float, color: Tuple[int, int, int] = HIT_COLOR):
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 40,
                'max_life': 40,
                'color': color,
                'size': random.uniform(2, 5)
            })
    
    def add_miss_effect(self, x: float, y: float):
        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 20,
                'max_life': 20,
                'color': (150, 150, 150),
                'size': 2
            })
    
    def add_streak_effect(self, x: float, y: float, streak: int):
        colors = [GOLD_COLOR, ACCENT_COLOR, SECONDARY_ACCENT]
        for _ in range(streak * 2):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 60,
                'max_life': 60,
                'color': random.choice(colors),
                'size': random.uniform(3, 6)
            })
    
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vx'] *= 0.98
            particle['vy'] *= 0.98
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen):
        for particle in self.particles:
            alpha = particle['life'] / particle['max_life']
            size = int(particle['size'] * alpha)
            if size > 0:
                base_color = particle['color']
                color = (int(base_color[0] * alpha), int(base_color[1] * alpha), int(base_color[2] * alpha))
                pygame.draw.circle(screen, color, 
                                 (int(particle['x']), int(particle['y'])), size)

class AchievementSystem:
    def __init__(self, stats_manager):
        self.stats_manager = stats_manager
        self.achievements = self.create_achievements()
        self.load_achievements()
        self.new_unlocks = []
    
    def create_achievements(self):
        return [
            Achievement("First Steps", "Play your first game", 
                       lambda s: s["games_played"] >= 1),
            Achievement("Sharpshooter", "Achieve 90% accuracy", 
                       lambda s: s["best_accuracy"] >= 90),
            Achievement("Speed Demon", "Hit 3 targets per second", 
                       lambda s: s["best_targets_per_second"] >= 3),
            Achievement("Marathon Runner", "Play for 1 hour total", 
                       lambda s: s["total_playtime"] >= 3600),
            Achievement("Perfectionist", "Achieve 100% accuracy in a game", 
                       lambda s: s["best_accuracy"] >= 100),
            Achievement("Lightning Fast", "Average reaction time under 200ms", 
                       lambda s: s["best_reaction_time"] < 0.2),
            Achievement("Streak Master", "Get a 20-hit streak", 
                       lambda s: s["longest_streak"] >= 20),
            Achievement("High Scorer", "Score over 1000 points", 
                       lambda s: s["highest_score"] >= 1000),
            Achievement("Dedicated", "Play 50 games", 
                       lambda s: s["games_played"] >= 50),
            Achievement("Elite", "Play 100 games", 
                       lambda s: s["games_played"] >= 100),
        ]
    
    def load_achievements(self):
        if os.path.exists(ACHIEVEMENTS_FILE):
            try:
                with open(ACHIEVEMENTS_FILE, 'r') as f:
                    data = json.load(f)
                    for achievement in self.achievements:
                        if achievement.name in data:
                            achievement.unlocked = data[achievement.name]["unlocked"]
                            achievement.unlock_time = data[achievement.name].get("unlock_time")
            except (json.JSONDecodeError, IOError, OSError, KeyError):
                pass
    
    def save_achievements(self):
        data = {}
        for achievement in self.achievements:
            data[achievement.name] = {
                "unlocked": achievement.unlocked,
                "unlock_time": achievement.unlock_time
            }
        with open(ACHIEVEMENTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def check_achievements(self):
        stats = self.stats_manager.stats
        for achievement in self.achievements:
            if not achievement.unlocked and achievement.condition_func(stats):
                achievement.unlocked = True
                achievement.unlock_time = time.time()
                self.new_unlocks.append(achievement)
        
        if self.new_unlocks:
            self.save_achievements()

class AimTrainer:
    def __init__(self):
        try:
            # Initialize display with proper resolution handling
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("Elite Aim Trainer Pro")
            self.clock = pygame.time.Clock()
            
            # Enhanced fonts with better sizing for resolution
            font_scale = min(WINDOW_WIDTH / 1400, WINDOW_HEIGHT / 900)
            try:
                self.font_title = pygame.font.Font(None, int(64 * font_scale))
                self.font_large = pygame.font.Font(None, int(48 * font_scale))
                self.font_medium = pygame.font.Font(None, int(32 * font_scale))
                self.font_small = pygame.font.Font(None, int(24 * font_scale))
                self.font_tiny = pygame.font.Font(None, int(18 * font_scale))
            except Exception as e:
                print(f"Warning: Font initialization issue: {e}")
                # Fallback to default fonts
                self.font_title = pygame.font.Font(None, 64)
                self.font_large = pygame.font.Font(None, 48)
                self.font_medium = pygame.font.Font(None, 32)
                self.font_small = pygame.font.Font(None, 24)
                self.font_tiny = pygame.font.Font(None, 18)
            
            self.state = GameState.MENU
            self.stats_manager = StatsManager()
            self.particle_system = ParticleSystem()
            self.achievement_system = AchievementSystem(self.stats_manager)
            
            # Initialize advanced features if available
            if ADVANCED_FEATURES_AVAILABLE:
                try:
                    self.target_pool = TargetPool()
                    self.particle_pool = ParticlePool()
                    self.quality_system = AdaptiveQualitySystem()
                    self.settings_manager = AdvancedSettingsManager()
                    self.sound_manager = SoundManager()
                    self.theme_manager = ThemeManager()
                    self.analytics = AdvancedAnalytics()
                    self.render_cache = RenderCache()
                    self.use_object_pools = True
                    
                    # Load saved theme and apply it
                    self.theme_manager.load_theme_preference()
                    self.apply_current_theme()
                    
                    print("Advanced features enabled: Sound, themes, analytics, object pooling, performance monitoring")
                except Exception as e:
                    print(f"Warning: Advanced features initialization failed: {e}")
                    print("Falling back to compatibility mode")
                    self.sound_manager = None
                    self.theme_manager = None
                    self.analytics = None
                    self.render_cache = None
                    self.use_object_pools = False
            else:
                self.sound_manager = None
                self.theme_manager = None
                self.analytics = None
                self.render_cache = None
                self.use_object_pools = False
                print("Running in compatibility mode")
            
            # Enhanced game modes
            self.game_modes = [
                GameMode("Classic", 60, 25, 0.5, 1, 3.0, "Traditional aim training", "Beginner"),
                GameMode("Precision", 60, 18, 0.4, 2, 3.5, "Small targets for accuracy", "Intermediate"),
                GameMode("Speed Blitz", 30, 35, 0.15, 6, 1.2, "Fast-paced target shooting", "Advanced"),
                GameMode("Reflexes", 45, 22, 0.25, 4, 2.0, "Quick reaction training", "Intermediate"),
                GameMode("Flick Master", 60, 16, 0.6, 1, 4.0, "Long-range flick shots", "Expert"),
                GameMode("Multi-Track", 45, 30, 0.12, 8, 1.5, "Multiple moving targets", "Expert"),
                GameMode("Sniper", 90, 12, 0.8, 1, 5.0, "Ultra-precise long shots", "Master"),
                GameMode("Chaos Mode", 40, 28, 0.08, 12, 1.0, "Maximum intensity", "Insane")
            ]
            self.selected_mode = 0
            
            # Game state
            self.targets = []
            self.shots_fired = 0
            self.hits = 0
            self.score = 0
            self.streak = 0
            self.max_streak = 0
            self.game_start_time = 0
            self.game_duration = 60
            self.last_spawn_time = 0
            self.reaction_times = []
            self.crosshair_pos = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
            
            # Enhanced UI
            self.menu_buttons = []
            
        except Exception as e:
            print(f"Critical initialization error: {e}")
            print("Some features may not be available")
            # Set minimal defaults to prevent crashes
            self.sound_manager = None
            self.theme_manager = None
            self.analytics = None
            self.render_cache = None
            self.use_object_pools = False
        self.result_screen_timer = 0
        self.achievement_notification_timer = 0
        self.current_achievement = None
        self.background_stars = self.generate_stars()
        self.ui_animations = {}
        
        # Settings
        self.settings = {
            "crosshair_style": 0,  # 0: default, 1: dot, 2: cross, 3: tenz
            "sound_enabled": True,
            "sound_volume": 0.7,
            "music_enabled": True,
            "music_volume": 0.3,
            "particles_enabled": True,
            "show_trail": True,
            "theme": "default"  # For theme manager
        }
        
        # Mouse visibility will be controlled based on game state
        pygame.mouse.set_visible(True)  # Start with mouse visible for menu
        
        # Synchronize settings with sound manager
        if self.sound_manager:
            self.sound_manager.enabled = self.settings["sound_enabled"]
            self.sound_manager.set_volume(self.settings["sound_volume"])
            self.sound_manager.set_music_volume(self.settings["music_volume"])
        
        # Start menu background music
        if self.settings["music_enabled"]:
            self.start_menu_music()
        
        print(f"Initialized with resolution: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    
    def generate_stars(self):
        stars = []
        for _ in range(100):
            stars.append({
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'brightness': random.uniform(0.3, 1.0),
                'twinkle_speed': random.uniform(0.01, 0.03)
            })
        return stars
    
    def handle_events(self) -> bool:
        try:
            # Control mouse visibility based on game state
            if self.state == GameState.PLAYING:
                pygame.mouse.set_visible(False)  # Hide mouse during gameplay
            else:
                pygame.mouse.set_visible(True)   # Show mouse in menus
                
            for event in pygame.event.get():
                try:
                    if event.type == pygame.QUIT:
                        return False
                    
                    if event.type == pygame.MOUSEMOTION:
                        self.crosshair_pos = event.pos
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left click
                            try:
                                if self.state == GameState.MENU:
                                    self.handle_menu_click(event.pos)
                                elif self.state == GameState.PLAYING:
                                    self.handle_game_click(event.pos)
                                elif self.state == GameState.SETTINGS:
                                    self.handle_settings_click(event.pos)
                                elif self.state in [GameState.RESULTS, GameState.STATISTICS, 
                                                  GameState.ACHIEVEMENTS]:
                                    # For results screen, require minimum time before allowing exit
                                    if self.state == GameState.RESULTS:
                                        # Require at least 2 seconds on results screen before allowing click to exit
                                        if time.time() - self.result_screen_timer >= 2.0:
                                            self.transition_to_state(GameState.MENU)
                                    else:
                                        # Statistics and Achievements can exit immediately
                                        self.transition_to_state(GameState.MENU)
                            except Exception as e:
                                print(f"Warning: Click handler error: {e}")
                    
                    if event.type == pygame.KEYDOWN:
                        try:
                            if event.key == pygame.K_ESCAPE:
                                if self.state == GameState.PLAYING:
                                    self.end_game()
                                else:
                                    self.transition_to_state(GameState.MENU)
                            elif event.key == pygame.K_SPACE and self.state == GameState.MENU:
                                self.start_game()
                            elif event.key == pygame.K_UP and self.state == GameState.MENU and len(self.game_modes) > 0:
                                self.selected_mode = (self.selected_mode - 1) % len(self.game_modes)
                            elif event.key == pygame.K_DOWN and self.state == GameState.MENU and len(self.game_modes) > 0:
                                self.selected_mode = (self.selected_mode + 1) % len(self.game_modes)
                            elif event.key == pygame.K_s and self.state == GameState.MENU:
                                self.transition_to_state(GameState.STATISTICS)
                            elif event.key == pygame.K_a and self.state == GameState.MENU:
                                self.transition_to_state(GameState.ACHIEVEMENTS)
                            elif event.key == pygame.K_t and self.state == GameState.MENU:
                                self.transition_to_state(GameState.SETTINGS)
                        except Exception as e:
                            print(f"Warning: Key handler error: {e}")
                            
                except Exception as e:
                    print(f"Warning: Event processing error: {e}")
                    continue
            
            return True
            
        except Exception as e:
            print(f"Critical event handling error: {e}")
            return True  # Continue running but with error
    
    def handle_menu_click(self, pos: Tuple[int, int]):
        # Mode selection - Fixed coordinates and improved hit detection
        button_area_height = 120  # Space needed for buttons at bottom
        available_height = WINDOW_HEIGHT - 250 - button_area_height  # Account for title and buttons
        mode_height = min(50, available_height // len(self.game_modes) - 2)  # Dynamic height
        mode_spacing = 2
        mode_y_start = 250  # Fixed start position
        
        for i, mode in enumerate(self.game_modes):
            mode_y = mode_y_start + i * (mode_height + mode_spacing)
            mode_rect = pygame.Rect(WINDOW_WIDTH//2 - 350, mode_y, 700, mode_height)
            if mode_rect.collidepoint(pos):
                self.selected_mode = i
                return
        
        # Navigation buttons - Fixed positioning
        button_y = WINDOW_HEIGHT - 100
        button_width = 140
        button_height = 40
        button_spacing = 20
        
        # Calculate button positions for 4 buttons
        total_button_width = 4 * button_width + 3 * button_spacing
        start_x = WINDOW_WIDTH//2 - total_button_width//2
        
        buttons = [
            ("START GAME", start_x, self.start_game),
            ("STATISTICS", start_x + button_width + button_spacing, lambda: self.transition_to_state(GameState.STATISTICS)),
            ("ACHIEVEMENTS", start_x + 2 * (button_width + button_spacing), lambda: self.transition_to_state(GameState.ACHIEVEMENTS)),
            ("SETTINGS", start_x + 3 * (button_width + button_spacing), lambda: self.transition_to_state(GameState.SETTINGS))
        ]
        
        for text, x, action in buttons:
            button_rect = pygame.Rect(x, button_y, button_width, button_height)
            if button_rect.collidepoint(pos):
                # Play menu click sound
                if self.sound_manager:
                    self.sound_manager.play(SoundEffect.MENU_CLICK)
                action()
                return
    
    def handle_game_click(self, pos: Tuple[int, int]):
        self.shots_fired += 1
        hit = False
        
        for target in self.targets[:]:
            distance = math.sqrt((pos[0] - target.x)**2 + (pos[1] - target.y)**2)
            if distance <= target.radius and not target.hit:
                target.hit = True
                self.hits += 1
                self.score += target.points
                self.streak += 1
                self.max_streak = max(self.max_streak, self.streak)
                hit = True
                
                # Calculate reaction time
                reaction_time = time.time() - target.spawn_time
                self.reaction_times.append(reaction_time)
                
                # Play hit sound effects
                if self.sound_manager:
                    if target.target_type == "bonus":
                        self.sound_manager.play(SoundEffect.BONUS_HIT)
                    else:
                        self.sound_manager.play(SoundEffect.HIT)
                    
                    # Play streak sound for special streaks
                    if self.streak % 5 == 0 and self.streak >= 5:
                        self.sound_manager.play(SoundEffect.STREAK)
                
                # Enhanced particle effects
                if self.settings["particles_enabled"]:
                    self.particle_system.add_hit_effect(target.x, target.y, target.color)
                    if self.streak >= 5:
                        self.particle_system.add_streak_effect(target.x, target.y, self.streak // 5)
                
                # Return target to pool and remove from active list
                if self.use_object_pools:
                    self.target_pool.release(target)
                self.targets.remove(target)
                break
        
        if not hit:
            self.streak = 0
            # Play miss sound
            if self.sound_manager:
                self.sound_manager.play(SoundEffect.MISS)
            if self.settings["particles_enabled"]:
                self.particle_system.add_miss_effect(pos[0], pos[1])
        
        return hit
    
    def handle_settings_click(self, pos: Tuple[int, int]):
        """Handle clicks in the settings menu"""
        # Settings options coordinates
        settings_list = [
            ("Crosshair Style", ["Default", "Dot", "Cross", "TenZ"]),
            ("Sound Effects", ["Enabled", "Disabled"]),
            ("Music", ["Enabled", "Disabled"]),
            ("Particle Effects", ["Enabled", "Disabled"]),
            ("Mouse Trail", ["Enabled", "Disabled"]),
            ("Theme", ["Default", "Dark", "Cyberpunk", "Neon", "Retro", "Ocean"])
        ]
        
        y_start = 200
        for i, (setting_name, options) in enumerate(settings_list):
            y_pos = y_start + i * 80
            
            # Check if click is in this setting's area
            if y_pos <= pos[1] <= y_pos + 60:
                # Check which option was clicked
                for j, option in enumerate(options):
                    option_x = 200 + j * 150
                    option_rect = pygame.Rect(option_x, y_pos + 30, 120, 30)
                    
                    if option_rect.collidepoint(pos):
                        # Apply the setting
                        if setting_name == "Crosshair Style":
                            self.settings["crosshair_style"] = j
                        elif setting_name == "Sound Effects":
                            self.settings["sound_enabled"] = (j == 0)
                            if self.sound_manager:
                                self.sound_manager.set_volume(self.settings["sound_volume"] if self.settings["sound_enabled"] else 0)
                        elif setting_name == "Music":
                            old_music_enabled = self.settings["music_enabled"]
                            self.settings["music_enabled"] = (j == 0)
                            
                            # Handle music state changes
                            if self.sound_manager:
                                if self.settings["music_enabled"] and not old_music_enabled:
                                    # Music was just enabled - start appropriate music
                                    if self.state == GameState.PLAYING:
                                        self.start_game_music()
                                    else:
                                        self.start_menu_music()
                                elif not self.settings["music_enabled"] and old_music_enabled:
                                    # Music was just disabled - stop all music
                                    self.stop_all_music()
                        elif setting_name == "Particle Effects":
                            self.settings["particles_enabled"] = (j == 0)
                        elif setting_name == "Mouse Trail":
                            self.settings["show_trail"] = (j == 0)
                        elif setting_name == "Theme":
                            theme_map = ["default", "dark", "cyberpunk", "neon", "retro", "ocean"]
                            if j < len(theme_map):
                                self.settings["theme"] = theme_map[j]
                                # Apply theme immediately
                                if self.theme_manager:
                                    self.theme_manager.set_theme(theme_map[j])
                                    self.apply_current_theme()
                                    # Save theme preference
                                    self.theme_manager.save_theme_preference()
                        break
        
        # Volume slider handling removed for cleaner interface
        
        # Check if clicking outside settings area (return to menu)
        if pos[1] > WINDOW_HEIGHT - 100:
            self.transition_to_state(GameState.MENU)
    
    def apply_current_theme(self):
        """Apply the current theme colors to global variables"""
        if not self.theme_manager:
            return
        
        global BACKGROUND_COLOR, UI_COLOR, ACCENT_COLOR, SECONDARY_ACCENT, TEXT_COLOR, ERROR_COLOR, GOLD_COLOR
        
        BACKGROUND_COLOR = self.theme_manager.get_color("background")
        UI_COLOR = self.theme_manager.get_color("ui")
        ACCENT_COLOR = self.theme_manager.get_color("accent")
        SECONDARY_ACCENT = self.theme_manager.get_color("secondary_accent")
        TEXT_COLOR = self.theme_manager.get_color("text")
        ERROR_COLOR = self.theme_manager.get_color("error")
        GOLD_COLOR = self.theme_manager.get_color("gold")
    
    def create_custom_theme_example(self):
        """Example of how to create a custom theme"""
        if not self.theme_manager:
            return
        
        # Example: Create a "Purple Gaming" theme
        purple_theme_colors = {
            "background": (25, 10, 35),      # Dark purple background
            "ui": (45, 25, 60),              # Purple UI elements
            "accent": (147, 112, 219),       # Medium slate blue
            "secondary_accent": (255, 20, 147), # Deep pink
            "text": (230, 220, 255),         # Light purple text
            "text_secondary": (180, 170, 200), # Muted purple text
            "error": (255, 69, 0),           # Orange red for errors
            "target": (255, 69, 0),          # Orange red targets
            "hit": (50, 255, 50),            # Bright green hits
            "gold": (255, 215, 0),           # Standard gold
            "silver": (192, 192, 192),       # Standard silver
            "bronze": (205, 127, 50)         # Standard bronze
        }
        
        # Add the custom theme
        self.theme_manager.add_custom_theme("purple_gaming", purple_theme_colors)
        
        # You can then switch to it programmatically:
        # self.theme_manager.set_theme("purple_gaming")
        # self.apply_current_theme()
    
    def transition_to_state(self, new_state):
        """Safely transition between game states"""
        try:
            old_state = self.state
            self.state = new_state
            
            # Handle state-specific logic
            if new_state == GameState.MENU:
                # Reset mouse visibility
                pygame.mouse.set_visible(True)
                
            elif new_state == GameState.PLAYING:
                # Hide mouse cursor during gameplay
                pygame.mouse.set_visible(False)
                
            elif new_state == GameState.RESULTS:
                # Show mouse cursor for results
                pygame.mouse.set_visible(True)
                
            print(f"State transition: {old_state} -> {new_state}")
            
        except Exception as e:
            print(f"Warning: State transition error: {e}")
            # Fallback to menu state if transition fails
            self.state = GameState.MENU
    
    def start_game(self):
        self.transition_to_state(GameState.PLAYING)
        mode = self.game_modes[self.selected_mode]
        self.game_duration = mode.duration
        self.game_start_time = time.time()
        self.targets.clear()
        self.shots_fired = 0
        self.hits = 0
        self.score = 0
        self.streak = 0
        self.max_streak = 0
        self.reaction_times.clear()
        self.last_spawn_time = 0
        
        # Play game start sound and start analytics session
        if self.sound_manager:
            self.sound_manager.play(SoundEffect.GAME_START)
            # Start gameplay background music if enabled
            if self.settings["music_enabled"]:
                self.start_game_music()
        if self.analytics:
            self.analytics.start_session(mode.name)
    
    def end_game(self):
        self.transition_to_state(GameState.RESULTS)
        self.result_screen_timer = time.time()
        
        # Play game end sound and stop game music
        if self.sound_manager:
            self.sound_manager.play(SoundEffect.GAME_END)
            # Transition back to menu music if enabled
            if self.settings["music_enabled"]:
                self.start_menu_music()
        
        # Return all active targets to the pool
        if self.use_object_pools:
            for target in self.targets:
                self.target_pool.release(target)
        
        # Clear targets list
        self.targets.clear()
        
        # Calculate stats
        game_time = time.time() - self.game_start_time
        accuracy = (self.hits / self.shots_fired * 100) if self.shots_fired > 0 else 0
        targets_per_second = self.hits / game_time if game_time > 0 else 0
        avg_reaction_time = sum(self.reaction_times) / len(self.reaction_times) if self.reaction_times else float('inf')
        
        # Update stats
        self.stats_manager.update_stats(
            self.shots_fired, self.hits, accuracy, 
            targets_per_second, avg_reaction_time, game_time,
            self.score, self.max_streak, self.game_modes[self.selected_mode].name
        )
        
        # End analytics session and track data
        if self.analytics:
            self.analytics.end_session(self.score, self.max_streak)
        
        # Check achievements
        self.achievement_system.check_achievements()
        if self.achievement_system.new_unlocks:
            self.current_achievement = self.achievement_system.new_unlocks[0]
            self.achievement_notification_timer = time.time()
            # Play achievement sound
            if self.sound_manager:
                self.sound_manager.play(SoundEffect.ACHIEVEMENT)
            self.achievement_system.new_unlocks.clear()
    
    def start_menu_music(self):
        """Start the menu background music"""
        if not self.sound_manager or not self.settings["music_enabled"]:
            return
        
        # Try to play menu music, fallback to game music, then generate placeholder
        music_files = ["sounds/menu_music.wav", "sounds/menu_music.mp3", "sounds/background.wav", "sounds/background.mp3"]
        
        for music_file in music_files:
            try:
                if os.path.exists(music_file):
                    self.sound_manager.play_music(music_file, loops=-1)
                    return
            except (pygame.error, OSError):
                continue
        
        # If no music files exist, create a placeholder ambient track
        self.create_placeholder_music("menu")
    
    def start_game_music(self):
        """Start the gameplay background music"""
        if not self.sound_manager or not self.settings["music_enabled"]:
            return
        
        # Try to play game music, fallback to menu music, then generate placeholder
        music_files = ["sounds/game_music.wav", "sounds/game_music.mp3", "sounds/background.wav", "sounds/background.mp3"]
        
        for music_file in music_files:
            try:
                if os.path.exists(music_file):
                    self.sound_manager.play_music(music_file, loops=-1)
                    return
            except (pygame.error, OSError):
                continue
        
        # If no music files exist, create a placeholder intense track
        self.create_placeholder_music("game")
    
    def stop_all_music(self):
        """Stop all background music"""
        if self.sound_manager:
            self.sound_manager.stop_music()
    
    def create_placeholder_music(self, music_type="menu"):
        """Create a simple placeholder music track"""
        try:
            import numpy as np

            # Create a simple ambient/electronic music track
            sample_rate = 22050
            duration = 30  # 30 seconds loop
            frames = duration * sample_rate

            # Generate a simple harmonic progression
            time_array = np.linspace(0, duration, frames)

            if music_type == "menu":
                # Calm, ambient menu music
                base_freq = 220  # A3
                music = (
                    0.3 * np.sin(2 * np.pi * base_freq * time_array) +  # A
                    0.2 * np.sin(2 * np.pi * base_freq * 1.5 * time_array) +  # E
                    0.15 * np.sin(2 * np.pi * base_freq * 1.25 * time_array) +  # C#
                    0.1 * np.sin(2 * np.pi * base_freq * 0.75 * time_array)  # Low G
                )
                # Add a subtle pulse
                pulse = 0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * time_array)  # 0.5 Hz pulse
                music *= pulse
            else:
                # More intense game music
                base_freq = 330  # E4
                music = (
                    0.4 * np.sin(2 * np.pi * base_freq * time_array) +  # E
                    0.3 * np.sin(2 * np.pi * base_freq * 1.33 * time_array) +  # A
                    0.2 * np.sin(2 * np.pi * base_freq * 1.2 * time_array) +  # F#
                    0.15 * np.sin(2 * np.pi * base_freq * 0.67 * time_array)  # B
                )
                # Add intensity variation
                intensity = 0.7 + 0.3 * np.sin(2 * np.pi * 1 * time_array)  # 1 Hz intensity
                music *= intensity

            # Apply envelope and normalize
            envelope = 0.8 + 0.2 * np.sin(2 * np.pi * 0.1 * time_array)  # Slow variation
            music *= envelope * 0.3  # Keep volume low

            # Create stereo version
            stereo_music = np.zeros((frames, 2))
            stereo_music[:, 0] = music  # Left channel
            stereo_music[:, 1] = music * 0.9  # Right channel slightly different

            # Convert to pygame sound format and play directly
            music_array = (stereo_music * 32767).astype(np.int16)

            # Create pygame sound object directly instead of saving to file
            try:
                sound = pygame.sndarray.make_sound(music_array)
                # Note: This creates a sound effect, not background music
                # For true background music, we'd need file I/O which requires additional libraries
                print(f"Generated procedural {music_type} music (as sound effect)")
            except Exception:
                print(f"Could not create procedural {music_type} music")

        except ImportError:
            print(f"NumPy not available - cannot generate procedural music")
        except Exception as e:
            print(f"Could not create placeholder music: {e}")
    
    def update_game(self):
        if self.state != GameState.PLAYING:
            return
        
        current_time = time.time()
        elapsed_time = current_time - self.game_start_time
        
        # Check if game should end
        if elapsed_time >= self.game_duration:
            self.end_game()
            return
        
        mode = self.game_modes[self.selected_mode]
        
        # Remove old targets and return them to pool
        for target in self.targets[:]:
            if current_time - target.spawn_time > mode.target_lifetime:
                if self.use_object_pools:
                    self.target_pool.release(target)  # Return to pool
                self.targets.remove(target)
        
        # Update moving targets
        for target in self.targets:
            if target.target_type == "moving":
                target.x += target.velocity[0]
                target.y += target.velocity[1]
                
                # Bounce off walls
                if target.x <= target.radius or target.x >= WINDOW_WIDTH - target.radius:
                    target.velocity = (-target.velocity[0], target.velocity[1])
                if target.y <= target.radius + 100 or target.y >= WINDOW_HEIGHT - target.radius:
                    target.velocity = (target.velocity[0], -target.velocity[1])
        
        # Spawn new targets
        active_targets = len([t for t in self.targets if not t.hit])
        
        if (active_targets < mode.max_targets and 
            current_time - self.last_spawn_time >= mode.spawn_rate):
            
            self.spawn_target(mode)
            self.last_spawn_time = current_time
        
        # Update particles
        self.particle_system.update()
    
    def spawn_target(self, mode: GameMode):
        margin = mode.target_size + 30
        max_attempts = 30
        
        # Define stats panel area to avoid (top-left corner)
        stats_panel_width = 300
        stats_panel_height = 220
        stats_avoid_margin = 20  # Extra margin around stats panel
        
        for _ in range(max_attempts):
            x = random.randint(margin, WINDOW_WIDTH - margin)
            y = random.randint(margin + 120, WINDOW_HEIGHT - margin)
            
            # Check if target would overlap with stats panel (top-left area)
            if (x - mode.target_size < stats_panel_width + stats_avoid_margin and 
                y - mode.target_size < stats_panel_height + stats_avoid_margin + 30):
                continue  # Try another position
            
            # Check overlap with existing targets
            valid_position = True
            for existing_target in self.targets:
                if not existing_target.hit:
                    distance = math.sqrt((x - existing_target.x)**2 + (y - existing_target.y)**2)
                    min_distance = mode.target_size + existing_target.radius + 25
                    if distance < min_distance:
                        valid_position = False
                        break
            
            if valid_position:
                target_type = "normal"
                color = TARGET_COLOR
                points = 1
                velocity = (0, 0)
                
                # Special target types for advanced modes
                if mode.name in ["Multi-Track", "Chaos Mode"]:
                    if random.random() < 0.3:  # 30% chance for moving target
                        target_type = "moving"
                        velocity = (random.uniform(-2, 2), random.uniform(-1.5, 1.5))
                        color = (255, 150, 50)
                        points = 2
                
                if random.random() < 0.1:  # 10% chance for bonus target
                    target_type = "bonus"
                    color = GOLD_COLOR
                    points = 5
                
                # Use object pooling if available, otherwise create new target
                if self.use_object_pools:
                    target = self.target_pool.get_target(
                        x=x, y=y, radius=mode.target_size,
                        target_type=target_type, velocity=velocity,
                        color=color, points=points
                    )
                else:
                    # Fallback to original Target creation
                    target = Target(x, y, mode.target_size, time.time(), 
                                  target_type=target_type, velocity=velocity, 
                                  color=color, points=points)
                
                self.targets.append(target)
                
                # Play target spawn sound (quietly)
                if self.sound_manager:
                    self.sound_manager.play(SoundEffect.TARGET_SPAWN, 0.3)
                break
    
    def draw_crosshair(self):
        x, y = self.crosshair_pos
        
        # Static crosshair color - no more dynamic changes during gameplay
        color = (255, 255, 255)  # Always white for consistent visibility
        
        # Static crosshair styles - no performance-based changes
        if self.settings["crosshair_style"] == 0:  # Default crosshair
            gap = 8
            line_length = 12
            line_width = 2
            
            # Main crosshair lines
            pygame.draw.line(self.screen, color, (x - line_length - gap, y), (x - gap, y), line_width)
            pygame.draw.line(self.screen, color, (x + gap, y), (x + line_length + gap, y), line_width)
            pygame.draw.line(self.screen, color, (x, y - line_length - gap), (x, y - gap), line_width)
            pygame.draw.line(self.screen, color, (x, y + gap), (x, y + line_length + gap), line_width)
            
        elif self.settings["crosshair_style"] == 1:  # Dot
            size = 4
            pygame.draw.circle(self.screen, color, (x, y), size)
            pygame.draw.circle(self.screen, (0, 0, 0), (x, y), size, 1)
            
        elif self.settings["crosshair_style"] == 2:  # Cross
            cross_size = 8
            
            # Diagonal cross
            pygame.draw.line(self.screen, color, (x - cross_size, y - cross_size), (x + cross_size, y + cross_size), 2)
            pygame.draw.line(self.screen, color, (x - cross_size, y + cross_size), (x + cross_size, y - cross_size), 2)
            
        elif self.settings["crosshair_style"] == 3:  # TenZ style (actual Valorant cyan crosshair)
            # TenZ's actual Valorant crosshair settings: cyan color, very small and precise
            tenz_color = (0, 255, 255)  # Cyan color like TenZ uses
            gap = 3  # Very small gap for maximum precision
            line_length = 8  # Shorter, more compact lines
            line_width = 2   # Slightly thicker for better visibility at small size
            
            # Horizontal line (left and right)
            pygame.draw.line(self.screen, tenz_color, (x - line_length - gap, y), (x - gap, y), line_width)
            pygame.draw.line(self.screen, tenz_color, (x + gap, y), (x + line_length + gap, y), line_width)
            
            # Vertical line (top and bottom)
            pygame.draw.line(self.screen, tenz_color, (x, y - line_length - gap), (x, y - gap), line_width)
            pygame.draw.line(self.screen, tenz_color, (x, y + gap), (x, y + line_length + gap), line_width)
            
            # Add black outline for better visibility (essential for cyan crosshair)
            outline_color = (0, 0, 0)
            outline_width = 1
            
            # Horizontal outline
            pygame.draw.line(self.screen, outline_color, (x - line_length - gap - 1, y - 1), (x - gap + 1, y - 1), outline_width)
            pygame.draw.line(self.screen, outline_color, (x - line_length - gap - 1, y + 1), (x - gap + 1, y + 1), outline_width)
            pygame.draw.line(self.screen, outline_color, (x + gap - 1, y - 1), (x + line_length + gap + 1, y - 1), outline_width)
            pygame.draw.line(self.screen, outline_color, (x + gap - 1, y + 1), (x + line_length + gap + 1, y + 1), outline_width)
            
            # Vertical outline
            pygame.draw.line(self.screen, outline_color, (x - 1, y - line_length - gap - 1), (x - 1, y - gap + 1), outline_width)
            pygame.draw.line(self.screen, outline_color, (x + 1, y - line_length - gap - 1), (x + 1, y - gap + 1), outline_width)
            pygame.draw.line(self.screen, outline_color, (x - 1, y + gap - 1), (x - 1, y + line_length + gap + 1), outline_width)
            pygame.draw.line(self.screen, outline_color, (x + 1, y + gap - 1), (x + 1, y + line_length + gap + 1), outline_width)
    
    def draw_background(self):
        # Professional gradient background
        self.screen.fill(BACKGROUND_COLOR)
        
        # Subtle gradient effect
        for y in range(0, WINDOW_HEIGHT, 2):
            gradient_intensity = y / WINDOW_HEIGHT * 0.15  # Reduced intensity
            gradient_color = (min(255, int(BACKGROUND_COLOR[0] + BACKGROUND_COLOR[0] * gradient_intensity)),
                            min(255, int(BACKGROUND_COLOR[1] + BACKGROUND_COLOR[1] * gradient_intensity)),
                            min(255, int(BACKGROUND_COLOR[2] + BACKGROUND_COLOR[2] * gradient_intensity)))
            pygame.draw.line(self.screen, gradient_color, (0, y), (WINDOW_WIDTH, y), 2)
        
        # Enhanced animated stars - professional but attractive
        current_time = time.time()
        if hasattr(self, 'background_stars'):
            for i, star in enumerate(self.background_stars[:60]):  # Increased to 60 stars
                # Multiple layers for depth
                layer = i % 3
                base_brightness = 0.2 + layer * 0.15
                twinkle = math.sin(current_time * star['twinkle_speed'] + i) * 0.2
                brightness = base_brightness + twinkle
                brightness = max(0.1, min(0.8, brightness))
                
                # Size and color variation based on layer
                if layer == 0:  # Distant stars (small, dim)
                    color = (int(100 * brightness), int(120 * brightness), int(140 * brightness))
                    size = 1
                elif layer == 1:  # Medium stars 
                    color = (int(140 * brightness), int(150 * brightness), int(160 * brightness))
                    size = 1 if brightness < 0.5 else 2
                else:  # Foreground stars (larger, brighter)
                    color = (int(160 * brightness), int(170 * brightness), int(180 * brightness))
                    size = 2 if brightness > 0.4 else 1
                
                pygame.draw.circle(self.screen, color, (int(star['x']), int(star['y'])), size)
        
        # Subtle grid pattern for professional look (very faint)
        if hasattr(self, 'state') and self.state == GameState.PLAYING:
            grid_color = (int(BACKGROUND_COLOR[0] + 8), int(BACKGROUND_COLOR[1] + 8), int(BACKGROUND_COLOR[2] + 8))  # Very subtle
            grid_spacing = 40
            
            # Vertical lines
            for x in range(0, WINDOW_WIDTH, grid_spacing):
                if x % (grid_spacing * 4) == 0:  # Every 4th line slightly more visible
                    line_color = (int(BACKGROUND_COLOR[0] + 12), int(BACKGROUND_COLOR[1] + 12), int(BACKGROUND_COLOR[2] + 12))
                    pygame.draw.line(self.screen, line_color, (x, 0), (x, WINDOW_HEIGHT), 1)
                else:
                    pygame.draw.line(self.screen, grid_color, (x, 0), (x, WINDOW_HEIGHT), 1)
            
            # Horizontal lines
            for y in range(0, WINDOW_HEIGHT, grid_spacing):
                if y % (grid_spacing * 4) == 0:  # Every 4th line slightly more visible
                    line_color = (int(BACKGROUND_COLOR[0] + 12), int(BACKGROUND_COLOR[1] + 12), int(BACKGROUND_COLOR[2] + 12))
                    pygame.draw.line(self.screen, line_color, (0, y), (WINDOW_WIDTH, y), 1)
                else:
                    pygame.draw.line(self.screen, grid_color, (0, y), (WINDOW_WIDTH, y), 1)
    
    def draw_text_centered(self, surface, text, font, color, rect):
        """Helper function to draw centered text in a rectangle"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)
        return text_rect
    
    def draw_text_aligned(self, surface, text, font, color, rect, align='left'):
        """Helper function to draw aligned text in a rectangle"""
        text_surface = font.render(text, True, color)
        
        if align == 'left':
            text_rect = text_surface.get_rect(left=rect.left + 10, centery=rect.centery)
        elif align == 'right':
            text_rect = text_surface.get_rect(right=rect.right - 10, centery=rect.centery)
        elif align == 'center':
            text_rect = text_surface.get_rect(center=rect.center)
        else:
            text_rect = text_surface.get_rect(left=rect.left + 10, centery=rect.centery)
            
        surface.blit(text_surface, text_rect)
        return text_rect
    
    def draw_menu(self):
        self.draw_background()
        
        # Glowing title with animation
        title_glow = math.sin(time.time() * 2) * 0.3 + 0.7
        title_color = (int(ACCENT_COLOR[0] * title_glow), int(ACCENT_COLOR[1] * title_glow), int(ACCENT_COLOR[2] * title_glow))
        
        title_rect = pygame.Rect(0, 80, WINDOW_WIDTH, 80)
        self.draw_text_centered(self.screen, "ELITE AIM TRAINER PRO", self.font_title, title_color, title_rect)
        
        # Animated subtitle
        subtitle_rect = pygame.Rect(0, 140, WINDOW_WIDTH, 40)
        self.draw_text_centered(self.screen, "Professional Aim Training - Track Progress - Unlock Achievements", 
                               self.font_medium, TEXT_COLOR, subtitle_rect)
        
        # Version and stats preview
        version_text = self.font_small.render("v2.0 Pro Edition", True, (120, 140, 160))
        self.screen.blit(version_text, (20, WINDOW_HEIGHT - 40))
        
        stats = self.stats_manager.stats
        quick_stats = self.font_small.render(
            f"Games: {stats['games_played']} | Best Accuracy: {stats['best_accuracy']:.1f}% | High Score: {stats['highest_score']}", 
            True, (120, 140, 160))
        quick_stats_rect = quick_stats.get_rect(right=WINDOW_WIDTH - 20, bottom=WINDOW_HEIGHT - 20)
        self.screen.blit(quick_stats, quick_stats_rect)
        
        # Enhanced game mode selection
        mode_title_rect = pygame.Rect(0, 200, WINDOW_WIDTH, 50)
        self.draw_text_centered(self.screen, "SELECT TRAINING MODE", self.font_large, TEXT_COLOR, mode_title_rect)
        
        # Difficulty colors
        difficulty_colors = {
            "Beginner": (100, 255, 100),
            "Intermediate": (255, 255, 100),
            "Advanced": (255, 150, 100),
            "Expert": (255, 100, 100),
            "Master": (255, 50, 150),
            "Insane": (255, 0, 255)
        }
        
        # Game mode selection with proper alignment - adjusted to prevent overlap
        button_area_height = 120  # Space needed for buttons at bottom
        available_height = WINDOW_HEIGHT - 250 - button_area_height  # Account for title and buttons
        mode_height = min(50, available_height // len(self.game_modes) - 2)  # Dynamic height
        mode_spacing = 2
        mode_y_start = 250  # Fixed start position
        
        for i, mode in enumerate(self.game_modes):
            y_pos = mode_y_start + i * (mode_height + mode_spacing)
            is_selected = i == self.selected_mode
            
            # Mode background with glow effect
            mode_rect = pygame.Rect(WINDOW_WIDTH//2 - 350, y_pos, 700, mode_height)
            
            if is_selected:
                # Animated selection glow
                glow_intensity = math.sin(time.time() * 4) * 0.3 + 0.7
                glow_color = (int(ACCENT_COLOR[0] * glow_intensity), int(ACCENT_COLOR[1] * glow_intensity), int(ACCENT_COLOR[2] * glow_intensity))
                
                # Draw glow
                for offset in range(3):
                    glow_rect = pygame.Rect(mode_rect.x - offset, mode_rect.y - offset, 
                                          mode_rect.width + offset*2, mode_rect.height + offset*2)
                    dim_glow_color = (glow_color[0]//4, glow_color[1]//4, glow_color[2]//4)
                    pygame.draw.rect(self.screen, dim_glow_color, glow_rect)
                
                pygame.draw.rect(self.screen, UI_COLOR, mode_rect)
                pygame.draw.rect(self.screen, glow_color, mode_rect, 3)
            else:
                pygame.draw.rect(self.screen, UI_COLOR, mode_rect)
                pygame.draw.rect(self.screen, (60, 70, 80), mode_rect, 1)
            
            # Mode info with proper alignment - adjust font size based on mode height
            font_scale = min(1.0, mode_height / 50.0)  # Scale fonts if modes are smaller
            name_font = self.font_medium if font_scale >= 0.8 else self.font_small
            desc_font = self.font_small if font_scale >= 0.8 else self.font_tiny
            
            name_rect = pygame.Rect(mode_rect.x, mode_rect.y, mode_rect.width - 120, mode_height // 2)
            self.draw_text_aligned(self.screen, mode.name, name_font, 
                                 ACCENT_COLOR if is_selected else TEXT_COLOR, name_rect, 'left')
            
            # Difficulty badge - aligned to right
            diff_color = difficulty_colors.get(mode.difficulty, TEXT_COLOR)
            diff_rect = pygame.Rect(mode_rect.right - 120, mode_rect.y, 100, mode_height // 2)
            self.draw_text_aligned(self.screen, mode.difficulty, desc_font, diff_color, diff_rect, 'center')
            
            # Description - aligned left below name (only if there's enough space)
            if mode_height > 35:
                desc_rect = pygame.Rect(mode_rect.x, mode_rect.y + mode_height // 2, mode_rect.width - 200, mode_height // 2)
                self.draw_text_aligned(self.screen, mode.description, desc_font, 
                                     (180, 190, 200), desc_rect, 'left')
                
                # Mode stats - aligned right below difficulty
                mode_record = stats.get("mode_records", {}).get(mode.name, {})
                if mode_record.get("games_played", 0) > 0:
                    record_text = f"Best: {mode_record.get('best_score', 0)} pts"
                    record_rect = pygame.Rect(mode_rect.right - 200, mode_rect.y + mode_height // 2, 180, mode_height // 2)
                    self.draw_text_aligned(self.screen, record_text, self.font_tiny if font_scale >= 0.8 else desc_font, 
                                         (140, 150, 160), record_rect, 'right')
        
        # Navigation buttons with proper positioning
        self.draw_menu_buttons()
        
        # Controls help
        controls = [
            "SPACE or CLICK - Start Game",
            "UP/DOWN - Select Mode",
            "S - Statistics",
            "A - Achievements", 
            "T - Settings",
            "ESC - Exit"
        ]
        
        for i, control in enumerate(controls):
            text = self.font_small.render(control, True, (140, 150, 160))
            self.screen.blit(text, (20, 50 + i * 20))
    
    def draw_menu_buttons(self):
        button_y = WINDOW_HEIGHT - 100
        button_width = 140
        button_height = 40
        button_spacing = 20
        
        # Calculate centered button positions for 4 buttons
        total_button_width = 4 * button_width + 3 * button_spacing
        start_x = WINDOW_WIDTH//2 - total_button_width//2
        
        buttons = [
            ("START GAME", start_x, ACCENT_COLOR),
            ("STATISTICS", start_x + button_width + button_spacing, (100, 150, 255)),
            ("ACHIEVEMENTS", start_x + 2 * (button_width + button_spacing), GOLD_COLOR),
            ("SETTINGS", start_x + 3 * (button_width + button_spacing), (150, 100, 255))
        ]
        
        for text, x, color in buttons:
            button_rect = pygame.Rect(x, button_y, button_width, button_height)
            
            # Button glow effect
            glow_intensity = math.sin(time.time() * 3) * 0.2 + 0.8
            glow_color = (int(color[0] * glow_intensity), int(color[1] * glow_intensity), int(color[2] * glow_intensity))
            
            pygame.draw.rect(self.screen, UI_COLOR, button_rect)
            pygame.draw.rect(self.screen, glow_color, button_rect, 2)
            
            # Centered text
            self.draw_text_centered(self.screen, text, self.font_medium, glow_color, button_rect)
    
    def draw_game(self):
        self.draw_background()
        
        # Draw particles (only if enabled)
        if self.settings["particles_enabled"]:
            self.particle_system.draw(self.screen)
        
        # Draw targets
        for target in self.targets:
            if not target.hit:
                self.draw_enhanced_target(target)
        
        # Enhanced HUD
        self.draw_game_hud()
        
        # Draw crosshair
        self.draw_crosshair()
        
        # Achievement notification
        if self.current_achievement and time.time() - self.achievement_notification_timer < 3:
            self.draw_achievement_notification()
        
        # Subtle streak effects
        if self.streak >= 10:
            self.draw_streak_effects()
    
    # def draw_environmental_particles(self):
    #     """Draw ambient environmental particles - disabled for cleaner look"""
    #     pass
    
    def draw_aim_assistance(self):
        """Draw subtle aim assistance lines"""
        if not self.targets:
            return
            
        current_time = time.time()
        mouse_x, mouse_y = self.crosshair_pos
        
        # Find closest target
        closest_target = min(self.targets, 
                           key=lambda t: math.sqrt((t.x - mouse_x)**2 + (t.y - mouse_y)**2))
        
        distance = math.sqrt((closest_target.x - mouse_x)**2 + (closest_target.y - mouse_y)**2)
        
        # Only show for targets within reasonable distance
        if distance < 200:
            # Subtle line with pulsing alpha
            pulse = math.sin(current_time * 4) * 0.3 + 0.4
            alpha = int(pulse * 60)
            
            line_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            line_color = (ACCENT_COLOR[0], ACCENT_COLOR[1], ACCENT_COLOR[2], alpha)
            
            # Draw dashed line
            dash_length = 10
            gap_length = 5
            total_length = dash_length + gap_length
            
            dx = closest_target.x - mouse_x
            dy = closest_target.y - mouse_y
            line_length = math.sqrt(dx**2 + dy**2)
            
            if line_length > 0:
                unit_dx = dx / line_length
                unit_dy = dy / line_length
                
                current_pos = 0
                while current_pos < line_length - dash_length:
                    start_x = mouse_x + unit_dx * current_pos
                    start_y = mouse_y + unit_dy * current_pos
                    end_x = mouse_x + unit_dx * (current_pos + dash_length)
                    end_y = mouse_y + unit_dy * (current_pos + dash_length)
                    
                    pygame.draw.line(line_surface, line_color, 
                                   (start_x, start_y), (end_x, end_y), 2)
                    
                    current_pos += total_length
            
            self.screen.blit(line_surface, (0, 0))
    
    # def draw_combo_effects(self):
    #     """Draw combo visual effects - disabled for cleaner look"""
    #     pass
    
    # def draw_screen_edge_effects(self):
    #     """Draw effects around screen edges - disabled for cleaner look"""
    #     pass
    
    def draw_performance_warning(self):
        """Draw performance warning overlay"""
        warning_surface = pygame.Surface((WINDOW_WIDTH, 50), pygame.SRCALPHA)
        warning_color = (255, 200, 0, 180)
        pygame.draw.rect(warning_surface, warning_color, (0, 0, WINDOW_WIDTH, 50))
        
        warning_text = "Performance Warning: Low FPS detected"
        text_surface = self.font_medium.render(warning_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, 25))
        
        self.screen.blit(warning_surface, (0, WINDOW_HEIGHT - 50))
        self.screen.blit(text_surface, (text_rect.x, WINDOW_HEIGHT - 50 + text_rect.y))
    
    def draw_enhanced_target(self, target):
        current_time = time.time()
        age = current_time - target.spawn_time
        
        # Smooth pulsing effect
        pulse = math.sin(current_time * 3) * 0.08 + 1
        radius = int(target.radius * pulse)
        
        # Enhanced target colors with better contrast
        if target.target_type == "bonus":
            # Animated gold for bonus targets
            gold_intensity = math.sin(current_time * 4) * 0.2 + 0.8
            color = (int(GOLD_COLOR[0] * gold_intensity), int(GOLD_COLOR[1] * gold_intensity), int(GOLD_COLOR[2] * gold_intensity))
        elif target.target_type == "moving":
            # Pulsing orange for moving targets
            orange_intensity = math.sin(current_time * 5) * 0.3 + 0.7
            color = (int(255 * orange_intensity), int(140 * orange_intensity), int(0 * orange_intensity))
        else:
            color = target.color
        
        # Target lifetime indicator
        mode = self.game_modes[self.selected_mode]
        lifetime_ratio = min(1.0, age / mode.target_lifetime)
        
        # Enhanced glow effect
        glow_radius = radius + 6
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        
        # Double glow layers for better visibility - draw directly on SRCALPHA surface
        glow_rgb = (color[0], color[1], color[2])
        
        # Outer glow - draw circle with alpha directly
        outer_glow_color = (glow_rgb[0], glow_rgb[1], glow_rgb[2], 40)
        pygame.draw.circle(glow_surface, outer_glow_color, (glow_radius, glow_radius), glow_radius)
        
        # Inner glow - draw circle with alpha directly  
        inner_glow_color = (glow_rgb[0], glow_rgb[1], glow_rgb[2], 80)
        pygame.draw.circle(glow_surface, inner_glow_color, (glow_radius, glow_radius), glow_radius - 2)
        
        glow_rect = glow_surface.get_rect(center=(int(target.x), int(target.y)))
        self.screen.blit(glow_surface, glow_rect)
        
        # Main target with gradient-like effect
        # Outer ring
        pygame.draw.circle(self.screen, color, (int(target.x), int(target.y)), radius)
        
        # Inner gradient simulation
        inner_color = (min(255, int(color[0] * 1.2)), min(255, int(color[1] * 1.2)), min(255, int(color[2] * 1.2)))
        pygame.draw.circle(self.screen, inner_color, (int(target.x), int(target.y)), max(1, radius - 3))
        
        # Professional border
        border_color = (255, 255, 255) if lifetime_ratio < 0.7 else (255, 150, 150)
        border_width = 2 if lifetime_ratio < 0.8 else 3
        pygame.draw.circle(self.screen, border_color, (int(target.x), int(target.y)), radius, border_width)
        
        # Enhanced center indicator
        center_size = max(3, radius // 4)
        if target.target_type == "bonus":
            # Animated center for bonus targets
            center_pulse = math.sin(current_time * 8) * 0.4 + 0.6
            center_color = (int(255 * center_pulse), int(255 * center_pulse), int(255 * center_pulse))
            pygame.draw.circle(self.screen, center_color, (int(target.x), int(target.y)), int(center_size * center_pulse))
        else:
            # Clean white center
            pygame.draw.circle(self.screen, (255, 255, 255), (int(target.x), int(target.y)), center_size)
            # Dark outline for better contrast
            pygame.draw.circle(self.screen, (0, 0, 0), (int(target.x), int(target.y)), center_size, 1)
        
        # Enhanced points indicator
        if target.points > 1:
            points_text = f"+{target.points}"
            
            # Background for text
            text_surface = self.font_small.render(points_text, True, (255, 255, 255))
            text_bg = pygame.Surface((text_surface.get_width() + 8, text_surface.get_height() + 4), pygame.SRCALPHA)
            bg_color = (GOLD_COLOR[0], GOLD_COLOR[1], GOLD_COLOR[2], 180) if target.target_type == "bonus" else (color[0], color[1], color[2], 180)
            pygame.draw.rect(text_bg, bg_color, (0, 0, text_bg.get_width(), text_bg.get_height()), border_radius=3)
            
            # Position above target
            text_rect = text_bg.get_rect(center=(int(target.x), int(target.y - target.radius - 20)))
            self.screen.blit(text_bg, text_rect)
            
            # Text with shadow
            shadow_surface = self.font_small.render(points_text, True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 1, text_rect.centery + 1))
            self.screen.blit(shadow_surface, shadow_rect)
            
            text_rect = text_surface.get_rect(center=(text_rect.centerx, text_rect.centery))
            self.screen.blit(text_surface, text_rect)
        
        # Urgency warning for expiring targets
        if lifetime_ratio > 0.75:
            warning_intensity = (lifetime_ratio - 0.75) / 0.25
            warning_pulse = math.sin(current_time * 12) * 0.5 + 0.5
            warning_alpha = int(warning_intensity * warning_pulse * 150)
            
            if warning_alpha > 20:
                warning_surface = pygame.Surface((radius * 3, radius * 3), pygame.SRCALPHA)
                warning_color_with_alpha = (255, 100, 100, warning_alpha)
                pygame.draw.circle(warning_surface, warning_color_with_alpha, 
                                 (radius * 3 // 2, radius * 3 // 2), radius + 8, 3)
                warning_rect = warning_surface.get_rect(center=(int(target.x), int(target.y)))
                self.screen.blit(warning_surface, warning_rect)
    
    def draw_rotating_star(self, x, y, size, color, rotation_degrees):
        """Draw a rotating star shape"""
        points = []
        for i in range(10):
            angle = math.radians(i * 36 + rotation_degrees)  # 36 degrees between points
            radius = size if i % 2 == 0 else size // 2
            px = x + radius * math.cos(angle - math.pi / 2)
            py = y + radius * math.sin(angle - math.pi / 2)
            points.append((px, py))
        
        if len(points) >= 3:
            pygame.draw.polygon(self.screen, color, points)
    
    def draw_star(self, x, y, size, color):
        points = []
        for i in range(10):
            angle = i * math.pi / 5
            radius = size if i % 2 == 0 else size // 2
            px = x + radius * math.cos(angle - math.pi / 2)
            py = y + radius * math.sin(angle - math.pi / 2)
            points.append((px, py))
        pygame.draw.polygon(self.screen, color, points)
    
    def draw_game_hud(self):
        elapsed_time = time.time() - self.game_start_time
        remaining_time = max(0, self.game_duration - elapsed_time)
        mode = self.game_modes[self.selected_mode]
        current_time = time.time()
        
        # Enhanced time bar
        bar_width = 320
        bar_height = 28
        bar_x = WINDOW_WIDTH - bar_width - 25
        bar_y = 25
        
        progress = remaining_time / self.game_duration
        
        # Time bar background with subtle gradient
        bg_surface = pygame.Surface((bar_width, bar_height))
        for i in range(bar_height):
            intensity = 1 - (i / bar_height) * 0.2
            bg_color = tuple(int(c * intensity) for c in (40, 50, 60))
            pygame.draw.line(bg_surface, bg_color, (0, i), (bar_width, i))
        self.screen.blit(bg_surface, (bar_x, bar_y))
        
        # Time bar fill with color coding
        if progress > 0.5:
            bar_color = ACCENT_COLOR
        elif progress > 0.25:
            bar_color = (255, 200, 0)
        else:
            # Pulsing red when time is low
            pulse = math.sin(current_time * 6) * 0.3 + 0.7
            bar_color = tuple(int(c * pulse) for c in (255, 120, 120))
        
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            fill_surface = pygame.Surface((fill_width, bar_height))
            for i in range(bar_height):
                intensity = 1 - (i / bar_height) * 0.15
                fill_color = tuple(int(c * intensity) for c in bar_color)
                pygame.draw.line(fill_surface, fill_color, (0, i), (fill_width, i))
            self.screen.blit(fill_surface, (bar_x, bar_y))
        
        # Time bar border
        border_color = tuple(min(255, c + 40) for c in bar_color)
        pygame.draw.rect(self.screen, border_color, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Time text with subtle shadow
        time_text = f"{remaining_time:.1f}s"
        shadow_surface = self.font_medium.render(time_text, True, (0, 0, 0))
        text_surface = self.font_medium.render(time_text, True, (255, 255, 255))
        
        text_center_x = bar_x + bar_width // 2
        text_center_y = bar_y + bar_height // 2
        
        # Shadow
        shadow_rect = shadow_surface.get_rect(center=(text_center_x + 1, text_center_y + 1))
        self.screen.blit(shadow_surface, shadow_rect)
        
        # Main text
        text_rect = text_surface.get_rect(center=(text_center_x, text_center_y))
        self.screen.blit(text_surface, text_rect)
        
        # Enhanced stats panel
        stats_panel = pygame.Rect(25, 25, 300, 220)
        
        # Panel background with gradient
        panel_surface = pygame.Surface((stats_panel.width, stats_panel.height), pygame.SRCALPHA)
        for i in range(stats_panel.height):
            alpha = int(180 - (i / stats_panel.height) * 30)
            color = (UI_COLOR[0], UI_COLOR[1], UI_COLOR[2], alpha)
            pygame.draw.line(panel_surface, color, (0, i), (stats_panel.width, i))
        
        self.screen.blit(panel_surface, (stats_panel.x, stats_panel.y))
        
        # Panel border - static color for clean gameplay
        pygame.draw.rect(self.screen, ACCENT_COLOR, stats_panel, 2)
        
        # Mode name with background
        mode_bg = pygame.Rect(stats_panel.x + 5, stats_panel.y + 8, stats_panel.width - 10, 25)
        mode_bg_surface = pygame.Surface((mode_bg.width, mode_bg.height), pygame.SRCALPHA)
        pygame.draw.rect(mode_bg_surface, (ACCENT_COLOR[0], ACCENT_COLOR[1], ACCENT_COLOR[2], 60), (0, 0, mode_bg.width, mode_bg.height))
        self.screen.blit(mode_bg_surface, mode_bg)
        
        mode_text = self.font_medium.render(mode.name, True, ACCENT_COLOR)
        mode_rect = mode_text.get_rect(center=mode_bg.center)
        self.screen.blit(mode_text, mode_rect)
        
        # Stats content
        accuracy = (self.hits / self.shots_fired * 100) if self.shots_fired > 0 else 0
        active_targets = len([t for t in self.targets if not t.hit])
        
        stats_data = [
            ("Score", f"{self.score}", GOLD_COLOR if self.score > 100 else ACCENT_COLOR),
            ("Accuracy", f"{accuracy:.1f}%", ACCENT_COLOR if accuracy >= 80 else (255, 200, 0) if accuracy >= 60 else (255, 150, 150)),
            ("Hits/Shots", f"{self.hits}/{self.shots_fired}", TEXT_COLOR),
            ("Streak", f"{self.streak}", GOLD_COLOR if self.streak >= 10 else ACCENT_COLOR),
            ("Active", f"{active_targets}/{mode.max_targets}", TEXT_COLOR)
        ]
        
        for i, (label, value, color) in enumerate(stats_data):
            y_offset = 45 + i * 28
            
            # Stat background (alternating)
            if i % 2 == 0:
                stat_bg = pygame.Rect(stats_panel.x + 3, stats_panel.y + y_offset - 2, stats_panel.width - 6, 24)
                stat_bg_surface = pygame.Surface((stat_bg.width, stat_bg.height), pygame.SRCALPHA)
                pygame.draw.rect(stat_bg_surface, (UI_COLOR[0], UI_COLOR[1], UI_COLOR[2], 40), (0, 0, stat_bg.width, stat_bg.height))
                self.screen.blit(stat_bg_surface, stat_bg)
            
            # Label
            label_surface = self.font_small.render(f"{label}:", True, (200, 210, 220))
            self.screen.blit(label_surface, (stats_panel.x + 12, stats_panel.y + y_offset))
            
            # Value
            value_surface = self.font_small.render(value, True, color)
            value_x = stats_panel.x + stats_panel.width - value_surface.get_width() - 12
            self.screen.blit(value_surface, (value_x, stats_panel.y + y_offset))
        
        # Enhanced streak indicator
        if self.streak >= 5:
            streak_text = f"STREAK x{self.streak}!"
            
            # Background glow
            if self.streak >= 15:
                streak_glow = math.sin(current_time * 5) * 0.4 + 0.6
                glow_color = (GOLD_COLOR[0], GOLD_COLOR[1], GOLD_COLOR[2], int(60 * streak_glow))
                glow_surface = pygame.Surface((400, 50), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, glow_color, (0, 0, 400, 50))
                glow_rect = glow_surface.get_rect(center=(WINDOW_WIDTH//2, 110))
                self.screen.blit(glow_surface, glow_rect)
            
            # Text with shadow
            shadow_surface = self.font_large.render(streak_text, True, (0, 0, 0))
            text_surface = self.font_large.render(streak_text, True, GOLD_COLOR if self.streak >= 10 else ACCENT_COLOR)
            
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH//2, 110))
            shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))
            
            self.screen.blit(shadow_surface, shadow_rect)
            self.screen.blit(text_surface, text_rect)
        
        # Performance indicator
        fps = int(self.clock.get_fps())
        if fps < 60:
            perf_color = (255, 150, 150) if fps < 30 else (255, 200, 100)
            perf_text = f"FPS: {fps}"
            perf_surface = self.font_small.render(perf_text, True, perf_color)
            self.screen.blit(perf_surface, (WINDOW_WIDTH - 80, WINDOW_HEIGHT - 25))
    
    def draw_achievement_notification(self):
        if not self.current_achievement:
            return
            
        elapsed = time.time() - self.achievement_notification_timer
        if elapsed > 3:
            self.current_achievement = None
            return
        
        # Enhanced notification panel with slide-in animation
        slide_progress = min(1.0, elapsed / 0.5)
        x_offset = int((1 - slide_progress) * 200)
        
        panel_rect = pygame.Rect(WINDOW_WIDTH - 320 + x_offset, 150, 300, 90)
        
        # Panel background with gradient
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        for i in range(panel_rect.height):
            alpha = int(200 - (i / panel_rect.height) * 40)
            color = (UI_COLOR[0], UI_COLOR[1], UI_COLOR[2], alpha)
            pygame.draw.line(panel_surface, color, (0, i), (panel_rect.width, i))
        
        self.screen.blit(panel_surface, panel_rect)
        
        # Border with glow
        glow_intensity = math.sin(time.time() * 4) * 0.3 + 0.7
        border_color = tuple(int(c * glow_intensity) for c in GOLD_COLOR)
        pygame.draw.rect(self.screen, border_color, panel_rect, 3)
        
        # Achievement text
        unlock_text = "ACHIEVEMENT UNLOCKED!"
        unlock_surface = self.font_medium.render(unlock_text, True, GOLD_COLOR)
        unlock_rect = unlock_surface.get_rect(center=(panel_rect.centerx, panel_rect.y + 20))
        self.screen.blit(unlock_surface, unlock_rect)
        
        # Achievement name
        name_surface = self.font_small.render(self.current_achievement.name, True, TEXT_COLOR)
        name_rect = name_surface.get_rect(center=(panel_rect.centerx, panel_rect.y + 45))
        self.screen.blit(name_surface, name_rect)
        
        # Achievement description
        desc_surface = self.font_tiny.render(self.current_achievement.description, True, (180, 190, 200))
        desc_rect = desc_surface.get_rect(center=(panel_rect.centerx, panel_rect.y + 65))
        self.screen.blit(desc_surface, desc_rect)
    
    def draw_streak_effects(self):
        """Draw subtle streak visual effects for high performance"""
        current_time = time.time()
        
        if self.streak >= 15:
            # Subtle screen edge glow for very high streaks
            glow_intensity = math.sin(current_time * 3) * 0.15 + 0.25
            alpha = int(glow_intensity * 80)
            
            edge_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            edge_color = (GOLD_COLOR[0], GOLD_COLOR[1], GOLD_COLOR[2], alpha)
            
            # Top and bottom edges
            pygame.draw.rect(edge_surface, edge_color, (0, 0, WINDOW_WIDTH, 3))
            pygame.draw.rect(edge_surface, edge_color, (0, WINDOW_HEIGHT-3, WINDOW_WIDTH, 3))
            
            # Left and right edges
            pygame.draw.rect(edge_surface, edge_color, (0, 0, 3, WINDOW_HEIGHT))
            pygame.draw.rect(edge_surface, edge_color, (WINDOW_WIDTH-3, 0, 3, WINDOW_HEIGHT))
            
            self.screen.blit(edge_surface, (0, 0))
        
        elif self.streak >= 10:
            # Subtle corner highlights for good streaks
            corner_size = 20
            corner_alpha = int((math.sin(current_time * 4) * 0.3 + 0.4) * 100)
            corner_color = (ACCENT_COLOR[0], ACCENT_COLOR[1], ACCENT_COLOR[2], corner_alpha)
            
            corner_surface = pygame.Surface((corner_size, corner_size), pygame.SRCALPHA)
            
            # Top-left corner triangle using polygon instead of set_at
            triangle_points = [(0, 0), (corner_size // 2, 0), (0, corner_size // 2)]
            pygame.draw.polygon(corner_surface, corner_color, triangle_points)
            
            self.screen.blit(corner_surface, (0, 0))
            
            # Top-right corner
            corner_surface_tr = pygame.transform.flip(corner_surface, True, False)
            self.screen.blit(corner_surface_tr, (WINDOW_WIDTH - corner_size, 0))
            
            # Bottom-left corner
            corner_surface_bl = pygame.transform.flip(corner_surface, False, True)
            self.screen.blit(corner_surface_bl, (0, WINDOW_HEIGHT - corner_size))
            
            # Bottom-right corner
            corner_surface_br = pygame.transform.flip(corner_surface, True, True)
            self.screen.blit(corner_surface_br, (WINDOW_WIDTH - corner_size, WINDOW_HEIGHT - corner_size))
    
    def draw_results(self):
        self.draw_background()
        
        # Calculate comprehensive stats
        game_time = self.game_duration
        accuracy = (self.hits / self.shots_fired * 100) if self.shots_fired > 0 else 0
        targets_per_second = self.hits / game_time if game_time > 0 else 0
        avg_reaction_time = sum(self.reaction_times) / len(self.reaction_times) if self.reaction_times else 0
        
        # Animated title
        title_glow = math.sin(time.time() * 3) * 0.3 + 0.7
        title_color = tuple(int(c * title_glow) for c in ACCENT_COLOR)
        
        title_rect = pygame.Rect(0, 80, WINDOW_WIDTH, 60)
        self.draw_text_centered(self.screen, "PERFORMANCE REPORT", self.font_title, title_color, title_rect)
        
        # Mode and grade
        mode_rect = pygame.Rect(0, 140, WINDOW_WIDTH, 40)
        self.draw_text_centered(self.screen, f"Mode: {self.game_modes[self.selected_mode].name}", 
                               self.font_large, TEXT_COLOR, mode_rect)
        
        # Performance grade
        grade = self.calculate_grade(accuracy, targets_per_second, avg_reaction_time)
        grade_color = self.get_grade_color(grade)
        grade_rect = pygame.Rect(0, 180, WINDOW_WIDTH, 60)
        self.draw_text_centered(self.screen, f"GRADE: {grade}", self.font_title, grade_color, grade_rect)
        
        # Detailed results in two columns with proper alignment
        left_col_x = WINDOW_WIDTH//2 - 250
        right_col_x = WINDOW_WIDTH//2 + 50
        col_width = 200
        
        left_results = [
            ("Final Score", f"{self.score:,} pts", self.score > self.stats_manager.stats.get('highest_score', 0)),
            ("Accuracy", f"{accuracy:.1f}%", accuracy > self.stats_manager.stats.get('best_accuracy', 0)),
            ("Targets Hit", f"{self.hits}", False),
            ("Shots Fired", f"{self.shots_fired}", False),
        ]
        
        right_results = [
            ("Max Streak", f"{self.max_streak}", self.max_streak > self.stats_manager.stats.get('longest_streak', 0)),
            ("Targets/Second", f"{targets_per_second:.2f}", targets_per_second > self.stats_manager.stats.get('best_targets_per_second', 0)),
            ("Avg Reaction", f"{avg_reaction_time*1000:.0f}ms" if avg_reaction_time > 0 else "N/A", 
             avg_reaction_time < self.stats_manager.stats.get('best_reaction_time', float('inf')) and avg_reaction_time > 0),
            ("Game Duration", f"{self.game_duration}s", False)
        ]
        
        # Draw results with proper alignment
        for i, ((left_label, left_value, left_record), (right_label, right_value, right_record)) in enumerate(zip(left_results, right_results)):
            y_pos = 280 + i * 50
            
            # Left column
            self.draw_result_item(left_col_x, y_pos, col_width, left_label, left_value, left_record)
            
            # Right column
            self.draw_result_item(right_col_x, y_pos, col_width, right_label, right_value, right_record)
        
        # Performance analysis
        analysis_y = 500
        analysis_text = self.get_performance_analysis(accuracy, targets_per_second, self.max_streak)
        analysis_rect = pygame.Rect(0, analysis_y, WINDOW_WIDTH, 40)
        self.draw_text_centered(self.screen, analysis_text, self.font_medium, ACCENT_COLOR, analysis_rect)
        
        # Continue instruction with timing
        continue_rect = pygame.Rect(0, WINDOW_HEIGHT - 80, WINDOW_WIDTH, 40)
        elapsed_time = time.time() - self.result_screen_timer
        
        if elapsed_time >= 2.0:
            # Can exit now
            self.draw_text_centered(self.screen, "Click anywhere to continue or press ESC", self.font_medium, (150, 255, 150), continue_rect)
        else:
            # Still in delay period
            remaining_time = 2.0 - elapsed_time
            wait_text = f"Please wait {remaining_time:.1f}s to continue... (or press ESC)"
            self.draw_text_centered(self.screen, wait_text, self.font_medium, (255, 200, 100), continue_rect)
    
    def draw_result_item(self, x, y, width, label, value, is_record):
        # Create rects for proper alignment
        label_rect = pygame.Rect(x, y, width * 0.6, 30)
        value_rect = pygame.Rect(x + width * 0.6, y, width * 0.4, 30)
        
        # Label - left aligned
        self.draw_text_aligned(self.screen, f"{label}:", self.font_medium, TEXT_COLOR, label_rect, 'left')
        
        # Value - right aligned
        color = GOLD_COLOR if is_record else TEXT_COLOR
        self.draw_text_aligned(self.screen, value, self.font_medium, color, value_rect, 'right')
        
        # Record indicator
        if is_record:
            record_rect = pygame.Rect(x + width + 10, y, 120, 30)
            self.draw_text_aligned(self.screen, "NEW RECORD!", self.font_small, GOLD_COLOR, record_rect, 'left')
    
    def calculate_grade(self, accuracy, tps, reaction_time):
        score = 0
        
        # More balanced accuracy scoring (40% weight) - easier to achieve good scores
        if accuracy >= 90: score += 40
        elif accuracy >= 85: score += 38
        elif accuracy >= 80: score += 35
        elif accuracy >= 75: score += 32
        elif accuracy >= 70: score += 28
        elif accuracy >= 65: score += 24
        elif accuracy >= 60: score += 20
        elif accuracy >= 50: score += 16
        elif accuracy >= 40: score += 12
        else: score += max(0, int(accuracy / 10) * 2)
        
        # More realistic TPS scoring (35% weight) - achievable targets
        if tps >= 2.5: score += 35
        elif tps >= 2.0: score += 32
        elif tps >= 1.8: score += 28
        elif tps >= 1.5: score += 25
        elif tps >= 1.2: score += 22
        elif tps >= 1.0: score += 18
        elif tps >= 0.8: score += 15
        elif tps >= 0.6: score += 12
        elif tps >= 0.4: score += 8
        else: score += max(0, int(tps * 10))
        
        # More forgiving reaction time scoring (25% weight)
        if reaction_time > 0:
            if reaction_time <= 0.2: score += 25
            elif reaction_time <= 0.3: score += 22
            elif reaction_time <= 0.4: score += 18
            elif reaction_time <= 0.5: score += 15
            elif reaction_time <= 0.6: score += 12
            elif reaction_time <= 0.8: score += 8
            else: score += 5
        else:
            score += 15  # Default decent score if no reaction time data
        
        # More achievable grade thresholds
        if score >= 90: return "S+"
        elif score >= 85: return "S"
        elif score >= 80: return "A+"
        elif score >= 75: return "A"
        elif score >= 70: return "B+"
        elif score >= 65: return "B"
        elif score >= 60: return "C+"
        elif score >= 55: return "C"
        elif score >= 45: return "D"
        else: return "F"
    
    def get_grade_color(self, grade):
        colors = {
            "S+": (255, 215, 0),    # Gold
            "S": (255, 215, 0),     # Gold
            "A+": (255, 165, 0),    # Orange
            "A": (255, 165, 0),     # Orange
            "B+": (0, 255, 0),      # Green
            "B": (0, 255, 0),       # Green
            "C+": (255, 255, 0),    # Yellow
            "C": (255, 255, 0),     # Yellow
            "D": (255, 100, 100),   # Red
            "F": (255, 0, 0)        # Bright Red
        }
        return colors.get(grade, TEXT_COLOR)
    
    def get_performance_analysis(self, accuracy, tps, streak):
        if accuracy >= 90 and tps >= 2.5:
            return "EXCEPTIONAL PERFORMANCE! Elite level precision and speed."
        elif accuracy >= 80 and tps >= 2.0:
            return "GREAT WORK! Your aim is improving consistently."
        elif accuracy >= 70:
            return "Good accuracy! Focus on increasing your speed."
        elif tps >= 2.0:
            return "Good speed! Work on your precision for better results."
        else:
            return "Keep practicing! Consistency is key to improvement."
    
    def draw_statistics(self):
        self.draw_background()
        
        title_rect = pygame.Rect(0, 60, WINDOW_WIDTH, 60)
        self.draw_text_centered(self.screen, "TRAINING STATISTICS", self.font_title, ACCENT_COLOR, title_rect)
        
        stats = self.stats_manager.stats
        
        # Overall stats panel with proper alignment
        panel_rect = pygame.Rect(50, 140, WINDOW_WIDTH - 100, 200)
        pygame.draw.rect(self.screen, UI_COLOR, panel_rect)
        pygame.draw.rect(self.screen, ACCENT_COLOR, panel_rect, 2)
        
        overall_stats = [
            ("Total Games Played", f"{stats['games_played']:,}"),
            ("Total Shots Fired", f"{stats['total_shots']:,}"),
            ("Total Hits", f"{stats['total_hits']:,}"),
            ("Overall Accuracy", f"{(stats['total_hits']/stats['total_shots']*100) if stats['total_shots'] > 0 else 0:.1f}%"),
            ("Total Playtime", f"{stats['total_playtime']/3600:.1f} hours"),
            ("Highest Score", f"{stats['highest_score']:,} pts")
        ]
        
        records = [
            ("Best Accuracy", f"{stats['best_accuracy']:.1f}%"),
            ("Best TPS", f"{stats['best_targets_per_second']:.2f}"),
            ("Best Reaction Time", f"{stats['best_reaction_time']*1000:.0f}ms" if stats['best_reaction_time'] < float('inf') else "N/A"),
            ("Longest Streak", f"{stats['longest_streak']}"),
            ("Games This Session", f"{self.stats_manager.session_stats['games_played']}"),
            ("Current Skill Level", self.get_skill_level(stats))
        ]
        
        # Draw stats in two columns with proper alignment
        col_width = panel_rect.width // 2
        for i, ((stat_name, stat_value), (record_name, record_value)) in enumerate(zip(overall_stats, records)):
            y_pos = panel_rect.y + 30 + i * 25
            row_height = 25
            
            # Left column - Overall stats
            left_col_rect = pygame.Rect(panel_rect.x, y_pos, col_width, row_height)
            label_rect = pygame.Rect(left_col_rect.x, left_col_rect.y, left_col_rect.width * 0.6, row_height)
            value_rect = pygame.Rect(left_col_rect.x + left_col_rect.width * 0.6, left_col_rect.y, left_col_rect.width * 0.4, row_height)
            
            self.draw_text_aligned(self.screen, f"{stat_name}:", self.font_small, TEXT_COLOR, label_rect, 'left')
            self.draw_text_aligned(self.screen, stat_value, self.font_small, ACCENT_COLOR, value_rect, 'right')
            
            # Right column - Records
            right_col_rect = pygame.Rect(panel_rect.x + col_width, y_pos, col_width, row_height)
            record_label_rect = pygame.Rect(right_col_rect.x, right_col_rect.y, right_col_rect.width * 0.6, row_height)
            record_value_rect = pygame.Rect(right_col_rect.x + right_col_rect.width * 0.6, right_col_rect.y, right_col_rect.width * 0.4, row_height)
            
            self.draw_text_aligned(self.screen, f"{record_name}:", self.font_small, TEXT_COLOR, record_label_rect, 'left')
            self.draw_text_aligned(self.screen, record_value, self.font_small, GOLD_COLOR, record_value_rect, 'right')
        
        # Mode-specific records
        mode_title_rect = pygame.Rect(0, 360, WINDOW_WIDTH, 40)
        self.draw_text_centered(self.screen, "MODE RECORDS", self.font_large, TEXT_COLOR, mode_title_rect)
        
        mode_records = stats.get("mode_records", {})
        y_start = 410
        
        for i, mode in enumerate(self.game_modes):
            if i >= 6:  # Limit display to prevent overflow
                break
                
            mode_data = mode_records.get(mode.name, {})
            y_pos = y_start + i * 40
            
            # Mode name
            name_rect = pygame.Rect(100, y_pos, 200, 20)
            self.draw_text_aligned(self.screen, mode.name, self.font_medium, TEXT_COLOR, name_rect, 'left')
            
            # Mode stats
            games = mode_data.get("games_played", 0)
            best_score = mode_data.get("best_score", 0)
            best_acc = mode_data.get("best_accuracy", 0)
            
            if games > 0:
                mode_stats = f"Games: {games} | Best Score: {best_score:,} | Best Accuracy: {best_acc:.1f}%"
                stats_color = ACCENT_COLOR
            else:
                mode_stats = "Not played yet"
                stats_color = (120, 130, 140)
            
            stats_rect = pygame.Rect(100, y_pos + 18, WINDOW_WIDTH - 200, 18)
            self.draw_text_aligned(self.screen, mode_stats, self.font_small, stats_color, stats_rect, 'left')
        
        # Back instruction
        back_rect = pygame.Rect(0, WINDOW_HEIGHT - 70, WINDOW_WIDTH, 40)
        self.draw_text_centered(self.screen, "Click anywhere or press ESC to return", self.font_medium, (150, 150, 150), back_rect)
    
    def draw_settings(self):
        self.draw_background()
        
        title_rect = pygame.Rect(0, 60, WINDOW_WIDTH, 60)
        self.draw_text_centered(self.screen, "SETTINGS", self.font_title, ACCENT_COLOR, title_rect)
        
        # Settings options - Enhanced with new features
        settings_list = [
            ("Crosshair Style", ["Default", "Dot", "Cross", "TenZ"]),
            ("Sound Effects", ["Enabled", "Disabled"]),
            ("Music", ["Enabled", "Disabled"]),
            ("Particle Effects", ["Enabled", "Disabled"]),
            ("Mouse Trail", ["Enabled", "Disabled"]),
            ("Theme", ["Default", "Dark", "Cyberpunk", "Neon", "Retro", "Ocean"])
        ]
        
        y_start = 200
        for i, (setting_name, options) in enumerate(settings_list):
            y_pos = y_start + i * 80
            
            # Setting name
            name_rect = pygame.Rect(200, y_pos, 300, 30)
            self.draw_text_aligned(self.screen, setting_name, self.font_medium, TEXT_COLOR, name_rect, 'left')
            
            # Options
            for j, option in enumerate(options):
                option_x = 200 + j * 150
                option_rect = pygame.Rect(option_x, y_pos + 30, 120, 30)
                
                # Determine if this option is selected
                is_selected = False
                if setting_name == "Crosshair Style" and j == self.settings["crosshair_style"]:
                    is_selected = True
                elif setting_name == "Sound Effects" and (j == 0) == self.settings["sound_enabled"]:
                    is_selected = True
                elif setting_name == "Music" and (j == 0) == self.settings["music_enabled"]:
                    is_selected = True
                elif setting_name == "Particle Effects" and (j == 0) == self.settings["particles_enabled"]:
                    is_selected = True
                elif setting_name == "Mouse Trail" and (j == 0) == self.settings["show_trail"]:
                    is_selected = True
                elif setting_name == "Theme":
                    theme_map = ["default", "dark", "cyberpunk", "neon", "retro", "ocean"]
                    current_theme = self.settings.get("theme", "default")
                    is_selected = j < len(theme_map) and theme_map[j] == current_theme
                
                if is_selected:
                    pygame.draw.rect(self.screen, ACCENT_COLOR, option_rect)
                    text_color = BACKGROUND_COLOR
                else:
                    pygame.draw.rect(self.screen, UI_COLOR, option_rect)
                    text_color = TEXT_COLOR
                
                pygame.draw.rect(self.screen, ACCENT_COLOR, option_rect, 2)
                
                self.draw_text_centered(self.screen, option, self.font_small, text_color, option_rect)
        
        # Volume controls removed for cleaner settings interface
        # Audio settings can be controlled through simple on/off toggles above
        
        # Back instruction
        back_rect = pygame.Rect(0, WINDOW_HEIGHT - 70, WINDOW_WIDTH, 40)
        self.draw_text_centered(self.screen, "Click anywhere or press ESC to return", self.font_medium, (150, 150, 150), back_rect)
    
    # Volume slider functionality removed for cleaner interface
    
    def update_ui_animations(self):
        # Update any UI animations
        current_time = time.time()
        
        # Pulse effect for menu items
        if self.state == GameState.MENU:
            pulse_value = math.sin(current_time * 2) * 0.1 + 0.9
            self.ui_animations['menu_pulse'] = pulse_value
    
    def draw_performance_graph(self, surface, rect, data, title, color):
        """Draw a simple performance graph"""
        if not data or len(data) < 2:
            return
        
        # Graph background
        pygame.draw.rect(surface, UI_COLOR, rect)
        pygame.draw.rect(surface, color, rect, 2)
        
        # Title
        title_rect = pygame.Rect(rect.x, rect.y - 25, rect.width, 20)
        self.draw_text_centered(surface, title, self.font_small, TEXT_COLOR, title_rect)
        
        # Calculate points
        max_val = max(data) if data else 1
        min_val = min(data) if data else 0
        val_range = max_val - min_val if max_val != min_val else 1
        
        points = []
        for i, value in enumerate(data[-50:]):  # Last 50 games
            x = rect.x + (i / len(data[-50:])) * rect.width
            y = rect.bottom - ((value - min_val) / val_range) * rect.height
            points.append((x, y))
        
        # Draw line
        if len(points) > 1:
            pygame.draw.lines(surface, color, False, points, 2)
        
        # Draw points
        for point in points:
            pygame.draw.circle(surface, color, (int(point[0]), int(point[1])), 3)
    
    def draw_fps_counter(self):
        """Draw FPS counter in corner"""
        fps = int(self.clock.get_fps())
        fps_text = self.font_tiny.render(f"FPS: {fps}", True, (100, 120, 140))
        self.screen.blit(fps_text, (WINDOW_WIDTH - 80, 10))
    
    def draw_performance_info(self):
        """Draw performance information if advanced features are enabled"""
        if not ADVANCED_FEATURES_AVAILABLE:
            return
        
        performance_data = self.quality_system.get_performance_report()
        metrics = performance_data['performance_metrics']
        
        if not metrics:
            return
        
        # Performance info panel
        info_y = 30
        info_texts = [
            f"Avg FPS: {metrics.get('avg_fps', 0):.1f}",
            f"Frame Time: {metrics.get('avg_frame_time', 0):.1f}ms",
            f"Performance: {metrics.get('performance_score', 100):.0f}%"
        ]
        
        optimization_info = performance_data['optimization_info']
        if optimization_info['level'] > 0:
            info_texts.append(f"Optimization: Level {optimization_info['level']}")
        
        for i, text in enumerate(info_texts):
            color = (100, 120, 140)
            if "Performance:" in text:
                score = metrics.get('performance_score', 100)
                if score > 80:
                    color = (100, 255, 100)  # Green
                elif score > 60:
                    color = (255, 255, 100)  # Yellow
                else:
                    color = (255, 100, 100)  # Red
            
            text_surface = self.font_tiny.render(text, True, color)
            self.screen.blit(text_surface, (WINDOW_WIDTH - 200, info_y + i * 15))
    
    def draw_combo_meter(self):
        """Draw combo/streak meter during gameplay"""
        if self.state != GameState.PLAYING or self.streak < 3:
            return
        
        # Combo meter position
        meter_x = WINDOW_WIDTH//2 - 100
        meter_y = WINDOW_HEIGHT - 80
        meter_width = 200
        meter_height = 20
        
        # Background
        pygame.draw.rect(self.screen, UI_COLOR, (meter_x, meter_y, meter_width, meter_height))
        
        # Fill based on streak
        fill_width = min(meter_width, (self.streak / 20) * meter_width)
        
        # Color based on streak level
        if self.streak >= 15:
            fill_color = GOLD_COLOR
        elif self.streak >= 10:
            fill_color = SECONDARY_ACCENT
        else:
            fill_color = ACCENT_COLOR
        
        pygame.draw.rect(self.screen, fill_color, (meter_x, meter_y, fill_width, meter_height))
        pygame.draw.rect(self.screen, TEXT_COLOR, (meter_x, meter_y, meter_width, meter_height), 2)
        
        # Combo text
        combo_rect = pygame.Rect(meter_x, meter_y - 25, meter_width, 20)
        self.draw_text_centered(self.screen, f"COMBO x{self.streak}", self.font_small, TEXT_COLOR, combo_rect)
    
    def draw_advanced_crosshair_trail(self):
        """Draw mouse trail effect"""
        if not self.settings["show_trail"] or self.state != GameState.PLAYING:
            return
        
        # Simple trail effect - store recent mouse positions
        if not hasattr(self, 'mouse_trail'):
            self.mouse_trail = []
        
        # Add current position
        self.mouse_trail.append(self.crosshair_pos)
        
        # Keep only recent positions
        if len(self.mouse_trail) > 10:
            self.mouse_trail.pop(0)
        
        # Draw trail
        for i, pos in enumerate(self.mouse_trail[:-1]):
            alpha = (i + 1) / len(self.mouse_trail)
            color = tuple(int(c * alpha * 0.5) for c in ACCENT_COLOR)
            pygame.draw.circle(self.screen, color, pos, max(1, int(3 * alpha)))
    
    def draw_target_preview_area(self):
        """Show target spawn prediction areas"""
        if self.state != GameState.PLAYING:
            return
        
        mode = self.game_modes[self.selected_mode]
        current_time = time.time()
        
        # Show potential spawn areas with subtle overlay
        if current_time - self.last_spawn_time >= mode.spawn_rate * 0.8:  # 80% of spawn time
            overlay_color = (ACCENT_COLOR[0], ACCENT_COLOR[1], ACCENT_COLOR[2], 20)
            margin = mode.target_size + 30
            
            # Create semi-transparent overlay for spawn area
            spawn_area = pygame.Rect(margin, margin + 120, 
                                   WINDOW_WIDTH - 2*margin, 
                                   WINDOW_HEIGHT - margin - 120)
            
            # Draw subtle indication with dimmed accent color
            dimmed_accent = (ACCENT_COLOR[0]//8, ACCENT_COLOR[1]//8, ACCENT_COLOR[2]//8)
            pygame.draw.rect(self.screen, dimmed_accent, spawn_area, 1)
    
    def save_session_data(self):
        """Save session data when closing"""
        session_data = {
            "session_games": self.stats_manager.session_stats["games_played"],
            "session_shots": self.stats_manager.session_stats["shots_fired"],
            "session_hits": self.stats_manager.session_stats["hits"],
            "timestamp": time.time()
        }
        
        try:
            with open("session_data.json", "w") as f:
                json.dump(session_data, f, indent=2)
        except (IOError, OSError):
            pass
    
    def get_skill_level(self, stats):
        games = stats['games_played']
        accuracy = stats['best_accuracy']
        tps = stats['best_targets_per_second']
        
        if games >= 100 and accuracy >= 95 and tps >= 3.5:
            return "ELITE"
        elif games >= 50 and accuracy >= 90 and tps >= 3.0:
            return "EXPERT"
        elif games >= 25 and accuracy >= 80 and tps >= 2.5:
            return "ADVANCED"
        elif games >= 10 and accuracy >= 70 and tps >= 2.0:
            return "INTERMEDIATE"
        elif games >= 5:
            return "BEGINNER"
        else:
            return "ROOKIE"
    
    def draw_achievements(self):
        self.draw_background()
        
        title_rect = pygame.Rect(0, 60, WINDOW_WIDTH, 60)
        self.draw_text_centered(self.screen, "ACHIEVEMENTS", self.font_title, GOLD_COLOR, title_rect)
        
        # Achievement progress
        unlocked_count = sum(1 for a in self.achievement_system.achievements if a.unlocked)
        total_count = len(self.achievement_system.achievements)
        progress_rect = pygame.Rect(0, 120, WINDOW_WIDTH, 30)
        self.draw_text_centered(self.screen, f"Progress: {unlocked_count}/{total_count} Unlocked", 
                               self.font_medium, TEXT_COLOR, progress_rect)
        
        # Achievement list
        y_start = 180
        for i, achievement in enumerate(self.achievement_system.achievements):
            y_pos = y_start + i * 60
            
            # Achievement panel
            panel_rect = pygame.Rect(100, y_pos, WINDOW_WIDTH - 200, 50)
            
            if achievement.unlocked:
                pygame.draw.rect(self.screen, UI_COLOR, panel_rect)
                pygame.draw.rect(self.screen, GOLD_COLOR, panel_rect, 2)
                name_color = GOLD_COLOR
                desc_color = TEXT_COLOR
            else:
                pygame.draw.rect(self.screen, (20, 20, 30), panel_rect)
                pygame.draw.rect(self.screen, (60, 60, 70), panel_rect, 1)
                name_color = (120, 120, 130)
                desc_color = (100, 100, 110)
            
            # Achievement icon - draw geometric shapes instead of text symbols
            icon_x = panel_rect.x + 15
            icon_y = panel_rect.y + 15
            icon_size = 20
            
            if achievement.unlocked:
                # Draw a filled circle for unlocked achievements
                pygame.draw.circle(self.screen, GOLD_COLOR, (icon_x, icon_y), icon_size // 2)
                pygame.draw.circle(self.screen, (255, 255, 255), (icon_x, icon_y), icon_size // 2, 2)
                # Add a checkmark effect with lines
                pygame.draw.line(self.screen, (255, 255, 255), 
                               (icon_x - 6, icon_y), (icon_x - 2, icon_y + 4), 3)
                pygame.draw.line(self.screen, (255, 255, 255), 
                               (icon_x - 2, icon_y + 4), (icon_x + 6, icon_y - 4), 3)
            else:
                # Draw a gray square for locked achievements
                icon_rect = pygame.Rect(icon_x - icon_size//2, icon_y - icon_size//2, icon_size, icon_size)
                pygame.draw.rect(self.screen, (60, 60, 70), icon_rect)
                pygame.draw.rect(self.screen, (120, 120, 130), icon_rect, 2)
                # Add an X for locked
                pygame.draw.line(self.screen, (120, 120, 130), 
                               (icon_x - 6, icon_y - 6), (icon_x + 6, icon_y + 6), 2)
                pygame.draw.line(self.screen, (120, 120, 130), 
                               (icon_x - 6, icon_y + 6), (icon_x + 6, icon_y - 6), 2)
            
            # Achievement name - better padding
            name_rect = pygame.Rect(panel_rect.x + 50, panel_rect.y + 5, panel_rect.width - 180, 20)
            self.draw_text_aligned(self.screen, achievement.name, self.font_medium, name_color, name_rect, 'left')
            
            # Achievement description - better padding
            desc_rect = pygame.Rect(panel_rect.x + 50, panel_rect.y + 25, panel_rect.width - 180, 20)
            self.draw_text_aligned(self.screen, achievement.description, self.font_small, desc_color, desc_rect, 'left')
            
            # Unlock date for completed achievements - fixed positioning
            if achievement.unlocked and achievement.unlock_time:
                unlock_date = time.strftime("%m/%d/%Y", time.localtime(achievement.unlock_time))
                date_rect = pygame.Rect(panel_rect.right - 150, panel_rect.y + 30, 140, 15)
                self.draw_text_aligned(self.screen, f"Unlocked: {unlock_date}", self.font_tiny, 
                                     (140, 150, 160), date_rect, 'right')
        
        # Back instruction
        back_rect = pygame.Rect(0, WINDOW_HEIGHT - 70, WINDOW_WIDTH, 40)
        self.draw_text_centered(self.screen, "Click anywhere or press ESC to return", self.font_medium, (150, 150, 150), back_rect)
    
    def run(self):
        running = True
        performance_update_counter = 0
        
        try:
            while running:
                try:
                    # Start performance monitoring if available
                    if ADVANCED_FEATURES_AVAILABLE:
                        self.quality_system.performance_monitor.start_frame()
                    
                    running = self.handle_events()
                    self.update_game()
                    self.update_ui_animations()
                    
                    # Draw current state with error handling
                    try:
                        if self.state == GameState.MENU:
                            self.draw_menu()
                        elif self.state == GameState.PLAYING:
                            self.draw_game()
                            self.draw_combo_meter()
                            self.draw_target_preview_area()
                            self.draw_advanced_crosshair_trail()
                        elif self.state == GameState.RESULTS:
                            self.draw_results()
                        elif self.state == GameState.STATISTICS:
                            self.draw_statistics()
                        elif self.state == GameState.ACHIEVEMENTS:
                            self.draw_achievements()
                        elif self.state == GameState.SETTINGS:
                            self.draw_settings()
                    except Exception as e:
                        print(f"Warning: Rendering error in state {self.state}: {e}")
                        # Continue running but skip this frame
                        continue
                    
                    # Always draw FPS counter
                    # Draw FPS counter only in debug mode (disabled for clean gameplay)
                    # self.draw_fps_counter()
                    
                    # Performance info disabled for clean gameplay experience
                    # Only enable for debugging performance issues
                    # if ADVANCED_FEATURES_AVAILABLE and performance_update_counter % 60 == 0:
                    #     try:
                    #         self.draw_performance_info()
                    #     except Exception as e:
                    #         print(f"Warning: Performance info rendering error: {e}")
                    
                    pygame.display.flip()
                    current_fps = self.clock.tick(FPS)
                    
                    # Update performance monitoring and optimization
                    if ADVANCED_FEATURES_AVAILABLE:
                        try:
                            self.quality_system.performance_monitor.end_frame(current_fps)
                            
                            # Update settings based on performance every 2 seconds
                            if performance_update_counter % 120 == 0:
                                self.quality_system.update_settings()
                        except Exception as e:
                            print(f"Warning: Performance monitoring error: {e}")
                    
                    performance_update_counter += 1
                    
                except pygame.error as e:
                    print(f"Pygame error in main loop: {e}")
                    # Try to continue or break if critical
                    if "display" in str(e).lower():
                        print("Critical display error, shutting down")
                        break
                    continue
                    
                except Exception as e:
                    print(f"Unexpected error in main loop: {e}")
                    # Try to continue for non-critical errors
                    continue
                    
        except Exception as e:
            print(f"Fatal error in game loop: {e}")
            running = False
            
            # Update session stats
            if self.state == GameState.PLAYING:
                self.stats_manager.session_stats["games_played"] = 1
                self.stats_manager.session_stats["shots_fired"] = self.shots_fired
                self.stats_manager.session_stats["hits"] = self.hits
        
        # Clean up object pools and sound system before closing
        if ADVANCED_FEATURES_AVAILABLE:
            print(f"Target pool stats - Available: {len(self.target_pool.available)}, In use: {len(self.target_pool.in_use)}")
            print(f"Particle pool stats - Available: {len(self.particle_pool.available)}, In use: {len(self.particle_pool.in_use)}")
            
            # Clean up sound system
            if self.sound_manager:
                self.sound_manager.cleanup()
            
            # Save analytics data
            if self.analytics:
                self.analytics.save_data()
        
        # Save data before closing
        self.save_session_data()
        pygame.quit()

def setup_logging():
    """Setup logging for debugging and error tracking"""
    import logging
    from datetime import datetime
    
    log_filename = f"aim_trainer_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def main():
    """Main function to run the aim trainer"""
    logger = setup_logging()
    
    try:
        logger.info("Initializing Elite Aim Trainer Pro v2.0")
        
        # Check system requirements
        import pygame
        logger.info(f"Pygame version: {pygame.version.ver}")
        
        # Initialize the game
        game = AimTrainer()
        logger.info(f"Game initialized with resolution: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # Display startup message
        print("=" * 60)
        print("ELITE AIM TRAINER PRO v2.0")
        print("=" * 60)
        print("Features:")
        print("* 8 Professional Training Modes")
        print("* Advanced Statistics Tracking")
        print("* Achievement System")
        print("* Performance Grading")
        print("* Enhanced Visual Effects")
        print("* Multiple Target Types")
        print("* Real-time Performance Analysis")
        print("* Detailed Analytics & Heat Maps")
        print("* Customizable Themes & Settings")
        print("=" * 60)
        print("Controls:")
        print("* SPACE/Click - Start Game")
        print("* UP/DOWN Keys - Navigate Modes")
        print("* S - Statistics")
        print("* A - Achievements")
        print("* ESC - Exit/Menu")
        print("=" * 60)
        print("Starting application...")
        
        # Run the game
        logger.info("Starting main game loop")
        game.run()
        
    except ImportError as e:
        error_msg = f"Missing required dependency: {e}"
        logger.error(error_msg)
        print(error_msg)
        print("Please install required packages:")
        print("pip install pygame numpy")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"Error running aim trainer: {e}")
        print("Check the log file for more details.")
    
    finally:
        logger.info("Application shutdown")
        print("Thanks for training! Keep improving your aim!")

if __name__ == "__main__":
    main()