# AsMath to AsBrMath Migration Utility

A Python script designed to assist in migrating Automation Studio 4 projects by replacing obsolete AsMath functions and constants with their AsBrMath equivalents. This tool ensures compatibility and alignment with Automation Studio 6 standards.

## Features

- Automatically detects and replaces:
- AsMath functions with AsBrMath functions.
- AsMath constants with AsBrMath constants.
- Validates the presence of the AsMath library in the project.
- Ensures the integrity of project files by computing hashes before and after modifications.
- Provides a summary of changes for transparency.

## Prerequisites

- Python 3.6 or later.
- A valid Automation Studio project directory.

## Usage

### Running the Script

Clone the repository and navigate to the script directory:


Run the script by providing the path to your Automation Studio project directory:
```bash
python AsMathToAsBrMath.py <path-to-your-project>
```

#### Example
To scan a specific project directory:
```bash
python AsMathToAsBrMath.py C:\path\to\your\AutomationStudioProject
```

To scan the current directory where the script is located:
```bash
python AsMathToAsBrMath.py
```

#### Output
- The script provides a summary of changes directly in the terminal.
- Modified files are overwritten in place.

## Key Features Explained
- Function Replacement: Replaces functions like atan2 with brmatan2, ceil with brmceil, and others based on the provided mapping.
- Constant Replacement: Replaces constants such as amPI with brmPI and amE with brmE.
- Hash Validation: Ensures no unintended changes are introduced by verifying file hashes.

## Limitations
- Only processes .st files under the Logical directory.
- Does not add or remove libraries; only updates existing function and constant references.
- Assumes the Package.pkg file is located at Logical/Libraries/Package.pkg.

## Contribution
Contributions are welcome! Feel free to fork the repository, make changes, and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.