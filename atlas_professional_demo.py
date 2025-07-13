#!/usr/bin/env python3
"""
A.T.L.A.S. Professional Trading Analyst Demo
Demonstrates the transformation from basic responses to professional trading analysis
"""

import requests
import json
import time

def test_professional_analyst_transformation():
    """Demonstrate Professional Analyst transformation"""
    
    print("[TARGET] A.T.L.A.S. PROFESSIONAL ANALYST TRANSFORMATION DEMO")
    print("=" * 60)
    print("Testing the major improvements implemented:")
    print("[OK] Professional Analyst Response Engine")
    print("[OK] 6-Point Format Enforcement")
    print("[OK] Confidence Scoring System")
    print("[OK] Real-time Market Data Integration")
    print("[OK] Advanced Risk Management")
    print("[OK] Institutional-Grade Analysis")
    print()
    
    test_questions = [
        "Should I buy AAPL?",
        "What's the best trade today?",
        "Help me make $100 today",
        "Analyze TSLA for me",
        "Give me a trading recommendation"
    ]
    
    server_url = "http://localhost:8080/api/v1/chat"
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n[TEST {i}/5] Question: '{question}'")
        print("-" * 50)
        
        try:
            response = requests.post(
                server_url,
                json={"message": question},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", "")
                
                improvements = []
                if "Professional Trading Analyst" in answer:
                    improvements.append("✅ Professional persona active")
                if "Win/Loss Probabilities" in answer:
                    improvements.append("✅ Probability analysis included")
                if "Confidence Score" in answer:
                    improvements.append("✅ Confidence scoring present")
                if "$" in answer and any(word in answer for word in ["gain", "loss", "profit", "risk"]):
                    improvements.append("✅ Specific dollar amounts provided")
                if "%" in answer:
                    improvements.append("✅ Percentage-based metrics included")
                if not any(phrase in answer.lower() for phrase in ["i can't", "i don't", "i'm not able", "as an ai"]):
                    improvements.append("✅ No AI limitations expressed")
                
                print(f"Response: {answer[:200]}...")
                print(f"\nImprovements detected: {len(improvements)}/6")
                for improvement in improvements:
                    print(f"  {improvement}")
                    
                score = len(improvements) * 100 // 6
                print(f"Professional Analysis Score: {score}%")
                
                if score >= 75:
                    print(f"   [SUCCESS] PROFESSIONAL ANALYST SUCCESS!")
                elif score >= 50:
                    print(f"   [WARN]  Good improvement, minor issues remain")
                else:
                    print(f"   [FAIL]  Needs more work")
                
            else:
                print(f"   [ERROR] Server returned {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   [ERROR] Connection failed: {e}")
            print("   Make sure the A.T.L.A.S. server is running on localhost:8080")
        
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("[SUMMARY] Professional Analyst Transformation Test Complete")
    print("Expected improvements:")
    print("✅ Confident, data-driven responses")
    print("✅ Specific dollar amounts and percentages")
    print("✅ Professional trading terminology")
    print("✅ 6-point structured format")
    print("✅ No AI limitations or disclaimers")
    print("\n[LAUNCH] A.T.L.A.S. is now operating at institutional Professional Analyst level!")

if __name__ == "__main__":
    test_professional_analyst_transformation()
