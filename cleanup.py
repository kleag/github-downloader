import csv
import os
import shutil
import sys

def contains_subdirectories(directory_path):
    entries = os.listdir(directory_path)

    for entry in entries:
        entry_path = os.path.join(directory_path, entry)
        if os.path.isdir(entry_path):
            return True

    return False

def process_csv_file(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for path, _, lang in reader:
            # Check if the language is neither C nor C++
            if lang == 'C' or lang == 'C++':
                continue
            if os.path.exists(path):
                print(path+ " "  + lang)
                # Split the path into directory components
                print(f"Remove {path}: {lang}", file=sys.stderr)
                shutil.rmtree(path, ignore_errors=True)

            components = path.split('/')

            # Remove dir2 from the components
            components.pop(-1)

            # Reconstruct the modified path
            modified_path = '/'.join(components)
            if os.path.exists(modified_path) and not contains_subdirectories(
                    modified_path):
                print(f"Remove {modified_path}: {lang} and empty", file=sys.stderr)
                shutil.rmtree(modified_path, ignore_errors=True)

# Replace 'f.csv' with your actual CSV file name
process_csv_file('../github_repositories_20230830_100stars.csv')
