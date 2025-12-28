"""
ARP Packet Parser Utilities
"""
from typing import Optional, Dict, Tuple
from scapy.all import ARP
import logging

logger = logging.getLogger(__name__)


def extract_arp_info(packet) -> Optional[Dict[str, str]]:
    """
    Extract relevant information from an ARP packet
    
    Args:
        packet: Scapy packet object
    
    Returns:
        Dictionary with ARP info or None if invalid
    """
    try:
        if not packet.haslayer(ARP):
            return None
        
        arp = packet[ARP]
        
        return {
            "op": arp.op,  # 1 = request, 2 = reply
            "src_mac": arp.hwsrc,
            "src_ip": arp.psrc,
            "dst_mac": arp.hwdst,
            "dst_ip": arp.pdst
        }
    except Exception as e:
        logger.error(f"Error extracting ARP info: {e}")
        return None


def classify_arp_type(arp_info: Dict[str, str]) -> str:
    """
    Classify ARP packet as request or reply
    
    Args:
        arp_info: Dictionary from extract_arp_info
    
    Returns:
        "request" or "reply"
    """
    return "request" if arp_info["op"] == 1 else "reply"


def validate_arp_packet(arp_info: Dict[str, str]) -> bool:
    """
    Validate ARP packet for sanity checks
    
    Args:
        arp_info: Dictionary from extract_arp_info
    
    Returns:
        True if packet appears valid
    """
    # Check for null/broadcast addresses
    if arp_info["src_ip"] == "0.0.0.0":
        return False
    
    if arp_info["src_mac"] == "00:00:00:00:00:00":
        return False
    
    # Check for multicast MAC (first octet odd)
    try:
        first_octet = int(arp_info["src_mac"].split(":")[0], 16)
        if first_octet & 1:  # Multicast bit set
            return False
    except:
        return False
    
    return True


def get_relationship_endpoints(arp_info: Dict[str, str]) -> Tuple[Dict, Dict]:
    """
    Extract source and target node information from ARP packet
    
    Args:
        arp_info: Dictionary from extract_arp_info
    
    Returns:
        Tuple of (source_node_info, target_node_info) dictionaries
    """
    arp_type = classify_arp_type(arp_info)
    
    if arp_type == "request":
        # In a request: source asks about target IP
        source = {
            "ip": arp_info["src_ip"],
            "mac": arp_info["src_mac"]
        }
        target = {
            "ip": arp_info["dst_ip"],
            "mac": None  # Unknown in request
        }
    else:  # reply
        # In a reply: source responds to target
        source = {
            "ip": arp_info["src_ip"],
            "mac": arp_info["src_mac"]
        }
        target = {
            "ip": arp_info["dst_ip"],
            "mac": arp_info["dst_mac"]
        }
    
    return source, target
