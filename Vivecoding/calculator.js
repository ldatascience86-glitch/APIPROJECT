// Calculator state variables
let currentInput = '0';
let previousInput = '';
let operation = null;
let waitingForOperand = false;
let memory = 0;
let angleMode = 'deg'; // deg, rad, grad
let history = [];

// DOM elements
const mainDisplay = document.getElementById('mainDisplay');
const historyDisplay = document.getElementById('historyDisplay');

// Initialize calculator
document.addEventListener('DOMContentLoaded', function() {
    // Set up angle mode buttons
    setupAngleModeButtons();
    
    // Add keyboard support
    setupKeyboardSupport();
    
    // Initialize display
    updateDisplay();
});

// Angle mode setup
function setupAngleModeButtons() {
    const modeButtons = document.querySelectorAll('.mode-btn');
    modeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            modeButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            angleMode = this.dataset.mode;
        });
    });
}

// Keyboard support
function setupKeyboardSupport() {
    document.addEventListener('keydown', function(e) {
        const key = e.key;
        
        if (key >= '0' && key <= '9') {
            appendNumber(key);
        } else if (key === '.') {
            appendDecimal();
        } else if (key === '+' || key === '-') {
            setOperation(key === '+' ? '+' : '-');
        } else if (key === '*') {
            setOperation('*');
        } else if (key === '/') {
            setOperation('/');
        } else if (key === 'Enter' || key === '=') {
            calculate();
        } else if (key === 'Escape') {
            clearAll();
        } else if (key === 'Backspace') {
            backspace();
        } else if (key === '%') {
            calculateFunction('percent');
        } else if (key === '^') {
            calculateFunction('pow');
        }
    });
}

// Number input functions
function appendNumber(number) {
    if (waitingForOperand) {
        currentInput = number;
        waitingForOperand = false;
    } else {
        currentInput = currentInput === '0' ? number : currentInput + number;
    }
    updateDisplay();
}

function appendDecimal() {
    if (waitingForOperand) {
        currentInput = '0.';
        waitingForOperand = false;
    } else if (currentInput.indexOf('.') === -1) {
        currentInput += '.';
    }
    updateDisplay();
}

// Basic operations
function setOperation(nextOperation) {
    const inputValue = parseFloat(currentInput);
    
    if (previousInput === '' && !isNaN(inputValue)) {
        previousInput = inputValue;
    } else if (operation) {
        const result = performCalculation(previousInput, inputValue, operation);
        currentInput = String(result);
        previousInput = result;
    }
    
    waitingForOperand = true;
    operation = nextOperation;
    updateDisplay();
}

function performCalculation(firstValue, secondValue, operation) {
    switch (operation) {
        case '+': return firstValue + secondValue;
        case '-': return firstValue - secondValue;
        case '*': return firstValue * secondValue;
        case '/': return secondValue !== 0 ? firstValue / secondValue : 'Error';
        default: return secondValue;
    }
}

function calculate() {
    if (!operation || waitingForOperand) return;
    
    const inputValue = parseFloat(currentInput);
    const result = performCalculation(previousInput, inputValue, operation);
    
    if (result === 'Error') {
        currentInput = 'Error';
        addToHistory(`${previousInput} ${operation} ${inputValue} = Error`);
    } else {
        addToHistory(`${previousInput} ${operation} ${inputValue} = ${result}`);
        currentInput = String(result);
    }
    
    operation = null;
    previousInput = '';
    waitingForOperand = true;
    updateDisplay();
}

