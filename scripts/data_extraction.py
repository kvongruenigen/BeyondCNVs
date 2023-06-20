#!/usr/bin/env python3
# coding: utf-8

#####################################################################

# Data extraction from MAF files
# All information will be stored at data/maf_data.csv

#####################################################################

# Module import
import pandas as pd
import os
import shutil
import glob
from tqdm import tqdm

# Create a dataframe and a list for the MAF data
data = pd.DataFrame()
df_list = []

# Information to be extracted for variant import
relevant_columns = ["Tumor_Sample_UUID", "Matched_Norm_Sample_UUID",
                       "case_id", "Chromosome",
                       "Start_Position", "End_Position",
                       "Variant_Classification", "Variant_Type",
                       "Reference_Allele", "Tumor_Seq_Allele2",
                       "Tumor_Sample_Barcode"]

# Iterate through directory with downloaded maf files and
# load the relevant information in "data"
print("Starting data extraction...")
for file in tqdm(glob.glob("data/maf_files/*.maf"), desc = "Extraction progress"): 
    df = pd.read_csv(file, sep = "\t", skiprows = 7, header = 0,
        low_memory = False)
    df_list.append(df[relevant_columns])

# Create one data frame from the list
data = pd.concat(df_list).reset_index(drop=True)
print("Data extraction completed.")

# Tumor Barcode shortening to get the sample barcode instead of the
# aliquot barcode (first 16 characters = sample barcode)
data["aliquot_barcode"] = data["Tumor_Sample_Barcode"]
data["Tumor_Sample_Barcode"] = data["Tumor_Sample_Barcode"].str.slice(stop = 16)

 # Check for the directory
os.makedirs("temp/", exist_ok = True)
print("Writing output file...")
# and create .csv file in the directory
data.to_csv("temp/maf_data.csv", index = False)
print("Done.")