
# py_az_vm_controller

## Introduction
This is simple library for doing remote turn on and off azure virtual machine. 

The library requires the user to have 

* Azure Subscription with Entra ID (Entra ID's app id as **tenantID**) for register new app (`registered app`) for oauth login
    * App ID as **clientId**
    * Creating `Credential` as (**clientSecret**)
* The `registered app` configured to be able to perform
    * Microsoft.Compute/virtualMachines/read
    * Microsoft.Compute/virtualMachines/instanceView/read
    * Microsoft.Compute/virtualMachines/start/action
    * Microsoft.Compute/virtualMachines/powerOff/action  

## Execution
*_This is a library rather then a executable problem. The execution will trigger the demo only_*

Run through python interpreter:
```shell
python -m py_az_vm_controller
```

### Demo Code
```py
import os
os.environ["using-j-vault-rest-server"]="localhost,7910,false,harden"
import py_az_vm_controller as project
from j_vault_http_client_xethhung12 import client

# Make sure you defined the system variables:
#     * tenantId              <--- The microsoft Entra Id
#     * clientId              <--- The client id of the app registered
#     * clientSecret          <--- The client secret of the app registered 
#     * subscriptionId        <--- The subscription id of the VM
#     * resourceGroupName     <--- The resource group name of the VM
#     * vmName                <--- The name of the virtual machine

import time
def main():
    client.load_to_env()
    tenantId = os.getenv("tenantId")
    clientId = os.getenv("clientId")
    clientSecret = os.getenv("clientSecret")
    subscriptionId = os.getenv("subscriptionId")
    resourceGroupName = os.getenv("resourceGroupName")
    vmName = os.getenv("vmName")
    print(tenantId, clientId, clientSecret, subscriptionId, resourceGroupName, vmName)
    azOAuth = project.AzOAuth(tenantId)
    session = azOAuth.get_session(clientId, clientSecret)
    vm = session.vm(subscriptionId, resourceGroupName, vmName)
    if vm.isVMStopped():
        print("Try power on the machine")
        vm.powerOn()
    while(True):
        time.sleep(5)
        print(vm.instanceState())
        if vm.isVMRunning():
            print("running finally")
            break
        
    time.sleep(10)

    print("stopping machine")
    vm.powerOff()
    while(True):
        time.sleep(5)
        print(vm.instanceState())
        if vm.isVMStopped():
            print("stopped finally")
            break
```

## Development
The project requires `python` (3+ version) installed and `pip` ready for use on adding manage dependencies

#### Tools
|Name|Platform|Type|Description|
|---|---|---|---|
|install-dependencies.sh|shell|script| The scripts for installing depencies required|
|build.sh|shell|script| The scripts for build the package|
|build-and-deploy.sh|shell|script| The scripts for build and deploy the package|

* install-dependencies.sh
The script will install dependencies listed in `dev-requirements.txt` and `requirements.txt`. The first requirement file contains the dependencies for development like build and deploy tools. The second requirement file defined all required dependencies for the making the package works (**actual dependencies**).

## Useful Scripts
### Project Versioning
For version update in `pyproject.toml`.
This project use package [`xh-py-project-versioning`](https://github.com/xh-dev/xh-py-project-versioning) to manipulate the project version.

Simple usage includes:\
Base on current version, update the patch number with dev id
`python -m xh_py_project_versioning --patch` \
In case current version is `0.0.1`, the updated version will be `0.0.2-dev+000` 

To prompt the dev version to official version use command.
`python -m xh_py_project_versioning -r`.
Through the command, version `0.0.2-dev+000` will be prompt to `0.0.2` official versioning.

Base on current version, update the patch number directly
`python -m xh_py_project_versioning --patch -d` \
In case current version is `0.0.1`, the updated version will be `0.0.2` 

Base on current version, update the minor number directly
`python -m xh_py_project_versioning --minor -d` \
In case current version is `0.0.1`, the updated version will be `0.1.0` 

Base on current version, update the minor number directly
`python -m xh_py_project_versioning --minor -d` \
In case current version is `0.0.1`, the updated version will be `1.0.0` 