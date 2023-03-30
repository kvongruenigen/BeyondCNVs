# Find all directories in the current directory
cd data

for dir in */; do
    echo "Processing directory: $dir"

    # Go into the directory
    cd "$dir"

    # Look for tar.gz files and extract them
    for file in *.maf.gz; do
        echo "Extracting file: $file"
        gunzip "$file"
    
    done

    # Go back up to the parent directory
    cd ..
done

for dir in */; do
    # Go into the directory
    cd "$dir"

    # Move all files in the directory up one level
    mv * ../

    # Go back up to the parent directory
    cd ..

    rmdir "$dir"
done