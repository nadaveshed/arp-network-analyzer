from datetime import datetime
from typing import Optional


class NetworkNode:
    
    def __init__(self, ip: Optional[str] = None, mac: Optional[str] = None):
        if not ip and not mac:
            raise ValueError("Node must have at least IP or MAC address")
        
        self.ip = ip
        self.mac = mac
        self.hostname: Optional[str] = None
        self.first_seen = datetime.now()
        self.last_seen = datetime.now()
        self.packet_count = 0
        self.metadata = {}
    
    def get_id(self) -> str:
        # Prefer MAC as it's more stable, fallback to IP
        return self.mac if self.mac else self.ip
    
    def update_activity(self):
        self.last_seen = datetime.now()
        self.packet_count += 1
    
    def add_metadata(self, key: str, value):
        self.metadata[key] = value
    
    def to_dict(self) -> dict:
        return {
            "id": self.get_id(),
            "ip": self.ip,
            "mac": self.mac,
            "hostname": self.hostname,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "packet_count": self.packet_count,
            "metadata": self.metadata
        }
    
    def __repr__(self):
        return f"NetworkNode(ip={self.ip}, mac={self.mac})"
    
    def __eq__(self, other):
        if not isinstance(other, NetworkNode):
            return False
        return self.get_id() == other.get_id()
    
    def __hash__(self):
        return hash(self.get_id())
