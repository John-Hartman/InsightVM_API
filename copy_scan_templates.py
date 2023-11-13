#!/usr/local/bin/python3

import requests
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

old_console_url = "Console IP:3780"
new_console_url = "Console IP:3780"
base64_cred = "Base64 encode"


################################
# Variables for Old Environment
old_url = "https://"+old_console_url+"/api/3/scan_templates"
payload={}
headers = {
  'Accept': 'application/json;charset=UTF-8',
  'Authorization': 'Basic '+base64_cred
}

################################
# Getting all old scan templates
old_response = requests.request("GET", old_url, headers=headers, data=payload, verify=False)
old_json_text = old_response.text
old_parsed = json.loads(old_json_text)


################################
# Variables for New Environment
new_url = "https://"+new_console_url+"/api/3/scan_templates"

################################
# Getting all new scan templates
new_response = requests.request("GET", new_url, headers=headers, data=payload, verify=False)
new_json_text = new_response.text
new_parsed = json.loads(new_json_text)


################################
# Making a list of all new scan template ids
new_scan_ids = []
for new_ids in new_parsed['resources']:
	new_scan_ids.append((new_ids['id']))

################################
# Check if old ID exists in New ID list
for old_info in old_parsed['resources']:
	old_scan_ids =(old_info['id'])

	if old_scan_ids in new_scan_ids:
		print("Scan Template:"+old_scan_ids+" Already Exists")
	elif old_scan_ids not in new_scan_ids:
		new_payload = json.dumps(old_info)
		headers = {
			'Content-Type': 'application/json',
			'Accept': 'application/json;charset=UTF-8',
			'Authorization': 'Basic '+base64_cred
		}
		put_response = requests.request("POST", new_url, headers=headers, data=new_payload, verify=False)
		print("Scan Template:"+old_scan_ids+" copied to new console")
