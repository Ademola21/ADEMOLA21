"""
Slider CAPTCHA Solver with Retry Logic
v2.6 - Wrapper with automatic retry on failure
"""
from sliderSolverFinal import solve_slider_captcha as _solve_single
import time

def solve_slider_captcha_with_retry(url, verbose=True, max_attempts=2):
    """
    Solve slider CAPTCHA with automatic retry logic
    
    Args:
        url: The URL to solve CAPTCHA on
        verbose: Print detailed logs
        max_attempts: Maximum number of attempts (default: 2)
    
    Returns:
        dict with 'success', 'attempts', and other solve details
    """
    print("=" * 70)
    print("SLIDER CAPTCHA SOLVER v2.6 - WITH RETRY LOGIC")
    print(f"Maximum Attempts: {max_attempts}")
    print("=" * 70)
    
    for attempt in range(1, max_attempts + 1):
        if attempt > 1:
            print(f"\n{'='*70}")
            print(f"RETRY - ATTEMPT {attempt}/{max_attempts}")
            print(f"{'='*70}\n")
            time.sleep(2)  # Brief pause before retry
        
        result = _solve_single(url, verbose=verbose)
        
        if result['success']:
            print(f"\n✓ SUCCESS ON ATTEMPT {attempt}!")
            result['attempts'] = attempt
            return result
        else:
            if attempt < max_attempts:
                print(f"\n✗ Attempt {attempt} failed. Retrying...")
            else:
                print(f"\n✗ All {max_attempts} attempts failed.")
                result['attempts'] = attempt
                return result
    
    return {"success": False, "attempts": max_attempts}


if __name__ == "__main__":
    result = solve_slider_captcha_with_retry("http://localhost:3000", verbose=True, max_attempts=2)
    print("\nFINAL RESULT:")
    print(result)
