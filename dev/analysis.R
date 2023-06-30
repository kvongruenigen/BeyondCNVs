rm(list = ls())

library(tidyverse)
library(ggplot2)
df <- read_csv("Projects/BeyondCNVs/data/analysis_df.csv", 
               col_types = cols(...1 = col_skip()))

# cols.num <- colnames(df)
# df[cols.num] <- sapply(df[cols.num], as.factor)
df <- as.data.frame(unclass(df),                     # Convert all columns to factor
                       stringsAsFactors = TRUE)
summary(df)

ggplot(df, aes(followup_state_label))+
  geom_histogram()
