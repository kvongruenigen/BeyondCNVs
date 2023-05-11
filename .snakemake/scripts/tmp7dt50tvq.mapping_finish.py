
######## snakemake preamble start (automatically inserted, do not edit) ########
import sys; sys.path.extend(['/opt/homebrew/mambaforge/envs/snakemake/lib/python3.11/site-packages', '/Users/kayvongrunigen/Library/Caches/snakemake/snakemake/source-cache/runtime-cache/tmpz4dcqa5n/file/Users/kayvongrunigen/Desktop/Project/scripts', '/Users/kayvongrunigen/Desktop/Project/scripts']); import pickle; snakemake = pickle.loads(b'\x80\x04\x95\xc0\x03\x00\x00\x00\x00\x00\x00\x8c\x10snakemake.script\x94\x8c\tSnakemake\x94\x93\x94)\x81\x94}\x94(\x8c\x05input\x94\x8c\x0csnakemake.io\x94\x8c\nInputFiles\x94\x93\x94)\x81\x94}\x94(\x8c\x06_names\x94}\x94\x8c\x12_allowed_overrides\x94]\x94(\x8c\x05index\x94\x8c\x04sort\x94eh\x0f\x8c\tfunctools\x94\x8c\x07partial\x94\x93\x94h\x06\x8c\x19Namedlist._used_attribute\x94\x93\x94\x85\x94R\x94(h\x15)}\x94\x8c\x05_name\x94h\x0fsNt\x94bh\x10h\x13h\x15\x85\x94R\x94(h\x15)}\x94h\x19h\x10sNt\x94bub\x8c\x06output\x94h\x06\x8c\x0bOutputFiles\x94\x93\x94)\x81\x94}\x94(h\x0b}\x94h\r]\x94(h\x0fh\x10eh\x0fh\x13h\x15\x85\x94R\x94(h\x15)}\x94h\x19h\x0fsNt\x94bh\x10h\x13h\x15\x85\x94R\x94(h\x15)}\x94h\x19h\x10sNt\x94bub\x8c\x06params\x94h\x06\x8c\x06Params\x94\x93\x94)\x81\x94}\x94(h\x0b}\x94h\r]\x94(h\x0fh\x10eh\x0fh\x13h\x15\x85\x94R\x94(h\x15)}\x94h\x19h\x0fsNt\x94bh\x10h\x13h\x15\x85\x94R\x94(h\x15)}\x94h\x19h\x10sNt\x94bub\x8c\twildcards\x94h\x06\x8c\tWildcards\x94\x93\x94)\x81\x94}\x94(h\x0b}\x94h\r]\x94(h\x0fh\x10eh\x0fh\x13h\x15\x85\x94R\x94(h\x15)}\x94h\x19h\x0fsNt\x94bh\x10h\x13h\x15\x85\x94R\x94(h\x15)}\x94h\x19h\x10sNt\x94bub\x8c\x07threads\x94K\x01\x8c\tresources\x94h\x06\x8c\tResources\x94\x93\x94)\x81\x94(K\x01K\x01\x8c0/var/folders/n3/gb4qgnr95d9bk6_y9qtj6p980000gq/T\x94e}\x94(h\x0b}\x94(\x8c\x06_cores\x94K\x00N\x86\x94\x8c\x06_nodes\x94K\x01N\x86\x94\x8c\x06tmpdir\x94K\x02N\x86\x94uh\r]\x94(h\x0fh\x10eh\x0fh\x13h\x15\x85\x94R\x94(h\x15)}\x94h\x19h\x0fsNt\x94bh\x10h\x13h\x15\x85\x94R\x94(h\x15)}\x94h\x19h\x10sNt\x94bhTK\x01hVK\x01hXhQub\x8c\x03log\x94h\x06\x8c\x03Log\x94\x93\x94)\x81\x94}\x94(h\x0b}\x94h\r]\x94(h\x0fh\x10eh\x0fh\x13h\x15\x85\x94R\x94(h\x15)}\x94h\x19h\x0fsNt\x94bh\x10h\x13h\x15\x85\x94R\x94(h\x15)}\x94h\x19h\x10sNt\x94bub\x8c\x06config\x94}\x94\x8c\x04rule\x94\x8c\x07mapping\x94\x8c\x0fbench_iteration\x94N\x8c\tscriptdir\x94\x8c-/Users/kayvongrunigen/Desktop/Project/scripts\x94ub.'); from snakemake.logging import logger; logger.printshellcmds = False; __real_file__ = __file__; __file__ = '/Users/kayvongrunigen/Desktop/Project/scripts/mapping_finish.py';
######## snakemake preamble end #########
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


# Generate ids for import
variant_ids = []
cs_id = generate_id('pgxcs')
call_ids = []

for i in range(0, len(df)):
    variant_ids.append(generate_id('pgxvar'))
    call_ids.append(cs_id)
    
# Add the ids to the data frame
df['variant_id'] = variant_ids
df['callset_id'] = call_ids


# Create sets of ids for
sid = set(df['sample_id'])

# Map sample_id and get biosample_id
for i in sid:
    hit = bs.find({"external_references.id": {'$regex': i},"biosample_status.id":"EFO:0009656"})
    for entry in hit:
        df.loc[df['sample_id'] == i, 'biosample_id'] = entry['id']
        df.loc[df['sample_id'] == i, 'individual_id'] = entry['individual_id']
        

# Rearrange the columns
df = df[['biosample_id', 'variant_id', 'callset_id', 'chromosome', 'start', 'end', 'strand',
        'reference_bases', 'alternate_bases_1', 'alternate_bases_2', 'variant_classification', 'variant_type', 'hgvsc',
        'hgvsp', 'hgvsp_short', 'aliquot_id', 'reference_id', 'case_id', 'sample_id']]

# Compare alternate_bases_1/2 with reference_bases and add non-matching values to alternate_bases
df.loc[df['reference_bases'] != df['alternate_bases_1'], 'alternate_bases'] = df['alternate_bases_1']
df.loc[df['reference_bases'] != df['alternate_bases_2'], 'alternate_bases'] = df['alternate_bases_2']

# Remove the 'alternate_bases_1' and 'alternate_bases_2' columns
df = df.drop(['alternate_bases_1', 'alternate_bases_2'], axis=1)


# Write finished mapping file
os.makedirs('temp/', exist_ok = True) # Check for the directory
df.to_csv('temp/mappingfile.tsv', sep = '\t', index = False)  # and create .tsv file in the directory