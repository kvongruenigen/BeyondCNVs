#!/usr/bin/env python3
# coding: utf-8

#####################################################################

# Data extraction from MAF files
# (identifiers and variant information)

#####################################################################

# Module import
import pandas as pd
import os
import shutil
import glob
from tqdm import tqdm

# Create a dataframe for the data
data = pd.DataFrame()

# Iterate through directory with downloaded maf files and
# load the relevant information in "data"

print("Starting data extraction...")

df_list = []

for file in tqdm(glob.glob("data/maf_files/*.maf"), desc = "Extraction progress"): 
    df = pd.read_csv(file, sep = "\t", skiprows = 7, header = 0,
        low_memory = False)
    df_list.append(df)

if os.path.isfile("data/maf_data.csv"):
    print("Found existing data. Comparing...")
    existing_data = pd.read_csv("data/maf_data.csv", low_memory = False)
    # Compare the existing data with the new data
    existing_data_columns = existing_data.columns.tolist()
    new_data_columns = df_list[0].columns.tolist()
    # Adding only new rows
    existing_data = pd.concat([existing_data, *df_list], ignore_index=True)
    data = existing_data

else:
    # If the maf_data.csv file doesn't exist, create it with the new data
    data = pd.concat(df_list).reset_index(drop=True)
print("Data extraction completed.")
# Tumor Barcode shortening to get the sample barcode instead of the
# aliquot barcode (first 16 characters = sample barcode)
data["aliquot_barcode"] = data["Tumor_Sample_Barcode"]
data["Tumor_Sample_Barcode"] = data["Tumor_Sample_Barcode"].str.slice(stop = 16)

 # Check for the directory
os.makedirs("data/", exist_ok = True)
print("Writing output file...")
# and create .csv file in the directory
data.to_csv("data/maf_data.csv", index = False)
shutil.copy("data/maf_data.csv", "temp/maf_data.csv")
print("Done")