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

# Create placeholder for variant id, gets created while import
df['variant_id'] = ['pgxvar-'] * len(df)

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

# alternate_bases_1 is the same as reference_bases
df['alternate_bases'] = df['alternate_bases_2']

# Clean up
df = df[['biosample_id', 'variant_id', 'callset_id', 'chromosome', 'start', 'end', 'strand',
        'reference_bases', 'alternate_bases', 'hgvsc', 'variant_classification', 'variant_type', 
        'hgvsp', 'hgvsp_short', 'aliquot_id', 'reference_id', 'case_id', 'sample_id']]

variants_in_db = df.dropna(subset = ['biosample_id'])
new = df[df['biosample_id'].isna()]

# Write finished mapping file
os.makedirs('temp/', exist_ok = True) # Check for the directory
variants_in_db.to_csv('/temp/varImport.tsv', sep = '\t', index = False)  # and create .tsv file in the directory
new.to_csv('/temp/varNew.tsv', sep = '\t', index = False)