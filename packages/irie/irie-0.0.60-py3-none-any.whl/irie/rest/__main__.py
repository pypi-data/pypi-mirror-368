# Claudio M. Perez
import os
import requests
import sys
import json
import time
import tqdm
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

class IrieRest:
    def __init__(self):
        pass

def list_evals():

    # Environment variables for authentication and hostname
    username = os.getenv("IRIE_USERNAME")
    password = os.getenv("IRIE_PASSWORD")
    hostname = os.getenv("IRIE_HOSTNAME")

    if not all([username, password, hostname]):
        raise ValueError("Ensure all required environment variables and file path are set.")

    # API endpoint
    url = f"{hostname}/api/evals/"
    headers = {
        "Content-Type": "multipart/form-data",
    }


    # Perform the POST request with Basic Auth
    response = requests.get(url, auth=(username, password))

    # Output the response
    return json.loads(response.text)

def post_motions(filenames):
    progress = tqdm.tqdm(filenames)
    for filename in progress:
        if (response := post_motion(filename)) and response.get("data",""):
            progress.set_description(f"Analyzing {Path(filename).name}")
            time.sleep(5)
        else:
            progress.set_description(f"Skipping {Path(filename).name}")
            continue 

def post_motion(filename):
    import os
    import requests

    # Environment variables for authentication and hostname
    username = os.getenv("IRIE_USERNAME")
    password = os.getenv("IRIE_PASSWORD")
    hostname = os.getenv("IRIE_HOSTNAME")

    if not all([username, password, hostname]):
        raise ValueError("Ensure all required environment variables and file path are set.")

    # API endpoint
    url = f"{hostname}/api/events/"

    # Open the file to upload
    with open(filename, "rb") as file:
        # Prepare the multipart-form data
        files = {
            "event_file": file
        }
        # Perform the POST request with Basic Auth
        response = requests.post(url, auth=(username, password), files=files)
    try:
        return json.loads(response.text)
    except:
        return None


def post_evaluations(data):
    eval_data   = data["evaluation"]
    motion_data = data["motion_data"]
    eval_data.pop("event")
#   event_file = eval_data.pop("event_file")

    # Framework parameters
    # ----------------------------------
    username = os.getenv("IRIE_USERNAME")
    password = os.getenv("IRIE_PASSWORD")
    hostname = os.getenv("IRIE_HOSTNAME")

    if not all([username, password, hostname]):
        raise ValueError("Ensure all required environment variables and file path are set.")


    # Setup API request
    # ----------------------------------
    headers = {
            # "Content-Type": "multipart/form-data",
    }

    files = {
        "evaluation":  (None, json.dumps(eval_data)),
        "motion_data": (None, json.dumps(motion_data)),
#       "event_file": (event_file, open(event_file, "rb")),
    }

    # Perform request
    # ----------------------------------
    response = requests.post(
        hostname + "/api/events/",
        headers=headers,
        files=files,
        auth=HTTPBasicAuth(username, password)
    )

    print(response.content)


if __name__ == "__main__":

    if len(sys.argv) == 1:
        # python -m irie.rest
        # List all evaluations
        print(json.dumps(list_evals()))

    elif len(sys.argv) > 2:
        # python -m irie.rest <file1> <file2> ...
        # Post multiple motion files
        post_motions(sys.argv[1:])

    elif sys.argv[1].endswith(".zip"):
        post_motion(sys.argv[1])

    elif sys.argv[1].endswith(".json"):
        with open(sys.argv[1], "r") as f:
            data = json.load(f)["data"]

        for bridge in data:
            for event in bridge["events"]:
                post_evaluations(event)
            time.sleep(3)

