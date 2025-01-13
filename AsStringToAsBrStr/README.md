# Replace AsString and AsWStr Utility

A Python script designed to assist in migrating and refactoring Automation Studio project files by replacing deprecated AsString and AsWStr functions and constants with their modern AsBr equivalents.

## Features

Automatically detects and replaces:
- Detects and replaces deprecated AsString and AsWStr functions with AsBr equivalents.
- Replaces constants related to AsWStr with updated AsBr constants.
- Outputs a summary of replacements made across all project files.

## Prerequisites

- Python 3.6 or later.
- A valid Automation Studio project directory.
- The script assumes the project structure includes a Logical/Libraries/Package.pkg file.

## Usage

### Running the Script

Clone the repository and navigate to the script directory:


Run the script by providing the path to your Automation Studio project directory:
```bash
python AsStringToAsBrStr.py <path-to-your-project>
```

#### Example
To scan a specific project directory:
```bash
python AsStringToAsBrStr.py C:\path\to\your\AutomationStudioProject
```

To scan the current directory where the script is located:
```bash
python AsStringToAsBrStr.py
```

#### Output
- The script provides a summary of changes directly in the terminal.
- Modified files are overwritten in place.

## Key Features Explained
- Function Mapping: The script replaces old AsString and AsWStr functions with their modern AsBr equivalents. For example: ftoa is replaced by brsftoa.
- Constant Replacement: Replaces constants such as U8toUC with brwU8toUC.

## Limitations
- Only processes .st files under the Logical directory.
- Does not add or remove libraries; only updates existing function and constant references.
- Assumes the Package.pkg file is located at Logical/Libraries/Package.pkg.

## Contribution
Contributions are welcome! Feel free to fork the repository, make changes, and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.