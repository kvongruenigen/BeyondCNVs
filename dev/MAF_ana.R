rm(list = ls())

# Import needs deletion of the first commented line in the .maf file. 
# Write python script for it?
# Do I want the .maf in R?
dd <- read_table("Programming/Project/data/0b92bd19-e3d4-40dd-bd53-3af901298d8f.wxs.aliquot_ensemble_masked.maf")

head(dd)

dd$Chromosome <- as.factor(dd$Chromosome)
plot(dd$Chromosome)
