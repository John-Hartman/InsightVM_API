#!/usr/local/bin/python3

import requests
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

old_console_url = "Console IP:3780"
new_console_url = "Console IP:3780"
base64_cred = "Base 64 of credentials"
new_password = "R@pid7!"



################################
# Variables for Old Environment
old_url = "https://"+old_console_url+"/api/3/users"
payload={}
headers = {
  'Accept': 'application/json;charset=UTF-8',
  'Authorization': 'Basic '+base64_cred
}

################################
# Getting all old User info
old_response = requests.request("GET", old_url, headers=headers, data=payload, verify=False)
old_json_text = old_response.text
old_parsed = json.loads(old_json_text)


################################
# Variables for New Environment
new_url = "https://"+new_console_url+"/api/3/users"

################################
# Getting all new User info
new_response = requests.request("GET", new_url, headers=headers, data=payload, verify=False)
new_json_text = new_response.text
new_parsed = json.loads(new_json_text)



################################
# Making a list of all old user IDs
old_user_ids = []
for old_info in old_parsed['resources']:
	old_user_ids.append((old_info['id']))

################################
# Making a list of all new user names
new_user_names = []
for new_names in new_parsed['resources']:
	new_user_names.append((new_names['name']))


################################
# Starting logic, for each UID go get the user info
for old_uid in old_user_ids:
	old_user_url = old_url+"/"+str(old_uid)

	old_user_response = requests.request("GET", old_user_url, headers=headers, data=payload, verify=False)
	old_user_json_text = old_user_response.text
	old_user_parsed = json.loads(old_user_json_text)
	################################
	# Create variable for the old users name, login, and email
	old_user_name=old_user_parsed['name']
	old_user_login=old_user_parsed['login']
	old_user_email=old_user_parsed['email']
	
	################################
	# Check if the username on the old console exists in the lists of usernames in the new console
	# if it already exists, skip to the next one, if it does not exist, copy it over
	if old_user_name in new_user_names:
		print("Username:"+old_user_name+" Already Exists")
	elif old_user_name not in new_user_names:
		new_payload = json.dumps({
			"login": old_user_login,
  		"name": old_user_name,
  		"email": old_user_email,
  		"password": new_password,
  		"passwordResetOnLogin": True,
  		"role": {
        "allAssetGroups": True,
        "allSites": True,
        "id": "global-admin",
        "name": "Global Administrator"
      }
		})
		headers = {
			'Content-Type': 'application/json',
			'Accept': 'application/json;charset=UTF-8',
			'Authorization': 'Basic '+base64_cred
		}
		put_response = requests.request("POST", new_url, headers=headers, data=new_payload, verify=False)
		print("Username:"+old_user_name+" copied to new console")
