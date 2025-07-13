#!/usr/bin/env python3
import requests
import json

def capture_atlas_response(prompt):
    print(f"\n{'='*80}")
    print(f"[TARGET] PROMPT: {prompt}")
    print('='*80)
    
    try:
        response = requests.post(
            "http://localhost:8080/api/v1/chat",
            json={
                "message": prompt,
                "session_id": "capture_test",
                "context": {"test_mode": True}
            },
            timeout=30
        )
        
        print(f"[DATA] Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "")
            
            print(f"\n[NOTE] A.T.L.A.S. RESPONSE:")
            print("-" * 80)
            print(response_text)
            print("-" * 80)
            
            # Quick analysis
            print(f"\n[UP] ANALYSIS:")
            print(f"   Length: {len(response_text)} chars")
            print(f"   Contains $: {'[OK]' if '$' in response_text else '[ERROR]'}")
            print(f"   Trading terms: {'[OK]' if any(w in response_text.lower() for w in ['buy', 'sell', 'trade', 'entry', 'target']) else '[ERROR]'}")
            print(f"   A.T.L.A.S.: {'[OK]' if 'A.T.L.A.S' in response_text else '[ERROR]'}")
            
            return True
            
        else:
            print(f"[ERROR] ERROR: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"[ERROR] EXCEPTION: {e}")
        return False

# Test 3 key prompts
prompts = [
    "What's Apple trading at right now?",
    "Can you suggest an options trade on NVIDIA that could make me money this week?",
    "Please buy 10 shares of Amazon for me now."
]

print("[LAUNCH] A.T.L.A.S. RESPONSE CAPTURE")
print("[TARGET] Capturing actual Trading God responses")

for i, prompt in enumerate(prompts, 1):
    print(f"\n🔄 Test {i}/{len(prompts)}")
    capture_atlas_response(prompt)

print(f"\n{'='*80}")
print("[OK] Response capture complete!")
print('='*80)
