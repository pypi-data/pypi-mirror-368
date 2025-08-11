import requests
import datetime
import requests
import re

class AzManagement:
    def login_host_url()->str:
        return "https://login.microsoftonline.com"

    @staticmethod
    def az_management_host_url()->str:
        return "https://management.azure.com"
    
    @staticmethod
    def construct_login_url(tenantId: str) -> str:
        return f"https://login.microsoftonline.com/{tenantId}/oauth2/token"
    
    @staticmethod
    def extrac_resource_matcher(url)-> re.Match | None:
        reg_matching_str = r"^(https://management.azure.com){0,1}/subscriptions/(?P<subId>[^/]+)/resourceGroups/(?P<resourceGroupName>[^/]+)/providers/(?P<provider>[^/]+)/(?P<resourceType>[^/]+)/(?P<resourceName>[^/]+)(\?.*){0,1}$"
        matcher = re.match(reg_matching_str, url)
        if matcher is None:
            return None
        else:
            return matcher

    @staticmethod
    def extrac_resource_and_build_component(session:'AzOAuthSession',url: str)-> re.Match | None:
        matcher = AzManagement.extrac_resource_matcher(url)
        if matcher is not None:
            provider = matcher.group("provider")
            resourceType = matcher.group("resourceType")
            name = matcher.group("resourceName")
            subId = matcher.group("subId")
            resourceGroupName = matcher.group("resourceGroupName")

            if provider == "Microsoft.Compute":
                if resourceType == "virtualMachines":
                    return session.vm(subId, resourceGroupName, name)
            elif provider == "Microsoft.Network":
                if resourceType == "networkInterfaces":
                    return AzNetworkInterfaces(session, AzManagement.construct_network_interface_url(subId, resourceGroupName, name))
                else:
                    return AzPublicIpConfig(session, AzManagement.construct_network_interface_url(subId, resourceGroupName, name))

        else:
            raise Exception(f"The url[{url}] failed to be reconstruct!")


    @staticmethod
    def construct_component_url(subId: str, resGroupName: str, resourceScope:str, resource: str, name:str, api_version:str, action:str=None, extraParam: dict = None) -> str:
        name_str = '' if name is None else f'/{name}'
        action_str = '' if action is None else f"/{action}"
        extraParamStr = ''
        if extraParam is not None:
            for key in extraParam:
                extraParam = extraParam+f"&{key}={extraParam[key]}"
        return f"https://management.azure.com/subscriptions/{subId}/resourceGroups/{resGroupName}/providers/{resourceScope}/{resource}{name_str}{action_str}?api-version={api_version}{extraParamStr}"
    
    @staticmethod
    def construct_network_interface_url(subId: str, resGroupName: str, name:str=None, api_version:str="2025-01-01", action:str=None, extraParam: dict = None):
        return AzManagement.construct_component_url(subId, resGroupName, "Microsoft.Network", "networkInterfaces", name, api_version, action, extraParam) 

    @staticmethod
    def construct_ip_address_url(subId: str, resGroupName: str, name:str=None, api_version:str="2025-01-01", action:str=None, extraParam: dict = None):
        return AzManagement.construct_component_url(subId, resGroupName, "Microsoft.Network", "publicIPAddresses", name, api_version, action, extraParam) 
    
    def construct_virtual_machine_url(subId: str, resGroupName: str, name:str = None, api_version:str="2024-11-01", action:str=None, extraParam: dict = None):
        return AzManagement.construct_component_url(subId, resGroupName,"Microsoft.Compute","virtualMachines", name, api_version, action, extraParam)

    @staticmethod
    def construct_header(authSession: 'AzOAuthSession'=None,extra: dict=None, payload: bytes=None)->dict:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        if payload is None:
            headers.update({"Content-Length": str(0)})
        else:
            headers.update({"Content-Length": str(len(payload))})
            

        if authSession is not None:
            headers.update(
                {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {authSession.get_token()}"
                }
            )
        if extra is not None:
            for key in extra:
                headers.update({key: extra[key]})
        return headers

    @staticmethod
    def construct_login_payload(clientId: str, clientSecret: str)->dict:
        data = {
            "grant_type": "client_credentials",
            "client_id": clientId,
            "client_secret": clientSecret,
            "resource": AzManagement.az_management_host_url()
        }
        return data
    
    


