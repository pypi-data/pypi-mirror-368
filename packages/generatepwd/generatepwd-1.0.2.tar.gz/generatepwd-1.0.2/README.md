# generatepwd

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

- Install using pip command

```bash
pip install generatepwd
```

## Usage

- Run the CLI with default options (default length - 12, default complexity - SIMPLE):

```bash
generatepwd
```

Or use the `generatepwd`:

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

## Contributing

Contributions, issues, and feature requests are welcome. Please open an issue or submit a pull request.

## License

MIT License

Copyright (c) 2025 Sriram Dhanaraj

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