// Scientific functions
function calculateFunction(func) {
    const inputValue = parseFloat(currentInput);
    let result;
    
    try {
        switch (func) {
            // Trigonometric functions
            case 'sin':
                result = Math.sin(convertAngle(inputValue));
                break;
            case 'cos':
                result = Math.cos(convertAngle(inputValue));
                break;
            case 'tan':
                result = Math.tan(convertAngle(inputValue));
                break;
            case 'asin':
                result = convertAngle(Math.asin(inputValue), true);
                break;
            case 'acos':
                result = convertAngle(Math.acos(inputValue), true);
                break;
            case 'atan':
                result = convertAngle(Math.atan(inputValue), true);
                break;
                
            // Hyperbolic functions
            case 'sinh':
                result = Math.sinh(inputValue);
                break;
            case 'cosh':
                result = Math.cosh(inputValue);
                break;
            case 'tanh':
                result = Math.tanh(inputValue);
                break;
                
            // Logarithmic functions
            case 'log':
                result = Math.log10(inputValue);
                break;
            case 'ln':
                result = Math.log(inputValue);
                break;
                
            // Power and root functions
            case 'sqrt':
                result = Math.sqrt(inputValue);
                break;
            case 'cbrt':
                result = Math.cbrt(inputValue);
                break;
            case 'x2':
                result = Math.pow(inputValue, 2);
                break;
            case 'cube':
                result = Math.pow(inputValue, 3);
                break;
            case 'pow':
                if (previousInput !== '') {
                    result = Math.pow(previousInput, inputValue);
                    previousInput = '';
                } else {
                    result = 'Enter base first';
                }
                break;
                
            // Exponential functions
            case 'exp':
                result = Math.exp(inputValue);
                break;
            case 'tenPower':
                result = Math.pow(10, inputValue);
                break;
                
            // Mathematical constants
            case 'pi':
                result = Math.PI;
                break;
            case 'e':
                result = Math.E;
                break;
                
            // Other mathematical functions
            case 'factorial':
                result = factorial(inputValue);
                break;
            case 'abs':
                result = Math.abs(inputValue);
                break;
            case 'floor':
                result = Math.floor(inputValue);
                break;
            case 'ceil':
                result = Math.ceil(inputValue);
                break;
            case 'round':
                result = Math.round(inputValue);
                break;
            case 'sign':
                result = Math.sign(inputValue);
                break;
            case 'inverse':
                result = 1 / inputValue;
                break;
            case 'reciprocal':
                result = 1 / inputValue;
                break;
            case 'percent':
                result = inputValue / 100;
                break;
            case 'mod':
                if (previousInput !== '') {
                    result = previousInput % inputValue;
                    previousInput = '';
                } else {
                    result = 'Enter dividend first';
                }
                break;
            case 'rand':
                result = Math.random();
                break;
                
            default:
                result = 'Function not implemented';
        }
        
        if (typeof result === 'number' && !isNaN(result)) {
            if (result === Infinity || result === -Infinity) {
                result = 'Infinity';
            } else if (Math.abs(result) < 1e-10) {
                result = 0;
            } else {
                result = parseFloat(result.toFixed(10));
            }
            addToHistory(`${func}(${inputValue}) = ${result}`);
        }
        
        currentInput = String(result);
        updateDisplay();
        
    } catch (error) {
        currentInput = 'Error';
        addToHistory(`${func}(${inputValue}) = Error`);
        updateDisplay();
    }
}

// Angle conversion functions
function convertAngle(angle, isInverse = false) {
    if (angleMode === 'deg') {
        return isInverse ? (angle * 180) / Math.PI : (angle * Math.PI) / 180;
    } else if (angleMode === 'grad') {
        return isInverse ? (angle * 200) / Math.PI : (angle * Math.PI) / 200;
    }
    return angle; // radians
}