class AzOAuth:
    GRANT_TYPE: str = "client_credentials"
    def url(self)->str:
        return AzManagement.construct_login_url(self.tenantId)

    def __init__(self, tenantId: str):
        self.tenantId = tenantId
    
    def get_session(self, clientId: str, clientSecret: str)->'AzOAuthSession':
        return AzOAuthSession(self, clientId, clientSecret)

class AzOAuthSession:
    def __init__(self, azOAuth: 'AzOAuth', clientId: str, clientSecret: str):
        self.azOAuth = azOAuth
        self.client_id = clientId
        self.client_secret = clientSecret
        self.cached_token = None
    
    def _get_network_url(self, subId: str, resName: str, networkCompName: str):
        return AzManagement.construct_network_interface_url(subId, resName, networkCompName)

    def get_token(self)->str:
        if self.cached_token is not None:
            notBefore = datetime.datetime.fromtimestamp(int(self.cached_token['not_before']))
            timeExpire = datetime.datetime.fromtimestamp(int(self.cached_token['expires_on']))
            timeNow = datetime.datetime.now()

            if timeNow > notBefore and timeExpire - timeNow > datetime.timedelta(minutes=5):
                return self.cached_token['access_token']

        resp = requests.post(self.azOAuth.url(), AzManagement.construct_login_payload(self.client_id, self.client_secret), headers=AzManagement.construct_header())
        if resp.status_code == 200:
            self.cached_token = resp.json()
            expiresInInt = int(self.cached_token['expires_on'])
            return self.cached_token['access_token']
        else:
            raise Exception(f"Failed with status: {resp.status_code}")
    
    def list_vm(self, subscriptionId:str, resourceGroupName: str):
        resp = requests.get(AzManagement.construct_virtual_machine_url(subscriptionId, resourceGroupName),headers=AzManagement.construct_header(self))
        if resp.status_code == 200:
            return resp
        else:
            raise Exception(f"Error with response code: {resp.status_code}")
        

    def vm(self, subscriptionId: str, resourceGroupName: str, vmName: str)->'AzVM':
        return AzVM(self, subscriptionId, resourceGroupName, vmName)

    def networkInfteraces(self, subscriptionId: str, resourceGroupName: str, name: str)->'AzNetworkInterface':
        return AzNetworkInterfaces(self, self._get_network_url(subscriptionId, resourceGroupName, name))

class AzNetworkInterfaces:
    def __init__(self, session: AzOAuthSession, url: str):
        self.azOAuthSession = session
        
        self.url=url
        res = requests.get(url, headers=AzManagement.construct_header(self.azOAuthSession))
        if res.status_code == 200:
            self.data = res.json()
        else:
            print(res.text)
            raise Exception("Fail to fetch the network interfaces")
    
    def ipConfigs(self)->['AzIpConfig']:
        configs = []
        for index, data in enumerate(self.data["properties"]['ipConfigurations']):
            configs.append(AzIpConfig(self, index))
        return configs

    def get_ip_config_by_index(self, index: int)->dict:
        return self.data["properties"]['ipConfigurations'][index]

        
class AzIpConfig():
    def __init__(self, nic: AzNetworkInterfaces, index: int):
        self.nic = nic
        self.index = index
    
    def privateIp(self):
        return self.nic.get_ip_config_by_index(self.index)["properties"]["privateIPAddress"]

    def publicIp(self)->'AzPublicIpConfig':
        id = self.nic.get_ip_config_by_index(self.index)["properties"]["publicIPAddress"]["id"]
        AzManagement.construct_network_interface_url
        matcher = AzManagement.extrac_resource_matcher(id)
        if matcher is None:
            raise Exception("IP configuration url not correct")
        return AzPublicIpConfig(self.nic.azOAuthSession, AzManagement.construct_ip_address_url(
            matcher["subId"], matcher["resourceGroupName"], matcher['resourceName']
            )
        )

class AzPublicIpConfig:
    def __init__(self, session: AzOAuthSession, url: str):
        self.azOAuthSession = session
        self.url=url
        res = requests.get(url, headers=AzManagement.construct_header(self.azOAuthSession))
        if res.status_code == 200:
            self.data = res.json()
        else:
            raise Exception("Fail to fetch the network interfaces")
    
    def ip(self)->str:
        return self.data["properties"]["ipAddress"]

