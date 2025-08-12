"""Basic audit logging for Community Edition"""
import time
from datetime import datetime
from typing import List, Optional, Dict

class BasicAuditLogger:
    """Simple in-memory audit logger - Community Edition"""
    
    def __init__(self, max_events: int = 1000):
        self.events: List[Dict] = []
        self.max_events = max_events  # Community limit
    
    def log_event(self, event_type: str, user_id: str, details: dict):
        """Log a security event (Community: basic logging only)"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "details": details
        }
        
        self.events.append(event)
        
        # Community Edition: Keep only recent events
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
    
    def get_events(self, user_id: Optional[str] = None, limit: int = 100) -> List[dict]:
        """Get filtered events (Community: limited to 100)"""
        filtered_events = self.events
        
        if user_id:
            filtered_events = [e for e in filtered_events if e["user_id"] == user_id]
        
        # Community Edition: Return limited results
        return filtered_events[-limit:]
    
    def get_stats(self) -> dict:
        """Get basic statistics"""
        return {
            "total_events": len(self.events),
            "event_types": list(set(e["event_type"] for e in self.events)),
            "unique_users": len(set(e["user_id"] for e in self.events))
        }
