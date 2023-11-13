#!/usr/local/bin/python3

import requests
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from IVM_functions import IVM_functions

################################
# Starting Variables
console_url = 'Console IP:3780'
base64_cred = 'Base64 encode'
resource = 'sites'
new_engine_id = 'some number'

################################
# Getting all old site info
sites = IVM_functions.get_stuff(onsole_url, base64_cred, resource)
ids = []
for site in sites['resources']:
  ids.append((site['id']))


for id_num in ids:
	site = IVM_functions.get_stuff(console_url, base64_cred, resource+"/"+str(id_num))
	name = site['name']
	s_type = site['type']

	if s_type != "agent" and 'External' not in site['name']:
		IVM_functions.put_stuff(console_url, base64_cred, resource+"/"+str(new_site_id)+"/scan_engine", new_engine_id)
