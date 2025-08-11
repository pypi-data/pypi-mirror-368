from typing import Optional
from uuid import uuid4
import pandas as pd
from loguru import logger

from .utils.ut_graphql import GraphQLUtil
from .core_interface import ITechStack
from .dynamicobjects_interface import IDynamicObjects

class Schedule():
    def __init__(self, endpoint: str, techStack: ITechStack, dynamicObjects: IDynamicObjects) -> None:
        self.endpoint = endpoint
        self.techStack = techStack
        self.dynamicObjects = dynamicObjects

    def getVersion(self):
        """
        Returns name and version of the responsible micro service
        """

        return GraphQLUtil.get_service_version(self.techStack, self.endpoint, 'schedule')

    def _resolve_where(self, where: str):
        resolvedFilter = ''
        if where != None:
            resolvedFilter = f'{GraphQLUtil.resolve_where_dyno(self.techStack, self.dynamicObjects, where)["topLevel"]}'

        return resolvedFilter

    def schedules(
            self,
            workflowId: Optional[str] = None,
            fields: Optional[list] = None,
            where: Optional[str] = None,
            fireTimeOffset: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Returns schedules in a DataFrame

        Parameters:
        -----------
        workflowId: str = None
            The ID of the workflow to query schedules for. If None, all schedules will be queried.
        fields: list | str = None
            A list of all properties to be queried. If None, all properties will be queried.
        where: str = None
            Use a string to add where criteria like
            ''workflowId eq "meteoData"'.
        fireTimeOffset: str = None
            Use the fire time offset in ISO format to obtain the next fireTime after the specified time.

        Example:
        --------
        >>> Schedule.schedules(
                where='workflowId eq "meteoData"', 
                fields=['name', 'cron', 'timeZone'],
                fireTimeOffset=datetime(2024, 11, 21)
            )   
        """

        key = 'schedules'

        if fields != None:
            if type(fields) != list:
                fields = [fields]
            _fields = GraphQLUtil.query_fields(fields, recursive=True)
        else:
            _fields = f'''
                scheduleId
                name
                description
                workflowId
                businessKey
                cron
                timeZone
                isActive
                nextFireTime
                fireTimeAfterNext
                variables {{
                    key
                    value
                }}'''

        if workflowId != None:
            _workflowId = f'workflowId: "{workflowId}"'
        else:
            _workflowId = ''

        if fireTimeOffset != None:
            _fireTimeOffset = f'fireTimeOffset: "{fireTimeOffset}"'
        else:
            _fireTimeOffset = ''
        
        resolvedFilter = ''
        if where != None:
            resolvedFilter = self._resolve_where(where)

        # Ensure proper formatting of the GraphQL query
        parameters = ', '.join(filter(None, [_workflowId, _fireTimeOffset, resolvedFilter]))
        if parameters:
            parameters = f'({parameters})'

        graphQLString = f'''query schedules {{
            {key}{parameters} {{
            {_fields}
            }}
        }}
        '''
        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        if result == None:
            return
        elif not isinstance(result, dict):
            return

        df = pd.json_normalize(result[key])
        return df

    def createSchedule(self, name: str, workflowId: str, businessKey: str, cron: str,
                       isActive: bool = True, description: Optional[str] = None, variables: Optional[dict] = None, timeZone: Optional[str] = None) -> Optional[str]:
        """Creates a schedule and returns the schedule Id"""

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            if isActive == True:
                isActiveStr = 'true'
            else:
                isActiveStr = 'false'

            if description != None:
                description = description
            else:
                description = ''

            if timeZone == None:
                timeZone = ''

            if variables != None:
                _variables = 'variables: [\n'
                for k, v in variables.items():
                    _variables += f'{{key: "{k}", value: "{v}"}}\n'
                _variables += ']'
            else:
                _variables = ''

            graphQLString = f'''mutation createSchedule {{
                createSchedule(input:{{
                    name: "{name}"
                    workflowId: "{workflowId}"
                    businessKey: "{businessKey}"
                    cron: "{cron}"
                    timeZone: "{timeZone}"
                    description: "{description}"
                    isActive: {isActiveStr}
                    {_variables}      
                }})
                {{
                    schedule {{
                        scheduleId
                    }}
                    errors {{
                        message
                    }}
                }}
            }}'''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            logger.debug(graphQLString)
            if result == None:
                return
            elif not isinstance(result, dict):
                return

            key = 'createSchedule'
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)
                return None
            else:
                scheduleId = result[key]['schedule']['scheduleId']
                logger.info(f"New schedule {scheduleId} created.")

            return scheduleId

    def updateSchedule(self, scheduleId, name: Optional[str] = None, workflowId: Optional[str] = None, businessKey: Optional[str] = None,
                       cron: Optional[str] = None, isActive: Optional[bool] = None, description: Optional[str] = None, variables: Optional[dict] = None, timeZone: Optional[str] = None) -> None:
        """
        Updates a schedule. Only arguments that ar not None will overwrite respective fields.

        Parameters:
        -----------
        scheduleId : str
            The Id of the schedule that is to be updated.
        name : str
            The name of the schedule.
        workflowId : str
            The Id of the workflow that shall be executed with this schedule.
        cron : str
            The cron expression. For detailed information loop up
            http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html
        isActive : bool
            Determines, if the schedule should execute the workflow or not.
        description : str
            A description of the schedule.
        variables : dict
            A dictionary of variables that are used by tasks in the workflow.
        timeZone : str
            IANA time zone Id the schedule cron is evaluated in. If empty the installed default is used.
            e.g. 'Europe/Berlin', 'UTC'

        Example:
        --------
        >>> vars = {
                'var1': 99,
                'var2': "AnyString"
            }
        >>> client.Scheduler.updateSchedule('112880211090997248', name='test_schedule',
                isActive=True, variables=vars)

        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            updateScheduleArgs = ''

            if name != None:
                updateScheduleArgs += f'name: "{name}"\n'
            if workflowId != None:
                updateScheduleArgs += f'workflowId: "{workflowId}"\n'
            if businessKey != None:
                updateScheduleArgs += f'businessKey: "{businessKey}"\n'
            if cron != None:
                updateScheduleArgs += f'cron: "{cron}"\n'
            if isActive != None:
                updateScheduleArgs += f'isActive: {str(isActive).lower()}\n'
            if description != None:
                updateScheduleArgs += f'description: "{description}"\n'
            if timeZone != None:
                updateScheduleArgs += f'timeZone: "{timeZone}"\n'

            if variables != None:
                _variables = 'variables: [\n'
                for k, v in variables.items():
                    _variables += f'{{key: "{k}", value: "{v}"}}\n'
                _variables += ']'
                updateScheduleArgs += _variables

            graphQLString = f'''mutation updateSchedule {{
                updateSchedule(
                    scheduleId: "{scheduleId}"
                    input:{{
                        {updateScheduleArgs}
                }})
                {{
                    errors {{
                        message
                    }}
                }}
            }}'''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            logger.debug(graphQLString)
            if result == None:
                return
            elif not isinstance(result, dict):
                return

            key = 'updateSchedule'
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)
            else:
                logger.info(f"Schedule {scheduleId} updated.")

            return

    def deleteSchedule(self, scheduleId: str, force: bool = False):
        """Deletes a schedule"""

        confirm = None
        if force == False:
            confirm = input(f"Press 'y' to delete schedule '{scheduleId}': ")

        graphQLString = f'''mutation deleteSchedule {{
            deleteSchedule (scheduleId: "{scheduleId}")
            {{
                errors {{
                message
                }}
            }}
        }}
        '''

        if force == True:
            confirm = 'y'
        if confirm == 'y':
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            if result == None:
                return
            elif not isinstance(result, dict):
                return
            
            key = 'deleteSchedule'
            if result[key]['errors']:
                GraphQLUtil.list_graphQl_errors(result, key)
            else:
                logger.info(f"Schedule {scheduleId} deleted")

    def nextFireTimes(self, workflowIds: Optional[list] = None, businessKeys: Optional[list] = None, fromTimepoint: Optional[str] = None, 
                      toTimepoint: Optional[str] = None, count: Optional[int] = None):
        
        """
        Show next fire times of a workflow. Returns a DataFrame with the schedule ID and fire time.

        Parameters:
        -----------
        workflowIds: list| str = None
            List of workflow IDs to query the next fire times for. If None, all workflow IDs will be queried.
        businessKeys: list| str = None
            List of business keys to query the next fire times for. If None, all business keys will be queried.
        fromTimepoint: str = None
            The starting timepoint for the query in ISO format. Defaults to the current time.
        toTimepoint: str = None
            The ending timepoint for the query in ISO format. Defaults to three days from the current time.
        count: int = None
            The number of fire times to retrieve. If None, then there is limit to the quantity.

        Example:
        --------
        >>> client.Schedule.nextFireTimes(workflowIds=['112880211090997248', '112880211090997249], businessKeys=['key1', 'key2'],
            fromTimepoint='2022-01-01T00:00:00Z', toTimepoint='2022-01-02T00:00:00Z', count=10)
        """
        
        key = 'nextFireTimes'

        _fields = f'''
            scheduleId
            fireTime
        '''

        if workflowIds != None:
            _workflowIds = f'workflowIds: {GraphQLUtil.graphQL_list(workflowIds)}'
        else:
            _workflowIds = ''

        if businessKeys != None:
            _businessKeys = f'businessKeys: {GraphQLUtil.graphQL_list(businessKeys)}'
        else:
            _businessKeys = ''

        if fromTimepoint != None:
            _fromTimepoint = f'from: "{fromTimepoint}"'
        else:
            _fromTimepoint = ''

        if toTimepoint != None:
            _toTimepoint = f'to: "{toTimepoint}"'
        else:
            _toTimepoint = ''
        
        if count != None:
            _count = f'count: {count}'
        else:
            _count = ''

        #Ensure proper formatting of the GraphQL query
        parameters = ', '.join(filter(None, [_workflowIds, _businessKeys, _fromTimepoint,
                                            _toTimepoint, _count]))
        if parameters:
            parameters = f'({parameters})'
        
        graphQLString = f'''query nextFireTimes {{
            {key}{parameters} {{
                {_fields}
            }}
        }}
        '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        if result == None:
            return
        elif not isinstance(result, dict):
            return
        
        df = pd.json_normalize(result['nextFireTimes'])

        return df
