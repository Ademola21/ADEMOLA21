from sliderSolverFinal import solve_slider_captcha
import time

results = []
for i in range(3):
    print(f"\n{'='*50}\nTEST {i+1}/3\n{'='*50}")
    result = solve_slider_captcha("http://localhost:3000", verbose=True)
    results.append(result['success'])
    time.sleep(1)

print(f"\n\n{'='*50}")
print(f"SUCCESS RATE: {sum(results)}/3")
print(f"{'='*50}")
