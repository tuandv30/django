import json
import time
from datetime import datetime

import requests
from constance import config
from sentry_sdk import capture_exception


def action_switch_plan():
    now = datetime.now()
    create_time = now.strftime("%Y-%m-%d %H:%M:%S")
    path = "SortDirector/DownloadWCS205"
    url = "{}/{}".format(config.DAMON_WCS_API_URL, path)
    headers = {
        "Content-Type": "application/json",
        "WMS2WCS": config.DAMON_WCS_TOKEN
    }
    payload = {
        "RequestID": "{}".format(int(time.time())),
        "CreateTime": create_time,
    }
    try:
        response = requests.post(
            url, headers=headers, data=json.dumps(payload))
        r_json = response.json()
        result = r_json.get("Result")
        if result == "1":
            return True
        return False
    except BaseException:
        return False


def action_active_plan(plan_id):
    now = datetime.now()
    create_time = now.strftime("%Y-%m-%d %H:%M:%S")
    path = "SortDirector/DownloadWCS210"
    url = "{}/{}".format(config.DAMON_WCS_API_URL, path)
    headers = {
        "Content-Type": "application/json",
        "WMS2WCS": config.DAMON_WCS_TOKEN
    }
    payload = {
        "SortPlanID": str(plan_id),
        "State": "1",
        "CreateTime": create_time,
    }
    try:
        response = requests.post(
            url, headers=headers, data=json.dumps(payload))
        r_json = response.json()
        result = r_json.get("Result")
        if result == "1":
            return True
    finally:
        pass
    return False


def add_0_number(string=str()):
    len_str = len(string)
    if len_str < 3:
        new_string = "{}{}".format("0" * (3 - len_str), string)
    else:
        new_string = string

    return new_string


def action_lock_release_chute(action, list_chute_id):
    now = datetime.now()
    create_time = now.strftime("%Y-%m-%d %H:%M:%S")
    path = "SortDirector/DownloadWCS209"
    url = "{}/{}".format(config.DAMON_WCS_API_URL, path)
    headers = {
        "Content-Type": "application/json",
        "WMS2WCS": config.DAMON_WCS_TOKEN
    }
    payload = list()

    if action == "lock_selected":
        for i in list_chute_id:
            payload.append({
                "ChuteNo": add_0_number(str(i)),
                "Enable": "1",
                "CreateTime": create_time
            })
    elif action == "release_selected":
        for i in list_chute_id:
            payload.append({
                "ChuteNo": add_0_number(str(i)),
                "Enable": "0",
                "CreateTime": create_time
            })
    try:
        requests.post(
            url, headers=headers, data=json.dumps(payload))
        return True
    except BaseException as ex:
        capture_exception(ex)
        return False
