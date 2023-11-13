#!/usr/local/bin/python3

import requests
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from IVM_functions import IVM_functions

################################
# Starting Variables
old_console_url = 'console IP:3780'
new_console_url = 'console IP:3780'
base64_cred = 'base 64'


new_console_sites = IVM_functions.get_stuff(new_console_url, base64_cred, "sites")
new_sites = new_console_sites['resources']


old_reports = IVM_functions.get_stuff(old_console_url, base64_cred, "reports")
report_ids= []
for report in old_reports['resources']:
	report_ids.append(report['id'])

for report_id in report_ids:
	this_report = IVM_functions.get_stuff(old_console_url, base64_cred, "reports/"+str(report_id))
	del this_report['id']
	del this_report['links']
	scope = this_report['scope']
	new_ids = []
	for site_id in scope['sites']:
		site_info = IVM_functions.get_stuff(old_console_url, base64_cred, "sites/"+str(site_id))
		for new_site in new_sites:
			if new_site['name'] == site_info['name']:
				new_ids.append(new_site['id'])
	this_report['scope']['sites'] = new_ids
	IVM_functions.post_stuff(new_console_url, base64_cred, "reports", json.dumps(this_report))
