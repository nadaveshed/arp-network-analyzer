"""
Network Node Model - Represents a device on the network
מודל צומת רשת - מייצג מכשיר ברשת
"""
from datetime import datetime
from typing import Optional


class NetworkNode:
    """
    Represents a network device identified by IP and/or MAC address
    מייצג מכשיר רשת המזוהה על ידי כתובת IP ו/או MAC
    """
    
    def __init__(self, ip: Optional[str] = None, mac: Optional[str] = None):
        """
        אתחול צומת רשת חדש
        מטרה: יצירת אובייקט המייצג מכשיר ברשת עם כתובת IP ו/או MAC
        
        Args:
            ip: כתובת IP של המכשיר (אופציונלי)
            mac: כתובת MAC של המכשיר (אופציונלי)
        
        Raises:
            ValueError: אם לא סופקו גם IP וגם MAC
        """
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
        """
        יצירת מזהה ייחודי לצומת
        מטרה: להחזיר מזהה יציב ועקבי לצומת - מעדיף MAC על פני IP
        
        Returns:
            str: מזהה ייחודי (MAC אם קיים, אחרת IP)
        """
        # Prefer MAC as it's more stable, fallback to IP
        # מעדיף MAC כי הוא יציב יותר, נסיגה ל-IP
        return self.mac if self.mac else self.ip
    
    def update_activity(self):
        """
        עדכון פעילות הצומת
        מטרה: לעדכן את זמן הצפייה האחרון ולהגדיל את מונה החבילות
        משמש כאשר נתפסת חבילת ARP חדשה מהמכשיר הזה
        """
        self.last_seen = datetime.now()
        self.packet_count += 1
    
    def add_metadata(self, key: str, value):
        """
        הוספת או עדכון מטא-דאטה לצומת
        מטרה: לאחסן מידע נוסף על הצומת (למשל: centrality, activity_level)
        
        Args:
            key: מפתח המטא-דאטה
            value: ערך המטא-דאטה
        """
        self.metadata[key] = value
    
    def to_dict(self) -> dict:
        """
        המרת הצומת למילון
        מטרה: להמיר את האובייקט לפורמט JSON-friendly לצורך ייצוא והצגה
        
        Returns:
            dict: מילון המכיל את כל נתוני הצומת
        """
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
        """
        ייצוג טקסטואלי של הצומת
        מטרה: להציג את הצומת בצורה קריאה לצורכי debug
        """
        return f"NetworkNode(ip={self.ip}, mac={self.mac})"
    
    def __eq__(self, other):
        """
        השוואה בין שני צמתים
        מטרה: לבדוק אם שני צמתים מייצגים את אותו מכשיר (לפי ID)
        """
        if not isinstance(other, NetworkNode):
            return False
        return self.get_id() == other.get_id()
    
    def __hash__(self):
        """
        חישוב hash לצומת
        מטרה: לאפשר שימוש בצומת כמפתח במילון או בסט
        """
        return hash(self.get_id())
