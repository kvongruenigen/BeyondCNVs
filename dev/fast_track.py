#####################################################################
# Fast track 
######################################################################
import os
import tarfile
import shutil
import gzip
import requests
import json
import re
import pandas as pd
from bycon import *
from pymongo import MongoClient


##
## unpack_main.sh in python code
##
##



# Enter data directory
os.chdir('temp')

# Look for nested tar.gz files and extract them
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.tar.gz'):
            file_path = os.path.join(root, file)
            with tarfile.open(file_path, 'r:gz') as tar:
                tar.extractall()

# Delete all tar.gz files
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.tar.gz'):
            file_path = os.path.join(root, file)
            os.remove(file_path)

##
## unpack_sub.sh in python code
##

# Enter the 'temp' directory
os.chdir('temp')

# Find all directories in the current directory
for dir_name in os.listdir('.'):
    if os.path.isdir(dir_name):
        # Go into the directory
        os.chdir(dir_name)

        # Look for '.maf.gz' files and extract them
        for file_name in os.listdir('.'):
            if file_name.endswith('.maf.gz'):
                file_path = os.path.join('.', file_name)
                with gzip.open(file_path, 'rb') as gz_file:
                    with open(file_name[:-3], 'wb') as maf_file:
                        shutil.copyfileobj(gz_file, maf_file)

        # Go back up to the parent directory
        os.chdir('..')

# Move all files in the directories up one level
for dir_name in os.listdir('.'):
    if os.path.isdir(dir_name):
        # Go into the directory
        os.chdir(dir_name)

        # Move all files to the parent directory
        for file_name in os.listdir('.'):
            shutil.move(file_name, '..')

        # Go back up to the parent directory
        os.chdir('..')

        # Remove the directory
        os.rmdir(dir_name)

# Move all remaining files to the 'data' directory
for file_name in os.listdir('.'):
    shutil.move(file_name, '../data')

##
## get_maf.py
##



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

##
## intermediate_mapping.py
##
for file in os.listdir("data/"): # Iterate through directory
    if '.maf' in str(file): # discard MANIFEST.txt and other non-maf files
        df = pd.read_csv("data/"+ str(file), sep='\t', skiprows=7, header=0, low_memory = False) # read in the maf file as df
        df = df[relevant_columns] # subset dataframe to relevant information
        intermediate_file = pd.concat([intermediate_file, df]) # write the relevant information to intermediate_file

intermediate_file = intermediate_file.reset_index(drop=True) # Remove indexing column
intermediate_file['Tumor_Sample_Barcode'] = intermediate_file['Tumor_Sample_Barcode'].str.slice(stop=16) # Only keep the first 16 characters = sample barcode (instead of aliquot)
os.makedirs('temp/', exist_ok=True) # Check for the directory
intermediate_file.to_csv('temp/intermediate_mapping_file.csv', index = False)  # and create .csv file in the directory

##
## aliquot_to_sample.R in python code
##

import rpy2.robjects as robjects

r_code = '''
################################################################################

library(readr)
library(dplyr)
library(TCGAutils)

# Import data frame and extract barcodes
df <- read_csv("temp/intermediate_mapping_file.csv")
sample_barcodes <- unique(df['Tumor_Sample_Barcode'])

# Tumor Barcode shorten

# Create an empty list for the ids
sample_ids <- list()

# Convert barcodes into ids
for (id in sample_barcodes){
  sam <- barcodeToUUID(id)
  sam <- sam$sample_ids
  sample_ids <- c(sample_ids, sam)
}

# Make a data frame for mapping
conversion_df <- data.frame(unlist(as.list(sample_barcodes)), unlist(sample_ids))
colnames(conversion_df) <- c('sample_barcode', 'sample_ids')

# join the two data frames based on matching Barcodes
mapfile <- left_join(df, conversion_df,
                     by = c("Tumor_Sample_Barcode" = "sample_barcode"))

# Rename the columns
colnames(mapfile) <- c("aliquot_id", "reference_id", "case_id", "NCBI_Build",
                       "chromosome", "start", "end", "strand", "variant_classification",
                       "variant_type", "reference_bases", "alternate_bases_1", "alternate_bases_2",
                       "hgvsc", "hgvsp", "hgvsp_short", "sample_barcode", "sample_id")

# Select important ones and rearrange
mapfile <- mapfile %>% select(case_id, sample_id, aliquot_id, reference_id,
                              chromosome, start, end, strand, variant_classification,
                              variant_type, reference_bases, alternate_bases_1, alternate_bases_2,
                              hgvsc, hgvsp, hgvsp_short)
# Return to python
mapfile
'''

