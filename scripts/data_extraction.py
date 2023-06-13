#!/usr/bin/env python3
# coding: utf-8

#####################################################################

# Data extraction from MAF files
# (identifiers and variant information)

#####################################################################

# Module import
import pandas as pd
import os
import glob
from tqdm import tqdm

# This is a list of combined identifiers and variant information
# Documentation: 
# https://docs.gdc.cancer.gov/Data/File_Formats/MAF_Format/
relevant_columns = ['Tumor_Sample_UUID', 'Matched_Norm_Sample_UUID',
                    'case_id', 'Chromosome', 
                    'Start_Position', 'End_Position',
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

print('Starting data extraction...')

df_list = []

column_types = {
    'Tumor_Sample_UUID': str,
    'Matched_Norm_Sample_UUID': str,
    'case_id': str,
    'Chromosome': str, 
    'Start_Position': int,
    'End_Position': int,
    'Variant_Classification':str,
    'Variant_Type': str,
    'Reference_Allele': str,
    'Tumor_Seq_Allele2': str,
    'HGVSc': str,
    'HGVSp': str,
    'HGVSp_Short': str,
    'Tumor_Sample_Barcode': str,
    'all_effects': str,
    'Transcript_ID': str,
    'Gene': str,
    'Feature': str,
    'Feature_type': str,
    'HGNC_ID': str,
    'ENSP': str,
    'RefSeq': str

}
for file in tqdm(glob.glob("data/maf_files/*.maf"), desc = 'Extraction progress'): 
    df = pd.read_csv("data/maf_files/"+ str(file), sep='\t',
     skiprows=7, header=0, usecols=relevant_columns, low_memory = False, dtype=column_types)
    df_list.append(df)

data = pd.concat(df_list).reset_index(drop=True) # Remove indexing column

# Tumor Barcode shortening to get the sample barcode instead of the
# aliquot barcode (first 16 characters = sample barcode)
data['Tumor_Sample_Barcode'] = data['Tumor_Sample_Barcode'].str.slice(stop=16)

 # Check for the directory
os.makedirs('temp/', exist_ok=True)

# and create .csv file in the directory
data.to_csv('temp/maf_data.csv', index = False)

print('Data extraction completed.')