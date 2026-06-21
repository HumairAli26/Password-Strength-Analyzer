# 🔐 Password Strength Checker

<div align="center">

### A Modern Desktop Password Security Analyzer

**Real-time password strength analysis with entropy calculation, brute-force crack-time estimation, live visualizations, password generation, and dark/light themes.**

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-blue?style=for-the-badge)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-orange?style=for-the-badge)
![NumPy](https://img.shields.io/badge/NumPy-Numerical-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)

*A feature-rich desktop application designed to educate users about password security through interactive analysis and visualization.*

</div>

---

# 📖 Overview

Passwords remain the first line of defense against unauthorized access. Weak passwords are vulnerable to dictionary attacks, brute-force attacks, credential stuffing, and password spraying.

**Password Strength Checker** is a desktop application that helps users understand **how secure their passwords really are** by performing live analysis based on modern password-strength principles.

Instead of simply displaying "Strong" or "Weak", the application explains **why** a password received its score by analyzing:

* Password length
* Character diversity
* Entropy
* Estimated brute-force resistance
* Security best practices

The goal is both **education** and **practical password evaluation**.

---

# ✨ Features

## ⚡ Real-Time Password Analysis

No submit button required.
The password is analyzed instantly while typing, providing immediate feedback about its security.

---

## ✅ Intelligent Strength Classification

Passwords are automatically classified into four categories:

| Score | Rating         |
| ----: | -------------- |
|   0–2 | 🔴 Weak        |
|   3–4 | 🟡 Medium      |
|     5 | 🟢 Strong      |
|     6 | 🟣 Very Strong |

---

## 📋 Six Security Criteria

The application evaluates passwords using six essential security rules.

✔ Minimum length (8 characters)

✔ Recommended length (12+ characters)

✔ Uppercase letters

✔ Lowercase letters

✔ Numbers

✔ Special symbols

Each satisfied criterion contributes to the overall security score.

---

## 📊 Live Security Visualizations

Interactive charts make password analysis easier to understand.

### Horizontal Progress Chart

Displays which security criteria have been met.

### Circular Strength Gauge

Shows the overall password score on an easy-to-read radial indicator.
Visualizations update instantly as the password changes.

---

## 🧠 Entropy Calculation

The application estimates password entropy using Information Theory.

```
Entropy (bits)
=
Password Length × log₂(Character Pool Size)
```

Higher entropy indicates a significantly larger search space for attackers.

---

## ⏱️ Brute-Force Crack Time Estimation

The estimated time required for an offline brute-force attack is calculated assuming:

```
10 Billion Guesses / Second
```

Results are presented in human-readable form, ranging from:

* Seconds
* Minutes
* Hours
* Days
* Years
* Centuries

This helps users understand the real-world impact of stronger passwords.

---

## 🔑 Secure Password Generator

Generate highly secure passwords with customizable options.

Features include:

* Adjustable password length
* Uppercase letters
* Lowercase letters
* Numbers
* Symbols
* One-click generation

Perfect for creating passwords suitable for modern security standards.

---

## 📋 Copy to Clipboard

Copy generated or analyzed passwords instantly using a single button.
Visual feedback confirms successful copying.

---

## 👁️ Password Visibility Toggle

Switch between:

* Hidden password mode
* Visible password mode

Useful for verifying complex passwords without compromising usability.

---

## 🕘 Password History

The application securely stores the last five analyzed/generated passwords.

For privacy:

* Passwords are masked
* No passwords are permanently saved

---

## 🎨 Modern User Interface

Supports both:

🌞 Light Theme
🌙 Dark Theme

Designed with a clean layout that remains responsive across different screen sizes.

---

# 🖥️ Screenshots

| Light Theme             | Dark Theme              |
| ----------------------- | ----------------------- |
|<img width="1916" height="1019" alt="light" src="https://github.com/user-attachments/assets/98d65ad4-96cf-4122-93d3-8eb0409504ef" />
 |<img width="1910" height="1024" alt="dark" src="https://github.com/user-attachments/assets/da8a8d27-c522-483f-b6dc-07f6ac38a9c5" />
|

Example folder structure:

```
screenshots/
    light.png
    dark.png
```

---

# 🛠 Technology Stack

| Technology               | Purpose                   |
| ------------------------ | ------------------------- |
| Python 3                 | Core programming language |
| Tkinter                  | Desktop GUI               |
| Matplotlib               | Interactive charts        |
| NumPy                    | Mathematical computations |
| Regular Expressions (re) | Password validation       |
| random                   | Password generation       |
| string                   | Character pools           |

---

# 📦 Installation

## Clone Repository

```bash
git clone https://github.com/<your-username>/password-strength-checker.git
```

```bash
cd password-strength-checker
```

---

## Install Dependencies

```bash
pip install matplotlib numpy
```

Tkinter is included with most Python installations.
Ubuntu users may install it separately:

```bash
sudo apt install python3-tk
```

---

# ▶️ Running the Application

```bash
python password_checker.py
```

---

# 🚀 How to Use

1. Launch the application.
2. Enter a password.
3. Watch the live analysis update automatically.
4. Review the checklist of satisfied security criteria.
5. Examine entropy and crack-time estimates.
6. Observe the live visualization charts.
7. Generate secure passwords if needed.
8. Copy passwords directly to the clipboard.
9. Switch between Light and Dark themes.

---

# 🔍 Password Evaluation Algorithm

The application uses a **6-point scoring model**.

| Criterion         | Points |
| ----------------- | :----: |
| Length ≥ 8        |    ✅   |
| Length ≥ 12       |    ✅   |
| Uppercase Letters |    ✅   |
| Lowercase Letters |    ✅   |
| Numbers           |    ✅   |
| Symbols           |    ✅   |

### Overall Rating

| Score | Classification |
| ----: | -------------- |
|   0–2 | Weak           |
|   3–4 | Medium         |
|     5 | Strong         |
|     6 | Very Strong    |

---

# 📈 Entropy Formula

```
Entropy = Length × log₂(Character Pool)
```

Example:

```
Password:

Tr0ub4dor!@
Length = 11
Character Pool = 94
Entropy ≈ 72 Bits
```

---

# 📂 Project Structure

```
password-strength-checker/

├── password_checker.py
├── README.md
└── screenshots/
    ├── light.png
    └── dark.png
```

---

# 🎯 Learning Objectives

This project demonstrates practical applications of:

* String manipulation
* Regular expressions
* Conditional logic
* GUI programming
* Data visualization
* Password security principles
* Entropy calculation
* Brute-force estimation
* Python desktop application development

---

# 🚀 Future Improvements

Planned enhancements include:

* [ ] Integration with Have I Been Pwned API
* [ ] Dictionary word detection
* [ ] Keyboard pattern detection
* [ ] Detection of leaked/common passwords
* [ ] Password policy customization
* [ ] Password history export
* [ ] Password hashing demonstration
* [ ] Unit testing
* [ ] Standalone executable with PyInstaller
* [ ] Multi-language support

---

# 🤝 Contributing

Contributions are welcome!
If you have suggestions for improvements or discover any issues, feel free to:

* Open an Issue
* Submit a Pull Request
* Share feature ideas

---

# 👨‍💻 Author

**Humair Ali**

Cybersecurity Enthusiast • Python Developer • Full-Stack Learner  
If you found this project useful, consider giving the repository a ⭐ on GitHub!

---
