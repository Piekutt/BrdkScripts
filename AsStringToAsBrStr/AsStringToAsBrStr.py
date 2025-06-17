import os
import re
import hashlib
import sys

def calculate_file_hash(file_path):
    """
    Calculates the hash (MD5) of a file for comparison purposes.
    """
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            md5.update(chunk)
    return md5.hexdigest()

def replace_functions_and_constants(file_path : str, function_mapping, constant_mapping):
    """
    Replace function calls and constants in a file based on the provided mappings.
    """
    original_hash = calculate_file_hash(file_path)


    with open(file_path, "r", encoding="iso-8859-1", errors="ignore") as f:
        original_content = f.read()

    modified_content = original_content
    function_replacements = 0
    constant_replacements = 0

    # if file_path.endswith('ncsdcctrlInit.st'): 
    #     modified_content, num_replacements = re.subn(r'(\s*)((?:strcpy)|(?:strcat))', r'\1brs\2', original_content)
    #     pass



    # Replace function calls
    for old_func, new_func in function_mapping.items():
 
        pattern = rf"\b{re.escape(old_func)}\s*\("
        replacement = f"{new_func}("
        modified_content, num_replacements = re.subn(pattern, replacement, modified_content)
        function_replacements += num_replacements

    # Replace constants
    for old_const, new_const in constant_mapping.items():
        pattern = rf"\b{re.escape(old_const)}\b"
        replacement = new_const
        modified_content, num_replacements = re.subn(pattern, replacement, modified_content)
        constant_replacements += num_replacements

    if modified_content != original_content:
        with open(file_path, "w", encoding="iso-8859-1") as f:
            f.write(modified_content)

        new_hash = calculate_file_hash(file_path)
        if original_hash == new_hash:
            return function_replacements, constant_replacements, False

        print(f"{function_replacements + constant_replacements:4d} changes written to: {file_path}")
        return function_replacements, constant_replacements, True

    return function_replacements, constant_replacements, False

def check_for_library(project_path, library_names):
    """
    Checks if any specified library is used in the project.
    """
    pkg_file = os.path.join(project_path, "Logical", "Libraries", "Package.pkg")
    if not os.path.isfile(pkg_file):
        print(f"Error: Could not find Package.pkg file in: {pkg_file}")
        return []

    with open(pkg_file, "r", encoding="iso-8859-1", errors="ignore") as f:
        content = f.read()
        found_libraries = [lib for lib in library_names if lib in content]

    return found_libraries

def main():
    project_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    # Check if valid project path
    if not os.path.exists(project_path):
        print(f"Error: The provided project path does not exist: {project_path}")
        print("\nEnsure the path is correct and the project folder exists.")
        print("\nIf the path contains spaces, make sure to wrap it in quotes, like this:")
        print('   python AsStringToAsBrStr.py "C:\\path\\to\\your\\project"')
        sys.exit(1)

    # Check if .apj file exists in the provided path
    apj_files = [file for file in os.listdir(project_path) if file.endswith(".apj")]
    if not apj_files:
        print(f"Error: No .apj file found in the provided path: {project_path}")
        print("\nPlease specify a valid Automation Studio project path.")
        sys.exit(1)

    print(f"Project path validated: {project_path}")
    print(f"Using project file: {apj_files[0]}\n")

    library_names = ["AsString", "AsWStr"]
    found_libraries = check_for_library(project_path, library_names)

    if not found_libraries:
        print("Neither AsString nor AsWStr libraries found.\n")
        proceed = input("Do you want to proceed with replacing functions and constants anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Operation cancelled. No changes were made.")
            return

    else:
        print(f"Libraries found: {', '.join(found_libraries)}.\n"
              "This script will search for usages of AsString and AsWStr functions and constants and replace them with their AsBr equivalents.\n"
              "Before proceeding, make sure you have a backup or are using version control (e.g., Git).\n")
        proceed = input("Do you want to continue? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Operation cancelled. No changes were made.")
            return

    function_mapping = {
        "ftoa": "brsftoa",
        "atof": "brsatof",
        "itoa": "brsitoa",
        "atoi": "brsatoi",
        "memset": "brsmemset",
        "memcpy": "brsmemcpy",
        "memmove": "brsmemmove",
        "memcmp": "brsmemcmp",
        "strcat": "brsstrcat",
        "strlen": "brsstrlen",
        "strcpy": "brsstrcpy",
        "strcmp": "brsstrcmp",
        "wcscat": "brwcscat",
        "wcschr": "brwcschr",
        "wcscmp": "brwcscmp",
        "wcsconv": "brwcsconv",
        "wcscpy": "brwcscpy",
        "wcslen": "brwcslen",
        "wcsncat": "brwcsncat",
        "wcsncmp": "brwcsncmp",
        "wcsncpy": "brwcsncpy",
        "wcsrchr": "brwcsrchr",
        "wcsset": "brwcsset",
    }

    constant_mapping = {
        "U8toUC": "brwU8toUC",
        "UCtoU8": "brwUCtoU8",
    }

    logical_path = os.path.join(project_path, "Logical")
    total_function_replacements = 0
    total_constant_replacements = 0
    total_files_changed = 0

    # Loop through the files in the "Logical" directory and process .st, .c, and .cpp files
    for root, _, files in os.walk(logical_path):
        for file in files:
            # Add ".c" and ".cpp" to the list of file extensions to process
            if file.endswith((".st")):
                file_path = os.path.join(root, file)
                function_replacements, constant_replacements, changed = replace_functions_and_constants(
                    file_path, function_mapping, constant_mapping
                )
                if changed:
                    total_function_replacements += function_replacements
                    total_constant_replacements += constant_replacements
                    total_files_changed += 1

    print("\nSummary:")
    print(f"Total functions replaced: {total_function_replacements}")
    print(f"Total constants replaced: {total_constant_replacements}")
    print(f"Total files changed: {total_files_changed}")

    if total_function_replacements == 0 and total_constant_replacements == 0:
        print("No functions or constants needed to be replaced.")
    else:
        print("Replacement completed successfully.")

if __name__ == "__main__":
    main()
