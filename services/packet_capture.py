import logging
from typing import Callable, Optional
from scapy.all import sniff, conf
import threading

import config

logger = logging.getLogger(__name__)


class PacketCaptureService:
    
    def __init__(self, interface: Optional[str] = None):
        self.interface = interface or config.DEFAULT_INTERFACE
        self.is_running = False
        self.capture_thread: Optional[threading.Thread] = None
        self.packet_callback: Optional[Callable] = None
        self.packets_captured = 0
    
    def start(self, callback: Callable):
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
        self.is_running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        logger.info(f"Stopped packet capture. Total packets: {self.packets_captured}")
    
    def _capture_loop(self):
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
        try:
            self.packets_captured += 1
            
            if self.packet_callback:
                self.packet_callback(packet)
        except Exception as e:
            logger.error(f"Error handling packet: {e}")
    
    def get_status(self) -> dict:
        return {
            "running": self.is_running,
            "interface": self.interface,
            "packets_captured": self.packets_captured
        }
