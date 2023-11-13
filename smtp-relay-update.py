#!/usr/local/bin/python3

import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

################################
# Specific Variables to your console and desired outcome
console_url = "Console IP:3780"
base64_cred = "Base 64 of credentials"
current_server_value = "1.2.3.4"
new_server_value = "2.3.4.5"

################################
# Initial API call to get all Site IDs
sites_url = "https://"+console_url+"/api/3/sites"
payload={}
headers = {
  'Accept': 'application/json;charset=UTF-8',
  'Authorization': 'Basic '+base64_cred
}
sites_response = requests.request("GET", sites_url, headers=headers, data=payload, verify=False)
json_text = sites_response.text
parsed = json.loads(json_text)

################################
# Takes the Site IDs and puts them into a list to iterate through in the next step
site_ids = []
for ids in parsed['resources']:
	site_ids.append((ids['id']))

################################
# Iterates through each ID and pulls the Alerts configured
for sid in site_ids:
	smtp_url = "https://"+console_url+"/api/3/sites/"+str(sid)+"/alerts/smtp"
	smtp_payload={}
	smtp_headers = {
  	  'Accept': 'application/json;charset=UTF-8',
  	  'Authorization': 'Basic '+base64_cred
	}
	smtp_response = requests.request("GET", smtp_url, headers=smtp_headers, data=smtp_payload, verify=False)
	smtp_text = smtp_response.text
	smtp_json = json.loads(smtp_text)

		
	################################
	# Looks at the JSON output and only moves forward if there is an alert configured for the site
	if not len(smtp_json['resources']) == 0:
		################################
		# Replaces the current SMTP Relay Server value with the new value
		for alert in smtp_json['resources']:
			alert['relayServer'] = alert['relayServer'].replace(current_server_value, new_server_value)

			################################
			# Puts the updated alert into a new variable
			smtp_payload = json.dumps(smtp_json['resources'])
			smtp_put_headers = {
  			'Content-Type': 'application/json',
  			'Accept': 'application/json;charset=UTF-8',
  			'Authorization': 'Basic '+base64_cred
			}

			################################
			# Final PUT API call to update the site with new values
			smtp_put_response = requests.request("PUT", smtp_url, headers=smtp_put_headers, data=smtp_payload, verify=False)
			print(smtp_put_response.text)
			
		


