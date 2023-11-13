#!/usr/local/bin/python3

import requests
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from IVM_functions import IVM_functions
import logger_utility
from logger import Logger


################################
# Starting the logger
logger_utility.setup_logging()
logger = Logger().logger


################################
# Starting Variables
old_console_url = '<host>:3780'
new_console_url = '<host>:3780'
base64_cred = 'base64 of creds'
resource = 'sites'


################################
# Get shared credentials and stuff
new_cred_names = []
new_creds = IVM_functions.get_stuff(new_console_url, base64_cred, "shared_credentials")
for ncred in new_creds['resources']:
  new_cred_names.append(ncred['name'])
shared_creds = IVM_functions.get_stuff(old_console_url, base64_cred, "shared_credentials")
for cred in shared_creds['resources']:
  del cred['id']
  del cred['links']
  account = cred['account']
  if cred['name'] not in new_cred_names and account['service'] not in ['scan-assistant' ,'ssh-key']:
    post_creds = IVM_functions.post_stuff(new_console_url, base64_cred, "shared_credentials", json.dumps(cred))
    logger.info(f"Copied {cred['name']} to new console")


################################
# Copy remaining scan templates so we don't get an error on the next step
old_scan_templates = IVM_functions.get_stuff(old_console_url, base64_cred, "scan_templates")
new_scan_templates = IVM_functions.get_stuff(new_console_url, base64_cred, "scan_templates")
new_st_ids = []
for new_template in new_scan_templates['resources']:
    new_st_ids.append(new_template['id'])
for template in old_scan_templates['resources']:
    if template['id'] not in new_st_ids:
        IVM_functions.post_stuff(new_console_url, base64_cred, "scan_templates", json.dumps(template))
        logger.info(f"Copied {template['name']} to new console")
        

################################
# Getting all old site info
sites = IVM_functions.get_stuff(old_console_url, base64_cred, resource)
page = sites['page']
total = page['totalResources']
logger.info(f"{total} sites found on the old console")



################################
# Getting all new site info
new_sites = IVM_functions.get_stuff(new_console_url, base64_cred, resource)
site_names = []
for site in new_sites['resources']:
  site_names.append(site['name'])


################################
# loading the site ids into a list
ids = []
for site in sites['resources']:
  ids.append((site['id']))

