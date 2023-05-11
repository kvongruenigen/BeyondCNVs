#!/usr/bin/env python
# coding: utf-8

###############################################################################################################

import requests
import json
import re
import os

# Access the file endpoint from GDC for id retrieval
files_endpt = "https://api.gdc.cancer.gov/files"

# This set of filters is nested under an 'and' operator.
# Filtering for TCGA Masked Somatic Mutation - results in open access maf files.
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

# Here a GET is used, so the filter parameters should be passed as a JSON string.
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

# This step populates the download list with the file_ids from the previous query
for file_entry in json.loads(response.content.decode("utf-8"))["data"]["hits"]:
    file_uuid_list.append(file_entry["file_id"])

# Chunk the file ids so the server can handle it
ls = []
for i in range(0, len(file_uuid_list), 1000):
    ls.append(file_uuid_list[i:i + 1000])

# Download the files
for idls in ls:
    data_endpt = "https://api.gdc.cancer.gov/data"

    params = {"ids": idls}

    response = requests.post(data_endpt, data=json.dumps(params), headers={"Content-Type": "application/json"})

    response_head_cd = response.headers["Content-Disposition"]

    file_name = re.findall("filename=(.+)", response_head_cd)[0]

    save_path = 'temp/'

    completeName = os.path.join(save_path, file_name)

    with open(completeName, "wb") as output_file:
        output_file.write(response.content)