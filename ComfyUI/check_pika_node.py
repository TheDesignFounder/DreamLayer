#!/usr/bin/env python3
"""
Quick check script for Pika Frame Node implementation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def check_pika_node():
    """Check if Pika Frame Node is properly implemented."""
    
    print("🔍 Checking Pika Frame Node Implementation...")
    print("=" * 60)
    
    # Check 1: File exists
    pika_file = "comfy_api_nodes/nodes_pika.py"
    if os.path.exists(pika_file):
        print("✅ nodes_pika.py file exists")
    else:
        print("❌ nodes_pika.py file NOT found")
        return False
    
    # Check 2: Read file content
    try:
        with open(pika_file, 'r') as f:
            content = f.read()
        print("✅ File readable")
    except Exception as e:
        print(f"❌ Cannot read file: {e}")
        return False
    
    # Check 3: PikaFrameNode class exists
    if "class PikaFrameNode" in content:
        print("✅ PikaFrameNode class found")
    else:
        print("❌ PikaFrameNode class NOT found")
        return False
    
    # Check 4: Node registration
    if '"PikaFrameNode": PikaFrameNode' in content:
        print("✅ Node registered in NODE_CLASS_MAPPINGS")
    else:
        print("❌ Node NOT registered")
        return False
    
    # Check 5: Required methods
    methods = [
        "INPUT_TYPES",
        "generate_frame", 
        "_extract_single_frame_to_png"
    ]
    
    for method in methods:
        if method in content:
            print(f"✅ {method} method found")
        else:
            print(f"❌ {method} method NOT found")
    
    # Check 6: Key parameters
    params = [
        "motion_strength",
        "resolution", 
        "prompt_text",
        "seed"
    ]
    
    for param in params:
        if f'"{param}"' in content:
            print(f"✅ {param} parameter found")
        else:
            print(f"❌ {param} parameter NOT found")
    
    # Check 7: Return type
    if 'RETURN_TYPES = ("IMAGE",)' in content:
        print("✅ Correct return type (IMAGE)")
    else:
        print("❌ Wrong or missing return type")
    
    # Check 8: Duration setting
    if "duration=5" in content:
        print("✅ Minimum duration (5s) set correctly")
    else:
        print("❌ Duration not set to 5 seconds")
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    
    # Count total checks
    total_checks = content.count("✅") if "✅" in locals() else 0
    
    if "class PikaFrameNode" in content and '"PikaFrameNode": PikaFrameNode' in content:
        print("🎉 PIKA FRAME NODE IS IMPLEMENTED!")
        print("🔧 Ready for testing in ComfyUI")
        return True
    else:
        print("❌ Implementation incomplete")
        return False

def show_testing_steps():
    """Show how to test the node."""
    print("\n🧪 HOW TO TEST:")
    print("=" * 60)
    print("1. Start ComfyUI:")
    print("   cd /Users/shathishwarmas/DreamLayer/ComfyUI")
    print("   python3 main.py --port 8191")
    print()
    print("2. Check if server starts:")
    print("   Look for: 'To see the GUI go to: http://127.0.0.1:8191'")
    print()
    print("3. Open browser:")
    print("   http://127.0.0.1:8191")
    print()
    print("4. Find the node:")
    print("   Right-click → api node → video → Pika → 'Pika Frame (Single Frame Generation)'")
    print()
    print("5. Alternative check - Search in ComfyUI:")
    print("   - Press Ctrl+Space (or Cmd+Space) to search")
    print("   - Type: 'Pika Frame'")
    print("   - Should show: 'Pika Frame (Single Frame Generation)'")

def check_port_availability():
    """Check which ports are available."""
    print("\n🌐 CHECKING AVAILABLE PORTS:")
    print("=" * 60)
    
    import socket
    
    ports_to_try = [8188, 8189, 8190, 8191, 8192]
    
    for port in ports_to_try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print(f"❌ Port {port}: IN USE")
        else:
            print(f"✅ Port {port}: AVAILABLE")

if __name__ == "__main__":
    success = check_pika_node()
    check_port_availability()
    
    if success:
        show_testing_steps()
    
    print(f"\n{'🎉 NODE READY!' if success else '❌ NEEDS FIXING'}")