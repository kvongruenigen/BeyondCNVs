import pandas as pd
from bycon import *
from pymongo import MongoClient

client = MongoClient()
db = client.progenetix
bs = db.biosamples

df = pd.read_csv("temp/mapfile.tsv", sep='\t', header=0, low_memory = False)


# Create legacy ids / external references
df['case_id'] = 'pgx:TCGA-' + df['case_id']
df['sample_id'] = 'pgx:TCGA-' + df['biosample_id']


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
df = df[['case_id', 'sample_id', 'biosample_id', 'variant_id', 'callset_id', 'chromosome',
       'start', 'end', 'strand', 'reference_bases', 'alternate_bases_1', 'alternate_bases_2', 'variant_classification', 'variant_type', 'hgvsc',
       'hgvsp', 'hgvsp_short', 'aliquot_id', 'reference_id']]

# Compare alternate_bases_1/2 with reference_bases and add non-matching values to alternate_bases
df.loc[df['reference_bases'] != df['alternate_bases_1'], 'alternate_bases'] = df['alternate_bases_1']
df.loc[df['reference_bases'] != df['alternate_bases_2'], 'alternate_bases'] = df['alternate_bases_2']

# Remove the 'alternate_bases_1' and 'alternate_bases_2' columns
df = df.drop(['alternate_bases_1', 'alternate_bases_2'], axis=1)


# Write finished mapping file
os.makedirs('temp/', exist_ok = True) # Check for the directory
df.to_csv('temp/mappingfile.tsv', sep = '\t', index = False)  # and create .tsv file in the directory