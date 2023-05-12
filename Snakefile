
# Download the MAF files
rule maf_download: # 20 min
	script:
		"scripts/get_maf.py"

# Unzip and move the files from the temp into the data folder
rule unpack_all: # 1 min
	shell:
		"bash scripts/unpack_main.sh && bash scripts/unpack_sub.sh"

# Create an intermediate mapping file for conversion in R
rule intfile: # 25 min
	script:
		"scripts/intermediate_mapping.py"

# Match the barcodes of the aliquots to the sample ids
rule mapfile: # 1 min
	script:
		"scripts/aliquot_to_sample.R"

# Match the sample ids to the database to retrieve biosample_id
# Remove the alternate bases that matches the references bases
# Create callset and variant ids
rule mapping: # 3h 5 min
	script:
		"scripts/mapping_finish.py"

# Remove files in temp
rule clean_up:
    input:
        "temp/intermediate_mapping_file.csv",
        "temp/mapfile.tsv"
    shell:
        "rm temp/intermediate_mapping_file.csv temp/mapfile.tsv"