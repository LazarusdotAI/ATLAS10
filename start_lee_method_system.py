#!/usr/bin/env python3
"""
A.T.L.A.S. Lee Method System Startup Script
Starts the complete Lee Method scanner system including API server
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("=" * 70)
    print("🚀 A.T.L.A.S. LEE METHOD SCANNER SYSTEM")
    print("=" * 70)
    print("Advanced Trading & Learning Analysis System")
    print("Lee Method Pattern Detection - Replacing TTM Squeeze")
    print("=" * 70)

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n[CHECK] Verifying dependencies...")
    
    required_packages = [
        'flask', 'flask-cors', 'pandas', 'numpy', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n[ERROR] Missing packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("[OK] All dependencies are installed!")
    return True

def start_api_server():
    """Start the Lee Method API server in background"""
    print("\n[LAUNCH] Starting Lee Method API server...")
    
    try:
        # Import and start the API server
        from atlas_lee_method_api import start_api_server
        
        # Start in a separate thread
        api_thread = threading.Thread(
            target=start_api_server,
            kwargs={'host': 'localhost', 'port': 5001, 'debug': False}
        )
        api_thread.daemon = True
        api_thread.start()
        
        # Give the server time to start
        time.sleep(3)
        
        print("   ✅ Lee Method API server started on http://localhost:5001")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to start API server: {e}")
        return False

def open_interface():
    """Open the A.T.L.A.S. interface in browser"""
    print("\n[LAUNCH] Opening A.T.L.A.S. interface...")
    
    try:
        # Get the path to the HTML interface
        interface_path = Path(__file__).parent / "atlas_interface.html"
        
        if interface_path.exists():
            # Open in default browser
            webbrowser.open(f"file://{interface_path.absolute()}")
            print("   ✅ A.T.L.A.S. interface opened in browser")
            return True
        else:
            print(f"   ❌ Interface file not found: {interface_path}")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to open interface: {e}")
        return False

def show_system_info():
    """Show system information and usage instructions"""
    print("\n" + "=" * 70)
    print("🎯 LEE METHOD SYSTEM INFORMATION")
    print("=" * 70)
    
    print("\n📊 LEE METHOD CRITERIA:")
    print("   1. Three (or more) histogram bars that decrease, followed by an increase")
    print("   2. Momentum should be greater than the prior momentum bar")
    print("   3. Identify significant shifts from weekly and daily charts")
    
    print("\n🔗 API ENDPOINTS:")
    print("   • Status:     http://localhost:5001/api/lee-method/status")
    print("   • Signals:    http://localhost:5001/api/lee-method/signals")
    print("   • Health:     http://localhost:5001/api/lee-method/health")
    print("   • Criteria:   http://localhost:5001/api/lee-method/criteria")
    
    print("\n🎮 INTERFACE FEATURES:")
    print("   • Real-time Lee Method scanner results")
    print("   • Live signal updates every 30 seconds")
    print("   • Manual scan trigger")
    print("   • Scanner status monitoring")
    
    print("\n⚙️ SYSTEM COMPONENTS:")
    print("   • lee_method_scanner.py - Core pattern detection")
    print("   • atlas_lee_method_realtime_scanner.py - Real-time scanning")
    print("   • atlas_lee_method_api.py - Web API server")
    print("   • atlas_interface.html - Web interface")
    
    print("\n📝 USAGE NOTES:")
    print("   • Scanner monitors 24 popular stocks")
    print("   • Signals expire after 1 hour")
    print("   • API requires valid FMP key for live data")
    print("   • Demo mode uses mock data when API unavailable")

def wait_for_exit():
    """Wait for user to exit"""
    print("\n" + "=" * 70)
    print("🟢 LEE METHOD SYSTEM IS RUNNING")
    print("=" * 70)
    print("\nThe system is now active and monitoring for Lee Method patterns.")
    print("The interface should be open in your browser.")
    print("\nPress Ctrl+C to stop the system...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[STOP] Shutting down Lee Method system...")
        print("Thank you for using A.T.L.A.S. Lee Method Scanner!")

def main():
    """Main startup function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start API server
    if not start_api_server():
        print("\n[WARNING] API server failed to start. Interface will use mock data.")
    
    # Open interface
    if not open_interface():
        print("\n[WARNING] Failed to open interface automatically.")
        print("Please open atlas_interface.html manually in your browser.")
    
    # Show system information
    show_system_info()
    
    # Wait for exit
    wait_for_exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[EXIT] Lee Method system stopped by user.")
    except Exception as e:
        print(f"\n[ERROR] System error: {e}")
        sys.exit(1)
