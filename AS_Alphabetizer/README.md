# AS_Alphabetizer

The AS_Alphabetizer is a Python GUI application designed to help users organize their B&R Automation Studio projects. Its primary purpose is to alphabetically sort files in selected folders, such as the mappView Media folder, ensuring that all objects (e.g., images) are listed in alphabetical order. The app provides an interactive folder tree view with checkboxes, allowing users to select specific folders for sorting.

## Features

- Alphabetical Sorting: Ensures that all files in selected folders (e.g., mappView Media folders) are organized alphabetically.
- Graphical User Interface (GUI): Built with tkinter and ttk, the app provides an easy-to-use interface for selecting and sorting folders.
- Folder Browsing: Allows users to browse their filesystem and display a folder hierarchy.
- Checkbox Treeview: Displays folders with checkboxes for user selection.

## Usage

### Prerequisites
- Python 3.x installed on your system.

### Running the Script

1. Clone the repository or download the script file.
2. Open in Visual Studio Code and run the script


### How to Use

1. Launch the Application: Run the script to open the AS_Alphabetizer.
2. Browse for Folders: 
    - Click the "Browse Folders" button.
    - Select the root folder of your Automation Studio project.
3. View and Select Folders: 
    - The folder tree will display the hierarchy of the selected folder.
    - Use checkboxes to select one or more folders (e.g., the mappView Media folder).
4. Sort Selected Folders:
    - Click the "Start" button to sort the selected folders.
    - Sorting organizes .pkg files alphabetically by <Objects> tags (e.g., Folder, Package, and others).
5. Success Message: A message box will confirm when sorting is complete.


### Future Enhancements
- Improve treeview styling with custom icons.

## Contribution
Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.