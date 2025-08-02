import pygame
from functools import lru_cache

class RenderCache:
    """Cache for commonly used surfaces to reduce rendering overhead"""
    
    def __init__(self):
        self.text_cache = {}
        self.surface_cache = {}
        self.max_cache_size = 100
    
    @lru_cache(maxsize=128)
    def get_text_surface(self, text, font_size, color, bold=False):
        """Cache text surfaces to avoid re-rendering"""
        key = (text, font_size, color, bold)
        if key not in self.text_cache:
            font = pygame.font.Font(None, font_size)
            font.set_bold(bold)
            surface = font.render(text, True, color)
            
            # Limit cache size
            if len(self.text_cache) >= self.max_cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self.text_cache))
                del self.text_cache[oldest_key]
            
            self.text_cache[key] = surface
        
        return self.text_cache[key]
    
    def create_gradient_surface(self, width, height, color1, color2, vertical=True):
        """Create gradient surface with caching"""
        key = (width, height, color1, color2, vertical)
        if key not in self.surface_cache:
            surface = pygame.Surface((width, height))
            
            for i in range(height if vertical else width):
                ratio = i / (height - 1 if vertical else width - 1)
                color = tuple(
                    int(color1[j] + (color2[j] - color1[j]) * ratio)
                    for j in range(3)
                )
                
                if vertical:
                    pygame.draw.line(surface, color, (0, i), (width, i))
                else:
                    pygame.draw.line(surface, color, (i, 0), (i, height))
            
            self.surface_cache[key] = surface
        
        return self.surface_cache[key]
    
    def clear_cache(self):
        """Clear all cached surfaces"""
        self.text_cache.clear()
        self.surface_cache.clear()

# Global render cache instance
render_cache = RenderCache()
