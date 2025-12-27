"""
Test script for reCAPTCHA v2 solver
"""
from recaptchaSolver import solver

# Test URL with reCAPTCHA v2
# You can use Google's demo page or any website with reCAPTCHA v2
test_url = "https://www.google.com/recaptcha/api2/demo"

print("=" * 70)
print("TESTING RECAPTCHA V2 SOLVER")
print("=" * 70)
print(f"URL: {test_url}\n")

try:
    result = solver(
        url=test_url,
        verbose=True,
        headless=False  # Set to True to run without showing browser
    )
    
    print("\n" + "=" * 70)
    print("RESULT:")
    print(f"  Token: {result.get('recaptcha_token', 'N/A')[:50]}...")
    print(f"  Time Taken: {result.get('time_taken', 'N/A')}s")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
