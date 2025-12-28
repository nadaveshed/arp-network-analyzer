"""
Test script to verify project structure and basic functionality
Run this to ensure all modules can be imported correctly
"""
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all modules can be imported"""
    logger.info("Testing module imports...")
    
    try:
        # Test data models
        from models.node import NetworkNode
        from models.edge import Connection
        from models.graph import NetworkGraph
        logger.info("✓ Data models imported successfully")
        
        # Test utilities
        from utils.arp_parser import extract_arp_info, classify_arp_type
        from utils.transformers import normalize_mac, calculate_confidence
        logger.info("✓ Utilities imported successfully")
        
        # Test services
        from services.packet_capture import PacketCaptureService
        from services.graph_builder import GraphBuilderService
        from services.analyzer import NetworkAnalyzer
        from services.visualizer import GraphVisualizer
        from services.exporter import GraphExporter
        logger.info("✓ Services imported successfully")
        
        # Test controllers
        from controllers.cli_controller import CLIController
        from controllers.api_controller import APIController
        logger.info("✓ Controllers imported successfully")
        
        return True
    except Exception as e:
        logger.error(f"✗ Import failed: {e}")
        return False

def test_data_models():
    """Test basic data model functionality"""
    logger.info("\nTesting data models...")
    
    try:
        from models.node import NetworkNode
        from models.edge import Connection
        from models.graph import NetworkGraph
        
        # Test NetworkNode
        node1 = NetworkNode(ip="192.168.1.1", mac="aa:bb:cc:dd:ee:ff")
        node2 = NetworkNode(ip="192.168.1.2", mac="11:22:33:44:55:66")
        assert node1.get_id() == "aa:bb:cc:dd:ee:ff"
        logger.info("✓ NetworkNode creation works")
        
        # Test Connection
        conn = Connection(node1.get_id(), node2.get_id(), Connection.ARP_REQUEST)
        assert conn.source_id == node1.get_id()
        assert conn.confidence == 1.0
        logger.info("✓ Connection creation works")
        
        # Test NetworkGraph
        graph = NetworkGraph()
        graph.add_or_update_node(node1)
        graph.add_or_update_node(node2)
        graph.add_or_update_edge(conn)
        
        stats = graph.get_stats()
        assert stats['node_count'] == 2
        assert stats['edge_count'] == 1
        logger.info("✓ NetworkGraph operations work")
        logger.info(f"  Graph stats: {stats}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Data model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_utilities():
    """Test utility functions"""
    logger.info("\nTesting utilities...")
    
    try:
        from utils.transformers import normalize_mac, calculate_confidence
        from datetime import datetime
        
        # Test MAC normalization
        mac1 = normalize_mac("AA:BB:CC:DD:EE:FF")
        assert mac1 == "aa:bb:cc:dd:ee:ff"
        
        mac2 = normalize_mac("AA-BB-CC-DD-EE-FF")
        assert mac2 == "aa:bb:cc:dd:ee:ff"
        logger.info("✓ MAC normalization works")
        
        # Test confidence calculation
        confidence = calculate_confidence(10, datetime.now(), 0.95)
        assert 0.0 <= confidence <= 1.0
        logger.info(f"✓ Confidence calculation works (score: {confidence:.3f})")
        
        return True
    except Exception as e:
        logger.error(f"✗ Utility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_graph_export():
    """Test graph export functionality"""
    logger.info("\nTesting graph export...")
    
    try:
        from models.node import NetworkNode
        from models.edge import Connection
        from models.graph import NetworkGraph
        from services.exporter import GraphExporter
        import json
        import os
        
        # Create a sample graph
        graph = NetworkGraph()
        node1 = NetworkNode(ip="192.168.1.1", mac="aa:bb:cc:dd:ee:ff")
        node2 = NetworkNode(ip="192.168.1.2", mac="11:22:33:44:55:66")
        graph.add_or_update_node(node1)
        graph.add_or_update_node(node2)
        
        conn = Connection(node1.get_id(), node2.get_id(), Connection.ARP_REQUEST)
        graph.add_or_update_edge(conn)
        
        # Test JSON export
        exporter = GraphExporter(graph)
        json_path = exporter.export_json("test_export.json")
        
        # Verify file exists and is valid JSON
        assert os.path.exists(json_path)
        with open(json_path, 'r') as f:
            data = json.load(f)
            assert 'nodes' in data
            assert 'edges' in data
            assert len(data['nodes']) == 2
            assert len(data['edges']) == 1
        
        logger.info(f"✓ JSON export works (saved to {json_path})")
        
        # Cleanup
        os.remove(json_path)
        
        return True
    except Exception as e:
        logger.error(f"✗ Export test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("ARP Network Analyzer - Verification Tests")
    logger.info("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("Data Models", test_data_models()))
    results.append(("Utilities", test_utilities()))
    results.append(("Graph Export", test_graph_export()))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    logger.info(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        logger.info("\n🎉 All tests passed! Project is ready to use.")
        logger.info("\nTo start the analyzer:")
        logger.info("  python main.py --api")
        logger.info("\nNote: Requires administrator/root privileges for packet capture")
        return 0
    else:
        logger.error("\n❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
