#!/usr/bin/env python3
# coding: utf-8

###############################################################################################################
# Sometimes the server times out and the script gets stuck - implement break after certain time?
# Mostly happens overnight.

import requests
import json
import re
import os

# Access the file endpoint from GDC for id retrieval
files_endpt = "https://api.gdc.cancer.gov/files"


# Filtering for TCGA Masked Somatic Mutation
# - results in open access maf files.
# This set of filters is nested under an 'and' operator.
filters = {
    "op": "and",
    "content": [
        {
            "op": "in",
            "content": {
                "field": "cases.project.program.name",
                "value": ["TCGA"]
            }
        },
        {
            "op": "in",
            "content": {
                "field": "files.data_type",
                "value": ["Masked Somatic Mutation"]
            }
        }
    ]
}

# Here a GET is used, so the filter parameters should be passed as a
# JSON string.
params = {
    "filters": json.dumps(filters),
    "fields": "file_id",
    "format": "JSON",
    "size": "20000"
}

# Download the ids
response = requests.get(files_endpt, params=params)

# Create a list for the ids
file_uuid_list = []

# This step populates the download list with the file_ids from the 
# previous query
for file_entry in json.loads(response.content.decode("utf-8"))["data"]["hits"]:
    file_uuid_list.append(file_entry["file_id"])
print('Found ', len(file_uuid_list), 'files to download.')

# Import record of existing files
existing_ids = []
if os.path.isfile('../data/existing_file_ids.txt'):
    with open('../data/existing_file_ids.txt') as f:
        lines = f.readlines()
    for i in lines:
        existing_ids.append(i)

# Remove existing file UUIDs from download queue
removed_ids = []
for i in existing_ids:
    i = i.strip('\n')
    if i in file_uuid_list:
        file_uuid_list.remove(i)
        removed_ids.append(i)
print('Removed', len(removed_ids), 'existing ids from download queue.')

# Create an empty list to store UUID chunks
ls = []

# Append sublists to 'ls' for 1000 ids each (server limits)
for i in range(0, len(file_uuid_list), 1000):
    ls.append(file_uuid_list[i:i + 1000])


# Create record if imported file UUIDs
for i in file_uuid_list:
    i = i + '\n'
    existing_ids.append(i)
with open('../data/existing_file_ids.txt', 'w') as file_ids:
    for i in existing_ids:
        file_ids.write(i)