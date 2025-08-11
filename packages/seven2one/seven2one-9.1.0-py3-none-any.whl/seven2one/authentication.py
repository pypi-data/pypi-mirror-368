from ast import List
from datetime import datetime, timedelta
from typing import Optional, Union, List
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient, OAuth2Error
from seven2one.utils import ut_device_client
import requests
import time
import json

class OidcConfig:
    def __init__(self, issuer: str, authorization_endpoint: str, token_endpoint: str, userinfo_endpoint: str, end_session_endpoint: str, device_authorization_endpoint: str):
        self.issuer = issuer
        self.authorization_endpoint = authorization_endpoint
        self.token_endpoint = token_endpoint
        self.userinfo_endpoint = userinfo_endpoint
        self.end_session_endpoint = end_session_endpoint
        self.device_authorization_endpoint = device_authorization_endpoint

    def to_dict(self):
        return {
            "issuer": self.issuer,
            "authorization_endpoint": self.authorization_endpoint,
            "token_endpoint": self.token_endpoint,
            "userinfo_endpoint": self.userinfo_endpoint,
            "end_session_endpoint": self.end_session_endpoint,
            "device_authorization_endpoint": self.device_authorization_endpoint
        }

    def to_json(self):
        return json.dumps(self.to_dict())

class OidcDiscoveryClient:
    def __init__(self, base_url: Union[str, List[str]]):
        self.base_url = base_url

    def discover(self) -> OidcConfig:
        config = None

        if (isinstance(self.base_url, str)):
            try:
                config = self._fetch(self.base_url)
            except Exception:
                try:
                    config = self._fetch(f"{self.base_url}/.well-known/openid-configuration")
                except Exception:
                    raise Exception("OIDC discovery failed. No configuration found")
        elif (isinstance(self.base_url, list)):
            for url in self.base_url:
                try:
                    config = self._fetch(url)
                    break
                except Exception:
                    try:
                        config = self._fetch(f"{url}/.well-known/openid-configuration")
                        break
                    except Exception:
                        continue
            else:
                raise Exception("No valid OIDC discovery URL found")
        
        if (config is None):
            raise Exception("OIDC discovery failed. No configuration found")

        return OidcConfig(
            issuer=config.get("issuer"),
            authorization_endpoint=config.get("authorization_endpoint"),
            token_endpoint=config.get("token_endpoint"),
            userinfo_endpoint=config.get("userinfo_endpoint"),
            end_session_endpoint=config.get("end_session_endpoint"),
            device_authorization_endpoint=config.get("device_authorization_endpoint")
        )

    def _fetch(self, url: str):
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

class OAuth2Credential:
    def __init__(self):
        return None

class OAuth2ServiceCredential(OAuth2Credential):
    def __init__(self, username: str, password: str):
        super().__init__()
        self.username = username
        self.password = password

class OAuth2InteractiveUserCredential(OAuth2Credential):
    def __init__(self):
        super().__init__()

class OAuth2Authentication:
    client_id: str
    credentials: OAuth2Credential
    oidcConfig: OidcConfig
    session: Optional[OAuth2Session]
    authenticated: bool = False
    tokenExpiresAt: datetime
    minimumTokenLifetimeSeconds: int = 60

    def __init__(self, client_id: str, credentials: OAuth2Credential , oidcConfig: OidcConfig):
        self.oidcConfig = oidcConfig
        self.client_id = client_id
        self.credentials = credentials
        if not (isinstance(self.credentials, OAuth2ServiceCredential) or isinstance(self.credentials, OAuth2InteractiveUserCredential)):
            raise Exception("Invalid credentials")
    
    def authenticate(self):
        self._authenticate()
        self.authenticated = True

    def get_access_token(self) -> str:
        if (not self.authenticated):
            raise Exception("Not authenticated. Call authenticate() first")
        if (not self.session):
            raise Exception("Session not initialized")
         
        self._refresh_authentication()
        return self.session.access_token

    def _process_token_response(self, response):
        self.tokenExpiresAt = datetime.fromtimestamp(response['expires_at'])
        return response

    def _is_token_expired(self):
        return (self.tokenExpiresAt - timedelta(seconds=self.minimumTokenLifetimeSeconds)) < datetime.now()

    def _refresh_authentication(self):
        if (not self.authenticated):
            raise Exception("Not authenticated. Call authenticate() first")
        
        if (not self._is_token_expired()):
            return

        if isinstance(self.credentials, OAuth2ServiceCredential):
            return self._refresh_authentication_service(self.credentials)
        elif isinstance(self.credentials, OAuth2InteractiveUserCredential):
            return self._refresh_authentication_client(self.credentials)
        else:
            raise Exception("Invalid credentials")
    
    def _refresh_authentication_service(self, credentials: OAuth2ServiceCredential) -> None:
        if (not self.session):
            raise Exception("Session not initialized")
        
        token_response = self.session.fetch_token(token_url=self.oidcConfig.token_endpoint,
                                 client_id=self.client_id,
                                 username=credentials.username,
                                 password=credentials.password)
        self._process_token_response(token_response)

    def _refresh_authentication_client(self, _: OAuth2InteractiveUserCredential) -> None:
        if (not self.session):
            raise Exception("Session not initialized")

        token_response = self.session.refresh_token(token_url=self.oidcConfig.token_endpoint,
                                                    client_id=self.client_id)
        self._process_token_response(token_response)
    
    def _authenticate(self) -> None:
        if isinstance(self.credentials, OAuth2ServiceCredential):
            return self._authenticate_service(self.credentials)
        elif isinstance(self.credentials, OAuth2InteractiveUserCredential):
            return self._authenticate_client(self.credentials)
        else:
            raise Exception("Invalid credentials")

    def _authenticate_service(self, credentials: OAuth2ServiceCredential) -> None:
        client = BackendApplicationClient(client_id=self.client_id)
        self.session = OAuth2Session(client=client)
        token_response = self.session.fetch_token(token_url=self.oidcConfig.token_endpoint,
                                 client_id=self.client_id,
                                 username=credentials.username,
                                 password=credentials.password)
        self._process_token_response(token_response)

        if (not self.session.authorized):
            raise Exception("Authentication failed")

    def _authenticate_client(self, _: OAuth2InteractiveUserCredential) -> None:
        def _get_device_code_response():
            response = requests.request("POST", f'{self.oidcConfig.device_authorization_endpoint}', data=f'client_id={self.client_id}', headers={
                                'Content-Type': 'application/x-www-form-urlencoded'})
            json_response = json.loads(response.text)
            device_code = json_response['device_code']
            interval = json_response['interval']
            verification_uri = json_response['verification_uri_complete']
            expires_in = json_response['expires_in']
            return {
                "device_code": device_code,
                "interval": interval,
                "verification_uri": verification_uri,
                "expires_in": expires_in
            }

        device_code_response = _get_device_code_response()

        print('Please go to %s and authorize access.' %
            device_code_response['verification_uri'])

        device_client = ut_device_client.DeviceClient(client_id=self.client_id) # type: ignore
        self.session = OAuth2Session(client=device_client, auto_refresh_url=self.oidcConfig.token_endpoint)
        while True:
            try:
                token_response = self.session.fetch_token(
                    token_url=self.oidcConfig.token_endpoint,
                    code=device_code_response['device_code'],
                    include_client_id=True)
                self._process_token_response(token_response)
                
                break
            except OAuth2Error as e:
                if e.error == 'authorization_pending':
                    time.sleep(device_code_response['interval'])
                else:
                    print(f'Authorization failed: {e.error}')
                    raise