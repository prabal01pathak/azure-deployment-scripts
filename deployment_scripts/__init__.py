'''deployment script'''

import os
import json
import subprocess
from dotenv import load_dotenv
load_dotenv()

# acr build
ACR_NAME = "vmscontainers"
RESOURCEGROUP = "testing"

services_and_paths = {
    "createvisit_fe_ms": "/home/prabal/Documents/vms/createvisit-fe-ms",
    "reception_fe_ms": "/home/prabal/Documents/vms/reception-be-ms",
    "mobile_fe_ms": "/home/prabal/Documents/vms/mobile-be-ms",

    "createvisit_be_ms": "/home/prabal/Documents/vms/createvisit-be-ms",
    "masterdata_be_ms": "/home/prabal/Documents/vms/masterdata-be-ms",
    "faceapi_be_ms": "/home/prabal/Documents/vms/faceapi-be-ms",
    "authentication_be_ms": "/home/prabal/Documents/vms/authentication-be-ms",
}


def build_image(image_name: str, path: str, registry_name: str = ACR_NAME):
    """ build images in acr"""
    for service, path in services_and_paths.items():
        # os.system(f"az acr build -t {acr_name}/{service}:latest -r {acr_name} {path}")
        print("service: ", service, ", path: ", path)
        os.chdir(path=path)
        print("dirs: ", os.listdir())
        build_output = subprocess.check_output(
            f"az acr build --registry "
            f"{registry_name} --image {image_name} .", shell=True
        )
        print("build output: ", build_output)
        command = f"az containerapp revision list -n {service} -g {RESOURCEGROUP}"
        revision_output = subprocess.check_output(command, shell=True)
        revision_output = json.loads(revision_output.decode("utf-8"))
        revision_name = revision_output[0]["id"].split("/")[-1]
        restart_command = (
            f"az containerapp revision restart "
            f"-n {service} -g {RESOURCEGROUP} --revision {revision_name}"
        )
        restart_output = subprocess.check_output(restart_command, shell=True)
        print("restart output: ", restart_output)
    return {"message": "build images is done"}
