from datetime import datetime
from typing import List


class Connection:    
    # Relationship types based on ARP packet types
    ARP_REQUEST = "arp_request"  # Source asks about target
    ARP_REPLY = "arp_reply"      # Source responds to target
    
    def __init__(self, source_id: str, target_id: str, relationship_type: str):
        self.source_id = source_id
        self.target_id = target_id
        self.relationship_type = relationship_type
        self.confidence = 1.0
        self.first_seen = datetime.now()
        self.last_seen = datetime.now()
        self.observation_count = 1
        self.timestamps: List[datetime] = [datetime.now()]
    
    def update_observation(self):
        self.last_seen = datetime.now()
        self.observation_count += 1
        self.timestamps.append(datetime.now())
        # Keep only recent timestamps to avoid memory bloat
        if len(self.timestamps) > 100:
            self.timestamps = self.timestamps[-100:]
    
    def calculate_confidence(self, decay_rate: float = 0.95) -> float:
        now = datetime.now()
        hours_since_last = (now - self.last_seen).total_seconds() / 3600
        
        # Time decay component
        time_factor = decay_rate ** hours_since_last
        
        # Frequency component (logarithmic scaling)
        import math
        frequency_factor = min(1.0, math.log10(self.observation_count + 1) / 2)
        
        # Combined confidence - אמון משולב: 70% עדכניות + 30% תדירות
        self.confidence = (time_factor * 0.7) + (frequency_factor * 0.3)
        return self.confidence
    
    def to_dict(self) -> dict:
        return {
            "source": self.source_id,
            "target": self.target_id,
            "type": self.relationship_type,
            "confidence": round(self.confidence, 3),
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "observation_count": self.observation_count
        }
    
    def __repr__(self):
        return f"Connection({self.source_id} -> {self.target_id}, type={self.relationship_type})"
