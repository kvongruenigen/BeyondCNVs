library(tidyverse)
library(ggplot2)

maf_data <- read_csv("Projects/BeyondCNVs/data/varImport.tsv")
maf_data$Chromosome <- as.factor(maf_data$Chromosome)

summary(maf_data)
