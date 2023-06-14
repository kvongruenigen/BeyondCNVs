
# This rule executes all the code except the Novel Data Download
rule targets:
	input:
		"data/maf_data.csv",
		"temp/mapfile.tsv",
		"data/varNew.tsv",
		"data/varImport.tsv"

##
## Novel Data Download
##

# Download the MAF files
rule maf_download: # 20 min
	script:
		"scripts/gdc_maf_download.py"

# Unzip and move the files from the temp into the data folder
rule unpack: # 1 min
	shell:
		"bash scripts/unpack.sh"

##
## If MAF files available:
##

# Create an intermediate mapping file for conversion in R
rule data_extraction: # 25 min
	output:
		"temp/maf_data.csv"
	script:
		"scripts/data_extraction.py"

# Match the barcodes of the aliquots to the sample ids
rule mapfile: # 1 min
	input: 
		"temp/maf_data.csv"
	output: 
		"temp/mapfile.tsv"
	script:
		"scripts/aliquot_to_sample.R"

# Match the sample ids to the database to retrieve biosample_id
# Remove the alternate bases that matches the references bases
# Create callset and variant ids
rule mapping: # 3h 5 min
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