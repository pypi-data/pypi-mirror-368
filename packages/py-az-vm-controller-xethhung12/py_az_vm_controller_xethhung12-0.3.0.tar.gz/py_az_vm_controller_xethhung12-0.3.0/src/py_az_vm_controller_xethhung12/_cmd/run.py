# import os
# os.environ["using-j-vault-rest-server"]="localhost,7910,false,harden"
import py_az_vm_controller_xethhung12 as project
from j_vault_http_client_xethhung12 import client
import argparse
from py_xh_custapp_xethhung12 import CustApp, Entry, Profile
import json
import time
from datetime import datetime as dt

import time
def main():
    client.load_to_env()

    parser = argparse.ArgumentParser(
                    prog='pyAzVMController',
                    description='A app help manage azure vm power state',
                    # epilog='Text at the bottom of help'
                    )
    
    resource_parser = parser.add_subparsers(dest="resource")
    profile_parser = resource_parser.add_parser("profiles", help="list app profiles")

    profile_parser = resource_parser.add_parser("profile", help="manage app profile")
    profile_parser.add_argument("--name", "-n", type=str, required=True, help="name of the profile to be operated")
    action_parser = profile_parser.add_subparsers(dest="action")
    de_reg_profile_parser = action_parser.add_parser("de-register", help="de-register profile")
    reg_profile_parser = action_parser.add_parser("register", help="register profile (override if register again)")
    reg_profile_parser.add_argument("--subscription-id", type=str, required=False, default=None, help="Subscription ID")
    reg_profile_parser.add_argument("--resource-group-name", type=str, required=False, default=None, help="Resource group name")
    reg_profile_parser.add_argument("--client-id", type=str, required=False, default=None, help="Client ID")
    reg_profile_parser.add_argument("--client-secret", type=str, required=False, default=None, help="Client Secret")
    reg_profile_parser.add_argument("--tenant-id", type=str, required=False, default=None, help="Tenant ID")

    show_profile_parser = action_parser.add_parser("show", help="show profile")
    show_profile_parser.add_argument("--out-cmd", action="store_true", required=False, help="out put as cmd args")
    rename_profile_parser = action_parser.add_parser("rename", help="rename profile")
    rename_profile_parser.add_argument("--new-name", type=str, required=True, default=None, help="new name of the profile")

    rename_profile_parser = action_parser.add_parser("copy-as", help="copy profile as new profile")
    rename_profile_parser.add_argument("--new-name", type=str, required=True, default=None, help="new name of the profile")

    # list_vms = action_parser.add_parser("visible-vm", help="list all vms. (may have problem if having permission issue)")

    vms_parser = resource_parser.add_parser("vms", help="Virtual machines that is visible to the configurated profile")
    vms_parser.add_argument("--profile", "-p", type=str, required=True, help="profile name")

    vm_parser = resource_parser.add_parser("vm", help="Virtual machine to be managed")
    vm_parser.add_argument("--name", "-n", dest='vm_name', type=str, required=True, help="name of the vm")
    vm_parser.add_argument("--profile", "-p", type=str, required=True, help="profile name")
    action_parser = vm_parser.add_subparsers(dest="action")
    state_parser = action_parser.add_parser("state")
    state_parser.add_argument("--raw", action="store_true", help="raw state")
    ip_parser = action_parser.add_parser("ip")
    config_parser = action_parser.add_parser("config")
    network_interfaces_parser = action_parser.add_parser("nic")
    first_pub_ip_interfaces_parser = action_parser.add_parser("first-public-ip")
    action_parser.add_parser("power-on")
    action_parser.add_parser("power-off")
    action_parser.add_parser("deallocate")

    nic_parser = resource_parser.add_parser("nic", help="network interface component")
    nic_parser.add_argument("--name", "-n", dest='nic_name', type=str, required=True, help="name of the network interface")
    nic_parser.add_argument("--profile", "-p", type=str, required=True, help="profile name")
    data = parser.parse_args()

    app = CustApp.appDefault("pyAzVMController")

    resource = data.resource

    def get_profile_data(profile: str) -> (str, str, str, str, str):
        subId =app.get_kv(Entry.with_profile("subscriptionId",profile))
        if subId is None:
            raise Exception("Failed to extract subscription ID")
        resName =app.get_kv(Entry.with_profile("resourceGroupName",profile))
        if resName is None:
            raise Exception("Failed to extract resource group name")
        cliId=app.get_kv(Entry.with_profile("clientId",profile))
        if cliId is None:
            raise Exception("Failed to extract Client ID")
        cliSec=app.get_kv(Entry.with_profile("clientSecret",profile))
        if cliSec is None:
            raise Exception("Failed to extract Client Secret")
        tenId=app.get_kv(Entry.with_profile("tenantId",profile))
        if tenId is None:
            raise Exception("Failed to extract Tenant ID")
        return subId, resName, cliId, cliSec, tenId

    def get_list_of_profiles()->[str]:
        return set([e.profile.name for e in [Entry.laod_from_str(n) for n in app.list() ] if e.has_profile()])

    if resource == "profiles":
        profiles = get_list_of_profiles()
        print(f"Having {len(profiles)} {'profile' if len(profiles) < 2 else 'profiles'}:")
        for p in profiles:
            print(f"* {p}")
    elif resource == "nic":
        nic_name=data.nic_name
        profile = data.profile

        subId, resName, cliId, cliSec, tenId=get_profile_data(profile)
        azOAuth = project.AzOAuth(tenId)
        session = azOAuth.get_session(cliId, cliSec)
        ni = session.networkInfteraces(subId, resName, nic_name)

        print(json.dumps(ni.data, indent=2))
    elif resource == "vms":
        profile = data.profile
        if profile not in get_list_of_profiles():
            print(f"Profile[{profile}] not exists")
        else:
            subId, resName, cliId, cliSec, tenId=get_profile_data(profile)
            azOAuth = project.AzOAuth(tenId)
            session = azOAuth.get_session(cliId, cliSec)
            res = session.list_vm(subId, resName)
            print("Visible VM for this profile: ")
            if res.status_code == 200:
                for vm in res.json()["value"]:
                    interfaces = session.vm(subId, resName, vm['name']).networkInterfaces()
                    nic = interfaces[list(interfaces.keys())[0]].ipConfigs()[0].publicIp()
                    print(f"* {vm['name']} ({nic.ip()})")
            else:
                print(f"error with status `{res.status_code}`, please check if there is permission issue")
    elif resource == "profile":
        profile=data.name
        action = data.action

        def show_profile(profile: str):
            subId, resName, cliId, cliSec, tenId=get_profile_data(profile)
            print(f"""
registered profile[{profile}]
    with Subscription ID: {subId}
    with Resource Group Name: {resName}
    with Client ID: {cliId}
    with Client Secret: {cliSec}
    with Tenant ID: {tenId}
""")

        def show_profile_cmd(profile: str):
            subId, resName, cliId, cliSec, tenId=get_profile_data(profile)
            print(f'profile --name "{profile}" register --subscription-id "{subId}" --resource-group-name "{resName}" --client-id "{cliId}" --client-secret "{cliSec}" --tenant-id "{tenId}"')

        def delete_profile(profile: str):
            if profile not in get_list_of_profiles():
                print(f"Profile[{profile}] not exists")
            else:
                for entryStr in app.list(profile=Profile(profile)):
                    entry = Entry.laod_from_str(entryStr)
                    if app.has_kv(entry):
                        app.rm_kv(entry)
                    else:
                        raise Exception(f"Entry[{entry.name()}] not exists, no action")
        
        def reg_profile(profile: str, subscriptionId:str, resouceGroupName:str, clientId:str, clientSecret:str, tenantId: str):
            app.set_kv(Entry.with_profile("subscriptionId",profile), subscriptionId)
            app.set_kv(Entry.with_profile("resourceGroupName",profile), resouceGroupName)
            app.set_kv(Entry.with_profile("clientId",profile), clientId)
            app.set_kv(Entry.with_profile("clientSecret",profile), clientSecret)
            app.set_kv(Entry.with_profile("tenantId",profile), tenantId)

        if action == "register":
            subscriptionId = data.subscription_id
            resouceGroupName = data.resource_group_name
            clientId = data.client_id
            clientSecret = data.client_secret
            tenantId = data.tenant_id
            reg_profile(profile, subscriptionId, resouceGroupName, clientId, clientSecret, tenantId)
            show_profile(profile)
        elif action == "de-register":
            delete_profile(profile)
            print(f"Profile[{profile}] detele")
        elif action == "copy-as":
            if profile not in get_list_of_profiles():
                print(f"Profile[{profile}] not exists")
            else:
                new_profile_name = data.new_name
                if new_profile_name in get_list_of_profiles():
                    print(f"New profile[{new_profile_name}] already exists")
                else:
                    subId, resName, cliId, cliSec, tenId=get_profile_data(profile)
                    reg_profile(new_profile_name, subId, resName, cliId, cliSec, tenId)
                    show_profile(new_profile_name)
                    print(f"Profile[{profile}] detele")
        elif action == "rename":
            if profile not in get_list_of_profiles():
                print(f"Profile[{profile}] not exists")
            else:
                new_profile_name = data.new_name
                if new_profile_name in get_list_of_profiles():
                    print(f"New profile[{new_profile_name}] already exists")
                else:
                    subId, resName, cliId, cliSec, tenId=get_profile_data(profile)
                    reg_profile(new_profile_name, subId, resName, cliId, cliSec, tenId)
                    show_profile(new_profile_name)
                    delete_profile(profile)
                    print(f"Profile[{profile}] detele")
        elif action == "show":
            if profile not in get_list_of_profiles():
                print(f"Profile[{profile}] not exists")
            elif data.out_cmd:
                show_profile_cmd(profile)
            else:
                show_profile(profile)
        else:
            raise Exception(f"Argument not valid")
        pass
    elif resource == "vm":
        vmname=data.vm_name
        action = data.action
        profile = data.profile

        if profile not in get_list_of_profiles():
            print(f"Profile[{profile}] not exists")
            return

        subId, resName, cliId, cliSec, tenId=get_profile_data(profile)
        azOAuth = project.AzOAuth(tenId)
        session = azOAuth.get_session(cliId, cliSec)
        vm = session.vm(subId, resName, vmname)

        if action == "state":
            is_raw = data.raw
            if is_raw:
                print(json.dumps(vm.instantState(),indent=2))
            else:
                print(json.dumps(vm.simpleState(),indent=2))
        elif action == "config":
            data = vm.metaInfo()
            print(json.dumps(data, indent=2))
        elif action == "nic":
            print("Network interfaces: ")
            interfaces = vm.networkInterfaces()
            for key in interfaces:
                print(f"* {interfaces[key].data['name']} [{interfaces[key].data['id']}]")
        elif action == "first-public-ip":
            for i in vm.metaInfo()["properties"]["networkProfile"]["networkInterfaces"]:
                id=i["id"]
                name = i["id"].split("/")[-1]
                ni = session.networkInfteraces(subId, resName, name)
                print(ni.ipConfigs()[0].publicIp().ip())
                break
        elif action == "power-on":
            state = vm.instantState()
            if vm.isVMRunning(state):
                print(f"[{vmname}] is already on")
            else:
                start_time = dt.now()
                print("start power on")
                vm.powerOn()
                print("power on triggered")
                time.sleep(5)
                for i in range(210):
                    seconds = (dt.now() - start_time).seconds
                    state = vm.instantState()
                    if vm.isProvissioning(state):
                        print(f"[{vmname}] is still provisioning. [{seconds} s]")
                    elif vm.isVMRunning(state):
                        print(f"[{vmname}] is now running. [{seconds} s]")
                        break
                    else:
                        print(json.dumps(vm.simpleState(state), indent=2))
                    time.sleep(5)
                print("done")
        elif action == "power-off":
            state = vm.instantState()
            if vm.isVMStopped(state):
                print(f"[{vmname}] is already stopped")
            else:
                start_time = dt.now()
                print("start power off")
                vm.powerOff()
                print("power off triggered")
                time.sleep(5)
                for i in range(210):
                    seconds = (dt.now() - start_time).seconds
                    state = vm.instantState()
                    if vm.isProvissioning(state):
                        print(f"[{vmname}] is still provisioning. [{seconds} s]")
                    elif vm.isVMStopped(state):
                        print(f"[{vmname}] is now stopped. [{seconds} s]")
                        break
                    else:
                        print(json.dumps(vm.simpleState(state), indent=2))
                    time.sleep(5)
                print("done")
        elif action == "deallocate":
            state = vm.instantState()
            if vm.isVMDeallocated(state):
                print(f"[{vmname}] is already deallocated")
            else:
                start_time = dt.now()
                print("start deallocate")
                vm.deallocate()
                print("deallocation triggered")
                time.sleep(5)
                for i in range(210):
                    seconds = (dt.now() - start_time).seconds
                    state = vm.instantState()
                    if vm.isProvissioning(state):
                        print(f"[{vmname}] is still provisioning. [{seconds} s]")
                    elif vm.isVMDeallocated(state):
                        print(f"[{vmname}] is now deallocated. [{seconds} s]")
                        break
                    else:
                        print(json.dumps(vm.simpleState(state), indent=2))
                    time.sleep(5)
                print("done")
        pass



