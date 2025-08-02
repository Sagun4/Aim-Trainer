import pygame
import time
from collections import deque
from typing import Dict, List, Any
import json

class PerformanceMonitor:
    """Monitor and optimize game performance"""
    
    def __init__(self, window_size: int = 60):
        self.window_size = window_size
        self.frame_times = deque(maxlen=window_size)
        self.fps_history = deque(maxlen=window_size)
        self.memory_usage = deque(maxlen=window_size)
        
        self.frame_start_time = 0
        self.target_fps = 144
        self.performance_metrics = {}
        
        # Performance thresholds
        self.low_fps_threshold = 30  # Changed from 60 to 30 - be less aggressive
        self.high_frame_time_threshold = 1000 / 30  # 30 FPS in ms
        
    def start_frame(self):
        """Call at the beginning of each frame"""
        self.frame_start_time = time.perf_counter()
    
    def end_frame(self, fps: float):
        """Call at the end of each frame"""
        frame_time = (time.perf_counter() - self.frame_start_time) * 1000  # Convert to ms
        self.frame_times.append(frame_time)
        self.fps_history.append(fps)
        
        # Update performance metrics
        self._update_metrics()
    
    def _update_metrics(self):
        """Update performance metrics"""
        if len(self.frame_times) > 0:
            self.performance_metrics = {
                'avg_frame_time': sum(self.frame_times) / len(self.frame_times),
                'max_frame_time': max(self.frame_times),
                'min_frame_time': min(self.frame_times),
                'avg_fps': sum(self.fps_history) / len(self.fps_history),
                'min_fps': min(self.fps_history),
                'frame_time_variance': self._calculate_variance(self.frame_times),
                'performance_score': self._calculate_performance_score()
            }
    
    def _calculate_variance(self, values):
        """Calculate variance of values"""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def _calculate_performance_score(self):
        """Calculate overall performance score (0-100)"""
        if not self.fps_history:
            return 100
        
        avg_fps = sum(self.fps_history) / len(self.fps_history)
        fps_ratio = min(1.0, avg_fps / self.target_fps)
        
        # Penalize frame time spikes
        if self.frame_times:
            frame_time_penalty = max(0, (max(self.frame_times) - self.high_frame_time_threshold) / 10)
            fps_ratio -= frame_time_penalty / 100
        
        return max(0, min(100, fps_ratio * 100))
    
    def get_optimization_suggestions(self) -> List[str]:
        """Get performance optimization suggestions"""
        suggestions = []
        
        if self.performance_metrics.get('avg_fps', 144) < self.low_fps_threshold:
            suggestions.append("Consider reducing particle count or visual effects")
            suggestions.append("Lower screen resolution if possible")
        
        if self.performance_metrics.get('max_frame_time', 0) > self.high_frame_time_threshold * 2:
            suggestions.append("Frame time spikes detected - check for expensive operations")
        
        if self.performance_metrics.get('frame_time_variance', 0) > 10:
            suggestions.append("Inconsistent frame times - consider frame pacing")
        
        return suggestions
    
    def should_reduce_quality(self) -> bool:
        """Determine if quality should be automatically reduced"""
        # Need more samples and significantly low FPS to trigger optimization
        return (self.performance_metrics.get('avg_fps', 144) < self.low_fps_threshold and
                len(self.fps_history) >= self.window_size and  # Changed from window_size // 2
                self.performance_metrics.get('avg_fps', 144) < 25)  # Very low threshold
    
    def export_performance_data(self, filename: str = "performance_data.json"):
        """Export performance data for analysis"""
        data = {
            'metrics': self.performance_metrics,
            'frame_times': list(self.frame_times),
            'fps_history': list(self.fps_history),
            'timestamp': time.time()
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to export performance data: {e}")

class OptimizationManager:
    """Automatically adjust settings based on performance"""
    
    def __init__(self, performance_monitor: PerformanceMonitor):
        self.performance_monitor = performance_monitor
        self.auto_optimize = False  # Disable auto-optimization for now
        self.optimization_level = 0  # 0 = no optimization, 5 = maximum optimization
        
        self.optimization_settings = {
            1: {"particles_enabled": True, "particle_count_multiplier": 0.8, "glow_effects": True},
            2: {"particles_enabled": True, "particle_count_multiplier": 0.6, "glow_effects": True},
            3: {"particles_enabled": True, "particle_count_multiplier": 0.4, "glow_effects": False},
            4: {"particles_enabled": True, "particle_count_multiplier": 0.2, "glow_effects": False},
            5: {"particles_enabled": False, "particle_count_multiplier": 0.0, "glow_effects": False, "reduce_animations": True}
        }
    
    def update(self, game_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update game settings based on performance"""
        if not self.auto_optimize:
            return game_settings
        
        should_optimize = self.performance_monitor.should_reduce_quality()
        
        if should_optimize and self.optimization_level < 5:
            self.optimization_level += 1
            print(f"Performance optimization level increased to {self.optimization_level}")
        elif not should_optimize and self.optimization_level > 0:
            # Only reduce optimization level if performance has been good for a while
            avg_fps = self.performance_monitor.performance_metrics.get('avg_fps', 144)
            if avg_fps > self.performance_monitor.target_fps * 0.9:
                self.optimization_level = max(0, self.optimization_level - 1)
                print(f"Performance optimization level decreased to {self.optimization_level}")
        
        # Apply optimization settings
        if self.optimization_level > 0:
            optimization = self.optimization_settings.get(self.optimization_level, {})
            for key, value in optimization.items():
                if key in game_settings:
                    game_settings[key] = value
        
        return game_settings
    
    def get_current_optimization_info(self) -> Dict[str, Any]:
        """Get information about current optimization level"""
        return {
            'level': self.optimization_level,
            'auto_optimize_enabled': self.auto_optimize,
            'current_settings': self.optimization_settings.get(self.optimization_level, {}),
            'performance_score': self.performance_monitor.performance_metrics.get('performance_score', 100)
        }

class AdaptiveQualitySystem:
    """System that adapts game quality based on performance"""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.optimization_manager = OptimizationManager(self.performance_monitor)
        self.quality_levels = {
            'ultra': {'particles': True, 'glow': True, 'animations': True, 'effects': True},
            'high': {'particles': True, 'glow': True, 'animations': True, 'effects': False},
            'medium': {'particles': True, 'glow': False, 'animations': True, 'effects': False},
            'low': {'particles': False, 'glow': False, 'animations': False, 'effects': False}
        }
        self.current_quality = 'ultra'
    
    def update_frame(self, fps: float, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update system each frame and return optimized settings"""
        self.performance_monitor.start_frame()
        # ... game logic here ...
        self.performance_monitor.end_frame(fps)
        
        return self.optimization_manager.update(settings)
    
    def set_quality_level(self, level: str):
        """Manually set quality level"""
        if level in self.quality_levels:
            self.current_quality = level
            self.optimization_manager.auto_optimize = False
    
    def enable_auto_optimization(self):
        """Enable automatic quality optimization"""
        self.optimization_manager.auto_optimize = True
    
    def update_settings(self):
        """Update settings based on performance (called from main game loop)"""
        try:
            if hasattr(self.optimization_manager, 'auto_optimize') and self.optimization_manager.auto_optimize:
                # Get current performance metrics
                metrics = self.performance_monitor.performance_metrics
                
                if metrics and 'avg_fps' in metrics:
                    avg_fps = metrics['avg_fps']
                    
                    # Auto-adjust quality based on FPS
                    if avg_fps < 30 and self.current_quality != 'low':
                        # Switch to lower quality
                        quality_order = ['ultra', 'high', 'medium', 'low']
                        current_index = quality_order.index(self.current_quality)
                        if current_index < len(quality_order) - 1:
                            self.current_quality = quality_order[current_index + 1]
                            print(f"Performance: Reduced quality to {self.current_quality} (FPS: {avg_fps:.1f})")
                    
                    elif avg_fps > 60 and self.current_quality != 'ultra':
                        # Switch to higher quality
                        quality_order = ['low', 'medium', 'high', 'ultra']
                        current_index = quality_order.index(self.current_quality)
                        if current_index < len(quality_order) - 1:
                            self.current_quality = quality_order[current_index + 1]
                            print(f"Performance: Increased quality to {self.current_quality} (FPS: {avg_fps:.1f})")
        except Exception as e:
            print(f"Warning: Settings update error: {e}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        return {
            'performance_metrics': self.performance_monitor.performance_metrics,
            'optimization_info': self.optimization_manager.get_current_optimization_info(),
            'quality_level': self.current_quality,
            'suggestions': self.performance_monitor.get_optimization_suggestions()
        }
