rule maf_download:
	script:
		"scripts/get_maf.py"
	
rule unpack_all:
	shell:
		"bash scripts/unpack_main.sh && bash scripts/unpack_sub.sh"

rule intermediate_file:
	script:
		"scripts/Mapping_file_creator.py"