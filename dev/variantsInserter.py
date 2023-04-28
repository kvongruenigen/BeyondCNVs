#!/usr/local/bin/python3

# Import modules

import re, json, yaml # web modules
from os import path, environ, pardir # OS module
import sys, datetime # just for time

# bycon is supposed to be in the same parent directory
dir_path = path.dirname( path.abspath(__file__) )
pkg_path = path.join( dir_path, pardir )
parent_path = path.join( pkg_path, pardir )
sys.path.append( parent_path )

from bycon import * # import everything from bycon module

"""
"""

################################################################################
################################################################################
################################################################################

def main():

    variantsInserter()

################################################################################

def variantsInserter():

    initialize_bycon_service(byc)
    parse_variant_parameters(byc)

    if byc["args"].datasetIds:
        byc["dataset_ids"] = re.split(",", byc["args"].datasetIds)

    if len(byc["dataset_ids"]) != 1:
        print("No single existing dataset was provided with -d ...")
        exit()

    ds_id = byc["dataset_ids"][0]

    if not byc["args"].inputfile:
        print("No input file file specified (-i, --inputfile) => quitting ...")
        exit()

    inputfile = byc["args"].inputfile
    variants, fieldnames = read_tsv_to_dictlist(inputfile, int(byc["args"].limit))

    var_no = len(variants)
    up_v_no = 0

    print("=> The variants file contains {} samples".format(var_no))

    mongo_client = MongoClient( )
    var_coll = MongoClient( )[ ds_id ][ "variants" ]

    for c, v in enumerate(variants):

        bs_id = v.get("biosample_id", False)
        if not bs_id:
            print("¡¡¡ The `biosample_id` parameter is required for variant assignment !!!")
            exit()
        if not "pgxbs-" in bs_id:
            print("¡¡¡ The `biosample_id` parameter has to start with 'pgxbs-' !!!")
            exit()

        n = str(c+1)
 
        # TODO: This is a bit of a double definition; disentangle ...
        update_v = {
            "legacy_id": v.get("variant_id", "pgxvar-"+n),
            "biosample_id": bs_id,            
            "callset_id": v.get("callset_id", re.sub("pgxbs-", "pgxcs-", bs_id)),
            "individual_id": v.get("individual_id", re.sub("pgxbs-", "pgxind-", bs_id))
        }

        update_v = import_datatable_dict_line(byc, update_v, fieldnames, v, "variant")
        update_v.update({
            "variant_internal_id": variant_create_digest(update_v, byc),
            "updated": datetime.datetime.now().isoformat()
        })

        if not byc["test_mode"]:
            vid = var_coll.insert_one( update_v  ).inserted_id
            vstr = 'pgxvar-'+str(vid)
            var_coll.update_one({'_id':vid},{'$set':{ 'id':vstr }})
            print("=> inserted {}".format(vstr))
        else:
            prjsonnice(update_v)

        prjsonnice(update_v)


    exit()

################################################################################
################################################################################
################################################################################

if __name__ == '__main__':
    main()
