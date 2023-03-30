# cBioPortal Access #########

library(rapiclient)
library(cBioPortalData)
library(AnVIL)
library(stringr)

# Get TCGA studies ----
client <- get_api(url = "https://www.cbioportal.org/api/v2/api-docs")
cbio <- cBioPortal()
studies <- getStudies(cbio, buildReport = TRUE)
head(studies)
# All mutation calls (in VCF or MAF format) are processed through an internal pipeline to annotate the variant effects in a consistent way across studies. 


# Select for 'tcga' in the studyID ----
selection <- list(str_detect(studies$studyId, 'tcga'))
studies$studyId

sum(studies$referenceGenome == 'hg38')

# Doesn't seem possible to get MAF from cBioportal - data created from MAFs



# # TCGAbiolinks access - for GDC, so nvm ########
# library(BiocManager)
# library(TCGAbiolinks)
# library(dplyr)
# library(DT)
# 
# browseVignettes("TCGAbiolinks")
