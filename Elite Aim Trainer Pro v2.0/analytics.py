import json
import time
import statistics
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

@dataclass
class ShotData:
    """Individual shot data for detailed analysis"""
    timestamp: float
    x: float
    y: float
    target_x: Optional[float]
    target_y: Optional[float]
    hit: bool
    reaction_time: Optional[float]
    distance_from_center: Optional[float]
    target_size: Optional[float]
    game_mode: str

@dataclass
class GameSession:
    """Complete game session data"""
    start_time: float
    end_time: float
    mode: str
    shots: List[ShotData]
    final_score: int
    final_accuracy: float
    max_streak: int
    average_reaction_time: float

class AdvancedAnalytics:
    """Advanced performance analytics and insights"""
    
    def __init__(self, data_file: str = "analytics_data.json"):
        self.data_file = data_file
        self.sessions: List[GameSession] = []
        self.current_session: Optional[GameSession] = None
        self.load_data()
    
    def start_session(self, mode: str):
        """Start a new game session"""
        self.current_session = GameSession(
            start_time=time.time(),
            end_time=0,
            mode=mode,
            shots=[],
            final_score=0,
            final_accuracy=0,
            max_streak=0,
            average_reaction_time=0
        )
    
    def record_shot(self, x: float, y: float, hit: bool, target_x: Optional[float] = None,
                   target_y: Optional[float] = None, reaction_time: Optional[float] = None,
                   target_size: Optional[float] = None):
        """Record a shot with all relevant data"""
        if not self.current_session:
            return
        
        distance_from_center = None
        if target_x is not None and target_y is not None:
            distance_from_center = ((x - target_x) ** 2 + (y - target_y) ** 2) ** 0.5
        
        shot = ShotData(
            timestamp=time.time(),
            x=x, y=y,
            target_x=target_x, target_y=target_y,
            hit=hit,
            reaction_time=reaction_time,
            distance_from_center=distance_from_center,
            target_size=target_size,
            game_mode=self.current_session.mode
        )
        
        self.current_session.shots.append(shot)
    
    def end_session(self, final_score: int, max_streak: int):
        """End the current session and save data"""
        if not self.current_session:
            return
        
        self.current_session.end_time = time.time()
        self.current_session.final_score = final_score
        self.current_session.max_streak = max_streak
        
        # Calculate session statistics
        hits = [shot for shot in self.current_session.shots if shot.hit]
        total_shots = len(self.current_session.shots)
        
        if total_shots > 0:
            self.current_session.final_accuracy = len(hits) / total_shots * 100
        
        reaction_times = [shot.reaction_time for shot in hits if shot.reaction_time is not None]
        if reaction_times:
            self.current_session.average_reaction_time = statistics.mean(reaction_times)
        
        self.sessions.append(self.current_session)
        self.current_session = None
        self.save_data()
    
    def get_accuracy_trend(self, days: int = 30) -> List[float]:
        """Get accuracy trend over the last N days"""
        cutoff_time = time.time() - (days * 24 * 3600)
        recent_sessions = [s for s in self.sessions if s.start_time > cutoff_time]
        
        if not recent_sessions:
            return []
        
        return [session.final_accuracy for session in recent_sessions]
    
    def get_reaction_time_trend(self, days: int = 30) -> List[float]:
        """Get reaction time trend over the last N days"""
        cutoff_time = time.time() - (days * 24 * 3600)
        recent_sessions = [s for s in self.sessions if s.start_time > cutoff_time]
        
        return [session.average_reaction_time for session in recent_sessions 
                if session.average_reaction_time > 0]
    
    def get_mode_performance(self, mode: str) -> Dict[str, Any]:
        """Get detailed performance statistics for a specific mode"""
        mode_sessions = [s for s in self.sessions if s.mode == mode]
        
        if not mode_sessions:
            return {}
        
        accuracies = [s.final_accuracy for s in mode_sessions]
        scores = [s.final_score for s in mode_sessions]
        reaction_times = [s.average_reaction_time for s in mode_sessions if s.average_reaction_time > 0]
        
        return {
            "games_played": len(mode_sessions),
            "average_accuracy": statistics.mean(accuracies),
            "best_accuracy": max(accuracies),
            "average_score": statistics.mean(scores),
            "best_score": max(scores),
            "average_reaction_time": statistics.mean(reaction_times) if reaction_times else 0,
            "best_reaction_time": min(reaction_times) if reaction_times else 0,
            "improvement_rate": self._calculate_improvement_rate(accuracies)
        }
    
    def get_heat_map_data(self, mode: Optional[str] = None) -> List[Dict[str, float]]:
        """Get shot position data for heat map visualization"""
        sessions = self.sessions
        if mode:
            sessions = [s for s in sessions if s.mode == mode]
        
        heat_map_data = []
        for session in sessions:
            for shot in session.shots:
                heat_map_data.append({
                    'x': shot.x,
                    'y': shot.y,
                    'hit': shot.hit,
                    'accuracy_weight': 1.0 if shot.hit else 0.0
                })
        
        return heat_map_data
    
    def get_weekly_summary(self) -> Dict[str, Any]:
        """Get performance summary for the current week"""
        week_start = time.time() - (7 * 24 * 3600)
        week_sessions = [s for s in self.sessions if s.start_time > week_start]
        
        if not week_sessions:
            return {"games_played": 0}
        
        total_shots = sum(len(s.shots) for s in week_sessions)
        total_hits = sum(len([shot for shot in s.shots if shot.hit]) for s in week_sessions)
        total_playtime = sum(s.end_time - s.start_time for s in week_sessions)
        
        return {
            "games_played": len(week_sessions),
            "total_shots": total_shots,
            "total_hits": total_hits,
            "overall_accuracy": (total_hits / total_shots * 100) if total_shots > 0 else 0,
            "total_playtime_hours": total_playtime / 3600,
            "average_session_length": total_playtime / len(week_sessions) / 60,  # minutes
            "best_accuracy": max(s.final_accuracy for s in week_sessions),
            "best_score": max(s.final_score for s in week_sessions)
        }
    
    def _calculate_improvement_rate(self, values: List[float]) -> float:
        """Calculate improvement rate as percentage change over time"""
        if len(values) < 2:
            return 0.0
        
        # Compare first quarter to last quarter of data
        quarter_size = max(1, len(values) // 4)
        early_avg = statistics.mean(values[:quarter_size])
        late_avg = statistics.mean(values[-quarter_size:])
        
        if early_avg == 0:
            return 0.0
        
        return ((late_avg - early_avg) / early_avg) * 100
    
    def load_data(self):
        """Load analytics data from file"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.sessions = []
                
                for session_data in data.get('sessions', []):
                    # Convert shot data
                    shots = []
                    for shot_data in session_data.get('shots', []):
                        shots.append(ShotData(**shot_data))
                    
                    # Create session
                    session = GameSession(
                        start_time=session_data['start_time'],
                        end_time=session_data['end_time'],
                        mode=session_data['mode'],
                        shots=shots,
                        final_score=session_data['final_score'],
                        final_accuracy=session_data['final_accuracy'],
                        max_streak=session_data['max_streak'],
                        average_reaction_time=session_data['average_reaction_time']
                    )
                    self.sessions.append(session)
        
        except (FileNotFoundError, json.JSONDecodeError):
            self.sessions = []
    
    def save_data(self):
        """Save analytics data to file"""
        data = {
            'sessions': []
        }
        
        for session in self.sessions:
            session_dict = asdict(session)
            data['sessions'].append(session_dict)
        
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save analytics data: {e}")
    
    def export_csv(self, filename: str = "aim_trainer_data.csv"):
        """Export shot data to CSV for external analysis"""
        import csv
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'mode', 'x', 'y', 'target_x', 'target_y', 
                         'hit', 'reaction_time', 'distance_from_center', 'target_size']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for session in self.sessions:
                for shot in session.shots:
                    writer.writerow({
                        'timestamp': shot.timestamp,
                        'mode': session.mode,
                        'x': shot.x,
                        'y': shot.y,
                        'target_x': shot.target_x,
                        'target_y': shot.target_y,
                        'hit': shot.hit,
                        'reaction_time': shot.reaction_time,
                        'distance_from_center': shot.distance_from_center,
                        'target_size': shot.target_size
                    })
