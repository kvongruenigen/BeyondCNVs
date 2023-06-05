#!/usr/bin/env python3
# coding: utf-8

#####################################################################

# Data extraction from MAF files
# (identifiers and variant information)

#####################################################################

# Module import
import pandas as pd
import os

# This is a list of combined identifiers and variant information
# Documentation: 
# https://docs.gdc.cancer.gov/Data/File_Formats/MAF_Format/
relevant_columns = ['Tumor_Sample_UUID','Matched_Norm_Sample_UUID',
                    'case_id', 'NCBI_Build','Chromosome', 
                    'Start_Position','End_Position',
                    'Variant_Classification', 'Variant_Type',
                    'Reference_Allele', 'Tumor_Seq_Allele2',
                    'HGVSc', 'HGVSp', 'HGVSp_Short',
                    'Tumor_Sample_Barcode', 'all_effects',
                    'Transcript_ID', 'Gene', 'Feature',
                    'Feature_type', 'HGNC_ID', 'ENSP',
                    'RefSeq']

# Create a dataframe for the data
data = pd.DataFrame()

# Assign columns from relevant list
for info in relevant_columns:
    data[info] = []

# Iterate through directory with downloaded maf files and
# load the relevant information in 'data'
for file in os.listdir("temp/"): 
    if '.maf' in str(file): 
        df = pd.read_csv("data/"+ str(file), sep='\t', skiprows=7,
        header=0, low_memory = False)
        df = df[relevant_columns]
        data = pd.concat([data, df])

data = data.reset_index(drop=True) # Remove indexing column

# Tumor Barcode shortening to get the sample barcode instead of the
# aliquot barcode (first 16 characters = sample barcode)
data['Tumor_Sample_Barcode'] = data['Tumor_Sample_Barcode'].str.slice(stop=16)

 # Check for the directory
os.makedirs('data/', exist_ok=True)

# and create .csv file in the directory
data.to_csv('data/maf_data.csv', index = False)