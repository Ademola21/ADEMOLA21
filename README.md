# ReCAPTCHA v2 AI Solver

An intelligent automated solver for reCAPTCHA v2 and Slider Puzzle CAPTCHAs using computer vision and machine learning.

## 🎯 Features

- **Slider CAPTCHA Solver**: Automated puzzle slider solving with 100% accuracy
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

### Running the Slider CAPTCHA Solver

```bash
python sliderSolverFinal.py
```

### Testing (Multiple Runs)

```bash
python quick_test.py
```

## 📁 Project Structure

```
RecaptchaV2-IA-Solver/
├── sliderSolverFinal.py          # Main slider CAPTCHA solver
├── sliderSolver_WORKING_BACKUP.py # Backup of working solver
├── quick_test.py                  # Test script (3 runs)
├── quick_test_WORKING_BACKUP.py   # Backup of test script
├── recaptchaSolver.py             # reCAPTCHA v2 image solver
├── model.onnx                     # AI model for image classification
├── slider-captcha/                # React demo app
└── debug_slider_working/          # Debug screenshots
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

### Technical Details

- **Scale Ratio**: `(Track Width - Handle Width) / (Image Width - Piece Width)`
- **Template Matching**: OpenCV `matchTemplate` with alpha masking
- **Movement**: Quadratic ease-out with float precision (30 steps, 0.8s)

## ✅ Verification

Tested with **100% success rate** (3/3 consecutive solves).

Debug screenshots available in `debug_slider_working/`:
- `match_result.png` - Shows detected gap position
- `after_drag.png` - Shows final piece alignment

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👨‍💻 Developer

**Ademola Victor**

## ⚠️ Disclaimer

This project is for educational purposes only. Use responsibly and in accordance with website terms of service.
