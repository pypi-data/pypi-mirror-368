from typing import Optional
import pandas as pd
import json
import os
from loguru import logger
from uuid import uuid4

from .utils.ut_autprog import AutProgUtils
from .utils.ut_graphql import GraphQLUtil
from seven2one.core_interface import ITechStack

class Programming():

    def __init__(self, endpoint: str, techStack: ITechStack) -> None:

        self.techStack = techStack
        self.endpoint = endpoint
        return

    def getVersion(self):
        """
        Returns name and version of the responsible micro service
        """

        return GraphQLUtil.get_service_version(self.techStack, self.endpoint, 'programming')

    def functions(self) -> Optional[pd.DataFrame]:
        """ Get available programming service functions"""

        graphQLString = f'''query functions {{
            functions {{
                name
                functionId
                languageVersion
                }}
            }}
        '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        if result == None:
            return
        elif (not isinstance(result, dict)):
            return
        
        df = pd.json_normalize(result['functions'])
        return df

    def createFunction(
        self,
        name: str,
        languageVersion: str,
        description: Optional[str] = None,
        files: Optional[list] = None,
        deploy: bool = False,
        deploymentName: Optional[str] = None,
        envVars: Optional[dict] = None,
        memoryLimit: str = '250Mi',
        cpuLimit: float = 0.2,
        secrets: Optional[list] = None
    ) -> Optional[str]:
        """ 
        Creates a function with possibility to commit files and deployment
        in one step. The function Id is returned.

        Parameters:
        ----------
        name : str
            The name of the function, which is also taken for deployment, if the option is 
            chosen. The deployment function name is converted to small letters. Special characters 
            will be removed.
        languageVersion : str
            Choose between a languange and its version, e.g. 'PYTHON_3_9' and 'CSHARP_NET_6_0'.
        description : str
            Additional description to the function.
        files : list
            A list of full file paths to be committed.
        deploy : bool
            If True, the function will be deployed. The files argument must not be 
            None in this case.
        deploymentName:
            The name of the deployed function. If left to default (None) the function name 
            will be used. Use small letters only and no special characters.
        envVars : dict
            A Dictionary of Environment variables provided to the deployment function. All values
            will be converted to string.
        secrets: list = None
            A list of kubernetes secrets to be provided to the deployment function. 
            The secrets have to exist in the function's namespace.
            Secrets of type 'Opaque' are mounted automatically inside the function container at
            /var/openfaas/secrets/<key> as file(s) with the value as content.

        Examples of a function for Python:
        ---------
        >>> createFunction('myfunction', 'PYTHON_3_9')
        >>> files = [path1, path2, path3]
            vars = {'var1': 42, 'var2': 'full_scale'}
            createFunction('myfunction', 'PYTHON_3_9', files=files, deploy=True, 
                envVars=vars)
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            graphQLString = f'''mutation createFunction {{
                createFunction(input:{{
                    name: "{name}"
                    languageVersion: {languageVersion}
                    description: "{description}"
                    }}) {{
                    functionId
                    errors {{
                        message
                        code
                        }}
                    }}
                }}
            '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            elif not isinstance(result, dict):
                return

            if result['createFunction']['errors']:
                GraphQLUtil.list_graphQl_errors(result, 'createInventory')
                return

            functionId = result['createFunction']['functionId']

            if files == None:
                logger.info(
                    f"Function with id {functionId} created. No files committed")
                return functionId
            else:
                if type(files) != list:
                    msg = "Files must be of type list!"
                    if self.techStack.config.raiseException:
                        raise Exception(msg)
                    else:
                        logger.error(msg)
                        return

                self.commitFunctionFiles(functionId, files)
                logger.info(f"Function with id {functionId} created.")
                if deploy == False:
                    return functionId
                else:
                    if deploymentName == None:
                        deploymentName = name.lower()
                    self.deployFunction(
                        functionId, deploymentName, envVars, memoryLimit, cpuLimit, secrets)
                    return functionId

    def commitFunctionFiles(
        self,
        functionId: str,
        files: Optional[list] = None,
        deploy: bool = False,
        deploymentName: Optional[str] = None,
        envVars: Optional[dict] = None,
        memoryLimit: str = '250Mi',
        cpuLimit: float = 0.2,
        secrets: Optional[list] = None
    ) -> None:
        """
        Upload programming files to an existing function. 

        Parameters:
        ----------
        functionId : str
            Id of an existing function.
        files : list
            A list of full file paths to be committed.
        deploy : bool
            If True, the function will be deployed after committing the files. 
        deploymentName:
            The name of the deployed function. Use small letters only and no special characters.
        envVars : dict
            A dictionary of environment variables provided to the deployed function. All values
            will be converted to string.
        memoryLimit: str = '250Mi'
            The memory that is assigned for execution of this function. 
        cpuLimit: float = 0.2
            The assigned amount of CPU capacity to this function: note, that a too high capacity
            might affect other services negatively.
        secrets: list = None
            A list of kubernetes secrets to be provided to the deployment function. 
            The secrets have to exist in the function's namespace.
            Secrets of type 'Opaque' are mounted automatically inside the function container at
            /var/openfaas/secrets/<key> as file(s) with the value as content.


        Example:
        --------
        >>> files = [path1, path2, path3]
            vars = {'var1': 42, 'var2': 'full_scale'}
            commitFunctionFiles('3dba276e3c8645838c2d598043cab057', files=files, deploy=True, 
                deploymentName='myfunction', envVars=vars)
        """
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            if (files == None):
                return
            fileList = AutProgUtils._upsetFiles(files)
            if fileList == None:
                return

            graphQLString = f'''mutation commitFunctionFiles {{
                commitFunctionFiles(input:{{
                    functionId: "{functionId}"
                    upsetFiles: [
                        {fileList}
                    ]

                    }}) {{
                    errors {{
                        message
                        code
                        }}
                    }}
                }}
            '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            else:
                logger.info(
                    f"Committed files: {AutProgUtils._getFileNames(files)}")
                if deploy == False:
                    return
                else:
                    if deploymentName == None:
                        msg = f"No deployment name was provided for deployment. Function id: {functionId}"
                        if self.techStack.config.raiseException:
                            raise Exception(msg)
                        else:
                            logger.error(msg)
                            return
                    self.deployFunction(functionId, deploymentName, envVars, memoryLimit, cpuLimit, secrets)

            return

    def deployFunction(
            self,
            functionId: str,
            deploymentName: str,
            envVars: Optional[dict] = None,
            memoryLimit: str = '250Mi',
            cpuLimit: float = 0.2,
            secrets: Optional[list] = None):
        """
        Deploys a function to make it executable.

        Parameters:
        ----------
        functionId: str
            Id of an existing function.
        deploymentName:
            The name of the deployed function. Use small letters only and no special characters.
        envVars: dict = None
            A Dictionary of Environment variables provided to the deployment function. 
        memoryLimit: str = '250M'
            The memory that is assigned for execution of this function.   
        cpuLimit: loat = 0.2
            The assigned amount of CPU capacity to this function: note, that a too high capacity
            might affect other services negatively.
        secrets: list = None
            A list of kubernetes secrets to be provided to the deployment function. 
            The secrets have to exist in the function's namespace.
            Secrets of type 'Opaque' are mounted automatically inside the function container at
            /var/openfaas/secrets/<key> as file(s) with the value as content.

        Example:
        --------
        >>> vars = {'exec_timeout': '2m', 'read_timeout': '2m','write_timeout': '2m'}
            deployFunction('3dba276e3c8645838c2d598043cab057', deploymentName=myfunction, 
            automationTopic='autFunction', envVars=vars)
        """
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            if envVars == None:
                _vars = ''
            else:
                _vars = AutProgUtils._varsToString(envVars, 'env')

            if secrets == None:
                _secrets = ''
            else:
                _secretsStrings = [f"\"{s}\"" for s in secrets]
                _secrets = f"secrets: [{','.join(_secretsStrings)}]"

            graphQLString = f'''mutation deployFunction {{
                deployFunction(
                    input: {{
                    functionId: "{functionId}"
                    functionName: "{deploymentName}"
                    memoryLimit: "{memoryLimit}"
                    cpuLimit: "{str(cpuLimit)}"
                    {_vars}
                    {_secrets}
                    }}
                ) {{
                    deploymentId
                    errors {{
                        code
                        message
                        }}
                    }}
                }}
                '''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            if result == None:
                return
            elif not isinstance(result, dict):
                return
            else:
                deploymentId = result['deployFunction']['deploymentId']
                logger.info(
                    f"Deployed function with deploymentId {deploymentId}")
                return deploymentId

    def functionFiles(self, functionId: str, downloadPath: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Shows files of a function.

        Parameters:
        ----------
        functionId : str
            Id of an existing function.

        Example:
        --------
        >>> functionFiles('3dba276e3c8645838c2d598043cab057')
        """

        if downloadPath == None:
            _contentBase64 = ''
        else:
            _contentBase64 = 'contentBase64'

        graphQLString = f''' query functionFiles {{
            functionFiles (functionId: "{functionId}") {{
                version
                files {{
                    fullname
                    {_contentBase64}
                    }}
                }}
            }}
        '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        if result == None:
            return
        elif not isinstance(result, dict):
            return

        df = pd.json_normalize(result['functionFiles'], meta=[
                               'version'], record_path=['files'])

        if downloadPath != None:
            if os.path.exists(downloadPath) == False:
                msg = f"Download path '{downloadPath}' does not exist."
                if self.techStack.config.raiseException:
                    raise Exception(msg)
                else:
                    logger.error(msg)
                    return

            else:
                fileList = []
                for file in result['functionFiles']['files']:
                    AutProgUtils._downloadFunctionFile(
                        downloadPath, file['fullname'], file['contentBase64'])
                    fileList.append(file['fullname'])
                logger.info(f"Downloaded {fileList} to {downloadPath}")
                del df['contentBase64']

        return df

    def executeFunction(self, deploymentId: str, inputVariables: Optional[dict] = None) -> Optional[dict]:
        """
        Executes a function

        Parameters:
        ----------
        deploymentId : str
            Id of a deployment. Can be retrieved by Programming.deployments().

        Example:
        --------
        >>> executeFunction('c877cc1b568a4c489aacdb4538b3f544')
        """
        correlationId = str(uuid4())
        context_logger = logger.bind(correlation_id=correlationId)

        if inputVariables == None:
            _vars = ''
        else:
            _vars = GraphQLUtil.to_graphql(json.dumps(inputVariables))

        graphQLString = f''' mutation executeFunction {{
            executeFunction(
                input: {{ 
                    deploymentId: {GraphQLUtil.to_graphql(deploymentId)},
                    input: {_vars}
                    }}
            ) {{
                executionId
                result {{
                    output
                    errorMessage
                    hasError
                }}
                errors {{
                    code
                    message
                    }}
                }}
            }}
        '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
        context_logger.info("Executed function with result {}", result)

        if result == None:
            return
        elif not isinstance(result, dict):
            return
        return result

    def deleteFunction(self, functionId: str, force: bool = False) -> Optional[dict]:
        """
        Deletes a function.

        Parameters:
        ----------
        functionId : str
            Id of the function to be deleted.
        force : bool
            Use True to ignore confirmation.

        Example:
        --------
        >>> executeFunction('3dba276e3c8645838c2d598043cab057')
        """
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            confirm = None
            if force == False:
                confirm = input(
                    f"Press 'y' to delete  function with id {functionId}")

            graphQLString = f''' mutation deleteFunction {{
                deleteFunction (input: {{
                    functionId: "{functionId}"
                }}) {{
                    errors {{
                        message
                    }}
                }}
            }}
            '''

            if force == True:
                confirm = 'y'
            if confirm == 'y':
                result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
                logger.info("Deleted function with result {}", result)
            else:
                return
            if result == None:
                return
            elif not isinstance(result, dict):
                return
            return result

    def deployments(self, functionId: str, fields: list = []) -> Optional[pd.DataFrame]:
        """
        Shows deployments of a function as a DataFrame.
        Parameters:
        ----------
        functionId : str
            Id of the function.
        fields: list = []
            A list of fields to be queried. If None, all properties but 'log' will be queried.
            Available fields are: 'functionAggregateId', 'functionAggregateVersion', 'deploymentId', 'functionName', 'log', 'state'
        Example:
        --------
        >>> deployments('77725d50-78b5-4a16-992b-7f68f2dd261f')
        >>> deployments(
                '77725d50-78b5-4a16-992b-7f68f2dd261f',
                fields=['deploymentId', 'functionName', 'state']
                )
        >>> df = deployments('77725d50-78b5-4a16-992b-7f68f2dd261f', fields=['log'])
            logs = df['log'].values[0]
        """
        allFields = ['functionAggregateId', 'functionAggregateVersion', 'deploymentId', 'functionName', 'log', 'state']
        if not fields:
            fields = allFields.copy()
            fields.remove('log')
        else:
            for field in fields:
                if field not in allFields:
                    msg = f"Field '{field}' is not available. Choose from {allFields}"
                    if self.techStack.config.raiseException:
                        raise Exception(msg)
                    else:
                        logger.error(msg)
                        return

        graphQLString = f'''query deployments($functionId: UUID!) {{
            deployments(functionId: $functionId) {{
                    {' '.join(fields)}
                }}
            }}
            '''
        
        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, params={"functionId": functionId})
        if result == None:
            return
        if (not isinstance(result, dict)):
            return
        
        df = pd.json_normalize(result['deployments'])
        return df
