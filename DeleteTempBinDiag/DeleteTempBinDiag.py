import os
import time
import sys
import stat

DEFAULT_ROOT_DIRECTORY = r'C:\projects'
FOLDERS_TO_DELETE = ('Temp', 'Binaries', 'Diagnosis')


def measure_folder_size(folder_path):
    """Calculate the size of a folder in MB."""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for file in filenames:
                fp = os.path.join(dirpath, file)
                total_size += os.path.getsize(fp)
    except Exception as e:
        print(f"Error calculating size for {folder_path}: {e}")
    return total_size / (1024 * 1024)  # Convert bytes to MB


def find_folders_to_delete(root_dir):
    """Find folders to delete where .apj files exist."""
    folders_to_delete = []
    total_size = 0

    print(f"Searching for folders {FOLDERS_TO_DELETE} in {root_dir}")

    try:
        for root, dirs, files in os.walk(root_dir):
            clean_root = root.replace('\n', ' ').replace('\r', '')
            sys.stdout.write(f'\rChecking directory: {clean_root[:75]:<75}')
            sys.stdout.flush()

            # Check if .apj files exist in the current directory
            if any(file.endswith('.apj') for file in files):
                for folder_name in FOLDERS_TO_DELETE:
                    folder_path = os.path.join(root, folder_name)
                    if os.path.isdir(folder_path):
                        folder_size = measure_folder_size(folder_path)
                        total_size += folder_size
                        folders_to_delete.append((folder_size, folder_path))

                # Do not traverse deeper into subdirectories
                dirs.clear()

    except Exception as e:
        print(f"Error accessing {root_dir}: {e}")

    sys.stdout.write('\r' + ' ' * 100 + '\r')  # Clear the progress line
    sys.stdout.flush()

    return folders_to_delete, total_size


def delete_folders(folders):
    """Delete specified folders with error handling for access issues."""
    for folder_size, folder_path in folders:
        try:
            for root, dirs, files in os.walk(folder_path, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                    except PermissionError:
                        os.chmod(file_path, stat.S_IWRITE)  # Give write permission
                        os.remove(file_path)
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        os.rmdir(dir_path)
                    except PermissionError:
                        os.chmod(dir_path, stat.S_IWRITE)  # Give write permission
                        os.rmdir(dir_path)
            os.rmdir(folder_path)
            print(f"Deleted: {folder_size:.2f} MB Found here: {folder_path}")
        except Exception as e:
            print(f"Error deleting {folder_path}: {e}")

def main():
    start_time = time.time()

    # Get root directory from command-line argument or use default
    root_directory = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ROOT_DIRECTORY

    # Validate the root directory
    if not os.path.isdir(root_directory):
        print(f"Error: The specified directory '{root_directory}' does not exist or is not accessible.")
        return

    # Find folders to delete
    folders_to_delete, total_size = find_folders_to_delete(root_directory)

    if folders_to_delete:
        print('\nThe following folders will be deleted:')

        # Find the maximum width of the size portion (align after decimal point)
        max_size_width = max(len(f"{size:.2f}") for size, _ in folders_to_delete)

        for folder_size, folder_path in folders_to_delete:
            # Align sizes to the right based on the decimal point
            size_str = f"{folder_size:.2f}"
            print(f"{size_str:>{max_size_width}} MB Found here: {folder_path}")

        print(f"\nTime taken to find folders: {time.time() - start_time:.2f} seconds")
        print(f"Total size of folders to be deleted: {total_size:.2f} MB")

        confirmation = input("Do you want to delete all these folders? (y/n): ").strip().lower()

        if confirmation == 'y':
            delete_start_time = time.time()
            delete_folders(folders_to_delete)
            print(f"\nFolders deleted in {time.time() - delete_start_time:.2f} seconds.")
        else:
            print("Deletion cancelled.")
    else:
        print(f"\nTime taken to find folders: {time.time() - start_time:.2f} seconds")
        print("No folders to delete.")

    elapsed_time = time.time() - start_time
    print(f"\nExecution completed in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    main()
