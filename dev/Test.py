import os

print(os.getcwd())

import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

# Check if the TCGAutils package is installed
if not robjects.packages.isinstalled('TCGAutils'):
    # Install the package if not found
    utils = importr('utils')
    utils.install_packages('TCGAutils')

# Load the TCGAutils package
TCGAutils = importr('TCGAutils')