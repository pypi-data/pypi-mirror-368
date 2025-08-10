
# VibeIsOdd

[![PyPI](https://img.shields.io/pypi/v/vibeisodd.svg)](https://pypi.org/project/vibeisodd/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Why use math when you can use AI?**

VibeIsOdd is the most over-engineered way to check if a number is odd. Instead of using arithmetic, it asks a large language model (like OpenAI GPT or Gemini) if your number is odd. Because, why not?

## 🤔 What is this?
A parody Python package that uses AI to answer the age-old question: "Is this number odd?" It’s a real, installable package with all the trimmings—just for fun (and maybe a little learning).

## 🚀 Installation

```bash
pip install vibeisodd
```

Or, for the truly adventurous:

```bash
git clone https://github.com/yourusername/VibeIsOdd.git
cd VibeIsOdd
pip install .
```

## 🔑 Setup

You'll need an API key for your chosen AI provider (OpenAI or Gemini). Set it as an environment variable:

- For OpenAI: `OPENAI_API_KEY`
- For Gemini: `GEMINI_API_KEY`

Example (PowerShell):
```powershell
$env:OPENAI_API_KEY="your-openai-key"
$env:GEMINI_API_KEY="your-gemini-key"
```

## 🤖 Usage

```python
from vibeisodd import vibeisodd

print(vibeisodd(7))  # True (7 is odd, confirmed by AI)
print(vibeisodd(8))  # False (8 is even, AI never lies)
```

### Batch Processing

```python
from vibeisodd import vibeisodd_batch

numbers = [1, 2, 3.0, 4.5]
results = vibeisodd_batch(numbers)
print(results)  # [True, False, True, True]
```

### Example Script

You can also run the included example:

```bash
python -m vibeisodd.example
```

## 🛠 Development

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Set your API key(s)
4. Run tests/examples

## 📦 Package Info
- **Version:** 1.0.0
- **Author:** Your Name
- **License:** MIT
- **Repo:** [https://github.com/yourusername/VibeIsOdd](https://github.com/yourusername/VibeIsOdd)

## 😂 Why does this exist?
Because sometimes, you just want to see what happens when you replace a one-line function with a large language model. For science. For fun. For the memes.

## 🧑‍💻 Contributing
PRs welcome! Bonus points for adding even more unnecessary AI.

## 📄 License
MIT
