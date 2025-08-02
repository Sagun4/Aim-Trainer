from dataclasses import dataclass
from typing import Tuple, Any, Callable, List
import time

@dataclass
class Target:
    """Target class for object pooling"""
    x: float
    y: float
    radius: float
    spawn_time: float
    hit: bool = False
    target_type: str = "normal"  # normal, bonus, moving
    velocity: Tuple[float, float] = (0, 0)
    color: Tuple[int, int, int] = (255, 70, 70)
    points: int = 1

class ObjectPool:
    """Generic object pool for reusing objects"""
    def __init__(self, create_func, reset_func, initial_size=50):
        self.create_func = create_func
        self.reset_func = reset_func
        self.available = [create_func() for _ in range(initial_size)]
        self.in_use = []
    
    def get(self):
        if self.available:
            obj = self.available.pop()
        else:
            obj = self.create_func()
        self.in_use.append(obj)
        return obj
    
    def release(self, obj):
        if obj in self.in_use:
            self.in_use.remove(obj)
            self.reset_func(obj)
            self.available.append(obj)

class TargetPool(ObjectPool):
    """Specialized pool for Target objects"""
    def __init__(self):
        super().__init__(
            create_func=lambda: Target(0, 0, 0, time.time()),
            reset_func=self._reset_target
        )
    
    def _reset_target(self, target):
        target.hit = False
        target.target_type = "normal"
        target.velocity = (0, 0)
        target.color = (255, 70, 70)
        target.points = 1
    
    def get_target(self, x: float, y: float, radius: float, target_type: str = "normal", 
                   velocity: Tuple[float, float] = (0, 0), color: Tuple[int, int, int] = (255, 70, 70), 
                   points: int = 1):
        """Get a configured target from the pool"""
        target = self.get()
        target.x = x
        target.y = y
        target.radius = radius
        target.spawn_time = time.time()
        target.target_type = target_type
        target.velocity = velocity
        target.color = color
        target.points = points
        return target

class ParticlePool(ObjectPool):
    """Specialized pool for particle objects"""
    def __init__(self):
        super().__init__(
            create_func=lambda: {
                'x': 0, 'y': 0, 'vx': 0, 'vy': 0,
                'life': 0, 'max_life': 0, 'color': (255, 255, 255), 'size': 0
            },
            reset_func=self._reset_particle
        )
    
    def _reset_particle(self, particle):
        particle.update({
            'x': 0, 'y': 0, 'vx': 0, 'vy': 0,
            'life': 0, 'max_life': 0, 'color': (255, 255, 255), 'size': 0
        })
