"""
Packet Capture Service - Handles real-time ARP packet sniffing
שירות לכידת חבילות - מטפל בתפיסת חבילות ARP בזמן אמת
"""
import logging
from typing import Callable, Optional
from scapy.all import sniff, conf
import threading

import config

logger = logging.getLogger(__name__)


class PacketCaptureService:
    """
    Service for capturing ARP packets from the network
    שירות ללכידת חבילות ARP מהרשת - רץ בתהליך נפרד ומעביר חבילות לעיבוד
    """
    
    def __init__(self, interface: Optional[str] = None):
        """
        אתחול שירות לכידת חבילות
        
        מטרה: הכנת השירות ללכידת חבילות ARP מממשק רשת מסוים
        
        קלט (Input):
            interface: שם ממשק הרשת (למשל "Wi-Fi", "eth0")
                      אם None - יבחר אוטומטית את ממשק ברירת המחדל
        
        פלט (Output): אין - מאתחל את המשתנים הפנימיים
        
        משתנים פנימיים:
            - is_running: האם הלכידה פעילה
            - capture_thread: תהליך הלכידה המקבילי
            - packet_callback: פונקציה שתקרא לכל חבילה שנתפסת
            - packets_captured: מונה חבילות שנתפסו
        """
        self.interface = interface or config.DEFAULT_INTERFACE
        self.is_running = False
        self.capture_thread: Optional[threading.Thread] = None
        self.packet_callback: Optional[Callable] = None
        self.packets_captured = 0
    
    def start(self, callback: Callable):
        """
        התחלת לכידת חבילות
        
        מטרה: להפעיל את תהליך הלכידה בתהליך נפרד (thread) שלא יחסום את התוכנית
        
        Start capturing packets
        
        קלט (Input):
            callback: פונקציה שתקרא לכל חבילה שנתפסת
                     הפונקציה מקבלת פרמטר אחד: packet (אובייקט Scapy)
                     דוגמה: graph_builder.process_packet
        
        פלט (Output): אין
        
        תופעות לוואי:
            - יוצר thread חדש שרץ ברקע
            - מתחיל ללכוד חבילות ARP מהרשת
            - קורא ל-callback לכל חבילה שנתפסת
        
        הערות:
            - אם הלכידה כבר רצה, מדפיס אזהרה ולא עושה כלום
            - דורש הרשאות admin/root
        """
        if self.is_running:
            logger.warning("Capture already running")
            return
        
        self.packet_callback = callback
        self.is_running = True
        
        # Start capture in separate thread
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        logger.info(f"Started packet capture on interface: {self.interface or 'default'}")
    
    def stop(self):
        """
        עצירת לכידת חבילות
        
        מטרה: לעצור את תהליך הלכידה בצורה מסודרת
        
        קלט (Input): אין
        
        פלט (Output): אין
        
        תופעות לוואי:
            - משנה את is_running ל-False (גורם ל-thread להפסיק)
            - ממתין עד 2 שניות שה-thread יסתיים
            - מדפיס למסך כמה חבילות נתפסו בסך הכל
        
        הערות:
            - נקרא אוטומטית בעת כיבוי התוכנית (Ctrl+C)
        """
        self.is_running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        logger.info(f"Stopped packet capture. Total packets: {self.packets_captured}")
    
    def _capture_loop(self):
        """
        לולאת לכידה פנימית - רצה בתהליך נפרד
        
        מטרה: הלולאה המרכזית שתופסת חבילות מהרשת
        
        Internal capture loop running in separate thread
        
        קלט (Input): אין (משתמש במשתנים פנימיים של המחלקה)
        
        פלט (Output): אין
        
        תופעות לוואי:
            - משתמש ב-Scapy sniff() ללכידת חבילות
            - מסנן רק חבילות ARP (config.CAPTURE_FILTER)
            - קורא ל-_handle_packet לכל חבילה
            - רץ עד ש-is_running משתנה ל-False
        
        טיפול בשגיאות:
            - PermissionError: אין הרשאות admin/root
            - Exception: שגיאה כללית בלכידה
        
        הערות:
            - פונקציה פרטית (מתחילה ב-_) - לא לקרוא ישירות
            - רצה ב-daemon thread (נסגר אוטומטית עם התוכנית)
        """
        try:
            # Configure Scapy to be less verbose
            conf.verb = 0
            
            # Start sniffing
            sniff(
                iface=self.interface,
                filter=config.CAPTURE_FILTER,
                prn=self._handle_packet,
                store=False,  # Don't store packets in memory
                stop_filter=lambda _: not self.is_running
            )
        except PermissionError:
            logger.error("Permission denied. Run with administrator/root privileges.")
            self.is_running = False
        except Exception as e:
            logger.error(f"Capture error: {e}")
            self.is_running = False
    
    def _handle_packet(self, packet):
        """
        טיפול בחבילה בודדת שנתפסה
        
        מטרה: לעבד חבילה אחת ולהעביר אותה ל-callback
        
        Handle a single captured packet
        
        קלט (Input):
            packet: אובייקט חבילה מ-Scapy
                   מכיל את כל המידע על חבילת ה-ARP (IP, MAC, type)
        
        פלט (Output): אין
        
        תופעות לוואי:
            - מגדיל את מונה החבילות (packets_captured)
            - קורא ל-callback עם החבילה (אם הוגדר)
        
        טיפול בשגיאות:
            - תופס כל Exception ומדפיס שגיאה ללוג
            - לא עוצר את הלכידה גם אם יש שגיאה
        
        הערות:
            - נקרא אוטומטית על ידי Scapy לכל חבילה
            - פונקציה פרטית - לא לקרוא ישירות
        """
        try:
            self.packets_captured += 1
            
            if self.packet_callback:
                self.packet_callback(packet)
        except Exception as e:
            logger.error(f"Error handling packet: {e}")
    
    def get_status(self) -> dict:
        """
        קבלת סטטוס נוכחי של הלכידה
        
        מטרה: לספק מידע על מצב הלכידה הנוכחי
        
        Get current capture status
        
        קלט (Input): אין
        
        פלט (Output):
            dict: מילון עם המידע הבא:
                - running (bool): האם הלכידה פעילה כרגע
                - interface (str): שם ממשק הרשת
                - packets_captured (int): כמה חבילות נתפסו עד כה
        
        דוגמת פלט:
            {
                "running": True,
                "interface": "Wi-Fi",
                "packets_captured": 142
            }
        
        שימוש:
            משמש להצגת סטטוס למשתמש ב-CLI mode
        """
        return {
            "running": self.is_running,
            "interface": self.interface,
            "packets_captured": self.packets_captured
        }
