#!/usr/bin/env python
# coding: utf-8

# In[2]:


###############################################################################################################
## Intermediate file for identifiers and variant information -- Working -- not in Snakemake tho
# Module import

import pandas as pd
import os


# Preparation

relevant = ['Tumor_Sample_UUID','Matched_Norm_Sample_UUID','case_id', 'NCBI_Build','Chromosome',
          'Start_Position','End_Position','Strand', 'Variant_Classification', 'Variant_Type',
          'Reference_Allele', 'Tumor_Seq_Allele1', 'Tumor_Seq_Allele2', 'HGVSc', 'HGVSp',
          'HGVSp_Short'] # combined identifiers and variant information

imf = pd.DataFrame() # Create empty dataframe for intermediate file

for info in relevant: # Assign columns from relevant list
    imf[info] = []

for file in os.listdir("data/"): # Iterate through directory
    if '.maf' in str(file): # discard MANIFEST.txt and other non-maf files
        df = pd.read_csv("data/"+ str(file), sep='\t', skiprows=7, header=0, low_memory = False) # read in the maf file as df
        df = df[relevant] # subset dataframe to relevant information
        imf = pd.concat([imf, df]) # write the relevant information to imf

imf = imf.reset_index(drop=True) # Remove indexing column
os.makedirs('temp/', exist_ok=True) # Check for the directory
imf.to_csv('temp/intermediate_mapping_file.csv', index = False)  # and create .csv file in the directory

