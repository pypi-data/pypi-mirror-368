from typing import Optional, Union
from uuid import uuid4
import pandas as pd
from loguru import logger

from .dynamicobjects_interface import IDynamicObjects
from .utils.ut_graphql import GraphQLUtil
from .utils.ut_autprog import AutProgUtils
from .core_interface import ITechStack

class Workflow():

    def __init__(self, endpoint: str, techStack: ITechStack, dynamicObjects: IDynamicObjects) -> None:
        self.endpoint = endpoint
        self.techStack = techStack
        self.dynamicObjects = dynamicObjects

    def getVersion(self):
        """
        Returns name and version of the responsible micro service
        """

        return GraphQLUtil.get_service_version(self.techStack, self.endpoint, 'automation')

    def _resolve_where(self, where: str):
        resolvedFilter = ''
        if where != None:
            resolvedFilter = GraphQLUtil.resolve_where_dyno(self.techStack, self.dynamicObjects, where)["topLevel"]

        return resolvedFilter

    def workflows(self) -> Optional[pd.DataFrame]:
        """Returns a DataFrame of all Workflows"""

        graphQLString = f'''query workflows {{
            workflows {{
                id
                name
                description
                }}
            }}
            '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        if result == None:
            return
        if (not isinstance(result, dict)):
            return
        
        df = pd.json_normalize(result['workflows'])
        return df

    def workflowInstances(self, workflowId: Optional[str] = None, fromTimepoint: Optional[str] = None, toTimepoint: Optional[str] = None,
                          fields: Optional[list] = None, where: Optional[str] = None, distinctBy: Union[list, str, None] = None, showTasks=False, 
                          skip=0, maxResults=50) -> Optional[pd.DataFrame]:
        """Shows Instances of a workflow. If workflowId=None, all Instances of all workflows will be returned.

        Parameters:
        -----------
        workflowId : str
            The id of the workflow.
        fromTimepoint : str
            Filter on instances started after this timepoint (format: "%Y-%m-%dT%H:%M:%S.%fZ").
        toTimepoint : str
            Filter on instances ended before this timepoint (format: "%Y-%m-%dT%H:%M:%S.%fZ").
        fields : list
            A list of all properties to be queried. If None, all properties will be queried.
        where : str
            Filter based on query string. Examples: 'state eq COMPLETED', 
        distinctBy : list | str = None
            Remove duplicates of the given properties. Only entities with at least one unique value will be returned.
        showTasks : bool
            If True, the tasks of the workflow instances will be shown.
        skip : int
            Offset pagination: skip the first n instances.
        maxResults : int
            Offset pagination: take up to the first n instances.

        Examples:
        ---------
        >>> client.Automation.workflowInstances(workflowId='workflowId', where='state eq COMPLETED', 
            distinctBy=['businessKey'], fields=['id', 'name', 'state', 'businessKey'])
        """

        meta: list = ['id', 'name', 'businessKey', 'version', 'startTime', 'endTime', 'state']
        key = 'workflowInstances'

        if workflowId != None:
            _workflowId = f'workflowId: "{workflowId}"'
        else:
            _workflowId = ''

        if fromTimepoint != None:
            _fromTimepoint = f'from: "{fromTimepoint}"'
        else:
            _fromTimepoint = ''

        if toTimepoint != None:
            _toTimepoint = f'to: "{toTimepoint}"'
        else:
            _toTimepoint = ''

        if fields != None:
            if type(fields) != list:
                fields = [fields]
            _fields = GraphQLUtil.query_fields(fields, recursive=True)
        else:
            _fields = f'''
                id
                workflowId
                name
                businessKey
                version
                startTime
                endTime
                duration
                state
                variables {{
                    name
                    value
                    time
                }}'''

        resolvedFilter = ''
        if where != None:
            resolvedFilter = self._resolve_where(where)

        if distinctBy != None:
            _distinctBy = f'distinctBy: {GraphQLUtil.to_graphql(distinctBy)}'
        else:
            _distinctBy = ''

        if showTasks != False:
            _tasks = f'''tasks {{
                            id
                            topic
                            workerId
                            timestamp
                            state
                            retries
                            errorMessage
                        }}'''
        else:
            _tasks = ''

        graphQLString = f'''query Instances {{
            {key}(skip: {skip} take: {maxResults} {_workflowId} {_fromTimepoint} {_toTimepoint} {resolvedFilter} {_distinctBy}) {{
            items {{
                {_fields}
                {_tasks}
                }}
            }}
        }}
        '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        if result == None:
            return
        if (not isinstance(result, dict)):
            return
        
        if showTasks != False:
            df = pd.json_normalize(result[key]['items'], meta=meta, record_path=['tasks'], record_prefix='task.', errors='ignore')
            if 'startTime' in df.columns:
                df = df.sort_values(by='startTime', ascending=False)
        else:
            df = pd.json_normalize(result[key]['items'])
            if 'startTime' in df.columns:
                df = df.sort_values(by='startTime', ascending=False)
        return df

    def createWorkflow(self, id, name, description: Optional[str] = None):

        correlationId = str(uuid4())
        context_logger = logger.bind(correlation_id=correlationId)

        graphQLString = f'''mutation createWorkflow {{
            createWorkflow(
                input: {{
                    id: "{id}"
                    name: "{name}"
                    description: "{description}"
                }}
                ) {{
                    ...on CreateWorkflowError {{
                    message
                    }}
                    ... on WorkflowCreated {{
                        workflow {{
                            id
                        }}
                    }}
                }}
            }}
        '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        if result == None:
            return

        context_logger.info(f"New workflow {id} created.")

        return result

    def deployWorkflow(self, workflowId: str, filePath: str):
        """Deploys a Camunda XML to an existing workflow"""

        correlationId = str(uuid4())
        context_logger = logger.bind(correlation_id=correlationId)

        fileContent = AutProgUtils._encodeBase64(filePath)
        context_logger.debug(f"fileContent: {fileContent[:10]}")

        graphQLString = f'''mutation deployWorkflow {{
            deployWorkflow(
                input: {{
                    fileContentBase64: "{fileContent}"
                    workflowId: "{workflowId}"
                }}
            ) {{
                ... on DeployWorkflowError {{
                    message
                }}
                ... on InvalidWorkflowProcessId {{
                    processId
                    workflowId
                    message
                }}
                ... on WorkflowDeployed {{
                    version
                }}
            }}
        }}
        '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        if result == None:
            return

        context_logger.info(f"Workflow '{workflowId}' deployed.")
        return result

    def startWorkflow(self, workflowId: str, businessKey: str, inputVariables: Optional[dict] = None):
        """Starts a workflow"""

        correlationId = str(uuid4())
        context_logger = logger.bind(correlation_id=correlationId)

        if inputVariables == None:
            _vars = ''
        else:
            _vars = AutProgUtils._varsToString(inputVariables, 'input')

        graphQLString = f'''
            mutation ExecuteWF {{
                startWorkflow(input: {{ 
                    businessKey: "{businessKey}"
                    workflowId: "{workflowId}" 
                    {_vars}
                    }}
                ) {{
                    ... on ProcessDefinitionNotFound {{
                        workflowId
                        message
                        }}
                    ... on StartWorkflowError {{
                            message
                            }}
                    ... on WorkflowStarted {{
                        workflowInstanceId
                        }}
                    }}
                }}
            '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        if result == None:
            return

        context_logger.info(f"Workflow {workflowId} started.")

        return result

    def deleteWorkflow(self, workflowId: str):
        """Deletes a workflow"""

        correlationId = str(uuid4())
        context_logger = logger.bind(correlation_id=correlationId)

        graphQLString = f'''mutation deleteWorkflow {{
            deleteWorkflow (id: "{workflowId}")
            {{
                ... on DeleteWorkflowError {{
                    message
                    }}
                ...on WorkflowDeleted {{
                    success
                    }}
                ... on WorkflowNotFound {{
                    workflowId
                    message
                    }}
                
                }}
            }}
        '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        context_logger.info(f"Workflow {workflowId} deleted.")
        return result

    def terminateWorkflowInstance(self, workflowInstanceId):
        """Terminates a workflow instance"""

        correlationId = str(uuid4())
        context_logger = logger.bind(correlation_id=correlationId)

        graphQLString = f'''mutation terminateWorkflowInstance {{
            terminateWorkflowInstance(
                workflowInstanceId:"{workflowInstanceId}") {{
                ...on TerminateWorkflowInstanceError {{
                    message
                    }}
                ...on WorkflowInstanceNotFound {{
                    workflowInstanceId
                    message
                    }}
                ...on WorkflowInstanceTerminated {{
                    success
                    }}
                }}
            }}
        '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        context_logger.info(f"Workflow instance {workflowInstanceId} started.")
        return result

    def updateWorkflow(self, workflowId: str, name: Optional[str] = None, description: Optional[str] = None):
        """Updates a workflow (name and description can be changed)"""

        correlationId = str(uuid4())
        context_logger = logger.bind(correlation_id=correlationId)

        name = GraphQLUtil.arg_none('name', name)
        description = GraphQLUtil.arg_none('description', description)

        key = 'updateWorkflow'
        graphQLString = f'''mutation updateWorkflow {{
            {key}(workflowId: "{workflowId}", properties: {{
                {description}
                {name}
                }}) {{
                    ... on UpdateWorkflowError {{
                    message
                    }}
                    ... on WorkflowNotFound {{
                    workflowId
                    message
                    }}
                    ... on WorkflowUpdated {{
                    workflow {{
                        id
                        name
                        description
                        }}
                    }}
                }}
            }}
            '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        context_logger.info(f"Workflow {workflowId} updated.")
        return result

    def retryTasks(self, externalTaskIds: list):
        """
        Retries task instances of a workflow instance.

        Parameters:
        ----------
        externalTaskIds: list
            External task ids of the tasks to be retried.
        
        Remark: Get ids from instances in state INCIDENT like this:
        >>> ids = workflowInstances(workflow_id, where='state eq INCIDENT', fields='tasks.id')
        >>> retryTasks(['2fb2bd12-9b61-11ee-81c2-7eb9c6d765ed', '52e9c8b9-9b61-11ee-81c2-7eb9c6d765ed'])
        """
        key = 'retryTasks'

        correlationId = str(uuid4())
        context_logger = logger.bind(correlation_id=correlationId)

        graphQLString = f'''mutation retryTasks($ids: [String]!) {{
            {key}(externalTaskIds: $ids) {{
                ... on RetryTasksError {{
                    message
                }}
                ...on TasksNotFound {{
                    message
                }}
                ... on TasksRetried {{
                    success
                }}
            }}
        }}
        '''
        params = {
            "ids": externalTaskIds
        }

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId=correlationId, params=params)
        context_logger.info(f"Tasks {','.join(externalTaskIds)} retried.")
        return result

    def retryTask(self, externalTaskId):
        """
        Retries a task instance of a workflow instance.

        Parameters:
        ----------
        externalTaskId: str
            External task id of the task to be retried.
        
        Example:
        >>> retryTask('2fb2bd12-9b61-11ee-81c2-7eb9c6d765ed')
        """
        return self.retryTasks([externalTaskId])

    def countWorkflowInstances(self, workflowId: Optional[str] = None, fromTimepoint: Optional[str] = None, toTimepoint: Optional[str] = None,
                               where: Optional[str] = None) -> Optional[int]:
        """Returns the number of workflow instances

        Parameters:
        -----------
        workflowId : str
            The id of the workflow.
        fromTimepoint : str
            Filter on instances started after this timepoint (format: "%Y-%m-%dT%H:%M:%S.%fZ").
        toTimepoint : str  
            Filter on instances ended before this timepoint (format: "%Y-%m-%dT%H:%M:%S.%fZ").
        where : str
            Filter based on query string. 
        
        Examples: 
        ----------
        >>> client.Automation.countWorkflowInstances(workflowId='workflowId', where='state eq COMPLETED')
        """

        key = 'countWorkflowInstances'

        if workflowId != None:
            _workflowId = f'workflowId: "{workflowId}"'
        else:
            _workflowId = ''

        if fromTimepoint != None:
            _fromTimepoint = f'from: "{fromTimepoint}"'
        else:
            _fromTimepoint = ''

        if toTimepoint != None:
            _toTimepoint = f'to: "{toTimepoint}"'
        else:
            _toTimepoint = ''

        resolvedFilter = ''
        if where != None:
            resolvedFilter = self._resolve_where(where)

        # Ensure proper formatting of the GraphQL query
        parameters = ', '.join(filter(None, [_workflowId, _fromTimepoint, _toTimepoint, resolvedFilter]))
        if parameters:
            parameters = f'({parameters})'        

        graphQLString = f'''query countWorkflowInstances {{
            {key}{parameters} {{
                count
                }}
        }}
        '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        if result == None:
            return
        elif (not isinstance(result, dict)):
            raise Exception("Result is not a dictionary.")
        
        return result[f'{key}']['count']