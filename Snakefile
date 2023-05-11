
rule maf_download:
	script:
		"scripts/get_maf.py"

	
rule unpack_all:
	shell:
		"bash scripts/unpack_main.sh && bash scripts/unpack_sub.sh"


rule intfile:
	script:
		"scripts/intermediate_mapping.py"


rule mapfile:
	script:
		"scripts/aliquot_to_sample.R"


rule mapping:
	script:
		"scripts/mapping_finish.py"

rule clean_up:
    input:
        "temp/intermediate_mapping_file.csv",
        "temp/mapfile.tsv"
    shell:
        "rm temp/intermediate_mapping_file.csv temp/mapfile.tsv"

rule all:
	input:
		"temp/mappingfile.tsv"