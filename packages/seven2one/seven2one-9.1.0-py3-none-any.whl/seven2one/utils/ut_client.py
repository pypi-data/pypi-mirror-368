from typing import Callable
from gql import Client
from seven2one.core_interface import ITechStack
from gql.transport.requests import RequestsHTTPTransport

class ClientUtil:
    @staticmethod
    def _create_client(techStack: ITechStack, endpoint: str, get_access_token: Callable[..., str]) -> Client:
        headers = {
            'authorization': 'Bearer ' + get_access_token()
        }
        transport = RequestsHTTPTransport(url=endpoint, headers=headers, verify=True, proxies=techStack.config.proxies)
        return Client(transport=transport, fetch_schema_from_transport=False)
