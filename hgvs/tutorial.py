import hgvs.parser

# start with these variants as strings
hgvs_g = 'NC_000007.13:g.36561662C>T'
hgvs_c = 'NM_001637.3:c.1582G>A'

# parse the genomic variant into a Python structure
hp = hgvs.parser.Parser()
var_g = hp.parse_hgvs_variant(hgvs_g)
var_g
SequenceVariant(ac=NC_000007.13, type=g, posedit=36561662C>T, gene=None)

# SequenceVariants are composed of structured objects, e.g.,
var_g.posedit.pos.start
SimplePosition(base=36561662, uncertain=False)

# format by stringification
str(var_g)

#'NC_000007.13:g.36561662C>T'