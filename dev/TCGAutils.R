# dd <- read_delim("Desktop/Project/data/0b3ab4ef-c43c-4184-a396-27c0c5398d85.wxs.aliquot_ensemble_masked.maf",
#               delim = "\t", escape_double = FALSE,
#               trim_ws = TRUE, skip = 7)

################################################################################
# Clean write
rm(list = ls())
library(readr)
library(dplyr)
library(TCGAutils)

df <- read_csv("temp/intermediate_mapping_file.csv")
sample_barcodes <- unique(df['Tumor_Sample_Barcode'])
sample_ids <- list()

start_time <- Sys.time()
for (id in sample_barcodes){
  sam <- barcodeToUUID(id)
  sam <- sam$sample_ids
  sample_ids <- c(sample_ids, sam)
}
end_time <- Sys.time()
end_time - start_time

conversion_df <- data.frame(unlist(as.list(unique_aliquots)), unlist(sample_ids))
colnames(conversion_df) <- c('aliquot_ids', 'sample_ids')
# join the two data frames based on matching UUID and aliquot_id
mapfile <- left_join(df, conversion_df, by = c("Tumor_Sample_UUID" = "aliquot_ids"))
colnames(mapfile) <- c("aliquot_id", "reference_id", "case_id", "NCBI_Build",
                       "chromosome", "start", "end", "strand", "variant_classification",
                       "variant_type", "reference_bases", "alternate_bases_1", "alternate_bases_2",
                       "hgvsc", "hgvsp", "hgvsp_short", "biosample_id")
mapfile <- mapfile %>% select(case_id, biosample_id, aliquot_id, reference_id,
                              chromosome, start, end, strand, variant_classification,
                              variant_type, reference_bases, alternate_bases_1, alternate_bases_2,
                              hgvsc, hgvsp, hgvsp_short)
write_tsv(mapfile, 'temp/mappingfile.tsv')