// Factorial function
function factorial(n) {
    if (n < 0 || n !== Math.floor(n)) {
        throw new Error('Invalid input for factorial');
    }
    if (n === 0 || n === 1) return 1;
    if (n > 170) return Infinity; // JavaScript limit
    let result = 1;
    for (let i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

// Memory functions
function memoryClear() {
    memory = 0;
    addToHistory('Memory cleared');
}

function memoryRecall() {
    currentInput = String(memory);
    waitingForOperand = false;
    updateDisplay();
}

function memoryAdd() {
    memory += parseFloat(currentInput) || 0;
    addToHistory(`M+ ${currentInput} = ${memory}`);
}

function memorySubtract() {
    memory -= parseFloat(currentInput) || 0;
    addToHistory(`M- ${currentInput} = ${memory}`);
}

// Clear functions
function clearAll() {
    currentInput = '0';
    previousInput = '';
    operation = null;
    waitingForOperand = false;
    updateDisplay();
}

function clearEntry() {
    currentInput = '0';
    updateDisplay();
}

function backspace() {
    if (currentInput.length === 1) {
        currentInput = '0';
    } else {
        currentInput = currentInput.slice(0, -1);
    }
    updateDisplay();
}

// Display functions
function updateDisplay() {
    mainDisplay.textContent = currentInput;
    
    // Update history display
    if (history.length > 0) {
        const recentHistory = history.slice(-3).join('\n');
        historyDisplay.textContent = recentHistory;
    }
}

function addToHistory(entry) {
    history.push(entry);
    if (history.length > 10) {
        history.shift();
    }
}

// Additional utility functions
function formatNumber(num) {
    if (typeof num !== 'number') return num;
    
    if (Math.abs(num) >= 1e6 || (Math.abs(num) < 1e-3 && num !== 0)) {
        return num.toExponential(6);
    }
    
    return parseFloat(num.toFixed(10));
}

// Error handling
function handleError(message) {
    currentInput = 'Error';
    addToHistory(message);
    updateDisplay();
    setTimeout(() => {
        currentInput = '0';
        updateDisplay();
    }, 2000);
}

// Advanced mathematical functions (extensions)
function calculateAdvancedFunction(func, ...args) {
    try {
        switch (func) {
            case 'gcd':
                return gcd(args[0], args[1]);
            case 'lcm':
                return lcm(args[0], args[1]);
            case 'prime':
                return isPrime(args[0]);
            case 'fibonacci':
                return fibonacci(args[0]);
            default:
                return 'Function not implemented';
        }
    } catch (error) {
        return 'Error';
    }
}

// GCD and LCM functions
function gcd(a, b) {
    a = Math.abs(a);
    b = Math.abs(b);
    while (b) {
        [a, b] = [b, a % b];
    }
    return a;
}

function lcm(a, b) {
    return Math.abs(a * b) / gcd(a, b);
}

// Prime number check
function isPrime(n) {
    if (n < 2) return false;
    if (n === 2) return true;
    if (n % 2 === 0) return false;
    for (let i = 3; i <= Math.sqrt(n); i += 2) {
        if (n % i === 0) return false;
    }
    return true;
}

// Fibonacci sequence
function fibonacci(n) {
    if (n <= 0) return 0;
    if (n === 1) return 1;
    if (n > 78) return Infinity; // JavaScript limit
    
    let a = 0, b = 1;
    for (let i = 2; i <= n; i++) {
        [a, b] = [b, a + b];
    }
    return b;
}

// Statistical functions
function calculateStatistics(numbers) {
    if (!Array.isArray(numbers) || numbers.length === 0) {
        return null;
    }
    
    const sum = numbers.reduce((a, b) => a + b, 0);
    const mean = sum / numbers.length;
    const variance = numbers.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / numbers.length;
    const stdDev = Math.sqrt(variance);
    
    return {
        count: numbers.length,
        sum: sum,
        mean: mean,
        variance: variance,
        stdDev: stdDev,
        min: Math.min(...numbers),
        max: Math.max(...numbers)
    };
}

// Export functions for external use
window.Calculator = {
    calculateFunction,
    calculateAdvancedFunction,
    calculateStatistics,
    setAngleMode: (mode) => {
        angleMode = mode;
        const modeButtons = document.querySelectorAll('.mode-btn');
        modeButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });
    },
    getMemory: () => memory,
    setMemory: (value) => { memory = value; },
    getHistory: () => [...history],
    clearHistory: () => { history = []; updateDisplay(); }
};