mapfile = robjects.r(r_code)

##
## mapping_finish.py
##

# Connect to MongoDB
client = MongoClient()
db = client.progenetix
bs = db.biosamples

# Read the data frame
df = pd.DataFrame(mapfile)

# Create legacy ids / external references
df['case_id'] = 'pgx:TCGA-' + df['case_id']
df['sample_id'] = 'pgx:TCGA-' + df['sample_id']

# Create placeholder for variant id, gets created while import
df['variant_id'] = [''] * len(df) 

# alternate_bases_1 is the same as reference_bases
df['alternate_bases'] = df['alternate_bases_2']

# Naming convention from pgx
df['variant_state_id'] = ['SO:0001059'] * len(df)
df['reference_name'] = df['chromosome'].str.slice(start=3)
df['variant_types'] = df['variant_type']

# Adding sequence ontologies - http://www.sequenceontology.org/browser/
df.loc[df['variant_type'] == 'SNP', 'specific_so'] = 'SO:0001483'
df.loc[df['variant_type'] == 'TNP', 'specific_so'] = 'SO:0002007'
df.loc[df['variant_type'] == 'ONP', 'specific_so'] = 'SO:0002007'
df.loc[df['variant_type'] == 'DEL', 'specific_so'] = 'SO:0000159'
df.loc[df['variant_type'] == 'INS', 'specific_so'] = 'SO:0000667'

# Convert 1-based MAF files to 0-based
df.loc[df['variant_type'] == 'SNP', 'start'] -= 1
df.loc[df['variant_type'] == 'TNP', 'start'] -= 1
df.loc[df['variant_type'] == 'ONP', 'start'] -= 1
df.loc[df['variant_type'] == 'DEL', 'start'] -= 1
df.loc[df['variant_type'] == 'INS', 'end'] -= 1 # explanation at https://www.biostars.org/p/84686/

# Generate callset_ids per aliquot for import and map sample_id to biosample_id
biosample_mapping = {}
for aliquot in set(df['aliquot_id']):
    cs_id = generate_id('pgxcs')
    df.loc[df['aliquot_id'] == aliquot, 'callset_id'] = cs_id

    sample_id = df.loc[df['aliquot_id'] == aliquot, 'sample_id'].iloc[0]
    if sample_id not in biosample_mapping:
        hit = bs.find({"external_references.id": {'$regex': sample_id}, "biosample_status.id": "EFO:0009656"})
        for entry in hit:
            biosample_mapping[sample_id] = (entry['id'], entry['individual_id'])
            break
    biosample_id, individual_id = biosample_mapping.get(sample_id, ('', ''))

    df.loc[df['aliquot_id'] == aliquot, 'biosample_id'] = biosample_id
    df.loc[df['aliquot_id'] == aliquot, 'individual_id'] = individual_id

# Clean up
df = df[['biosample_id', 'variant_id', 'callset_id', 'reference_name', 'start', 'end',
        'reference_bases', 'alternate_bases', 'hgvsc', 'variant_classification', 'variant_state_id', 
        'hgvsp', 'hgvsp_short', 'aliquot_id', 'reference_id', 'case_id', 'sample_id', 'variant_types',
        'specific_so']]

variants_in_db = df.dropna(subset = ['biosample_id'])
new = df[df['biosample_id'].isna()]

# Write finished mapping file
os.makedirs('temp/', exist_ok = True) # Check for the directory
variants_in_db.to_csv('/temp/varImport.tsv', sep = '\t', index = False)  # and create .tsv file in the directory
new.to_csv('/temp/varNew.tsv', sep = '\t', index = False)