# AS6 Migration Utility

A Python script designed to assist with migrating Automation Studio 4 projects to Automation Studio 6. This tool scans project files for obsolete libraries, functions, and unsupported hardware, providing actionable recommendations to help streamline the migration process.

## Features

- Detects and lists obsolete libraries, function blocks, and functions.
- Identifies unsupported hardware modules in .hw files.
- Verifies compatibility of .apj and .hw files.
- Finds misplaced .uad files and suggests corrective actions.
- Generates a detailed report summarizing findings and recommendations.

## Prerequisites

- Python 3.8 or later.
- A valid Automation Studio 4 project directory.

## Usage

### Running the Script

Clone the repository and navigate to the script directory:

```bash
git clone https://github.com/BRDK-GitHub/BrdkScripts.git
cd BrdkScripts
```

Run the script by providing the path to your Automation Studio 4 project directory:
```bash
python AS6_migration.py <path-to-your-project>
```

#### Example
To scan a specific project directory:
```bash
python AS6_migration.py C:\path\to\your\AutomationStudioProject
```

To scan the current directory where the script is located:
```bash
python AS6_migration.py
```
#### Output
The script generates a report file named AS6_migration_result.txt in the specified project directory, summarizing all findings.

## Key Features Explained
- Obsolete Libraries: Detects libraries listed in Package.pkg files that are no longer supported in Automation Studio 6.
- Obsolete Function Blocks and Functions: Scans .var, .typ, .st, and .c files for function blocks and functions marked as obsolete.
- Unsupported Hardware: Identifies hardware modules not compatible with Automation Studio 6.
- File Compatibility: Ensures .apj and .hw files meet the minimum required version for migration.
- Misplaced .uad Files: Flags .uad files located outside the Connectivity/OpcUA directory.

## Limitations
- Designed specifically for Automation Studio 4 projects.
- Requires Python 3.6 or later.
- The script does not modify project files; it only identifies and reports issues.

## Contribution
Contributions are welcome! Feel free to fork the repository, make changes, and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.