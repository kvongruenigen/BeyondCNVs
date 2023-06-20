
# This rule executes all the code except the Novel Data Download
rule targets:
	input:
		"temp/maf_data.csv",
		"temp/mapfile.tsv",
		"data/varNew.tsv",
		"data/varImport.tsv"

##
## Novel Data Download
##

# Download the MAF files
rule maf_download:
	script:
		"scripts/gdc_maf_download.py"

# Unzip and move the files from the temp into the data folder
rule unpack:
	shell:
		"bash scripts/unpack.sh"

##
## If MAF files available:
##

# Concatenate all the maf files into one CSV
rule data_extraction:
	output:
		"temp/maf_data.csv"
	script:
		"scripts/data_extraction.py"

# Convert the sample barcodes to the sample ids for mapping
rule mapfile:
	input: 
		"temp/maf_data.csv"
	output: 
		"temp/mapfile.tsv"
	script:
		"scripts/aliquot_to_sample.R"

# Match the sample ids to the database to retrieve biosample ids and individual ids
# Create callset and variant ids
rule mapping:
	input:
		"temp/mapfile.tsv"
	output:
		"data/varImport.tsv",
		"data/varNew.tsv"
	script:
		"scripts/mapping_finish.py"

# Remove files in temp
rule cleanup:
    shell:
        "rm temp/*"