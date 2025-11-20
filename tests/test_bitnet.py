import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.bitnet_service import analyze_text
import time

print("=== Testing BitNet Only ===\n")

print("Testing BitNet...")
start = time.time()
result = analyze_text("Explain why fruits are healthy?")
elapsed = time.time() - start

print(f"\nTime taken: {elapsed:.2f} seconds")
print(f"Model used: {result['model']}")
print(f"\nInput: {result['input']}")
print(f"\nOutput:\n{result['output']}")

print("\n=== Test Complete ===")
