# A.T.L.A.S. Lee Method Scanner System

## Overview

The A.T.L.A.S. Lee Method Scanner System replaces the traditional TTM Squeeze patterns with the advanced Lee Method pattern detection algorithm. This system provides real-time scanning and analysis of momentum patterns across multiple timeframes.

## Lee Method Criteria

The Lee Method identifies high-probability momentum shifts using three specific criteria:

### 1. Histogram Pattern Detection
- **Requirement**: Three (or more) histogram bars that decrease, followed by an increase
- **Implementation**: Scans momentum histogram for consecutive decreasing values followed by uptick
- **Note**: The increase does not have to be positive, just higher than the previous bar

### 2. Momentum Confirmation  
- **Requirement**: Momentum should be greater than the prior momentum bar
- **Implementation**: Validates that current momentum exceeds previous momentum value
- **Purpose**: Confirms the strength and validity of the pattern

### 3. Multi-Timeframe Analysis
- **Requirement**: Identify significant shifts from weekly and daily charts
- **Implementation**: Analyzes EMA alignment and trend direction across timeframes
- **Confirmation**: Weekly trend must align with daily trend for high-confidence signals

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    A.T.L.A.S. Lee Method System            │
├─────────────────────────────────────────────────────────────┤
│  Web Interface (atlas_interface.html)                      │
│  ├── Real-time scanner display                             │
│  ├── Signal visualization                                  │
│  └── Manual scan controls                                  │
├─────────────────────────────────────────────────────────────┤
│  API Layer (atlas_lee_method_api.py)                       │
│  ├── RESTful endpoints                                     │
│  ├── Real-time data serving                               │
│  └── Scanner control interface                            │
├─────────────────────────────────────────────────────────────┤
│  Real-time Scanner (atlas_lee_method_realtime_scanner.py)  │
│  ├── Continuous monitoring                                 │
│  ├── Batch processing                                      │
│  └── Signal management                                     │
├─────────────────────────────────────────────────────────────┤
│  Core Engine (lee_method_scanner.py)                       │
│  ├── Pattern detection algorithms                          │
│  ├── Technical indicator calculations                      │
│  └── Signal generation logic                              │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

### Core Components

- **`lee_method_scanner.py`** - Core Lee Method pattern detection engine
- **`atlas_lee_method_realtime_scanner.py`** - Real-time scanning infrastructure  
- **`atlas_lee_method_api.py`** - Web API server for interface integration
- **`atlas_interface.html`** - Updated web interface with Lee Method scanner

### Utilities

- **`start_lee_method_system.py`** - System startup script
- **`test_lee_method_implementation.py`** - Comprehensive test suite
- **`LEE_METHOD_README.md`** - This documentation file

## Quick Start

### 1. Install Dependencies

```bash
pip install flask flask-cors pandas numpy requests
```

### 2. Start the System

```bash
python start_lee_method_system.py
```

This will:
- Start the Lee Method API server on `http://localhost:5001`
- Open the A.T.L.A.S. interface in your browser
- Begin real-time scanning for Lee Method patterns

### 3. Using the Interface

The right panel of the A.T.L.A.S. interface now shows:
- **Lee Method Scanner Status** - Real-time scanner activity
- **Latest Scans** - Most recent pattern detections
- **Scanner Controls** - Manual refresh and pause/resume
- **Lee Method Criteria** - Reference information

## API Endpoints

### Scanner Status
```
GET /api/lee-method/status
```
Returns current scanner status and performance metrics.

### Latest Signals
```
GET /api/lee-method/signals?limit=10
```
Returns the most recent Lee Method signals.

### Signal by Symbol
```
GET /api/lee-method/signal/{symbol}
```
Returns Lee Method signal for a specific symbol.

### Manual Scan Trigger
```
POST /api/lee-method/scan
```
Triggers an immediate scan of all monitored symbols.

### Lee Method Criteria
```
GET /api/lee-method/criteria
```
Returns detailed information about Lee Method criteria.

### Health Check
```
GET /api/lee-method/health
```
Returns API health status and system information.

## Signal Structure

Lee Method signals contain the following information:

```json
{
  "symbol": "AAPL",
  "signal_type": "bullish_momentum",
  "entry_price": 175.50,
  "target_price": 182.00,
  "stop_loss": 171.00,
  "confidence": 0.85,
  "timeframe": "daily",
  "timestamp": "2024-01-15T10:30:00",
  "histogram_sequence": [0.5, 0.3, 0.1, -0.1, 0.2],
  "momentum_bars": [0.1, 0.15, 0.20, 0.18, 0.25],
  "momentum_confirmation": true,
  "weekly_trend": "bullish",
  "daily_trend": "bullish", 
  "trend_alignment": true,
  "risk_reward_ratio": 2.0,
  "position_size_percent": 2.0
}
```

## Monitored Symbols

The system monitors these 24 popular stocks:
- **Tech**: AAPL, MSFT, GOOGL, AMZN, META, NVDA, AMD, INTC
- **Growth**: TSLA, NFLX, CRM, ORCL, ADBE, PYPL
- **Emerging**: UBER, LYFT, SHOP, SQ, ROKU, ZM, DOCU, SNOW, PLTR, COIN

## Configuration

### Scanner Settings
- **Scan Interval**: 30 seconds
- **Signal Expiry**: 1 hour
- **Batch Size**: 5 symbols per batch
- **API Timeout**: 10 seconds

### Risk Management
- **Default Risk**: 2% per trade
- **Risk/Reward Ratio**: 2:1
- **Maximum Position Size**: 10%

## Testing

Run the comprehensive test suite:

```bash
python test_lee_method_implementation.py
```

The test suite validates:
- Core Lee Method pattern detection
- All three Lee Method criteria
- Real-time scanner functionality
- API integration
- Signal generation accuracy

## Advantages Over TTM Squeeze

1. **More Precise Entry Timing** - Lee Method provides clearer entry signals
2. **Better Momentum Confirmation** - Stricter momentum validation reduces false signals
3. **Multi-Timeframe Validation** - Weekly/daily trend alignment improves accuracy
4. **Reduced Noise** - Fewer false breakouts compared to traditional TTM Squeeze
5. **Adaptive Thresholds** - Dynamic pattern recognition vs fixed squeeze conditions

## Troubleshooting

### API Key Issues
- The system uses demo API keys by default
- For live data, obtain a valid Financial Modeling Prep API key
- Set the API key in the scanner initialization

### Scanner Not Running
- Check if port 5001 is available
- Verify all dependencies are installed
- Review logs for error messages

### No Signals Detected
- This is normal - Lee Method has strict criteria
- Patterns may not be present in current market conditions
- Try manual scan refresh

### Interface Not Loading
- Ensure API server is running on localhost:5001
- Check browser console for JavaScript errors
- Verify atlas_interface.html is accessible

## Support

For issues or questions about the Lee Method implementation:
1. Check the test results for system validation
2. Review API endpoint responses for data availability
3. Examine log files for detailed error information
4. Verify all three Lee Method criteria are being properly evaluated

---

**A.T.L.A.S. Lee Method Scanner System** - Advanced momentum pattern detection for professional trading analysis.
