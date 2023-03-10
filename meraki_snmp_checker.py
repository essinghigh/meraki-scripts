"""
Cisco Merkai SNMP configuration validator:
Checks through all Cisco Meraki networks in the specified org and returns devices that are configured for SNMPv2.

Please keep in mind that this script will take a long time to complete!
Due to Meraki API Rate-Limiting, we have to take a little break between each request.
"""

import requests
import json
import sys
import time

api_key = sys.argv[1]
org_id = sys.argv[2]

headers = {
  u'X-Cisco-Meraki-API-Key': api_key
}

network_list = requests.request("GET", "https://api.meraki.com/api/v1/organizations/" + org_id + "/networks", headers=headers)
network_list_JSON = json.loads(network_list.text)
time.sleep(5)

if network_list.status_code != 200:
    print("Error ocurred. You are either being rate-limited (unlikely) or your API key is wrong (likely).\nStatus code is " + str(network_list.status_code))
    exit()

for network in network_list_JSON:
    rate_limit = "true"
    network_id = network['id']
    while rate_limit == "true":
        rate_limit = "false"
        network_snmp = requests.get("https://api.meraki.com/api/v1/networks/" + network_id + "/snmp", headers=headers)
        # Ideally this should never happen as we're sleeping for five seconds between requests, but better safe than sorry!
        if network_snmp.status_code == 429:
            print("Rate-limit hit. Sleeping for 5 seconds and trying again...")
            rate_limit == "true"
            time.sleep(5)
        # If the text "communityString" is present in the response, then it's SNMPv2.
        if "communityString" in network_snmp.text:
            print(network['name'] + " - SNMPv2")
        #print(network['name'] + " - SNMPv3")
time.sleep(5)
