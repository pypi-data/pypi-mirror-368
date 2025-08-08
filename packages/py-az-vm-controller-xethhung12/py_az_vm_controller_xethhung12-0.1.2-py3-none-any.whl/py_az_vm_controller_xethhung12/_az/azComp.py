import requests
import datetime
import requests
class AzOAuth:
    def url(self)->str:
        return f"https://login.microsoftonline.com/{self.tenantId}/oauth2/token"

    def __init__(self, tenantId: str):
        self.tenantId = tenantId
    
    def get_session(self, clientId: str, clientSecret: str)->'AzOAuthSession':
        return AzOAuthSession(self, clientId, clientSecret)

class AzOAuthSession:
    contentType: str = "application/x-www-form-urlencoded"
    grantType: str = "client_credentials"
    accessingResource: str = "https://management.azure.com/"
    def __init__(self, azOAuth: 'AzOAuth', clientId: str, clientSecret: str):
        self.azOAuth = azOAuth
        self.client_id = clientId
        self.client_secret = clientSecret
        self.cached_token = None

    def get_token(self)->str:
        if self.cached_token is not None:
            notBefore = datetime.datetime.fromtimestamp(int(self.cached_token['not_before']))
            timeExpire = datetime.datetime.fromtimestamp(int(self.cached_token['expires_on']))
            timeNow = datetime.datetime.now()

            if timeNow > notBefore and timeExpire - timeNow > datetime.timedelta(minutes=5):
                return self.cached_token['access_token']

        headers = {
            "Content-Type": AzOAuthSession.contentType
        }
        data = {
            "grant_type": AzOAuthSession.grantType,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "resource": AzOAuthSession.accessingResource
        }
        resp = requests.post(self.azOAuth.url(), data, headers=headers)
        if resp.status_code == 200:
            self.cached_token = resp.json()
            expiresInInt = int(self.cached_token['expires_on'])
            # print(datetime.datetime.fromtimestamp(expiresInInt))
            return self.cached_token['access_token']
        else:
            raise Exception(f"Failed with status: {resp.status_code}")

    def vm(self, subscriptionId: str, resourceGroupName: str, vmName: str)->'AzVM':
        return AzVM(self, subscriptionId, resourceGroupName, vmName)

class AzVM:
    def __init__(self, azOAuthSession: 'AzOAuthsession', subscriptionId: str, resourceGroup: str, vmName: str):
        self.azOAuthSession = azOAuthSession
        self.subscriptionId = subscriptionId
        self.resourceGroup = resourceGroup
        self.vmName = vmName
    
    def powerOn(self):
        headers = {
            "Content-Length": str(0),
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.azOAuthSession.get_token()}"
        }
        resp = requests.post(self.url("start"), {},headers=headers)
        if resp.status_code in [200,202]:
            return resp
        else:
            print(resp.cotent)
            raise Exception(f"Error with response code: {resp.status_code}")


    def powerOff(self):
        headers = {
            "Content-Length": str(0),
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.azOAuthSession.get_token()}"
        }
        resp = requests.post(self.url("powerOff"),{},headers=headers)
        if resp.status_code in [200,202]:
            return resp
        else:
            print(resp.content)
            raise Exception(f"Error with response code: {resp.status_code}")

    def deallocate(self):
        headers = {
            "Content-Length": str(0),
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.azOAuthSession.get_token()}"
        }
        resp = requests.post(self.url("deallocate"),{},headers=headers)
        if resp.status_code in [200,202]:
            return resp
        else:
            print(resp.content)
            raise Exception(f"Error with response code: {resp.status_code}")
        
    def url(self, action: str):
        return f"https://management.azure.com/subscriptions/{self.subscriptionId}/resourceGroups/{self.resourceGroup}/providers/Microsoft.Compute/virtualMachines/{self.vmName}/{action}?api-version=2024-11-01"
    
    def simpleState(self, data:dict = None)->dict:
        if data is None:
            data = self.instanceState()
        powerState = self.powerState(data)
        provisioningState = self.provisioningState(data)

        return {
            "name": self.vmName,
            "provisioning-state": provisioningState,
            "power-state": powerState
        }


    def instanceState(self)->dict:
        headers = {
            "Content-Length": str(0),
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.azOAuthSession.get_token()}"
        }
        resp = requests.get(self.url("instanceView"),headers=headers)
        if resp.status_code == 200:
            # state= resp.json()
            # import json
            # print(json.dumps(state,indent=2))
            # return state
            return resp.json()
        else:
            raise Exception(f"Error with response code: {resp.status_code}")

    def provisioningState(self, data: dict = None):
        if data is None:
            data = self.instanceState()
        for status in data["statuses"]:
            code = status['code']
            prefix="ProvisioningState/"
            if code.startswith(prefix):
                return code[len(prefix):]
                
        return None
    
    def powerState(self, data:dict = None):
        if data is None:
            data = self.instanceState()
        for status in data["statuses"]:
            code = status['code']
            prefix="PowerState/"
            if code.startswith(prefix):
                return code[len(prefix):]
                
        return None

    def isProvissioning(self, data: dict = None)->bool:
        if data is None:
            data = self.instanceState()
        return self.provisioningState(data) == "updating"

    def isVMStopped(self, data: dict=None)->bool:
        if data is None:
            data = self.instanceState()
        state = self.powerState(data)
        if state is not None and state == "stopped":
            return True
        else:
            return False

    def isVMDeallocated(self, data: dict=None)->bool:
        if data is None:
            data = self.instanceState()
        state = self.powerState(data)
        if state is not None and state == 'deallocated':
            return True
        else:
            return False
        
    def isVMRunning(self, data: dict=None)->bool:
        if data is None:
            data = self.instanceState()
        state = self.powerState(data)
        if state is not None and state == "running":
            return True
        else:
            return False
                