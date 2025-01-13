# Delete Temp, Binaries, and Diagnosis Folders

This script helps you clean up your project directories by deleting specific folders (`Temp`, `Binaries`, and `Diagnosis`) that are often generated as part of build processes in Automation Studio or similar tools. The script ensures that only folders located alongside `.apj` files are deleted.

## Features

- Searches for `Temp`, `Binaries`, and `Diagnosis` folders within project directories.
- Only deletes folders found in the same directory as `.apj` files.
- Displays folder sizes in MB before deletion.
- Handles permission issues gracefully by attempting to adjust file permissions before deletion.
- Provides a summary of actions, including execution time.

## Usage

### Prerequisites
- Python 3.x installed on your system.

### Running the Script

1. Clone the repository or download the script file.
2. Open a terminal or command prompt.
3. Run the script using:

```bash
python deleteTempBinDiag.py [directory]
```

#### Example
Search in a specific directory:
```bash
python deleteTempBinDiag.py C:\MyAsProjectsFolder
```

Search in the default directory (C:\projects):
```bash
python AsStringToAsBrStr.py
```

#### Output
- A progress update is shown while scanning directories.
- Lists folders to be deleted, their sizes, and locations.
- Prompts for confirmation before deletion.

## Error Handling
- If a folder or file cannot be deleted due to permission issues, the script will attempt to modify its permissions.
- If the issue persists, it will log the error and continue with other folders.

## Contribution
Do you have ideas or scripts that could benefit others? Feel free to contribute! Submit your scripts via pull requests or create issues for improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.