#!/usr/bin/env python3
"""
A.T.L.A.S. Lee Method API
Web API endpoints for Lee Method scanner integration
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import json

from atlas_lee_method_realtime_scanner import get_scanner_instance

# Configure logging with ASCII-safe format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('atlas_lee_method_api.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
CORS(app)  # Enable CORS for web interface

# Global scanner instance
scanner = None
scanner_thread = None

def start_scanner_background():
    """Start the Lee Method scanner in background thread"""
    global scanner
    
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Get scanner instance
        scanner = get_scanner_instance()
        
        # Start scanning
        loop.run_until_complete(scanner.start_scanning())
        
    except Exception as e:
        logger.error(f"Error in scanner background thread: {e}")

@app.route('/api/lee-method/status', methods=['GET'])
def get_scanner_status():
    """Get Lee Method scanner status"""
    try:
        if scanner is None:
            return jsonify({
                'status': 'error',
                'message': 'Scanner not initialized'
            }), 500
        
        status = scanner.get_scanner_status()
        return jsonify({
            'status': 'success',
            'data': status
        })
        
    except Exception as e:
        logger.error(f"Error getting scanner status: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/lee-method/signals', methods=['GET'])
def get_latest_signals():
    """Get latest Lee Method signals"""
    try:
        if scanner is None:
            return jsonify({
                'status': 'error',
                'message': 'Scanner not initialized'
            }), 500
        
        # Get limit parameter
        limit = request.args.get('limit', 10, type=int)
        limit = min(max(limit, 1), 50)  # Clamp between 1 and 50
        
        signals = scanner.get_latest_signals(limit)
        
        return jsonify({
            'status': 'success',
            'data': {
                'signals': signals,
                'count': len(signals),
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting latest signals: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/lee-method/signal/<symbol>', methods=['GET'])
def get_signal_by_symbol(symbol):
    """Get Lee Method signal for specific symbol"""
    try:
        if scanner is None:
            return jsonify({
                'status': 'error',
                'message': 'Scanner not initialized'
            }), 500
        
        signal = scanner.get_signal_by_symbol(symbol)
        
        if signal:
            return jsonify({
                'status': 'success',
                'data': signal
            })
        else:
            return jsonify({
                'status': 'success',
                'data': None,
                'message': f'No Lee Method signal found for {symbol}'
            })
        
    except Exception as e:
        logger.error(f"Error getting signal for {symbol}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/lee-method/scan', methods=['POST'])
def trigger_manual_scan():
    """Trigger a manual Lee Method scan"""
    try:
        if scanner is None:
            return jsonify({
                'status': 'error',
                'message': 'Scanner not initialized'
            }), 500
        
        # Trigger scan in background (non-blocking)
        def run_scan():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(scanner._perform_lee_method_scan())
            except Exception as e:
                logger.error(f"Error in manual scan: {e}")
        
        scan_thread = threading.Thread(target=run_scan)
        scan_thread.daemon = True
        scan_thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'Manual scan triggered'
        })
        
    except Exception as e:
        logger.error(f"Error triggering manual scan: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/lee-method/criteria', methods=['GET'])
def get_lee_method_criteria():
    """Get Lee Method criteria information"""
    try:
        criteria = {
            'name': 'Lee Method',
            'description': 'Advanced momentum pattern detection replacing TTM Squeeze',
            'criteria': [
                {
                    'number': 1,
                    'description': 'Three (or more) histogram bars that decrease, followed by an increase',
                    'detail': 'Pattern must show at least 3 consecutive decreasing momentum bars followed by an uptick'
                },
                {
                    'number': 2,
                    'description': 'Momentum should be greater than the prior momentum bar',
                    'detail': 'The momentum increase must be confirmed by higher momentum than previous bar'
                },
                {
                    'number': 3,
                    'description': 'Identify significant shifts from weekly and daily charts',
                    'detail': 'Multi-timeframe analysis confirming weekly trend with daily trend alignment'
                }
            ],
            'advantages': [
                'More precise entry timing than TTM Squeeze',
                'Better momentum confirmation',
                'Multi-timeframe trend validation',
                'Reduced false signals'
            ]
        }
        
        return jsonify({
            'status': 'success',
            'data': criteria
        })
        
    except Exception as e:
        logger.error(f"Error getting Lee Method criteria: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/lee-method/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'success',
            'message': 'A.T.L.A.S. Lee Method API is running',
            'timestamp': datetime.now().isoformat(),
            'scanner_initialized': scanner is not None,
            'scanner_running': scanner.is_running if scanner else False
        })
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def start_api_server(host='localhost', port=5001, debug=False):
    """Start the Lee Method API server"""
    global scanner_thread
    
    try:
        logger.info(f"[LAUNCH] Starting A.T.L.A.S. Lee Method API server on {host}:{port}")
        
        # Start scanner in background thread
        scanner_thread = threading.Thread(target=start_scanner_background)
        scanner_thread.daemon = True
        scanner_thread.start()
        
        # Give scanner time to initialize
        import time
        time.sleep(2)
        
        # Start Flask app
        app.run(host=host, port=port, debug=debug, threaded=True)
        
    except Exception as e:
        logger.error(f"Error starting API server: {e}")
        raise

if __name__ == "__main__":
    # Start the API server
    start_api_server(debug=True)
