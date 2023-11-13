#!/usr/local/bin/python3

import requests
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

old_console_url = "Console IP:3780"
new_console_url = "Console IP:3780"
base64_cred = "Base64 of creds"
resource = "tags"


################################
# Variables for Old Environment
old_url = "https://"+old_console_url+"/api/3/"+resource
payload={}
headers = {
  'Accept': 'application/json;charset=UTF-8',
  'Authorization': 'Basic '+base64_cred
}

################################
# Getting all old asset groups
old_response = requests.request("GET", old_url, headers=headers, data=payload, verify=False)
old_json_text = old_response.text
old_parsed = json.loads(old_json_text)


################################
# Variables for New Environment
new_url = "https://"+new_console_url+"/api/3/"+resource

################################
# Getting all new asset groups
new_response = requests.request("GET", new_url, headers=headers, data=payload, verify=False)
new_json_text = new_response.text
new_parsed = json.loads(new_json_text)

################################
# Making a list of all new tags
new_thing_searchCriteria = []
for new_ids in new_parsed['resources']:
  new_thing_source = new_ids['source']
  if new_thing_source == 'custom' and 'searchCriteria' in new_ids:
    new_thing_searchCriteria.append((new_ids['searchCriteria']))


################################
# Check if old search criteria exists in new search criteria
for old_info in old_parsed['resources']:
  old_thing_source = (old_info['source'])
  if old_thing_source == 'custom' and 'searchCriteria' in new_ids:
    old_thing_searchCriteria =(old_info['searchCriteria'])
    old_thing_name = (old_info['name'])
    old_thing_type = (old_info['type'])
    old_thing_color = (old_info['color'])

    if old_thing_searchCriteria in new_thing_searchCriteria:
      print(resource+":"+old_thing_name+" Already Exists")
    elif old_thing_searchCriteria not in new_thing_searchCriteria:
      new_payload = json.dumps({
        "color": old_thing_color,
        "source": "custom",
        "name": old_thing_name,
        "type": old_thing_type,
        "searchCriteria": old_thing_searchCriteria
      })
      headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json;charset=UTF-8',
        'Authorization': 'Basic '+base64_cred
      }
      put_response = requests.request("POST", new_url, headers=headers, data=new_payload, verify=False)
      print(resource+":"+old_thing_name+" copied to new console")
      