class AzVM:
    def __init__(self, azOAuthSession: 'AzOAuthsession', subscriptionId: str, resourceGroup: str, vmName: str):
        self.azOAuthSession = azOAuthSession
        self.subscriptionId = subscriptionId
        self.resourceGroup = resourceGroup
        self.vmName = vmName
    
    def powerOn(self):
        resp = requests.post(self.url("start"), {},headers=AzManagement.construct_header(self.azOAuthSession))
        if resp.status_code in [200,202]:
            return resp
        else:
            print(resp.cotent)
            raise Exception(f"Error with response code: {resp.status_code}")

    def powerOff(self):
        resp = requests.post(self.url("powerOff"),{},headers=AzManagement.construct_header(self.azOAuthSession))
        if resp.status_code in [200,202]:
            return resp
        else:
            print(resp.content)
            raise Exception(f"Error with response code: {resp.status_code}")

    def deallocate(self):
        resp = requests.post(self.url("deallocate"),{},headers=AzManagement.construct_header(self.azOAuthSession))
        if resp.status_code in [200,202]:
            return resp
        else:
            print(resp.content)
            raise Exception(f"Error with response code: {resp.status_code}")
        
    def base_url(self):
        return f"https://management.azure.com/subscriptions/{self.subscriptionId}/resourceGroups/{self.resourceGroup}/providers/Microsoft.Compute/virtualMachines/{self.vmName}?api-version=2024-11-01"

    def url(self, action: str):
        return f"https://management.azure.com/subscriptions/{self.subscriptionId}/resourceGroups/{self.resourceGroup}/providers/Microsoft.Compute/virtualMachines/{self.vmName}/{action}?api-version=2024-11-01"
    
    def simpleState(self, data:dict = None)->dict:
        if data is None:
            data = self.instantState()
        powerState = self.powerState(data)
        provisioningState = self.provisioningState(data)

        return {
            "name": self.vmName,
            "provisioning-state": provisioningState,
            "power-state": powerState
        }

    def metaInfo(self)->dict:
        resp = requests.get(self.base_url(),headers=AzManagement.construct_header(self.azOAuthSession))
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(f"Error with response code: {resp.status_code}")
    

    def networkInterfaces(self)->dict:
        interfaces = {}
        for item in  self.metaInfo()["properties"]["networkProfile"]["networkInterfaces"]:
            interfaces.update({item['id']: AzManagement.extrac_resource_and_build_component(self.azOAuthSession, item['id'])})
        return interfaces
        # return self.metaInfo()["properties"]["networkProfile"]["networkInterfaces"]


    def instantState(self)->dict:
        resp = requests.get(self.url("instanceView"),headers=AzManagement.construct_header(self.azOAuthSession))
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(f"Error with response code: {resp.status_code}")

    def provisioningState(self, data: dict = None):
        if data is None:
            data = self.instantState()
        for status in data["statuses"]:
            code = status['code']
            prefix="ProvisioningState/"
            if code.startswith(prefix):
                return code[len(prefix):]
                
        return None
    
    def powerState(self, data:dict = None):
        if data is None:
            data = self.instantState()
        for status in data["statuses"]:
            code = status['code']
            prefix="PowerState/"
            if code.startswith(prefix):
                return code[len(prefix):]
                
        return None

    def isProvissioning(self, data: dict = None)->bool:
        if data is None:
            data = self.instantState()
        return self.provisioningState(data) == "updating"

    def isVMStopped(self, data: dict=None)->bool:
        if data is None:
            data = self.instantState()
        state = self.powerState(data)
        if state is not None and state == "stopped":
            return True
        else:
            return False

    def isVMDeallocated(self, data: dict=None)->bool:
        if data is None:
            data = self.instantState()
        state = self.powerState(data)
        if state is not None and state == 'deallocated':
            return True
        else:
            return False
        
    def isVMRunning(self, data: dict=None)->bool:
        if data is None:
            data = self.instantState()
        state = self.powerState(data)
        if state is not None and state == "running":
            return True
        else:
            return False
                