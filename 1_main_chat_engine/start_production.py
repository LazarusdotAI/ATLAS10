#!/usr/bin/env python3
"""
Start A.T.L.A.S in PRODUCTION MODE with real API keys
"""

import os
import sys
import subprocess

def setup_production_environment():
    """Set up production environment with API keys"""
    print("[LAUNCH] Setting up A.T.L.A.S PRODUCTION MODE")
    print("=" * 50)
    
    # Set API keys from memories
    api_keys = {
        "ALPACA_API_KEY": "PKI0KNC8HXZURYRA4OMC",
        "ALPACA_SECRET_KEY": "your_alpaca_secret",  # You'll need to provide this
        "FMP_API_KEY": "K63wnAbUDHNPICjzeq3JcEG1vi8Q2oz7",
        "OPENAI_API_KEY": "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",
        "PREDICTO_API_KEY": "VZ19mf7DvVovUKW0E7PTYmzrJkQjkC5N5fMcWwOsglWPFzhSQPU8m77cb3d3k760"
    }
    
    # Remove validation mode
    if "VALIDATION_MODE" in os.environ:
        del os.environ["VALIDATION_MODE"]
    
    # Set production API keys
    for key, value in api_keys.items():
        os.environ[key] = value
        print(f"[OK] {key}: {'*' * (len(value) - 8) + value[-8:]}")
    
    print("\n🔥 PRODUCTION MODE ACTIVATED!")
    print("[TARGET] Real trading capabilities enabled")
    print("[DATA] Live market data active")
    print("[BRAIN] Full AI analysis available")
    print("[UP] Predicto AI predictions enabled")
    
    return True

def start_production_server():
    """Start the production server"""
    print("\n[LAUNCH] Starting A.T.L.A.S Production Server...")
    print("[WEB] Server will be available at: http://localhost:8080")
    print("[TRADE] Live trading mode: ACTIVE")
    print("[WARN]  WARNING: This will use REAL API keys and can execute REAL trades!")
    
    # Start the server
    try:
        subprocess.run([sys.executable, "atlas_server_fixed.py"], check=True)
    except KeyboardInterrupt:
        print("\n⏹️ Server stopped by user")
    except Exception as e:
        print(f"[ERROR] Server error: {e}")

if __name__ == "__main__":
    print("🔥 A.T.L.A.S PRODUCTION MODE STARTUP")
    print("=" * 50)
    print("[WARN]  WARNING: This will enable REAL trading with LIVE money!")
    print("[DATA] Live market data and AI analysis will be active")
    print()
    
    response = input("Continue with PRODUCTION mode? (yes/no): ").lower().strip()
    
    if response in ['yes', 'y']:
        if setup_production_environment():
            start_production_server()
    else:
        print("[ERROR] Production mode cancelled")
        print("[IDEA] To run in test mode: python atlas_server_minimal.py")
