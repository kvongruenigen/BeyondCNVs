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
    cd "$dir"

    # Look for tar.gz files and extract them
    for file in *.maf.gz; do
        gunzip "$file"
    
    # Move all files in the directory up one level
    mv * ../

    done

    # Go back up to the parent directory
    cd ..

    # Remove empty folder
    rmdir "$dir"
done
