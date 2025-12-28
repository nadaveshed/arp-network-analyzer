"""
Connection Edge Model - Represents ARP relationships between nodes
מודל קשר - מייצג יחסי ARP בין צמתים
"""
from datetime import datetime
from typing import List


class Connection:
    """
    Represents a directed connection/relationship between two network nodes
    מייצג קשר מכוון בין שני צמתי רשת
    """
    
    # Relationship types based on ARP packet types
    # סוגי קשרים מבוססים על סוגי חבילות ARP
    ARP_REQUEST = "arp_request"  # Source asks about target / מקור שואל על יעד
    ARP_REPLY = "arp_reply"      # Source responds to target / מקור עונה ליעד
    
    def __init__(self, source_id: str, target_id: str, relationship_type: str):
        """
        אתחול קשר חדש בין שני צמתים
        מטרה: יצירת קשר מכוון המייצג תקשורת ARP בין שני מכשירים
        
        Args:
            source_id: מזהה צומת המקור
            target_id: מזהה צומת היעד
            relationship_type: סוג הקשר (ARP_REQUEST או ARP_REPLY)
        """
        self.source_id = source_id
        self.target_id = target_id
        self.relationship_type = relationship_type
        self.confidence = 1.0  # ציון אמון ראשוני
        self.first_seen = datetime.now()
        self.last_seen = datetime.now()
        self.observation_count = 1  # מספר הצפיות בקשר
        self.timestamps: List[datetime] = [datetime.now()]  # היסטוריית זמנים
    
    def update_observation(self):
        """
        רישום צפייה חדשה בקשר
        מטרה: לעדכן את הקשר כאשר נצפתה חבילת ARP נוספת בין אותם מכשירים
        שומר רק 100 הזמנים האחרונים כדי למנוע בעיות זיכרון
        """
        self.last_seen = datetime.now()
        self.observation_count += 1
        self.timestamps.append(datetime.now())
        # Keep only recent timestamps to avoid memory bloat
        # שומר רק זמנים אחרונים כדי למנוע נפיחות זיכרון
        if len(self.timestamps) > 100:
            self.timestamps = self.timestamps[-100:]
    
    def calculate_confidence(self, decay_rate: float = 0.95) -> float:
        """
        חישוב ציון אמון מבוסס על עדכניות ותדירות
        מטרה: לחשב עד כמה הקשר הזה רלוונטי - קשרים עדכניים ותכופים מקבלים ציון גבוה
        
        Calculate confidence score based on recency and frequency
        
        Args:
            decay_rate: מקדם דעיכה אקספוננציאלי (0-1), מוחל לכל שעה
        
        Returns:
            ציון אמון בין 0 ל-1
        """
        now = datetime.now()
        hours_since_last = (now - self.last_seen).total_seconds() / 3600
        
        # Time decay component - רכיב דעיכת זמן
        time_factor = decay_rate ** hours_since_last
        
        # Frequency component (logarithmic scaling) - רכיב תדירות (סקאלה לוגריתמית)
        import math
        frequency_factor = min(1.0, math.log10(self.observation_count + 1) / 2)
        
        # Combined confidence - אמון משולב: 70% עדכניות + 30% תדירות
        self.confidence = (time_factor * 0.7) + (frequency_factor * 0.3)
        return self.confidence
    
    def to_dict(self) -> dict:
        """
        המרת הקשר למילון
        מטרה: להמיר את הקשר לפורמט JSON לצורך ייצוא והצגה
        
        Returns:
            dict: מילון המכיל את כל נתוני הקשר
        """
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
        """
        ייצוג טקסטואלי של הקשר
        מטרה: להציג את הקשר בצורה קריאה לצורכי debug
        """
        return f"Connection({self.source_id} -> {self.target_id}, type={self.relationship_type})"
