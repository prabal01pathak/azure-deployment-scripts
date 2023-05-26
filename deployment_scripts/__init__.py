'''deployment script'''

import os
import json
import subprocess
from dotenv import load_dotenv

load_dotenv()

# acr build
ACR_NAME = "reattestcontainer" # => add your azure container registry name 
RESOURCEGROUP = "myfirsttest-res" # => add your azure resource group name 
ENV  = "managedEnvironment-myfirsttestres-ad45" # => add your azure environment name
REGISTRY_SERVER = "reattestcontainer.azurecr.io" # => add your azure registry server name


# service local need to be specified
services_and_paths = {
    "createvisit-fe": "/home/prabal/Documents/vms/createvisit-fe-ms",
    "reception-fe-ms": "/home/prabal/Documents/vms/reception-be-ms",
    "mobile-fe-ms": "/home/prabal/Documents/vms/mobile-be-ms",
    "createvisit-be-ms": "/home/prabal/Documents/vms/createvisit-be-ms",
    "masterdata-be-ms": "/home/prabal/Documents/vms/masterdata-be-ms",
    "faceapi-be-ms": "/home/prabal/Documents/vms/faceapi-be-ms",
    "authentication-be-ms": "/home/prabal/Documents/vms/authentication-be-ms",
}


def deploy(image_name: str, path: str, registry_name: str = ACR_NAME):
    """ build images in acr"""
    for service, path in services_and_paths.items():
        # os.system(f"az acr build -t {acr_name}/{service}:latest -r {acr_name} {path}")
        command = f"""az containerapp up \
             --name {service.replace("_", "-")} \
            --source . \
             --resource-group {RESOURCEGROUP} \
             --environment  {ENV} \
           --registry-server {REGISTRY_SERVER}  \
            --image {service}:latest \
            """
        print("service: ", service, ", path: ", path)
        os.chdir(path=path)
        print("dirs: ", os.listdir())
        deployment_output = subprocess.check_output(command, shell=True)
        print("deployment output: ", deployment_output)
        break
    return {"message": "deployment is done"}


def build_and_restart(image_name: str, path: str, registry_name: str = ACR_NAME):
    for service, path in services_and_paths.items():
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
    return {"message": "deployment images is done"}
