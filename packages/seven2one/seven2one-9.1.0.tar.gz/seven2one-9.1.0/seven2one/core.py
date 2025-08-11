import datetime
from distutils.util import strtobool
from uuid import uuid4
from loguru import logger
from typing import Optional, Union

import pandas as pd
import sys
import json
import os
import getpass
import warnings

from seven2one.authentication import OAuth2Authentication, OidcDiscoveryClient, OAuth2ServiceCredential, OAuth2Credential, OAuth2InteractiveUserCredential
from seven2one.core_interface import ITechStack
from seven2one.core_metadata import TechStackMetaData
from seven2one.core_config import TechStackConfig
from seven2one.dynamicobjects import DynamicObjects
from seven2one.utils.ut_graphql import GraphQLUtil
from seven2one.utils.defaults import Defaults
from seven2one.utils.ut_client import ClientUtil

from .fileimport import FileImport
from .workflow import Workflow
from .automation import Automation
from .schedule import Schedule
from .programming import Programming
from .authorization import Authorization
from .email import Email

from .utils.ut_log import LogUtils
from .utils.ut_timezone import TimeZoneUtil
from .utils.ut_structure import Structure
from .timeseries import TimeSeries

class TechStack(ITechStack):
    """
    Initializes a Seven2one TechStack client.

    Parameters:
    ----------
    host: str
        The host domain or ip address, e.g. 'app.organisation.com'
    client_id: str = None
        The client id belonging to the apps and specific for the system. If None, it needs to
        be entered interactively.
    service_account_name: str
        A techstack service account name. Leave blank to login interactively with user.
    service_account_secret: str = None
        The service account secret belonging to the service account and specific for the system. If None, it needs to
        be entered interactively.
    proxies: dict = None
        Provide one or more proxy addresses, e.g.: {'https':'159.98.7.123'} 
    usePorts: bool = False
        A developer feature: if True, ports with prefix '8' for a
        developer ComposeStack will be used.
    timeZone: str = None
        A time zone provided in IANA or isoformat (e.g. 'Europe/Berlin' or 'CET').
        Defaults to the local timezone. 
    dateTimeOffset: bool = True
        Choose, if a Timestamp should be displayed as time zone naive (dateTimeOffset = False) 
        or with Offset information. 
    raiseException: bool = False
        In default mode (False) exceptions will be avoided to provide better user experience.
        True is recommended in automated processes to avoid silent failures.
    copyGraphQLString: bool = False
        A developer feature: if True, with each method execution, 
        the graphQL string is copied to the clipboard (Windows only).

    Examples:
    >>> client = TechStack('app.orga.com/', client_id='...')
    >>> client = TechStack('app.orga.com/', client_id='...', service_account_name='my-service', service_account_secret='...')) 
    """

    _config: TechStackConfig = TechStackConfig()
    _metaData: TechStackMetaData = TechStackMetaData()

    @property
    def config(self) -> TechStackConfig:
        return self._config

    @config.setter
    def config(self, value: TechStackConfig) -> None:
        self._config = value

    @property
    def metaData(self) -> TechStackMetaData:
        return self._metaData

    @metaData.setter
    def metaData(self, value: TechStackMetaData) -> None:
        self._metaData = value
    
    @property
    def inventory(self) -> dict:
        return self._metaData.inventory
    
    @property
    def inventoryProperty(self) -> dict:
        return self._metaData.inventoryProperty
    
    @property
    def structure(self) -> dict:
        return self._metaData.structure
    
    @property
    def objects(self) -> dict:
        return self._metaData.objects
    
    @property
    def oAuthClient(self) -> OAuth2Authentication:
        return self._oAuthClient

    @oAuthClient.setter
    def oAuthClient(self, value: OAuth2Authentication) -> None:
        self._oAuthClient = value

    def get_access_token(self) -> str:
        return self.oAuthClient.get_access_token()
    
    def __init__(
        self,
        host: str,
        client_id: Optional[str] = None,
        service_account_name: Optional[str] = None,
        service_account_secret: Optional[str] = None,
        proxies: Optional[dict] = None,
        usePorts: bool = False,
        timeZone: Optional[str] = None,
        dateTimeOffset: bool = True,
        raiseException: bool = False,
        copyGraphQLString: bool = False
    ) -> None:

        def updateDynoSchema() -> None:
            self.updateClient()
        
        def updateTimeseriesSchema() -> None:
            self.TimeSeries.refreshSchema()

        self.config.raiseException = raiseException # self.raiseException = raiseException 
        warnings.filterwarnings('ignore', message="The zone attribute is specific to pytz")

        loglevelLocal = os.getenv("LOGLEVEL", "WARNING")
        loglevelServer = os.getenv("LOGLEVEL_SERVER", "ERROR")
        logToServer = strtobool(os.getenv("LOG_TO_SERVER", 'True').lower())
        sessionId = str(uuid4())

        try:
            logger.remove()

            if loglevelLocal in ['DEBUG', 'TRACE']:
                logger_format = "{level:<10} {time} {module}.{function} {line}: {message}"
                logger_diagnose = True
                logger_backtrace = True
            else:
                logger_format = "{level:<10} {time} {message}"
                logger_diagnose = False
                logger_backtrace = False

            def stdout_log_filter(record):
                return record["level"].no < logger.level('ERROR').no

            logger.add(sys.stdout, format=logger_format, level=loglevelLocal, catch=True,
                       diagnose=logger_diagnose, backtrace=logger_backtrace, filter=stdout_log_filter)
            logger.add(sys.stderr, format=logger_format, level='ERROR',
                       catch=True, diagnose=logger_diagnose, backtrace=logger_backtrace)
        except:
            pass

        if os.name == 'nt':
            logger.debug('Detected Windows, enabling pyperclip')
        else:
            logger.debug(f"Detected platform: {os.name}")

        if usePorts == False:
            idP_url = f'https://authentik.{host}'
            dynEndpoint = f'https://{host}/dynamic-objects/graphql/'
            workflowEndpoint = f'https://{host}/automation/graphql/'# TODO url in Workflow umbenennen, sobald die urls geändert werden
            scheduleEndpoint = f'https://{host}/schedule/graphql/'
            programmingEndpoint = f'https://{host}/programming/graphql/'
            tsGatewayEndpoint = f'https://{host}/timeseries/graphql/'
            logEndpoint = f'https://{host}/logging/loki/api/v1/push'
            authzEndpoint = f'https://{host}/authz/graphql/'
            emailEndpoint = f'https://{host}/emailservice/Email'
            automationEndpoint = f'https://{host}/automation-v2/graphql/' # TODO url in automation umbenennen, sobald die urls geändert werden
        else:
            idP_url = f'http://{host}:8044'
            dynEndpoint = f'http://{host}:8050/graphql/'
            workflowEndpoint = f'http://{host}:8120/graphql/'
            automationEndpoint = f'http://{host}:8125/graphql/'
            scheduleEndpoint = f'http://{host}:8130/graphql/'
            programmingEndpoint = f'http://{host}:8140/graphql/'
            tsGatewayEndpoint = f'http://{host}:8195/graphql/'
            logEndpoint = f'http://{host}:8175/loki/api/v1/push'
            authzEndpoint = f'http://{host}:8030/graphql/'
            emailEndpoint = f'http://{host}:8240/Email'

        idP_url = os.getenv("IDENDITYPROVIDER_URL", idP_url)
        dynEndpoint = os.getenv("DYNAMIC_OBJECTS_ENDPOINT", dynEndpoint)
        workflowEndpoint = os.getenv("WORKFLOW_ENDPOINT", workflowEndpoint)
        automationEndpoint = os.getenv("AUTOMATION_ENDPOINT", automationEndpoint)
        scheduleEndpoint = os.getenv("SCHEDULE_ENDPOINT", scheduleEndpoint)
        programmingEndpoint = os.getenv("PROGRAMMING_ENDPOINT", programmingEndpoint)
        tsGatewayEndpoint = os.getenv("TIMESERIES_ENDPOINT", tsGatewayEndpoint)
        logEndpoint = os.getenv("LOGGING_ENDPOINT", logEndpoint)
        authzEndpoint = os.getenv("AUTHORIZATION_ENDPOINT", authzEndpoint)
        
        if usePorts == True:
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        idp_discovery_urls = [
            f'{idP_url}/application/o/techstack',
            f'{idP_url}/application/o/questra']
        oidcDiscoveryClient = OidcDiscoveryClient(idp_discovery_urls)
        oidcDiscogeryResult = oidcDiscoveryClient.discover()
        
        if client_id is None:
            client_id = getpass.getpass('Enter client id: ')
        
        credentials: OAuth2Credential
        if service_account_name is None: # We are using device auth
            credentials = OAuth2InteractiveUserCredential()
        else: # We are using service auth
            if service_account_secret is None:
                service_account_secret = getpass.getpass('Enter secret: ')
            credentials = OAuth2ServiceCredential(service_account_name, service_account_secret)

        oAuthClient = OAuth2Authentication(client_id, credentials, oidcDiscogeryResult)
        oAuthClient.authenticate()
        self.oAuthClient = oAuthClient

        disbable_logging_oauth = os.getenv("LOGGING_ENDPOINT_OAUTH_ENABLED", '0') == '0'
        
        if logToServer:
            if os.getenv("LOG_SERVER") != None:
                logEndpoint = os.getenv("LOG_SERVER")
            
            if (logEndpoint == None):
                raise Exception("No log endpoint provided.")

            LogUtils._init_logging(logEndpoint, oAuthClient.get_access_token, loglevelServer, sessionId, disbable_logging_oauth)

        def getLocalTimeZone():
            local_now = datetime.datetime.utcnow().astimezone()
            if (local_now.tzinfo == None):
                raise Exception("Could not determine local time zone.")
            return local_now.tzinfo.tzname(local_now)
        logger.info(json.dumps({
            "SessionId": sessionId,
            "Configuration": {
                "host": host,
                "usePorts": usePorts,
                "timeZone": timeZone,
                "dateTimeOffset": dateTimeOffset,
                "raiseException": raiseException,
                "copyGraphQLString": copyGraphQLString,
                "logLevel": loglevelLocal,
                "logToServer": logToServer,
                "logLevelServer": loglevelServer
            },
            "System": {
                "timeZone": getLocalTimeZone(),
                "pythonVersion": sys.version,
                "machineName": os.getenv("HOSTNAME"),
                "osName": os.name
            }
        }))
        
        self.endpoint = dynEndpoint # self.endpoint = dynEndpoint
        self.config.proxies = proxies #self.proxies = proxies
        
        self.config.host = host # self.host = host
        client = ClientUtil._create_client(self, self.endpoint, oAuthClient.get_access_token)
        if (isinstance(client.introspection, dict)):
            self.metaData.scheme = client.introspection #self.scheme = self.client.introspection 

        # Defaults:
        if timeZone is None:
            timeZone = TimeZoneUtil.get_time_zone('local')

        self.config.defaults = Defaults(
            useDateTimeOffset=dateTimeOffset,
            copyGraphQLString=copyGraphQLString,
            timeZone=timeZone
        )

        # Get scheme
        if self.metaData.scheme == None:
            graphQLString = Structure.introspection_query_string()
            graphQLQueryResult = GraphQLUtil.execute_GraphQL(self, self.endpoint, graphQLString)
            if (isinstance(graphQLQueryResult, dict)):
                self.metaData.scheme = graphQLQueryResult
            else:
                raise Exception("Could not get scheme.")

        # Structures
        structure = GraphQLUtil.execute_GraphQL(self, self.endpoint, Structure.queryStructure)
        self.metaData.structure = Structure.full_structure_dict(structure)
        self.metaData.objects = Structure.full_Structure_NT(self.metaData.structure)
        self.metaData.inventory = Structure.inventory_NT(self.metaData.structure)
        self.metaData.inventoryProperty = Structure.inventory_Property_NT(self.metaData.structure)

        # Initialize further gateways
        self.DynamicObjects = DynamicObjects(dynEndpoint, self, updateDynoSchema, updateTimeseriesSchema)
        self.TimeSeries = TimeSeries(tsGatewayEndpoint, self, self.DynamicObjects)
        self.FileImport = FileImport(self, self.DynamicObjects, self.TimeSeries)
        self.Authorization = Authorization(authzEndpoint, self, self.DynamicObjects)
        self.Email = Email(emailEndpoint, self)
        self.Automation = Automation(automationEndpoint, self)
        self.Workflow = Workflow(workflowEndpoint, self, self.DynamicObjects)
        self.Schedule = Schedule(scheduleEndpoint, self, self.DynamicObjects)
        self.Programming = Programming(programmingEndpoint, self)

        def getVersions():

            worklow_available = automation_available = schedule_available = programming_available = True
            errors = []

            config_raiseException = self.config.raiseException
            self.config.raiseException = True

            versions = [
                self.getVersion(),
                self.TimeSeries.getVersion(),
                self.Authorization.getVersion(),
            ]

            # use try-except to catch errors, as only one autmation service may be available
            try:
                versions.append(self.Automation.getVersion())
            except Exception as e:
                automation_available = False
                errors.append(f"Could not get Version for automation service. Service might not be reachable, errormsg: {e}")

            try:
                versions.append(self.Workflow.getVersion())
            except Exception as e:
                worklow_available = False
                errors.append(f"Could not get Version for workflow service. Service might not be reachable, errormsg: {e}")

            try:
                versions.append(self.Schedule.getVersion())
            except Exception as e:
                schedule_available = False
                errors.append(f"Could not get Version for schedule service. Service might not be reachable, errormsg: {e}")

            try:
                versions.append(self.Programming.getVersion())
            except Exception as e:
                programming_available = False
                errors.append(f"Could not get Version for programming service. Service might not be reachable, errormsg: {e}")

            automation_v1_availabe = (worklow_available and schedule_available and programming_available)

            if not (automation_available or automation_v1_availabe):
                logger.warning("Could not get version information for any automation service. Detailed errors:")
                for error in errors:
                    logger.warning(error)                
            elif (automation_available != automation_v1_availabe):
                if automation_available:
                    logger.info("Automation service v2 is available, v1 is not.")
                else:
                    logger.info("Automation service v1 is available, v2 is not.")
            
            self.config.raiseException = config_raiseException   

            return versions
                
        logger.opt(lazy=True).debug("Service versions: {}", getVersions)

        return

    def getVersion(self) -> str:
        """
        Returns name and version of the responsible micro service
        """

        key = 'dynamicObjectsServiceInfo'
        graphQLString = f'''query version {{ 
            {key} {{
                name
                informationalVersion
            }}
        }}'''
        result = GraphQLUtil.execute_GraphQL(self, self.endpoint, graphQLString)
        if (result == None or (not isinstance(result, dict))):
            raise Exception("Could not get version information.")
        
        return f'{result[key]["name"]}: {result[key]["informationalVersion"]}'

    def updateClient(self) -> None:
        """
        Updates the client scheme and structures, e.g. after adding inventories
        or new inventory properties.
        """

        graphQLString = Structure.introspection_query_string()
        graphQLResult = GraphQLUtil.execute_GraphQL(self, self.endpoint, graphQLString)
        if (isinstance(graphQLResult, dict)):
            self.metaData.scheme = graphQLResult
        else:
            raise Exception("Could not get scheme.")
        structureResult = GraphQLUtil.execute_GraphQL(self, self.endpoint, Structure.queryStructure)
        self.metaData.structure = Structure.full_structure_dict(structureResult)
        self.metaData.objects = Structure.full_Structure_NT(self.metaData.structure)
        self.metaData.inventory = Structure.inventory_NT(self.metaData.structure)
        self.metaData.inventoryProperty = Structure.inventory_Property_NT(self.metaData.structure)

        return
    
    def inventories(
        self,
        fields: Optional[list] = None,
        where: Optional[str] = None,
        orderBy: Optional[str] = None,
        asc: bool = True
    ) -> Optional[pd.DataFrame]:
        return self.DynamicObjects.inventories(fields, where, orderBy, asc)

    def items(
        self,
        inventoryName: str, 
        references: bool = False, 
        fields: Union[list, str, None] = None,
        where: Union[list, tuple, str, None] = None, 
        orderBy: Union[dict, list, str, None] = None, 
        asc: Union[list, str, bool] = True, 
        pageSize: int = 5000, 
        arrayPageSize: int = 100000,
        top: int = 100000,
        validityDate: Optional[str] = None,
        allValidityPeriods: bool = False,
        includeSysProperties: bool = False,
        maxRecursionDepth = 2
    ) -> pd.DataFrame:
        return self.DynamicObjects.items(
            inventoryName, references, fields, where, orderBy, asc, pageSize, arrayPageSize, top, validityDate, allValidityPeriods, includeSysProperties, maxRecursionDepth
        )

    def inventoryProperties(
        self,
        inventoryName,
        namesOnly = False
    ) -> Union[pd.DataFrame, list, None]:
        return self.DynamicObjects.inventoryProperties(inventoryName, namesOnly)

    def propertyList(self, inventoryName: str, references = False, dataTypes = False, maxRecursionDepth = 2):
        return self.DynamicObjects.propertyList(inventoryName, references, dataTypes, maxRecursionDepth)

    def filterValues(
        self,
        inventoryName: str,
        top: int = 10000
    ) -> pd.DataFrame:
        return self.DynamicObjects.filterValues(inventoryName, top)

    def addItems(
        self,
        inventoryName: str, 
        items: list,
        chunkSize: int = 5000, 
        pause: int = 1
    ) -> list:
        return self.DynamicObjects.addItems(inventoryName, items, chunkSize, pause)

    def addValidityItemsToParents(
        self, 
        inventoryName: str, 
        items: list,
        chunkSize: int = 5000, 
        pause: int = 1
    ) -> list:
        return self.DynamicObjects.addValidityItemsToParents(inventoryName, items, chunkSize, pause)

    def updateItems(
        self,
        inventoryName: str,
        items: Union[list, dict]
    ) -> Optional[str]:
        return self.DynamicObjects.updateItems(inventoryName, items)

    def updateDataFrameItems(
        self,
        inventoryName: str,
        dataFrame: pd.DataFrame,
        columns: Optional[list] = None
    ) -> None:
        return self.DynamicObjects.updateDataFrameItems(inventoryName, dataFrame, columns)

    def createInventory(
        self,
        name: str,
        properties: list,
        variant: Optional[str] = None,
        propertyUniqueness: Optional[list] = None,
        historyEnabled: bool = False,
        hasValitityPeriods: bool = False,
        isDomainUserType: bool = False
    ) -> Optional[str]:
        return self.DynamicObjects.createInventory(name, properties, variant, propertyUniqueness, historyEnabled, hasValitityPeriods, isDomainUserType)

    def deleteInventories(
        self,
        inventoryNames: list,
        deleteWithData: bool = False,
        force: bool = False
    ) -> None:
        return self.DynamicObjects.deleteInventories(inventoryNames, deleteWithData, force)

    def variants(self) -> Optional[pd.DataFrame]:
        return self.DynamicObjects.variants()

    def deleteVariant(
        self,
        variantId: str,
        force: bool = False
    ) -> None:
        return self.DynamicObjects.deleteVariant(variantId, force)

    def deleteItems(
        self,
        inventoryName: str,
        inventoryItemIds: Optional[list] = None,
        where: Optional[str] = None,
        force: bool = False,
        pageSize: int = 500
    ) -> None:
        return self.DynamicObjects.deleteItems(inventoryName, inventoryItemIds, where, force, pageSize)

    def clearInventory(
        self,
        inventoryName: str,
        force: bool = False,
        pageSize: int = 500
    ) -> None:
        return self.DynamicObjects.clearInventory(inventoryName, force, pageSize)

    def updateVariant(
        self,
        variantName,
        newName = None,
        icon = None
    ) -> None:
        return self.DynamicObjects.updateVariant(variantName, newName, icon)

    def updateArrayProperty(
        self,
        inventoryName: str,
        inventoryItemId: str,
        arrayProperty: str,
        operation: str,
        arrayItems: Optional[list] = None,
        cascadeDelete: bool = False
    ) -> None:
        return self.DynamicObjects.updateArrayProperty(inventoryName, inventoryItemId, arrayProperty, operation, arrayItems, cascadeDelete)

    def addInventoryProperties(
        self,
        inventoryName: str,
        properties: list
    ) -> None:
        return self.DynamicObjects.addInventoryProperties(inventoryName, properties)

    def updateDisplayValue(
        self,
        inventoryName: str,
        displayValue: str
    ) -> None:
        return self.DynamicObjects.updateDisplayValue(inventoryName, displayValue)

    def updateInventoryName(
        self,
        inventoryName: str,
        newName: str
    ) -> None:
        return self.DynamicObjects.updateInventoryName(inventoryName, newName)

    def removeProperties(
        self,
        inventoryName: str,
        properties: list
    ) -> None:
        return self.DynamicObjects.removeProperties(inventoryName, properties)

    def updateProperty(
        self,
        inventoryName: str,
        propertyName: str,
        newPropertyName: Optional[str] = None,
        nullable: Optional[bool] = None
    ) -> None:
        return self.DynamicObjects.updateProperty(inventoryName, propertyName, newPropertyName, nullable)

    def resync(self) -> None:
        return self.DynamicObjects.resync()

    def defaultDataFrame(
        self,
        maxRows,
        maxColumns
    ) -> None:
        return self.DynamicObjects.defaultDataFrame(maxRows, maxColumns)

    def _convertId(
        self,
        sys_inventoryItemId: str
    ) -> Optional[str]:
        return self.DynamicObjects._convertId(sys_inventoryItemId)

    def _isInventoryOfValidVariant(
        self,
        inventoryName: str,
        variantName: Optional[str] = None
    ) -> Optional[bool]:
        return self.DynamicObjects._isInventoryOfValidVariant(inventoryName, variantName)
