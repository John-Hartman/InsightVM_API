import requests
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import logger_utility
from logger import Logger

# Starting the logger
logger_utility.setup_logging()
logger = Logger().logger

class IVM_functions:

	def get_stuff(console_url, creds, resource):
		url = "https://"+console_url+"/api/3/"+resource+"?size=500"
		payload={}
		headers = {
		  'Accept': 'application/json;charset=UTF-8',
		  'Authorization': 'Basic '+creds
		}

		################################
		# Getting all old asset groups
		response = requests.request("GET", url, headers=headers, data=payload, verify=False)
		json_text = response.text
		parsed = json.loads(json_text)
		return parsed

	def post_stuff(console_url, creds, resource, in_payload):
		url = "https://"+console_url+"/api/3/"+resource
		payload= in_payload
		headers = {
		  'Content-Type': 'application/json',
		  'Accept': 'application/json;charset=UTF-8',
		  'Authorization': 'Basic '+creds
		}
		response = requests.request("POST", url, headers=headers, data=payload, verify=False)
		json_text = response.text
		parsed = json.loads(json_text)
		if response.status_code == 201:
			id_num = parsed['id']
			return id_num
		else:
			err_msg = response.text
			this_stuff = json.loads(err_msg)
			msg = (f"ERROR {response.status_code} - {this_stuff['message']}")
			return msg

	def put_stuff(console_url, creds, resource, in_payload):
		url = "https://"+console_url+"/api/3/"+resource
		payload= in_payload
		headers = {
		  'Content-Type': 'application/json',
		  'Accept': 'application/json;charset=UTF-8',
		  'Authorization': 'Basic '+creds
		}
		response = requests.request("PUT", url, headers=headers, data=payload, verify=False)
		json_text = response.text
		parsed = json.loads(json_text)
		return parsed

	## This can be used for Included asset groups OR excluded asset groups by swapping out the resource
	def copy_asset_groups_from_old_to_new(response, resource, new_console_url, base64_cred, new_site_id, new_site_name):
		if len(response['resources']) == 0:
			logger.info(f"{new_site_name} has no {resource}")
		elif len(response['resources']) > 0:
			logger.info(f"{new_site_name} has {resource}")
			for ag in response['resources']:
				ag_id = ag['id']
				ag_name = ag['name']
				ag_type = ag['type']
				if ag_type == 'dynamic':
					ag_search_cri = ag['searchCriteria']
					new_ag_search_cri = []
					new_ag = IVM_functions.get_stuff(new_console_url, base64_cred, 'asset_groups')
					for ag_n in new_ag['resources']:
						ag_n_type = ag_n['type']
						if ag_n_type == 'dynamic':
							new_ag_search_cri.append(ag_n['searchCriteria'])

					if ag_search_cri not in new_ag_search_cri:
						logger.info(f"Asset Group: {ag_name} does not exist yet on the new console")
						ag_payload = json.dumps({
							"name": ag_name,
							"type": ag_type,
							"searchCriteria": ag_search_cri
						})
						post_ag = IVM_functions.post_stuff(new_console_url, base64_cred, 'asset_groups', ag_payload)
						logger.info(f"Asset Group: {ag_name} created on the new console with new ag_id: {post_ag}")
						json_ag = json.dumps([post_ag])
						put_ag = IVM_functions.put_stuff(new_console_url, base64_cred, "sites/"+str(new_site_id)+"/"+resource, json_ag)
						logger.info(f"Asset Group: {ag_name} added as {resource} in Site: {new_site_name} on the new console")
						logger.info(" ")
					elif ag_search_cri in new_ag_search_cri:
						logger.info(f"Asset Group: {ag_name} already exists on the new console")
						for ag_n in new_ag['resources']:
							ag_n_type = ag_n['type']
							if ag_n_type == 'dynamic':
								if ag_n['searchCriteria'] == ag_search_cri:
									new_ag_id = ag_n['id']
									new_ag_name = ag_n['name']
									logger.info(f"Asset Group: {ag_name} from the old console was found on the new console as Asset Group: {new_ag_name} with an id of ag_id: {new_ag_id}")
									json_ag = json.dumps([new_ag_id])
									put_ag = IVM_functions.put_stuff(new_console_url, base64_cred, "sites/"+str(new_site_id)+"/"+resource, json_ag)
									logger.info(f"Asset Group: {new_ag_name} added as {resource} in new Site: {new_site_name} on the new console")
	
	# This function is to take a ton of old sites from an existing console and recreate them as asset groups on a new console while also aggregating them to a new site based on the scopes
	# This requires the new sites to be staged on the new console and pass in the new site id
	def aggregate(old_site_ids, new_site_id, old_console_url, new_console_url, base64_cred):
		agg_scope = []
		full_scope = []
		for id_num in old_site_ids:
			site = IVM_functions.get_stuff(old_console_url, base64_cred, f"sites/{id_num}")
			name = site['name']
			s_type = site['type']
			ic_response = IVM_functions.get_stuff(old_console_url, base64_cred, "sites/"+str(id_num)+"/included_targets")
			#appending the scopes to the full list of scopes that will be PUT into the staged sites
			agg_scope.append(ic_response['addresses'])

			#Setting up the payload to create the new asset group
			filters = []
			for scope in ic_response['addresses']:
				if " - " in scope:
					upper, lower = scope.split(' - ')
					ag_filter = {
								"field": "ip-address",
								"operator": "in-range",
								"lower": upper,
								"upper": lower
								}
					filters.append(ag_filter)
				else:
					ag_filter = {
								"field": "ip-address",
								"operator": "is",
								"value": scope
								}
					filters.append(ag_filter)
			ag_payload = json.dumps({
				"name": name,
				"type": "dynamic",
				"description": "Created from site on Danaher Console",
				"searchCriteria": {
					"match": "all",
					"filters": filters
				},
			})
			#IVM_functions.post_stuff(new_console_url, base64_cred, "asset_groups", ag_payload)
			#logger.info(f"Created Asset group called {name} on new console from Site: {name} on old console")

		for address in agg_scope:
			for item in address:
				full_scope.append(item)
		put_scope = IVM_functions.put_stuff(new_console_url, base64_cred, f"sites/{new_site_id}/included_targets", json.dumps(full_scope))
		logger.info(f"Updated included targets on staged site for site id: {new_site_id}")	
							


