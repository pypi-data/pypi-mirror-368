# genpass

A simple Python CLI tool for generating secure passwords with customizable length and complexity.

## Features

- Supports three complexity levels:
  - **SIMPLE**: Lowercase letters only
  - **MEDIUM**: Mixed uppercase and lowercase letters
  - **HIGH**: Mixed letters, digits, and special characters
- Input validation for length (integer between 1 and 100) and complexity
- Colored CLI output for success and error messages using `click`
- Modular design with strategies, validators, and distribution calculator

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/genpass.git
   cd genpass
   ```

2. (Optional) Create and activate a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Install as an editable package:

   ```bash
   pip install -e .
   ```

## Usage

- Run the CLI with default options (entry point is `cli.py`):

```bash
python -m generatepwd.cli
```

Or use the `generatepwd` entry point (if installed):

```bash
generatepwd -l 16 -c HIGH
```

Options:

- `-l`, `--length`: Password length (default: 12)
- `-c`, `--complexity`: Complexity level (`SIMPLE`, `MEDIUM`, `HIGH`, default: `SIMPLE`)

Example:

```bash
generatepwd -l 20 -c medium
# Output: Generated Password: fRLsSiPlnYaNtgpMfPQY
```

## Project Structure

```
pyproject.toml
requirements.txt
README.md
src/generatepwd/
├── cli.py               # CLI command definitions
├── main.py              # Entry point for the application
├── complexity.py        # Defines complexity levels and strategies
├── distribution.py      # Calculates character distribution
├── generator.py         # Generates password using strategies
├── validators.py        # Validates user inputs
├── password_exceptions.py # Custom exceptions for errors
└── print_handler.py     # Colored CLI output handling
```

## Contributing

Contributions, issues, and feature requests are welcome. Please open an issue or submit a pull request.

## License

MIT License

Copyright (c) 2025 Sriram Dhanaraj

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

