#!/usr/bin/env python
# coding: utf-8

###############################################################################################################

import pandas as pd
from bycon import *
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient()
db = client.progenetix
bs = db.biosamples

# Read the data frame
df = pd.read_csv("temp/mapfile.tsv", sep='\t', header=0, low_memory = False)


# Create legacy ids / external references
df['case_id'] = 'pgx:TCGA-' + df['case_id']
df['sample_id'] = 'pgx:TCGA-' + df['sample_id']


# Generate callset_ids per aliquot for import
callset_ids = []
for aliquot in set(df['aliquot_id']):
    cs_id = generate_id('pgxcs')
    df.loc[df['aliquot_id'] == aliquot, 'callset_id'] = cs_id

# Create placeholder for variant id, gets created while import
df['variant_id'] = ['pgxvar-'] * len(df)

# Create sets of ids for fast mapping
sid = set(df['sample_id'])

# Map sample_id and get biosample_id
for i in sid:
    # If there are more than one document, something is wrong
    if bs.count_documents({"external_references.id": {'$regex': i},"biosample_status.id":"EFO:0009656"}) > 1:
        print('More than one document found.')
        
    else:
        hit = bs.find({"external_references.id": {'$regex': i},"biosample_status.id":"EFO:0009656"})
        for entry in hit:
            df.loc[df['sample_id'] == i, 'biosample_id'] = entry['id']
            df.loc[df['sample_id'] == i, 'individual_id'] = entry['individual_id']

# alternate_bases_1 is the same as reference_bases
df['alternate_bases'] = df['alternate_bases_2']

# Clean up
df = df[['biosample_id', 'variant_id', 'callset_id', 'chromosome', 'start', 'end', 'strand',
        'reference_bases', 'alternate_bases', 'hgvsc', 'variant_classification', 'variant_type', 
        'hgvsp', 'hgvsp_short', 'aliquot_id', 'reference_id', 'case_id', 'sample_id']]

# Write finished mapping file
os.makedirs('temp/', exist_ok = True) # Check for the directory
df.to_csv('temp/mappingfile.tsv', sep = '\t', index = False)  # and create .tsv file in the directory