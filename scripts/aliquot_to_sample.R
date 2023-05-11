################################################################################
# Clean write
rm(list = ls())
library(readr)
library(dplyr)
library(TCGAutils)

df <- read_csv("temp/intermediate_mapping_file.csv")
sample_barcodes <- unique(df['Tumor_Sample_Barcode'])
sample_ids <- list()

for (id in sample_barcodes){
  sam <- barcodeToUUID(id)
  sam <- sam$sample_ids
  sample_ids <- c(sample_ids, sam)
}

conversion_df <- data.frame(unlist(as.list(sample_barcodes)), unlist(sample_ids))
colnames(conversion_df) <- c('sample_barcode', 'sample_ids')

# join the two data frames based on matching UUID and aliquot_id
mapfile <- left_join(df, conversion_df,
                     by = c("Tumor_Sample_Barcode" = "sample_barcode"))

# Rename the columns
colnames(mapfile) <- c("aliquot_id", "reference_id", "case_id", "NCBI_Build",
                       "chromosome", "start", "end", "strand", "variant_classification",
                       "variant_type", "reference_bases", "alternate_bases_1", "alternate_bases_2",
                       "hgvsc", "hgvsp", "hgvsp_short", "sample_barcode", "biosample_id")

# Select important ones and rearrange
mapfile <- mapfile %>% select(case_id, biosample_id, aliquot_id, reference_id,
                              chromosome, start, end, strand, variant_classification,
                              variant_type, reference_bases, alternate_bases_1, alternate_bases_2,
                              hgvsc, hgvsp, hgvsp_short)
write_tsv(mapfile, 'temp/mapfile.tsv')