################################
# doing a call to each site for each id
for id_num in ids:
  site = IVM_functions.get_stuff(old_console_url, base64_cred, resource+"/"+str(id_num))
  name = site['name']
  s_type = site['type']
  ic_response = IVM_functions.get_stuff(old_console_url, base64_cred, resource+"/"+str(id_num)+"/included_targets")
  payload = json.dumps({
    "name": name,
    "scan": {
      "assets": {
        "includedTargets": ic_response
      }
    }
  })


  #if s_type != "agent" and name not in site_names:   ########### uncomment this for actual use
  if id_num == 12:   ##### this is only here to filter scope down for testing, will need removed
      new_site_id = IVM_functions.post_stuff(new_console_url, base64_cred, resource, payload)
      if isinstance(new_site_id, int):
        logger.info(f"Copied site: {name} to new console with new site_id: {id_num}")
        ################################
        # Getting the included asset groups from the old console and posting to the new console then assigning to site on new console
        ic_ag = IVM_functions.get_stuff(old_console_url, base64_cred, resource+"/"+str(id_num)+"/included_asset_groups")
        IVM_functions.copy_asset_groups_from_old_to_new(ic_ag, "included_asset_groups", new_console_url, base64_cred, new_site_id, name)
        

        ################################
        # Getting the excluded asset groups from the old console and posting to the new console then assigning to site on new console    
        ex_ag = IVM_functions.get_stuff(old_console_url, base64_cred, resource+"/"+str(id_num)+"/excluded_asset_groups")
        IVM_functions.copy_asset_groups_from_old_to_new(ex_ag, "excluded_asset_groups", new_console_url, base64_cred, new_site_id, name)


        ################################
        # Getting the excluded targets and posting to new site
        ex_targs = IVM_functions.get_stuff(old_console_url, base64_cred, resource+"/"+str(id_num)+"/excluded_targets")
        if len(ex_targs) == 0:
          logger.info(f"Site: {name} has no excluded targets")
        elif len(ex_targs) > 0:
          logger.info(f"Site: {name} has excluded targets")
          ex_payload = json.dumps(
          ex_targs['addresses']
          )
          IVM_functions.put_stuff(new_console_url, base64_cred, resource+"/"+str(new_site_id)+"/excluded_targets", ex_payload)
          logger.info(f"Added excluded targets to new site: {name}")
          
        

        #won't be able to do anything about scan engines, needs to be done manually

        ################################
        # Get scan templates and stuff
        scan_template = IVM_functions.get_stuff(old_console_url, base64_cred, resource+"/"+str(id_num)+"/scan_template")
        if len(scan_template) == 0:
          logger.info(f"Site: {name} does not have an assigned scan template")
        elif len(scan_template) > 0:
          logger.info(f"Site: {name} has an assigned scan template of {scan_template['name']}")
          new_templates = IVM_functions.get_stuff(new_console_url, base64_cred, "scan_templates")
          template_ids = []
          for template in new_templates['resources']:
            template_ids.append(template['id'])
          if scan_template['id'] in template_ids:
            logger.info(f"{scan_template['name']} already exists on the new console")
            put_st = IVM_functions.put_stuff(new_console_url, base64_cred, resource+"/"+str(new_site_id)+"/scan_template", scan_template['id'])
            logger.info(f"{scan_template['name']} assigned to the new site: {name}")
          elif scan_template['id'] not in template_ids:
            logger.info(f"{scan_template['name']} does not exist on the new console")
            post_st = IVM_functions.post_stuff(new_console_url, base64_cred, "scan_templates", json.dumps(scan_template))
            logger.info(f"Created template {scan_template['name']} on the new console")
            put_st = IVM_functions.put_stuff(new_console_url, base64_cred, resource+"/"+str(new_site_id)+"/scan_template", post_st)
            logger.info(f"{scan_template['name']} assigned to the new site: {name}")



        ################################
        # Get scan schedules and stuff
        scan_schedules = IVM_functions.get_stuff(old_console_url, base64_cred, resource+"/"+str(id_num)+"/scan_schedules")
        if len(scan_schedules) == 0:
          logger.info(f"Site: {name} does not have scheduled scans")
        elif len(scan_schedules) > 0:
          logger.info(f"Site: {name} has scheduled scans")
          for scan_schedule in scan_schedules['resources']:
            del scan_schedule['links']
            del scan_schedule['nextRuntimes']
            del scan_schedule['id']
            post_schedules = IVM_functions.post_stuff(new_console_url, base64_cred, resource+"/"+str(new_site_id)+"/scan_schedules", json.dumps(scan_schedule))
            logger.info(f"{scan_schedule['scanName']} added as scheduled scans to the new site: {name}")
              
        

       
        ################################
        # Get site creds and stuff
        site_creds = IVM_functions.get_stuff(old_console_url, base64_cred, resource+"/"+str(id_num)+"/site_credentials")
        if len(site_creds) == 0:
          logger.info(f"Site: {name} does not have site specific credentials")
        elif len(site_creds) > 0:
          logger.info(f"Site: {name} has site specific credentials")
          for cred in site_creds['resources']:
            del cred['id']
            del cred['links']
            account = cred['account']
            if account['service'] != 'scan-assistant':
              post_creds = IVM_functions.post_stuff(new_console_url, base64_cred, resource+"/"+str(new_site_id)+"/site_credentials", json.dumps(cred))
              logger.info(f"{cred['name']}copied to the new site: {name}")


        ################################
        # Get site tags and stuff
        site_tags = IVM_functions.get_stuff(old_console_url, base64_cred, resource+"/"+str(id_num)+"/tags")
        if len(site_tags) == 0:
          logger.info(f"Site: {name} does not have site specific tags")
        elif len(site_tags) > 0:
          logger.info(f"Site: {name} has site specific tags")
          for tag in site_tags['resources']:
            del tag['id']
            del tag['links']
            del tag['created']
            post_tag = IVM_functions.put_stuff(new_console_url, base64_cred, resource+"/"+str(new_site_id)+"/tags", json.dumps(tag))
            logger.info(f"{tag['name']} copied to the new site: {name}")


      else:
        logger.error(f"{name} ran into an issue: {new_site_id}")
      

      
