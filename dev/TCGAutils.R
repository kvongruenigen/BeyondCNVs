# dd <- read_delim("Desktop/Project/data/0b3ab4ef-c43c-4184-a396-27c0c5398d85.wxs.aliquot_ensemble_masked.maf",
#               delim = "\t", escape_double = FALSE,
#               trim_ws = TRUE, skip = 7)

################################################################################
test_set <- unique_aliquots[1:10]
test_df <- df[1:100,]

################################################################################
# select only the UUID and sample_id columns



################################################################################
# Clean write
rm(list = ls())
library(readr)
library(dplyr)
library(TCGAutils)

df <- read_csv("temp/intermediate_mapping_file.csv")

unique_aliquots <- unique(df$Tumor_Sample_UUID)
barcodes <- list()
sample_ids <- list()
for (id in unique_aliquots){
  bar <- UUIDtoBarcode(id, from_type = "aliquot_ids")
  bar <- substr(bar$portions.analytes.aliquots.submitter_id, 1, 16)
  sam <- barcodeToUUID(bar)
  sam <- sam$sample_ids
  sample_ids <- c(sample_ids, sam)
  barcodes <- c(barcodes, bar)
}

conversion_df <- data.frame(unlist(as.list(unique_aliquots)), unlist(sample_ids))
colnames(conversion_df) <- c('aliquot_ids', 'sample_ids')
# join the two data frames based on matching UUID and aliquot_id
mapfile <- left_join(df, conversion_df, by = c("Tumor_Sample_UUID" = "aliquot_ids"))
colnames(mapfile) <- c("aliquot_id", "reference_id", "case_id", "NCBI_Build",
                       "chromosome", "start", "end", "strand", "variant_classification",
                       "variant_type", "ref_allele", "tumor_allele1", "tumor_allele2",
                       "hgvsc", "hgvsp", "hgvsp_short", "sample_id")
mapfile <- mapfile %>% select(case_id, sample_id, aliquot_id, reference_id,
                              chromosome, start, end, strand, variant_classification,
                              variant_type, ref_allele, tumor_allele1, tumor_allele2,
                              hgvsc, hgvsp, hgvsp_short)
write_tsv(mapfile, 'temp/mappingfile.txt')

