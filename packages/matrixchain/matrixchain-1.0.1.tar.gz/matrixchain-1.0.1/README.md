# Matrix Chain Multiplication Optimizer 🔗⚡

A **hacker-style** interactive visualizer for the Matrix Chain Multiplication problem using Dynamic Programming. This tool demonstrates the classic algorithm with colorful terminal output, live computation visualization, and detailed step-by-step analysis.

## 🎯 What is Matrix Chain Multiplication?

The Matrix Chain Multiplication problem is a classic dynamic programming problem that finds the optimal way to parenthesize a chain of matrix multiplications to minimize the total number of scalar multiplications.

**Example**: For matrices A₁(5×4), A₂(4×6), A₃(6×2), A₄(2×7)
- Bad parenthesization: `((A₁ × A₂) × A₃) × A₄` = 240 + 60 + 84 = **384 operations**
- Optimal parenthesization: `A₁ × ((A₂ × A₃) × A₄)` = 48 + 84 + 140 = **272 operations**

## ✨ Features

- 🎨 **Colorful hacker-style interface** with ASCII art banner
- 🔍 **Live computation visualization** showing each DP step
- 📊 **Beautiful table displays** for cost and split matrices
- 🎯 **Optimal parenthesization output**
- 📝 **Two input modes**: Quick paste or step-by-step interactive
- ⚡ **Real-time scanning effects** for enhanced user experience

## 🚀 Installation

### Option 1: Direct Installation
```bash
# Clone the repository
git clone <repository-url>
cd matrixchain

# Install dependencies
pip install colorama

# Run the program
python -m matrixchain
```

### Option 2: Package Installation
```bash
# Install as a package
pip install -e .

# Run from anywhere
matrixchain
```

## 🎮 Usage

### Quick Start
```bash
python -m matrixchain
```

### Input Formats

**Method 1: Quick Paste**
```
Enter matrix dimensions P as space-separated integers.
Example for matrices A1 (5x4), A2 (4x6), A3 (6x2), A4 (2x7):
    5 4 6 2 7  (this is P0 P1 P2 P3 P4)

[#] Paste dims (or press Enter to input step-by-step): 5 4 6 2 7
```

**Method 2: Interactive Input**
```
[#] Number of matrices (n): 4
  Enter rows of A1 (or P0): 5
  Enter cols of A1 (or P1): 4
  Enter rows of A2 (or P1): 4
  Enter cols of A2 (or P2): 6
  ...
```

### Example Session
```
 __  __       _        _   _       _ _   _
|  \/  | __ _| |_ _ __| | | |_ __ (_) |_(_) ___  _ __
| |\/| |/ _` | __| '__| | | | '_ \| | __| |/ _ \| '_ \
| |  | | (_| | |_| |  | |_| | | | | | |_| | (_) | | | |
|_|  |_|\__,_|\__|_|   \___/|_| |_|_|\__|_|\___/|_| |_|

        Matrix Chain Multiplication Optimizer
============================================================

Dimensions P = [5, 4, 6, 2, 7]  (matrices = 4)

[INFO] Initializing...
[INFO] Checking multiplication paths...
[SCAN] Enumerating chain lengths...
[SCAN] Evaluating possible splits...
[HIT] Possible optimization detected...
[INFO] Calculating minimal cost path...

[+] Starting DP computation...

[SCAN] DP[1,2] via k=1 -> cost=120
[HIT] DP[1,2] = 120 (k=1)
[SCAN] DP[2,3] via k=2 -> cost=48
[HIT] DP[2,3] = 48 (k=2)
...

[LOOT] Minimal Multiplication Cost Table (mTable)
+---------------+---------------+---------------+---------------+
|               |      A1       |      A2       |      A3       |
+---------------+---------------+---------------+---------------+
|      A1       |       0       |      120      |      168      |
|      A2       |      --       |       0       |       48      |
|      A3       |      --       |      --       |       0       |
+---------------+---------------+---------------+---------------+

[LOOT] Optimal Parenthesization
A1 x ((A2 x A3) x A4)

[+] Minimum multiplication cost: 272

[+] Mission Complete
```

## 🧮 Algorithm Details

The program implements the classic **Dynamic Programming** solution:

1. **State Definition**: `m[i][j]` = minimum cost to multiply matrices from i to j
2. **Recurrence**: `m[i][j] = min(m[i][k] + m[k+1][j] + p[i]*p[k+1]*p[j+1])` for all k
3. **Base Case**: `m[i][i] = 0` (single matrix requires no multiplication)
4. **Reconstruction**: Uses split table `s[i][j]` to build optimal parenthesization

**Time Complexity**: O(n³)
**Space Complexity**: O(n²)

## 📁 Project Structure

```
matrixchain/
├── matrixchain/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Module entry point
│   └── core.py              # Main algorithm and UI logic
├── setup.py                 # Package setup configuration
├── pyproject.toml           # Modern Python packaging
├── README.md                # This file
└── LICENSE                  # MIT License
```

## 🛠️ Requirements

- **Python**: 3.7+
- **Dependencies**:
  - `colorama` - For cross-platform colored terminal output

## 🎨 Features Breakdown

### Visual Elements
- **ASCII Art Banner**: Eye-catching startup screen
- **Color-coded Output**: Different colors for different types of information
- **Progress Indicators**: Live scanning effects during computation
- **Formatted Tables**: Professional-looking cost and split matrices

### Algorithm Features
- **Complete DP Implementation**: Full matrix chain multiplication solver
- **Parenthesization Reconstruction**: Shows optimal grouping
- **Step-by-step Visualization**: See each DP computation in real-time
- **Input Validation**: Robust error handling for user input

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Educational Use

This project is perfect for:
- **Algorithm Visualization**: Understanding how DP works step-by-step
- **Computer Science Education**: Teaching optimization problems
- **Interview Preparation**: Classic DP problem implementation
- **Performance Analysis**: Comparing different parenthesizations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Chauhan Pruthviraj**

## 🙏 Acknowledgments

- Classic Dynamic Programming algorithm for Matrix Chain Multiplication
- Colorama library for cross-platform terminal colors
- ASCII art generation tools

---

*Happy optimizing! 🚀*