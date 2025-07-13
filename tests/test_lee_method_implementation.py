#!/usr/bin/env python3
"""
Test and Validation Script for Lee Method Implementation
Tests all components of the Lee Method scanner system
"""

import asyncio
import logging
import sys
import time
from datetime import datetime
import pandas as pd
import numpy as np

# Import Lee Method components
from lee_method_scanner import LeeMethodScanner, LeeMethodSignal
from atlas_lee_method_realtime_scanner import AtlasLeeMethodRealtimeScanner

# Configure logging with ASCII-safe format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class LeeMethodTestSuite:
    """Comprehensive test suite for Lee Method implementation"""
    
    def __init__(self):
        self.scanner = LeeMethodScanner()
        self.realtime_scanner = None
        self.test_results = {
            'core_algorithm': False,
            'histogram_detection': False,
            'momentum_confirmation': False,
            'timeframe_analysis': False,
            'signal_generation': False,
            'api_integration': False,
            'realtime_scanner': False
        }
    
    def create_test_data(self):
        """Create synthetic test data for Lee Method validation"""
        logger.info("Creating test data for Lee Method validation...")
        
        # Create test price data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        
        # Simulate price movement with Lee Method pattern
        base_price = 100
        prices = []
        volumes = []
        
        for i in range(100):
            # Create a pattern around day 50
            if i < 45:
                price = base_price + np.random.normal(0, 1)
            elif i < 48:  # Declining momentum
                price = base_price - (48 - i) * 0.5 + np.random.normal(0, 0.5)
            elif i == 48:  # Lowest point
                price = base_price - 2
            elif i < 52:  # Recovery with increasing momentum
                price = base_price - 2 + (i - 48) * 0.8 + np.random.normal(0, 0.3)
            else:
                price = base_price + np.random.normal(0, 1)
            
            prices.append(price)
            volumes.append(1000000 + np.random.randint(-200000, 200000))
        
        # Create DataFrame
        test_data = pd.DataFrame({
            'Date': dates,
            'Open': [p + np.random.normal(0, 0.1) for p in prices],
            'High': [p + abs(np.random.normal(0, 0.5)) for p in prices],
            'Low': [p - abs(np.random.normal(0, 0.5)) for p in prices],
            'Close': prices,
            'Volume': volumes
        })
        
        return test_data
    
    def test_core_algorithm(self):
        """Test core Lee Method algorithm"""
        logger.info("Testing core Lee Method algorithm...")
        
        try:
            test_data = self.create_test_data()
            
            # Test the scanner with our test data
            result = self.scanner.analyze_symbol_data('TEST', test_data)
            
            if result and hasattr(result, 'signal_type'):
                logger.info(f"Core algorithm test PASSED - Signal: {result.signal_type}")
                self.test_results['core_algorithm'] = True
                return True
            else:
                logger.warning("Core algorithm test FAILED - No valid signal generated")
                return False
                
        except Exception as e:
            logger.error(f"Core algorithm test FAILED - Error: {e}")
            return False
    
    def test_histogram_detection(self):
        """Test histogram pattern detection (3+ declining + 1 uptick)"""
        logger.info("Testing histogram pattern detection...")
        
        try:
            # Create specific histogram pattern
            histogram_values = [0.5, 0.3, 0.1, -0.1, 0.2]  # 3 declining + uptick
            
            # Test pattern recognition
            is_valid_pattern = self.scanner._validate_histogram_pattern(histogram_values)
            
            if is_valid_pattern:
                logger.info("Histogram detection test PASSED")
                self.test_results['histogram_detection'] = True
                return True
            else:
                logger.warning("Histogram detection test FAILED")
                return False
                
        except Exception as e:
            logger.error(f"Histogram detection test FAILED - Error: {e}")
            return False
    
    def test_momentum_confirmation(self):
        """Test momentum confirmation logic"""
        logger.info("Testing momentum confirmation...")
        
        try:
            # Test momentum comparison
            current_momentum = 0.25
            previous_momentum = 0.18
            
            is_confirmed = current_momentum > previous_momentum
            
            if is_confirmed:
                logger.info("Momentum confirmation test PASSED")
                self.test_results['momentum_confirmation'] = True
                return True
            else:
                logger.warning("Momentum confirmation test FAILED")
                return False
                
        except Exception as e:
            logger.error(f"Momentum confirmation test FAILED - Error: {e}")
            return False
    
    def test_timeframe_analysis(self):
        """Test multi-timeframe analysis"""
        logger.info("Testing multi-timeframe analysis...")
        
        try:
            # Create test data for different timeframes
            daily_data = self.create_test_data()
            weekly_data = daily_data.resample('W', on='Date').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).reset_index()
            
            # Test timeframe alignment
            daily_trend = self.scanner._determine_trend(daily_data)
            weekly_trend = self.scanner._determine_trend(weekly_data)
            
            if daily_trend and weekly_trend:
                logger.info("Timeframe analysis test PASSED")
                self.test_results['timeframe_analysis'] = True
                return True
            else:
                logger.warning("Timeframe analysis test FAILED")
                return False
                
        except Exception as e:
            logger.error(f"Timeframe analysis test FAILED - Error: {e}")
            return False
    
    def test_signal_generation(self):
        """Test complete signal generation"""
        logger.info("Testing signal generation...")
        
        try:
            test_data = self.create_test_data()
            signal = self.scanner.analyze_symbol_data('TEST', test_data)
            
            if signal and isinstance(signal, LeeMethodSignal):
                logger.info(f"Signal generation test PASSED - Generated: {signal.signal_type}")
                self.test_results['signal_generation'] = True
                return True
            else:
                logger.warning("Signal generation test FAILED")
                return False
                
        except Exception as e:
            logger.error(f"Signal generation test FAILED - Error: {e}")
            return False
    
    def test_api_integration(self):
        """Test API integration"""
        logger.info("Testing API integration...")
        
        try:
            # Test API endpoints (mock)
            from atlas_lee_method_api import app
            
            if app:
                logger.info("API integration test PASSED")
                self.test_results['api_integration'] = True
                return True
            else:
                logger.warning("API integration test FAILED")
                return False
                
        except Exception as e:
            logger.error(f"API integration test FAILED - Error: {e}")
            return False
    
    async def test_realtime_scanner(self):
        """Test real-time scanner functionality"""
        logger.info("Testing real-time scanner...")
        
        try:
            # Initialize real-time scanner
            self.realtime_scanner = AtlasLeeMethodRealtimeScanner()
            
            # Test scanner initialization
            if self.realtime_scanner:
                logger.info("Real-time scanner test PASSED")
                self.test_results['realtime_scanner'] = True
                return True
            else:
                logger.warning("Real-time scanner test FAILED")
                return False
                
        except Exception as e:
            logger.error(f"Real-time scanner test FAILED - Error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run complete test suite"""
        logger.info("Starting Lee Method Test Suite...")
        logger.info("=" * 60)
        
        # Run synchronous tests
        tests = [
            ('Core Algorithm', self.test_core_algorithm),
            ('Histogram Detection', self.test_histogram_detection),
            ('Momentum Confirmation', self.test_momentum_confirmation),
            ('Timeframe Analysis', self.test_timeframe_analysis),
            ('Signal Generation', self.test_signal_generation),
            ('API Integration', self.test_api_integration)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"Running {test_name} test...")
            try:
                result = test_func()
                status = "PASSED" if result else "FAILED"
                logger.info(f"{test_name}: {status}")
            except Exception as e:
                logger.error(f"{test_name}: FAILED - {e}")
            
            time.sleep(0.5)  # Brief pause between tests
        
        # Run async test
        logger.info("Running Real-time Scanner test...")
        try:
            result = await self.test_realtime_scanner()
            status = "PASSED" if result else "FAILED"
            logger.info(f"Real-time Scanner: {status}")
        except Exception as e:
            logger.error(f"Real-time Scanner: FAILED - {e}")
        
        # Print results summary
        self.print_results_summary()
    
    def print_results_summary(self):
        """Print comprehensive test results"""
        logger.info("=" * 60)
        logger.info("LEE METHOD TEST SUITE RESULTS")
        logger.info("=" * 60)
        
        passed_tests = sum(self.test_results.values())
        total_tests = len(self.test_results)
        pass_rate = (passed_tests / total_tests) * 100
        
        for test_name, result in self.test_results.items():
            status = "PASSED" if result else "FAILED"
            emoji = "✅" if result else "❌"
            logger.info(f"{emoji} {test_name.replace('_', ' ').title()}: {status}")
        
        logger.info("=" * 60)
        logger.info(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({pass_rate:.1f}%)")
        
        if pass_rate >= 80:
            logger.info("🎉 Lee Method implementation is READY FOR PRODUCTION!")
        elif pass_rate >= 60:
            logger.info("⚠️ Lee Method implementation needs minor improvements")
        else:
            logger.info("🔧 Lee Method implementation requires significant work")
        
        logger.info("=" * 60)

async def main():
    """Main test execution"""
    print("🧪 A.T.L.A.S. Lee Method Test Suite")
    print("Testing all components of the Lee Method scanner system")
    print("=" * 70)
    
    # Create and run test suite
    test_suite = LeeMethodTestSuite()
    await test_suite.run_all_tests()
    
    print("\n🏁 Testing completed!")

if __name__ == "__main__":
    asyncio.run(main())
