#!/bin/bash

# Move to directory with the downloaded data
cd temp

# Look for nested tar.gz files and extract them
find . -name '*.tar.gz' -exec tar -xzf {} \;

# Delete all tar.gz files
find . -name '*.tar.gz' -delete

# Find all directories in the current directory
for dir in */; do
    # Go into the directory
    cd "$dir" || continue

    # Look for tar.gz files and extract them
    for file in *.maf.gz; do
        gunzip "$file" || continue
    done
    
    # Move all files in the directory up one level
    mv * ../ || continue

    # Go back up to the parent directory
    cd .. || continue

    # Remove empty folder
    rmdir "$dir" || continue
done

# Check for any errors during the script execution
if [ $? -eq 0 ]; then
    echo "Script executed successfully."
else
    echo "Error occurred during script execution."
fi

cd ..

if [ ! -d "data" ]; then
    mkdir "data"
fi

if [ ! -d "data/maf_files" ]; then
    mkdir "data/maf_files"
fi

mv temp/*.maf data/maf_files
