#!/usr/bin/env python
# coding: utf-8

###############################################################################################################
## Intermediate file for identifiers and variant information -- Working -- not in Snakemake tho
# Module import

import pandas as pd
import os

# Get the relevant columns
relevant_columns = ['Tumor_Sample_UUID','Matched_Norm_Sample_UUID','case_id', 'NCBI_Build','Chromosome',
          'Start_Position','End_Position','Strand', 'Variant_Classification', 'Variant_Type',
          'Reference_Allele', 'Tumor_Seq_Allele1', 'Tumor_Seq_Allele2', 'HGVSc', 'HGVSp',
          'HGVSp_Short', 'Tumor_Sample_Barcode'] # combined identifiers and variant information

# Create a dataframe for the data
intermediate_file = pd.DataFrame() # Create empty dataframe for intermediate file

for info in relevant_columns: # Assign columns from relevant list
    intermediate_file[info] = []

for file in os.listdir("data/"): # Iterate through directory
    if '.maf' in str(file): # discard MANIFEST.txt and other non-maf files
        df = pd.read_csv("data/"+ str(file), sep='\t', skiprows=7, header=0, low_memory = False) # read in the maf file as df
        df = df[relevant_columns] # subset dataframe to relevant information
        intermediate_file = pd.concat([intermediate_file, df]) # write the relevant information to intermediate_file

intermediate_file = intermediate_file.reset_index(drop=True) # Remove indexing column
intermediate_file['Tumor_Sample_Barcode'] = intermediate_file['Tumor_Sample_Barcode'].str.slice(stop=16) # Only keep the first 16 characters = sample barcode (instead of aliquot)
os.makedirs('temp/', exist_ok=True) # Check for the directory
intermediate_file.to_csv('temp/intermediate_mapping_file.csv', index = False)  # and create .csv file in the directory

