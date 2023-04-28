#!/bin/bash

# Enter data directory
cd temp

# Look for nested tar.gz files and extract them
find . -name '*.tar.gz' -exec tar -xzf {} \;

# Delete all tar.gz files
find . -name '*.tar.gz' -delete

