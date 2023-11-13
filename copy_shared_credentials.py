#!/usr/local/bin/python3

import requests
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

old_console_url = 'Console IP:3780'
new_console_url = 'Console IP:3780'
base64_cred = 'Base 64 of credentials'
resource = 'shared_credentials'

################################
# Variables for Old Environment
old_url = "https://"+old_console_url+"/api/3/"+resource
payload={}
headers = {
  'Accept': 'application/json;charset=UTF-8',
  'Authorization': 'Basic '+base64_cred
}

################################
# Getting all old shared credentials
old_response = requests.request("GET", old_url, headers=headers, data=payload, verify=False)
old_json_text = old_response.text
old_parsed = json.loads(old_json_text)


################################
# Variables for New Environment
new_url = "https://"+new_console_url+"/api/3/"+resource

################################
# Making a list of all old user IDs
old_creds_ids = []
for old_info in old_parsed['resources']:
  old_creds_ids.append((old_info['id']))


################################
# Starting logic, for each UID go get the user info
for old_uid in old_creds_ids:
  old_creds_url = old_url+"/"+str(old_uid)

  old_creds_response = requests.request("GET", old_creds_url, headers=headers, data=payload, verify=False)
  old_creds_json_text = old_creds_response.text
  old_creds_parsed = json.loads(old_creds_json_text)
  ################################
  # Create variable for the old users name, login, and email
  old_creds_account=old_creds_parsed['account']
  old_creds_name=old_creds_parsed['name']
  old_creds_assignment=old_creds_parsed['siteAssignment']

  new_payload = json.dumps({
    "account": old_creds_account,
    "name": old_creds_name,
    "siteAssignment": old_creds_assignment
  })
  headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json;charset=UTF-8',
    'Authorization': 'Basic '+base64_cred
  }
  put_response = requests.request("POST", new_url, headers=headers, data=new_payload, verify=False)
  print(resource+":"+old_creds_name+" copied to new console")
