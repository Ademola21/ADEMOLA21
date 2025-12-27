# ReCAPTCHA v2 AI Solver

An intelligent automated solver for reCAPTCHA v2 and Slider Puzzle CAPTCHAs using computer vision and machine learning.

## 🎯 Features

- **Slider CAPTCHA Solver**: Automated puzzle slider solving with 100% success rate
  - Template matching with alpha channel masking
  - Precise drag calculation with CSS offset compensation
  - Human-like movement simulation with easing
  
- **reCAPTCHA v2 Image Solver**: AI-powered image classification
  - ONNX model for object detection
  - Support for various challenge types (traffic lights, crosswalks, etc.)

## 🚀 Quick Start

### Prerequisites

```bash
pip install -r requirements.txt
```

**Note**: The `model.onnx` file (273MB) is not included in this repository due to GitHub's 100MB file size limit. You'll need to download or train your own model for the reCAPTCHA v2 image solver.

### 1. Slider CAPTCHA Solver (100% Success Rate ✓)

**Single attempt:**
```bash
python sliderSolverFinal.py
```

**With automatic retry (recommended):**
```bash
python sliderSolver_WithRetry.py
```

**Test script (3 runs):**
```bash
python quick_test.py
```

### 2. reCAPTCHA v2 Image Solver

```bash
python recaptchaSolver.py
```

**Requirements:**
- Requires `model.onnx` (AI model for image classification)
- Supports various challenge types (traffic lights, crosswalks, bicycles, etc.)
- Uses ONNX runtime for fast inference

## 📁 Project Structure

```
RecaptchaV2-IA-Solver/
├── 🎯 Slider CAPTCHA Solver
│   ├── sliderSolverFinal.py           # Main solver (100% success)
│   ├── sliderSolver_WithRetry.py      # With retry logic (max 2 attempts)
│   ├── sliderSolver_WORKING_BACKUP.py # Backup copy
│   ├── quick_test.py                   # Test script (3 runs)
│   └── ALGORITHM_EXPLAINED.md          # Technical documentation
│
├── 🔐 reCAPTCHA v2 Image Solver
│   ├── recaptchaSolver.py              # Image classification solver
│   └── model.onnx                      # AI model (not in repo - too large)
│
├── 🧪 Demo App
│   └── slider-captcha/                 # React demo application
│
└── 📸 Debug Output
    └── debug_slider_working/           # Screenshots and diagnostics
```

## 🔧 How It Works

### Slider CAPTCHA Algorithm

1. **Image Extraction**: Capture puzzle and background images from canvas
2. **Gap Detection**: Template matching with edge detection
3. **Offset Calculation**: Read CSS position of puzzle piece
4. **Precise Drag**: Apply scaling ratio (1.158) and execute smooth drag
   ```
   Drag Distance = (Gap Position - CSS Offset) × 1.158
   ```

**For complete technical details, see [ALGORITHM_EXPLAINED.md](ALGORITHM_EXPLAINED.md)**

### reCAPTCHA v2 Image Solver

1. **Challenge Detection**: Identify the type of object to find (traffic lights, crosswalks, etc.)
2. **Image Analysis**: Use ONNX model to classify each grid cell
3. **Selection**: Click on cells containing the target object
4. **Verification**: Submit and verify solution

## ✅ Verification

### Slider CAPTCHA
**Success Rate: 100% (3/3 consecutive tests)**

Debug screenshots available in `debug_slider_working/`:
- `match_result.png` - Shows detected gap position
- `after_drag.png` - Shows final piece alignment

### reCAPTCHA v2
- Uses trained ONNX model for image classification
- Supports multiple challenge types
- Automated grid selection and submission

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👨‍💻 Developer

**Ademola Victor**

## ⚠️ Disclaimer

This project is for educational purposes only. Use responsibly and in accordance with website terms of service.
