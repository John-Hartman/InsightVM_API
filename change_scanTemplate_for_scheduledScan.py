#!/usr/local/bin/python3

import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from IVM_functions import IVM_functions

console_url = "console IP:3780"
base64_cred = "base64 creds"
current_template_value = 'example_1'
new_template_value = 'example_2'

# Get all site ids
sites = IVM_functions.get_stuff(console_url, base64_cred, 'sites')
################################
# loading the site ids into a list
site_ids = []
for site in sites['resources']:
  site_ids.append((site['id']))


# for all site ids, get scheduled scans ids
for site_id in site_ids:
	scan_schedules = IVM_functions.get_stuff(console_url, base64_cred, 'sites'+str(site_id)+'scan_schedules')
	scan_ids = []
	for scan_schedule in scan_schedules['resources']:
		template_id = scan_schedule['scanTemplateId']
		if template_id == current_template_value:
			scan_ids.append(scan_schedule['id'])


	#for each scheduled scan id, change scan template id
	for scan_id in scan_ids:
		old_sched = IVM_functions.get_stuff(console_url, base64_cred, 'sites'+str(site_id)+'scan_schedules/'+str(scan_id))
		old_sched['scanTemplateId'] = old_sched['scanTemplateId'].replace(current_template_value, new_template_value)
		del old_sched['links']
		del old_sched['nextRuntimes']
		IVM_functions.put_stuff(console_url, base64_cred, 'sites'+str(site_id)+'scan_schedules/'+str(scan_id), json.dumps(old_sched))
