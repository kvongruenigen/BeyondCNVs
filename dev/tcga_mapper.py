#!/usr/local/bin/python3

from pymongo import MongoClient
import json
import re
import json
import argparse
from os import path

################################################################################

def _get_args():

    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--datasetid", help="dataset, usually progenetix")
    parser.add_argument('-t', '--tcgafile', help='TCGA json data file')
    parser.add_argument('-i', '--idfile', help='idfile')
    parser.add_argument('-u', '--update', help='update modus')

    return parser.parse_args()

################################################################################

def main():

	args = _get_args()

	update_TCGA_data(args)

################################################################################

def update_TCGA_data(args):

	if not args.datasetid:
		print("no datasetid was specified with -d")
		exit()

	if not args.idfile:
		print("no id file was specified with -i")
		exit()

	if not args.tcgafile:
		print("no tcga file was specified with -t")
		exit()

	if not args.update:
		print('no update will be performed - activate with "-u 1"')

	mongo_client = MongoClient()
	data_db = mongo_client[args.datasetid]
	bios_coll = data_db["biosamples"]
	ind_coll = data_db["individuals"]

	f = open(args.idfile, 'r+')
	id_lines = [line for line in f.readlines()]
	f.close()

	tcga_ids = {}

	for id_l in id_lines:
		id_l = id_l.rstrip()
		sample_id, case_id, submitter_id = re.split("\t", id_l)
		tcga_ids.update({sample_id:{"sample_id": sample_id, "case_id": case_id, "submitter_id": submitter_id }})

	with open(args.tcgafile, 'r') as c_f:
		c = c_f.read()
		c_l = json.loads(c)

	tcga_clin = {}

	for tcga_c in c_l:
		tcga_clin.update({ tcga_c["case_id"]: tcga_c })

	for s_id, s_id_o in tcga_ids.items():

		s = bios_coll.find_one({"info.legacy_id": s_id })
		if not s:
			print('!!! no biosample for "{}"'.format(s_id))
			continue

		c_id = s_id_o["case_id"]

		if not c_id in tcga_clin:
			print('!!! no tcga data for case_id "{}"'.format(c_id))
			continue

		clin = tcga_clin[c_id]

		bios_update = {
			"external_references": [],
			"info": s.get("info", {})     # <=== important!
		}

		# references
		# first collecting all "non-TCGA ones" for keeping, then adding the new TCGA ones
		for pgx_e_r in s["external_references"]:
			if "TCGA" in pgx_e_r["label"]:
				if not "project" in pgx_e_r["label"]:
					# skipping previous TCGA labels _except_ the TCGA-XXX for projects
					continue
			pgx_e_r.pop("description", None)
			bios_update["external_references"].append(pgx_e_r)

			for id_t in s_id_o.keys():
				n_id = s_id_o[id_t]
				if not "TCGA-" in n_id:
					n_id = "TCGA-"+s_id_o[id_t]
				id_obj = { "id": n_id, "label": "TCGA "+id_t }
				bios_update["external_references"].append(id_obj)

		# clinical
		f_u_s = clin["demographic"].get("vital_status", "").lower()
		if "dead" in f_u_s:
			bios_update.update({"followup_state":{"id":"EFO:0030049", "label":"dead (follow-up status)"}})
			bios_update["info"].update({"survival_status":"dead"})
		elif "alive" in f_u_s:
			bios_update.update({"followup_state":{"id":"EFO:0030041", "label":"alive (follow-up status)"}})
			bios_update["info"].update({"survival_status":"alive"})
        #Ziying update => since ["demographic"]["days_to_death"] should be correct for dead samples
        if clin["demographic"]["days_to_death"]:
            f_u_d = clin["demographic"]["days_to_death"]
        else:
            f_u_d = clin["diagnoses"][0]["days_to_last_follow_up"]
		#f_u_d = clin["diagnoses"][0]["days_to_last_follow_up"]
		if isinstance(f_u_d, int):
			f_u_m = round(f_u_d/30.5)
			bios_update["info"].update({"followup_months":f_u_m})

		a_d = clin["diagnoses"][0]["age_at_diagnosis"]
		if isinstance(a_d, int):
			a = _d2iso(a_d)
			bios_update.update({"individual_age_at_collection":"{}".format(a)})

		if args.update:
			bios_coll.update_one({"_id": s["_id"] }, { '$set': bios_update } )
		else:
			print(bios_update)

		########################################################################
		# individuals
		########################################################################

		i = ind_coll.find_one({"id": s["individual_id"] })
		if not s:
			print('!!! no individual for "{}"'.format(s["individual_id"]))
			continue

		ind_update = {
			"external_references": [],
			"info": i.get("info", {}),
		}

		# references
		for pgx_e_r in s["external_references"]:
			if "TCGA" in pgx_e_r["label"]:
				if "biosample" in pgx_e_r["label"]:
					continue
				if "TCGA collection" in pgx_e_r["label"]:
					continue
			pgx_e_r.pop("description", None)
			bios_update["external_references"].append(pgx_e_r)
			ind_update["external_references"].append(pgx_e_r)

			for id_t in s_id_o.keys():
				id_obj = { "id": "TCGA-"+s_id_o[id_t], "label": "TCGA "+id_t }
				bios_update["external_references"].append(id_obj)
				ind_update["external_references"].append(id_obj)

		sex = clin["demographic"].get("gender", "")
		if "female" in sex:
			ind_update.update({"sex":{"id":"PATO:0020002", "label":"female genotypic sex"}})
		elif "male" in sex:
			ind_update.update({"sex":{"id":"PATO:0020001", "label":"male genotypic sex"}})

		if args.update:
			ind_coll.update_one({"_id": i["_id"] }, { '$set': ind_update } )
		else:
			print(ind_update)

################################################################################

def _d2iso(d):

	y = int(d / 365.25)
	m = int((d % 365.25) / 30.5)
	d = int(d - (y * 365.25 + m * 30.5))

	return "P{}Y{}M{}D".format(y,m,d)

################################################################################
################################################################################

if __name__ == '__main__':
    main(  )
