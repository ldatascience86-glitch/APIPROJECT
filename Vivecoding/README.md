# Advanced Scientific Calculator

A comprehensive, modern scientific calculator built with HTML, CSS, and JavaScript. This calculator provides all the essential scientific functions needed for advanced mathematical calculations, engineering, physics, and academic work.

## 🌟 Features

### Basic Operations
- **Arithmetic**: Addition (+), Subtraction (-), Multiplication (×), Division (÷)
- **Decimal Support**: Full decimal number support
- **Percentage**: Calculate percentages
- **Backspace**: Remove last entered digit
- **Clear Functions**: Clear all (C) and clear entry (CE)

### Scientific Functions

#### Trigonometric Functions
- **Basic**: sin, cos, tan
- **Inverse**: sin⁻¹, cos⁻¹, tan⁻¹
- **Hyperbolic**: sinh, cosh, tanh
- **Angle Modes**: Degrees (DEG), Radians (RAD), Gradians (GRAD)

#### Logarithmic & Exponential
- **Natural Logarithm**: ln(x)
- **Base-10 Logarithm**: log(x)
- **Exponential**: exp(x)
- **Power Functions**: x², x³, xʸ
- **Root Functions**: √x (square root), ∛x (cube root)
- **10 to Power**: 10ˣ

#### Mathematical Constants
- **Pi (π)**: Mathematical constant π
- **Euler's Number (e)**: Natural logarithm base

#### Advanced Mathematical Functions
- **Factorial**: n!
- **Absolute Value**: |x|
- **Floor Function**: ⌊x⌋
- **Ceiling Function**: ⌈x⌉
- **Round Function**: round(x)
- **Sign Function**: ±
- **Modulo**: mod (remainder)
- **Random Number**: RND
- **Inverse**: 1/x

### Memory Functions
- **MC**: Memory Clear
- **MR**: Memory Recall
- **M+**: Memory Add
- **M-**: Memory Subtract

### Additional Features
- **History Display**: Shows last 3 calculations
- **Keyboard Support**: Full keyboard input support
- **Responsive Design**: Works on all device sizes
- **Modern UI**: Beautiful, intuitive interface
- **Error Handling**: Graceful error handling and display

## 🚀 Getting Started

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- No additional software installation required

### Installation
1. Download all files to a folder
2. Open `index.html` in your web browser
3. Start calculating!

### File Structure
```
scientific-calculator/
├── index.html          # Main HTML file
├── styles.css          # CSS styling
├── calculator.js       # JavaScript functionality
└── README.md          # This documentation
```

## 📱 Usage

### Basic Calculations
1. **Simple Arithmetic**: Enter numbers and use +, -, ×, ÷ operators
2. **Scientific Functions**: Click scientific function buttons after entering a number
3. **Memory Operations**: Use memory buttons to store and recall values

### Scientific Calculations Examples

#### Trigonometric Calculations
```
sin(30°) = 0.5
cos(60°) = 0.5
tan(45°) = 1
```

#### Logarithmic Calculations
```
log(100) = 2
ln(e) = 1
exp(1) = 2.718281828
```

#### Power and Root Calculations
```
5² = 25
√16 = 4
∛27 = 3
2³ = 8
```

### Keyboard Shortcuts
- **Numbers**: 0-9 keys
- **Operators**: +, -, *, / keys
- **Decimal**: . key
- **Calculate**: Enter or = key
- **Clear All**: Escape key
- **Backspace**: Backspace key
- **Percentage**: % key
- **Power**: ^ key

### Angle Mode Switching
- **DEG**: Degrees (0-360°)
- **RAD**: Radians (0-2π)
- **GRAD**: Gradians (0-400 grad)

## 🔧 Advanced Usage

### Programmatic Access
The calculator exposes functions for external use:

```javascript
// Access calculator functions
Calculator.calculateFunction('sin', 30);
Calculator.setAngleMode('rad');
Calculator.getMemory();
Calculator.setMemory(100);
```

### Statistical Functions
```javascript
// Calculate statistics for an array of numbers
const numbers = [1, 2, 3, 4, 5];
const stats = Calculator.calculateStatistics(numbers);
// Returns: {count, sum, mean, variance, stdDev, min, max}
```

### Advanced Mathematical Functions
```javascript
// GCD and LCM
Calculator.calculateAdvancedFunction('gcd', 48, 18); // Returns 6
Calculator.calculateAdvancedFunction('lcm', 12, 18); // Returns 36

// Prime number check
Calculator.calculateAdvancedFunction('prime', 17); // Returns true

// Fibonacci sequence
Calculator.calculateAdvancedFunction('fibonacci', 10); // Returns 55
```

## 🎨 Customization

### CSS Variables
The calculator uses CSS custom properties for easy theming:

```css
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --danger-color: #dc3545;
    --warning-color: #ffc107;
    --info-color: #17a2b8;
}
```

### Responsive Breakpoints
- **Desktop**: 1024px and above
- **Tablet**: 768px to 1023px
- **Mobile**: 480px to 767px
- **Small Mobile**: Below 480px

## 🐛 Troubleshooting

### Common Issues

1. **Calculator not responding**
   - Refresh the page
   - Check browser console for errors
   - Ensure JavaScript is enabled

2. **Scientific functions not working**
   - Check if angle mode is set correctly
   - Ensure input is a valid number
   - Check for domain restrictions (some functions)

3. **Display issues**
   - Clear calculator (C button)
   - Check browser zoom level
   - Ensure responsive design is working

### Browser Compatibility
- **Chrome**: 60+
- **Firefox**: 55+
- **Safari**: 12+
- **Edge**: 79+

## 📚 Mathematical Reference

### Trigonometric Identities
- sin²(x) + cos²(x) = 1
- tan(x) = sin(x)/cos(x)
- sin(-x) = -sin(x)
- cos(-x) = cos(x)

### Logarithmic Properties
- log(ab) = log(a) + log(b)
- log(a/b) = log(a) - log(b)
- log(aⁿ) = n·log(a)

### Power Rules
- xᵃ × xᵇ = xᵃ⁺ᵇ
- (xᵃ)ᵇ = xᵃᵇ
- x⁻ᵃ = 1/xᵃ

## 🤝 Contributing

Feel free to contribute to this project by:
1. Reporting bugs
2. Suggesting new features
3. Improving the UI/UX
4. Adding new mathematical functions
5. Optimizing performance

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with modern web technologies
- Inspired by professional scientific calculators
- Designed for educational and professional use
- Responsive design principles
- Accessibility considerations

---

**Happy Calculating! 🧮✨**
