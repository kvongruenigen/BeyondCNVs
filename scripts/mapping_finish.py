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
df = df[['biosample_id', 'variant_id', 'callset_id', 'individual_id', 'reference_name', 'start', 'end',
        'reference_bases', 'alternate_bases', 'hgvsc', 'variant_classification', 'variant_state_id', 
        'hgvsp', 'hgvsp_short', 'aliquot_id', 'reference_id', 'sample_id', 'case_id', 'variant_types',
        'specific_so']]

variants_in_db = df[df['biosample_id'] != '']
new = df[df['biosample_id'] == '']

# Write finished mapping file
os.makedirs('temp/', exist_ok = True) # Check for the directory
variants_in_db.to_csv('temp/varImport.tsv', sep = '\t', index = False)  # and create .tsv file in the directory
new.to_csv('temp/varNew.tsv', sep = '\t', index = False)