#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

# Set the directory path
d="./cloned_repos.new.80.c-cpp"

# Check if the directory exists
if [ ! -d "$d" ]; then
  echo "Error: Directory $d does not exist."
  exit 1
fi

# Loop through subdirectories
for subdir in "$d"/*; do
  # Check if it's a directory
  if [ -d "$subdir" ]; then
    # Get the directory name
    dir_name=$(basename "$subdir")

    # Create a tar.gz archive
    tar -czf "$d/$dir_name.tar.gz" -C "$d" "$dir_name"

    # Remove the original directory
    rm -rf "$subdir"

    echo "Archive created and original directory removed: $dir_name"
  fi
done

echo "Process completed."

