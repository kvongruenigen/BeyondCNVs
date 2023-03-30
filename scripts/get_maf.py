# Filtering ##################################################################

import os
import requests
import json
import re
import pandas as pd

fields = [
    "file_name",
    "cases.submitter_id",
    "cases.samples.sample_type",
    "cases.disease_type",
    "cases.project.project_id"
    ]

fields = ",".join(fields)

files_endpt = "https://api.gdc.cancer.gov/files"

# This set of filters is nested under an 'and' operator.
# Filtering for TCGA Masked Somatic Mutation - results in open access maf files.
filters = {
    "op": "and",
    "content":[
        {
        "op": "in",
        "content":{
            "field": "cases.project.program.name",
            "value": ["TCGA"]
            }
        },
                    {
        "op": "in",
        "content":{
            "field": "files.data_type",
            "value": ["Masked Somatic Mutation"]
            }
        }
    ]
}

# A POST is used, so the filter parameters can be passed directly as a Dict object.
params = {
    "filters": filters,
    "fields": fields,
    "format": "TSV",
    "size": "20"
    }
# The parameters are passed to 'json' rather than 'params' in this case
response = requests.post(files_endpt, headers = {"Content-Type": "application/json"}, json = params)

# Write .txt file to read ids
with open("ids_to_get.txt", "wb") as output_file:
    output_file.write(response.content)

df = pd.read_csv("ids_to_get.txt",sep='\t')
ids_to_get = []

for lines in df["id"]:
    ids_to_get += [lines]


# Post Request to Download Multiple Files ####################################

data_endpt = "https://api.gdc.cancer.gov/data"

params = {"ids": ids_to_get}

response = requests.post(data_endpt,
                        data = json.dumps(params),
                        headers={
                            "Content-Type": "application/json"
                            })

response_head_cd = response.headers["Content-Disposition"]

file_name = re.findall("filename=(.+)", response_head_cd)[0]

save_path = 'temp/'

completeName = os.path.join(save_path, file_name)


with open(completeName, "wb") as output_file:
    output_file.write(response.content)


# Remove generated .txt for clean space ######################################

os.remove("ids_to_get.txt")
