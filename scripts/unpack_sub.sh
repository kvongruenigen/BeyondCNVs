
cd temp

# Find all directories in the current directory
for dir in */; do
    # Go into the directory
    cd "$dir"

    # Look for tar.gz files and extract them
    for file in *.maf.gz; do
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

mv * ../data
