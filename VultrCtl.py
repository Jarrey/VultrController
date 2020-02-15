#!/usr/local/bin/python3

import argparse
import datetime
import json
import random
import ssl
import urllib.parse
import urllib.request
from urllib.error import HTTPError

TARGET_REGION = random.choice(['Sydney'])
TARGET_PLAN = 5 # $5.00 per month

SERVER_LIST = 'https://api.vultr.com/v1/server/list'
SNAPSHOT_LIST = 'https://api.vultr.com/v1/snapshot/list'
PLAN_LIST = 'https://api.vultr.com/v1/plans/list'
REGIONS_LIST = 'https://api.vultr.com/v1/regions/list'
OS_LIST = 'https://api.vultr.com/v1/os/list'
CREATE_VPS = 'https://api.vultr.com/v1/server/create'
DESTROY = 'https://api.vultr.com/v1/server/destroy'

context = ssl._create_unverified_context()
def get_header(api_key):
    return {'API-Key': api_key}


def get(url, api_key = None):
    header = get_header(api_key) if api_key else None
    req = urllib.request.Request(url, headers=header) if header else urllib.request.Request(url)
    try:
        response = urllib.request.urlopen(req, context=context)
        if response.code == 200:
            return json.loads(response.read())
    except HTTPError as e:
        print('Error code: ', e.code)
        print('Reason: ', e.reason)
        return None


def post(url, api_key, data):
    header = get_header(api_key)
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode("utf-8"), headers=header)
    try:
        response = urllib.request.urlopen(req, context=context)
        if response.code == 200:
            content = response.read()
            if content:
                return json.loads(content.decode('utf-8'))
            else:
                return True
    except HTTPError as e:
        print('Error code: ', e.code)
        print('Reason: ', e.reason)


def get_current_vpses(api_key):
    return get(SERVER_LIST, api_key)


def get_current_snaprshots(api_key):
    return get(SNAPSHOT_LIST, api_key)


def get_target_region():
    regions = get(REGIONS_LIST)
    for region in regions.values():
        if region['name'] == TARGET_REGION:
            return region['DCID']


def get_target_plan():
    plans = get(PLAN_LIST)
    for plan in plans.values():
        if float(plan['price_per_month']) == TARGET_PLAN:
            return plan['VPSPLANID']


def get_snapshot_os():
    oss = get(OS_LIST)
    for os in oss.values():
        if os['name'] == 'Snapshot':
            return os['OSID']


def destroy(api_key, sub_id):
    post(DESTROY, api_key, {'SUBID': sub_id})


def deploy(api_key):
    data = {
        'DCID': get_target_region(),
        'VPSPLANID': get_target_plan(),
        'OSID': get_snapshot_os(),
        'SNAPSHOTID': next(iter(get_current_snaprshots(api_key))),
        'label': 'AUTO_VPS_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    }
    return post(CREATE_VPS, api_key, data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Vultr VPS controller tool')
    parser.add_argument('-k', '--key', required=True, help='API Key of Vultr account', action='store')
    parser.add_argument('-a', '--action', required=True, choices=['d', 'r'], help='Action for Vultr VPSs, "destroy" or "renew"]', action='store')
    parser.add_argument('-d', '--destroy', help='Whether destroy the legacy VPS instance when renew VPS', action='store_true')

    args = parser.parse_args()
    api_key = args.key

    vpss = get_current_vpses(api_key)

    if args.action == 'r':
        deploy(api_key)

    if vpss:
        for vps in vpss.values():
            if args.action == 'd' or args.destroy:
                destroy(api_key, vps['SUBID'])
