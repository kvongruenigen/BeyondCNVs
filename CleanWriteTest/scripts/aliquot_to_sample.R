
#####################################################################

# Turning barcodes into Sample UUIDs for mapping in progenetix

#####################################################################

# Load necessary libraries
library(readr)
library(dplyr)
library(TCGAutils)

# Import data frame and extract barcodes
data <- read_csv("data/maf_data.csv")
sample_barcodes <- unique(data['Tumor_Sample_Barcode'])

# Create an empty list for the ids
sample_ids <- list()

# Convert barcodes into ids
for (id in sample_barcodes){
  sam <- barcodeToUUID(id)
  sam <- sam$sample_ids
  sample_ids <- c(sample_ids, sam)
}

# Make a data frame for mapping
mapping_df <- data.frame(unlist(as.list(sample_barcodes)), unlist(sample_ids))
colnames(mapping_df) <- c('sample_barcode', 'sample_ids')

# Join the two data frames based on matching Barcodes
mapfile <- left_join(data, mapping_df,
                     by = c("Tumor_Sample_Barcode" = "sample_barcode"))

#####################################################################

# Renaming for further processing

#####################################################################

# Rename the columns
colnames(mapfile) <- c("aliquot_id", "reference_id", "case_id",
            "ncbi_build", "chromosome", "start", "end",
            "variant_classification", "variant_type",
            "reference_bases", "alternate_bases", "hgvsc", "hgvsp",
            "hgvsp_short", "sample_barcode", "sample_id",
            "all_effects", "transcript_id", "gene", "feature",
            "feature_type", "hgnc_id", "ensp", "refseq")

# Select important ones and rearrange
mapfile <- mapfile %>% select(case_id, sample_id, aliquot_id,
  reference_id, chromosome, start, end, variant_classification,
  variant_type, reference_bases, alternate_bases, hgvsc, hgvsp,
  hgvsp_short, sample_id, sample_barcode, all_effects,
  transcript_id, gene, feature, feature_type, hgnc_id, ensp, refseq)

# Write file
write_tsv(mapfile, 'temp/mapfile.tsv')