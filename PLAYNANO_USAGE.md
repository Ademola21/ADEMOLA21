# PlayNano Automation - Usage Guide

## Quick Start

```bash
python playnano_automation.py
```

## Configuration

Edit the `CONFIG` dictionary in `playnano_automation.py`:

```python
CONFIG = {
    "url": "https://playnano.online/watch-and-learn/nano",
    "test_wallet": "YOUR_NANO_WALLET_ADDRESS_HERE",  # ← Change this!
    "max_countdown_wait": 180,  # Max seconds to wait per countdown
    "block_videos": True,        # Save bandwidth by blocking videos
    "headless": False,           # Set True to hide browser
    "verbose": True              # Print detailed logs
}
```

## What It Does

1. **Navigates to PlayNano** and clicks "Start Learning"
2. **Blocks videos** (saves bandwidth) 🎥❌
3. **Waits through 5 countdown pages** (1/5 → 5/5)
4. **Detects CAPTCHA type** automatically:
   - Slider CAPTCHA
   - reCAPTCHA v2
5. **Solves the CAPTCHA** using appropriate solver
6. **Submits wallet address** ONLY if CAPTCHA succeeds ✓

## Features

✅ **Video Blocking** - Automatically blocks videos to save bandwidth  
✅ **Smart Detection** - Identifies which CAPTCHA type is present  
✅ **Dual Solvers** - Uses both Slider and reCAPTCHA v2 solvers  
✅ **Countdown Handling** - Waits for timers automatically (up to 3 min each)  
✅ **Conditional Submission** - Only submits wallet if CAPTCHA solved  
✅ **Error Handling** - Graceful handling of timeouts and failures  

## Output Example

```
======================================================================
PLAYNANO AUTOMATED CAPTCHA SOLVER
======================================================================
URL: https://playnano.online/watch-and-learn/nano
Wallet: nano_3test123456789...
Video Blocking: Enabled
======================================================================

[1] Loading PlayNano page...
[2] Clicking 'Start Learning' button...
[3] Navigating through video pages...

[Page 1/5] Waiting for countdown...
  ✓ Videos blocked
  ✓ Countdown finished, clicking button...

[Page 2/5] Waiting for countdown...
  ✓ Videos blocked
  ✓ Countdown finished, clicking button...

... (pages 3-5) ...

✓ Completed all 5 video pages!

[CAPTCHA Detection] Checking type...
  ✓ Detected: Slider CAPTCHA

[CAPTCHA Solver] Solving slider...
[Slider] Clicking checkbox...
[Slider] Extracting images...
[Slider] Gap detected at: 140px
[Slider] Dragging 162px...
[Slider] ✓ SUCCESS!

✓ CAPTCHA SOLVED SUCCESSFULLY!

[Wallet Submission] Entering address...
  ✓ Entered wallet: nano_3test123456789...
  ✓ Submitted!

======================================================================
FINAL RESULTS
======================================================================
CAPTCHA Type: slider
CAPTCHA Status: ✓ SOLVED
Total Time: 245.32s
======================================================================
```

## Troubleshooting

### Videos Still Loading?
- Check browser console for errors
- Videos are hidden but may still load in background
- Consider using ad-blocker extension for extra protection

### Countdown Not Detected?
- Increase `max_countdown_wait` in CONFIG
- Check if button selector changed on website

### CAPTCHA Not Detected?
- Website may have changed structure
- Check browser window to see actual page state
- Set `headless: False` to debug visually

### Wallet Not Submitted?
- Verify CAPTCHA actually solved (check output)
- Wallet field selector may have changed
- Check for any error messages in output

## Requirements

- Python 3.x
- Selenium
- Chrome/ChromeDriver
- OpenCV (for Slider CAPTCHA)
- ONNX Runtime (for reCAPTCHA v2)
- model.onnx file (for reCAPTCHA v2)

## Notes

⚠️ **Test Wallet**: Always use a test wallet address, especially when testing  
⚠️ **Rate Limiting**: Website may have rate limits, use responsibly  
⚠️ **Bandwidth**: Video blocking significantly reduces data usage  
⚠️ **Timers**: Countdown timers are server-controlled and cannot be skipped  

---

**Created: 2025-12-26**  
**Developer: Ademola Victor**
