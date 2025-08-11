from typing import Optional, Union
from uuid import uuid4
import pandas as pd
from loguru import logger

from .utils.ut_graphql import GraphQLUtil
from .core_interface import ITechStack
from .utils.ut_autom_enums import TriggerType, ExecutionStatus, LimitType


class Automation():

    def __init__(self, endpoint: str, techStack: ITechStack) -> None: 
        self.endpoint = endpoint
        self.techStack = techStack
        self.ExecutionStatus = ExecutionStatus
        self.TriggerType = TriggerType
        self.LimitType = LimitType  
    
    
    def getVersion(self) -> str:
        """
        Returns name and version of the automation service.

        Parameters:
        -----------
            None

        Example:
        ---------
        >>> client.Automation.getVersion()

        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            result = GraphQLUtil.get_service_version(self.techStack, self.endpoint, 'automation') 
          

        return result

    ## TODO: whole section "ServiceAccount" commented until Backend will provide these features again
    # def createServiceAccount(self, username: str, password: str) -> dict:
    #     """
    #     Adds a new service account to the automation service.
    #     Returns the name of the added service account in a dictionary.

    #     Parameters:
    #     -----------
    #         username: str
    #             The name of the service account to add
    #         password: str
    #             The password of the service account

    #     Example:
    #     ---------
    #     >>> client.Automation.createServiceAccount(username="my_service_account", password="q3QDoUs2q8QeoumewEHJwCt8HemX49U9")
    #     """
    #     correlationId = str(uuid4())
    #     with logger.contextualize(correlation_id=correlationId):

    #         key = "createServiceAccount"

    #         graphQLString = f'''mutation {key} {{
    #             {key}(
    #                 input: {{
    #                     username: "{username}"
    #                     password: "{password}"
    #                 }}
    #             ) {{
    #                     username                        
    #                 }}
    #         }}
    #         '''

    #         result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
    #         result = GraphQLUtil.validate_result_object(result)

    #         logger.info(f"Service account {username} added.")


    #     return result
    
    
    # def serviceAccounts(self) -> pd.DataFrame:
    #     """
    #     Returns all service accounts of the automation service in a DataFrame.
    #     Returns for each service account the username and createdAt date time.

    #     Parameters:
    #     -----------
    #         None

 
    #     Example:
    #     ---------   
    #     >>> client.Automation.serviceAccounts()      

    #     """
        
    #     correlationId = str(uuid4())
    #     with logger.contextualize(correlation_id=correlationId):

    #         # fields
    #         _fields = '''username
    #                     createdAt'''


    #         key = "serviceAccounts"
    #         graphQLString = f'''query {key} {{
    #             {key} {{                    
    #                 nodes {{
    #                     {_fields}
    #                 }}                                                    
    #             }}
    #         }}
    #         '''         

    #         result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
    #         result = GraphQLUtil.validate_result_object(result)

    #         if result[key] == None or len(result[key]) == 0:
    #             return pd.DataFrame()

    #         # Convert to DataFrame and rename columns
    #         df = pd.json_normalize(result[key]['nodes'])
            
    #         if df is None or df.empty:
    #             return pd.DataFrame()      
            
    #         # Convert createdAt to datetime            
    #         df['createdAt'] = pd.to_datetime(df['createdAt']).dt.tz_convert('Europe/Berlin').dt.strftime("%Y-%m-%d %H:%M:%S%z")
            
    #     return pd.DataFrame(df)
    

    # def updateServiceAccount(self, username: str, new_password: str) -> dict:
    #     """
    #     Updates the password for an existing service account.            
    #     Returns the name of the updated service account in a dictionary.

    #     Parameters:
    #     -----------
    #         username: str
    #             The name of the service account to update
    #         new_password: str
    #             The new password for the service account

    #     Example:
    #     ---------
    #     >>> client.Automation.updateServiceAccount(username="my_service_account", new_password="3JjmTsiukARcvUaXoVKaHEjpwmFZCTQQ")

    #     """

    #     correlationId = str(uuid4())
    #     with logger.contextualize(correlation_id=correlationId):

    #         key = "updateServiceAccount"

    #         graphQLString = f'''mutation {key} {{
    #             {key}(
    #                 input: {{
    #                     username: "{username}"
    #                     password: "{new_password}"
    #                 }}
    #             ) {{
    #                     username                        
    #                 }}
    #         }}
    #         '''

    #         logger.info(f"Updating password for service account {username}")
            
    #         result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
    #         result = GraphQLUtil.validate_result_object(result)

    #         logger.info(f"Password for service account {username} updated.")


    #     return result
    

    # def assignServiceAccount(self, 
    #                          automation_path: str,
    #                          username:str,
    #                          workspace_name:str) -> dict:
    #     """
    #     Assigns a service account to an existing automation within a workspace.
    #     Returns the service account username.
    #     Returns for the corresponding automation path and workspace name.

    #     Parameters:
    #     -----------
    #         automation_path: str
    #             The path of the automation to assign the service account to
    #         username: str
    #             The name of the service account to assign to the automation
    #         workspace_name: str
    #             The name of the workspace, the automation is existing in
         
    #     Example:
    #     ---------
    #     >>> client.Automation.assignServiceAccount(automation_path="my_folder/calculate_revenue.py", username="my_service_account", workspace_name="workspaceName")
    #     """

    #     correlationId = str(uuid4())
    #     with logger.contextualize(correlation_id=correlationId):
    #         key = "assignServiceAccount"

    #         graphQLString = f'''mutation {key} {{
    #                 {key}(
    #                     input: {{
    #                         automationPath: "{automation_path}"
    #                         serviceAccountUsername: "{username}"
    #                         workspaceName: "{workspace_name}"
    #                     }}
    #                 ) {{
    #                         automationPath
    #                         workspaceName
    #                     }}
    #                 }}
    #             ''' 
        
    #         logger.info(f"Assigning service account {username} to automation {automation_path} in workspace {workspace_name}")

    #         result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
    #         result = GraphQLUtil.validate_result_object(result)

    #         logger.info(f"Service account {username} assigned to automation {automation_path} in workspace {workspace_name}.")
           

    #     return result
         

    # def deleteServiceAccount(self, username: str) -> dict:
    #     """
    #     Deletes a Service Account from the automation service.
    #     Returns the username of the deleted service account in a dictionary.

    #     Parameters:
    #     -----------

    #         username: str
    #             The username of the service account to delete

    #     Example:
    #     ---------
    #     >>> client.Automation.deleteServiceAccount(username="my_service_account")        
    #     """

    
    #     correlationId = str(uuid4())
    #     with logger.contextualize(correlation_id=correlationId): 

    #         key = "deleteServiceAccount"

    #         graphQLString = f'''mutation {key} {{
    #             {key}(
    #                 input: {{
    #                     username: "{username}"
    #                 }}
    #             ) {{
    #                     username                        
    #                 }}
    #             }}
    #         '''
    #         logger.info(f"Deleting service account {username}")

    #         result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
    #         result = GraphQLUtil.validate_result_object(result)

    #         logger.info(f"Service account {username} deleted.")


    #     return result

    
    def createRepository(self, 
                      name: str, 
                      url: str, 
                      ssh_authentication: bool = False, 
                      username: Optional[str] = None, 
                      password: Optional[str] = None) -> dict:
        """
        Adds a new TechStack repository to the automation service based on an existing git repository.

        Authentication:
        There are two ways to authenticate with the existing git repository, which should be chosen based on the supported login method of the git repository:

        1. ssh_authentication: chose ssh_authentication = True. The SSH key is returend after creating the repository and needs to be added to the git repository.
        2. username_passwort_authentication: Provide the username and password to log in to the git repository.

        URL:
        The url of the git repository can be provided as https or ssh url.
        If an HTTPS URL is provided, the username and password authentication must be used.
        If an SSH URL is provided, either authentication method can be used.

        Parameters:
        -----------
            name: str
                The name of the repository
            url: str
                The URL of the repository
            ssh_authentication: bool = False:
                If true, the ssh key is being returned to access the repository. If false, username and password are required.
            username: str = None
                The username to access the repository. Required if ssh_authentication is set to False.
            password: str = None
                The password to access the repository. Required if ssh_authentication is set to False.

        Returns:
            dict: 
                The name of the created repository.                

        Raises:
            ValueError: If the authentication method is invalid
            Exception: If the GraphQL did not respond or the response is unknown

        Examples:
        ---------
        >>> client.Automation.createRepository(name="repoName", url="git@repossh", ssh_authentication=True)
        >>> client.Automation.createRepository(name="repoName", url="git@repossh", username="user", password="password")
        >>> client.Automation.createRepository(name="repoName", url="https://repourl", username="user", password="password")
            
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            key = "createRepository"

            # Check if the authentication method is valid and create credentials
            if ssh_authentication and not username and not password:
                credentials = f'method: SSH_KEY'
            elif not ssh_authentication and username and password:
                credentials = f'method: USERNAME_PASSWORD, username: "{username}", password: "{password}"'
            else:
                raise ValueError("Invalid Authentication Method. Either set ssh_authentication to True or provide a username and password")
            
            logger.info(f"Creating repository {name} with URL {url}")
            
            graphQLString = f'''mutation {key} {{
                {key}(
                    input: {{
                        name: "{name}",
                        remote: {{
                            credentials: {{{credentials}}}
                            url: "{url}"
                        }}

                    }}
                ) {{
                        name                        
                    }}
                }}
            '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            result = GraphQLUtil.validate_result_object(result)
                        
            logger.info(f"Repository {name} created.")
            
            return result
            
    
    
    def repositories(self,
                    fields:Union[list, str, None]=None,
                    where:Union[list,tuple,str,None]=None,                   
                    ) -> pd.DataFrame: 
        """
        Returns all repositories of the automation service in a DataFrame.
        Returns for each repository the name, URL and used credential information: authenticationMethod, sshPublicKey and username.        

        Parameters:
        -----------
            fields: list, str, None
                The fields to return. If None, all fields are returned.
                Possible values: "name", "url", "authenticationMethod", "createdAt", "changedAt", "username", "sshPublicKey"                

            where: list, tuple, str, None
                The filter to apply to the repositories. If None, no filter is applied.
                Possible values: "name", "url", "authenticationMethod", "createdAt", "changedAt", "username"
                Note: "sshPublicKey" filters is not supported

 
        Example:
        ---------   
        >>> client.Automation.repositories()      
        >>> client.Automation.repositories(fields=["name", "url", "createdAt"])
        >>> client.Automation.repositories(where=[f'name contains "Test"',f'createdAt >= "2030-02-10T00:00:00+01:00"'])
        >>> client.Automation.repositories(where=[f'url startswith "git@github.com"'])
        >>> client.Automation.repositories(where=[f'authenticationMethod eq SSH_KEY']) # Note: SSH_KEY or USERNAME_PASSWORD  MUST be written without quotes due to GraphQL syntax
        >>> client.Automation.repositories(where=[f'username eq "new_user"'])

        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            
            # arguments
            _arguments = None            
            if where != None:
                resolved_where_filter = GraphQLUtil.resolve_where_automation(self.techStack, where)["topLevel"]
                _arguments = f'''(
                                {resolved_where_filter}
                                )
                            '''
            else:
                _arguments = ''

            # fields
            _fields = None

            if fields != None:
                if type(fields)!=list:
                    _fields = [fields]
                else:
                    _fields = GraphQLUtil.query_fields(field_list=fields,
                                                    array_type_fields=None,
                                                    array_page_size=None,
                                                    filter=None,
                                                    recursive=False)
            else:
                _fields = '''name
                            url
                            authenticationMethod
                            createdAt
                            changedAt
                            username
                            sshPublicKey      
                            '''
                

            # Create GraphQL query string and invoke GraphQL API
            key = "repositories"
            graphQLString = f'''query {key} {{
                {key} 
                    {_arguments}
                    {{
                    nodes {{
                        {_fields}
                    }}
                }}
            }}
            '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            result = GraphQLUtil.validate_result_object(result)

            if result[key] == None or len(result[key]) == 0:
                return pd.DataFrame()

            # Convert to DataFrame and rename columns
            df = pd.json_normalize(result[key]['nodes'])
            
            if df is None or df.empty:
                return pd.DataFrame()            

            # Convert createdAt to datetime  
            if 'createdAt' in df.columns:          
                df['createdAt'] = pd.to_datetime(df['createdAt'], utc=True).dt.tz_convert('Europe/Berlin').dt.strftime("%Y-%m-%d %H:%M:%S%z")
            if 'changedAt' in df.columns:
                df['changedAt'] = pd.to_datetime(df['changedAt'], utc=True).dt.tz_convert('Europe/Berlin').dt.strftime("%Y-%m-%d %H:%M:%S%z")

        return pd.DataFrame(df)

    
    
    def updateRepository(self,
                        name: str,
                        new_name: Optional[str] = None,
                        new_url: Optional[str] = None,
                        ssh_authentication: bool = False,
                        new_username: Optional[str] = None,
                        new_password: Optional[str] = None) -> dict:
        """
        Updates an existing repository in the automation service. 
        Allows updating the name of the repository, the URL, and the authentication method.
        If the url or authentication method is to be changed, both, authentication method and url need to be provided.
        For authentication, either ssh_authentication can be set to True OR a username and password can be provided.

        Returns the name of the updated repository in a dictionary.

        Parameters:
        -----------
            name: str
                The name of the repository to update
            new_name: Optional[str]
                The new name of the repository
            new_url: Optional[str]
                The new URL of the repository
            ssh_authentication: bool = False
                Sets authentication method to SSH_KEY, deletes username and password and returns the SSH key, which needs to be added to the git repository
            new_username: Optional[str] = None
                The new username for the repository
            new_password: Optional[str] = None
                The new password for the repository
        
        Returns:
            dict: name of the updated repository

        Raises:
            ValueError: If the authentication method is invalid or combination of new_url and authentication method is invalid
            Exception: If the GraphQL did not respond or the response is unknown

        Examples:
        ---------
        >>> # set new url using ssh authentication
        >>> client.Automation.updateRepository(name="repoName", ssh_authentication=True, new_url="https://new_repo_url")
        >>> # change user name and password
        >>> client.Automation.updateRepository(name="repoName", new_username="user", new_password="password", new_url="https://new_repo_url")
        >>> # change name of the repository
        >>> client.Automation.updateRepository(name="repoName", new_name="newRepoName")

        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            # Check if the authentication method is valid and create credentials
            credentials = None
            if ssh_authentication or new_username or new_password:
                if ssh_authentication and not new_username and not new_password:
                    credentials = f'method: SSH_KEY'
                elif new_username and new_password and not ssh_authentication:
                    credentials = f'method: USERNAME_PASSWORD, '
                    credentials += f'username: "{new_username}", '
                    credentials += f'password: "{new_password}"\n'                
                else:
                    raise ValueError("Invalid Authentication Method. Either set ssh_authentication to True OR provide username and password")
            
            # Ensure that new_url and credentials are either both set or both not set
            if new_url and not credentials:
                raise ValueError("To change the url, authentication method must also be provided (ssh_authentication=True OR username and password).")
            elif not new_url and credentials:
                raise ValueError("To change the authentication method, the repository url (new_url) must also be provided.")

            # create gql string
            key = "updateRepository"

            input_string = f'name: "{name}"\n'

            if new_name:
                input_string += f'newName: "{new_name}"\n'
            if new_url and credentials:
                input_string += f'remote:{{url: "{new_url}",\n credentials: {{{credentials}}}}}\n'

            graphQLString = f'''mutation {key} {{
                {key}(
                    input: {{
                        {input_string}
                        
                    }}
                ) {{
                        name
                    }}
                }}
            '''
            
            # execute the GraphQL and check for errors
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            result = GraphQLUtil.validate_result_object(result)

            logger.info(f"Repository {name} updated.")

        
        return result

    

    def renewRepositorySshKey(self, name: str) -> dict:
        """
        Renews the SSH key for an existing repository in the automation service.
        Returns the name of the repository the SSH key has been renewed for.

        Parameters:
        -----------
            name: str
                The name of the repository

        Examples:
        ---------
        >>> # renew the SSH key for an existing repository
        >>> repository_name = "my_repository"
        >>> client.Automation.renewRepositorySshKey(name=repository_name)
        >>> # get the new SSH key from the repository
        >>> new_ssh_key = client.Automation.repositories(where=[f'name eq "{repository_name}"'])['credentials.sshPublicKey'].iloc[0]
        >>> # print the new SSH key
        >>> print(new_ssh_key) 

        """
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            key = "renewRepositorySshKey"

            graphQLString = f'''mutation {key} {{
                {key}(
                    input: {{
                        name: "{name}"
                    }}
                ) {{
                        name
                    }}
            }}
            '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            result = GraphQLUtil.validate_result_object(result)

            logger.info(f"SSH Key for repository {name} renewed.")

        
        return result
    
    
    def deleteRepository(self, name: str) -> dict:
        """
        Deletes a repository from the automation service.
        Returns the name and URL of the deleted repository in a dictionary.

        Parameters:
        -----------
            name: str
                The name of the repository to delete

        Examples:
        ---------
        >>> client.Automation.deleteRepository(name="repoName")

        """
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            key = "deleteRepository"

            graphQLString = f'''mutation {key} {{
                {key}(
                    input: {{
                        name: "{name}"
                    }}
                ) {{
                        name                        
                    }}
            }}
            '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            result = GraphQLUtil.validate_result_object(result)

            logger.info(f"Repository {name} deleted.")
        
        
        return result


    def createWorkspace(self, name: str, repository: str, branch: str, commit: str = "") -> dict:
        """
        Adds a new workspace to the automation service on the basis of an existing repository.
        If a commit is provided, the workspace is created based on that commit.
        Otherwise, the workspace is created based on the latest commit of the specified branch.
        Returns the branch, commit and name of the added workspace in a dictionary.

        Parameters:
        -----------
        name: str
            The name of the workspace.
        repository: str
            The name of the repository.
        branch: str
            The branch of the git repository from which the workspace will be created.
        commit: str = ""
            The specific commit of the git repository to base the workspace on. If not provided, the latest commit of the branch is used.

        Examples:
        ---------
        # create a workspace based on the latest commit of the main branch
        >>> client.Automation.createWorkspace(branch="main", name="workspaceName", repository="repoName")
        # create a workspace based on a specific commit of the develop branch
        >>> client.Automation.createWorkspace(branch="develop", name="workspaceName", repository="repoName", commit="#123")        
        """
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            key = "createWorkspace"
            input = f'branch: {{commit: "{commit}", name: "{branch}"}}, name: "{name}", repositoryName: "{repository}"'

            graphQLString = f'''mutation {key} {{
                {key}(
                    input: {{{input}}}
                ) {{                        
                       name
                    }}
            }}
            '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            result = GraphQLUtil.validate_result_object(result)

        return result



    def workspaces(self,
                   fields:Union[list, str, None]=None,
                   where:Union[list,tuple,str,None]=None,
                   ) -> pd.DataFrame:
        """
        Returns all workspaces of the automation service in a DataFrame.
        Returns for each workspace the name, branch, commit, createdAt synchronizationStatus, lastSynchronizationDate, lastSuccessfulSynchronizationDate.
        Returns also the corresponding repository name and URL.

        Parameters:
        -----------
            fields: list, str, None
                The fields to return. If None, all fields are returned.
                Possible values: 
                "name", "activeBranch", "activeCommit", "repositoryName", "buildStatus", 
                "createdAt", "changedAt","buildBranch", "buildCommit", 
                "buildStartedAt", "buildFinishedAt"and "buildDuration"
        
            where: list, tuple, str, None
                The filter to apply to the workspaces. If None, no filter is applied.
                Possible values: see fields parameter.
 
        Example:
        ---------
        >>> client.Automation.workspaces()
        >>> client.Automation.workspaces(fields=["name", "activeBranch", "activeCommit", "createdAt"])
        >>> client.Automation.workspaces(where=[f'repositoryName eq "Demo3"'])
        >>> client.Automation.workspaces(where=[f'name contains "Test"',f'createdAt >= "2025-02-10T00:00:00+01:00"']) 
        >>> client.Automation.workspaces(where=[f'name eq "workspaceName"'])
        >>> client.Automation.workspaces(where=[f'buildStatus eq SUCCEEDED']) # Note: PENDING, RUNNING, SUCCEEDED or FAILED have to be written without quotes due to GraphQL syntax
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
 
            # arguments
            _arguments = None            
            if where != None:
                resolved_where_filter = GraphQLUtil.resolve_where_automation(self.techStack, where)["topLevel"]
                _arguments = f'''(
                                {resolved_where_filter}
                                )
                            '''
            else:
                _arguments = ''
 

            # fields
            _fields = None

            if fields != None:
                if type(fields)!=list:
                    _fields = [fields]
                else:
                    _fields = GraphQLUtil.query_fields(field_list=fields,
                                                    array_type_fields=None,
                                                    array_page_size=None,
                                                    filter=None,
                                                    recursive=False)
            else:
                _fields = '''name      
                            activeBranch
                            activeCommit
                            repositoryName
                            buildStatus
                            createdAt
                            changedAt
                            buildBranch
                            buildCommit
                            buildStartedAt     
                            buildFinishedAt'''           
                
                
            # Create GraphQL query string and invoke GraphQL API
            key = "workspaces"          
            graphQLString = f'''query {key} {{
                {key} 
                    {_arguments}
                {{
                    nodes {{
                        {_fields}
                    }}
                }}
            }}
            '''      

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            result = GraphQLUtil.validate_result_object(result)

            if result[key] == None or len(result[key]) == 0:
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.json_normalize(result[key]['nodes'])
            
            if df is None or df.empty:
                return pd.DataFrame()
            
            # Convert to datetime if date columns are in df
            if 'createdAt' in df.columns:	
                df['createdAt'] = pd.to_datetime(df['createdAt'], utc=True).dt.tz_convert('Europe/Berlin').dt.strftime("%Y-%m-%d %H:%M:%S%z")
            if 'changedAt' in df.columns:
                df['changedAt'] = pd.to_datetime(df['changedAt'], utc=True).dt.tz_convert('Europe/Berlin').dt.strftime("%Y-%m-%d %H:%M:%S%z")   
            if 'buildStartedAt' in df.columns:
                df['buildStartedAt'] = pd.to_datetime(df['buildStartedAt'], utc=True).dt.tz_convert('Europe/Berlin').dt.strftime("%Y-%m-%d %H:%M:%S%z")
            if 'buildFinishedAt' in df.columns:
                df['buildFinishedAt'] = pd.to_datetime(df['buildFinishedAt'], utc=True).dt.tz_convert('Europe/Berlin').dt.strftime("%Y-%m-%d %H:%M:%S%z")
        
        return pd.DataFrame(df)
    
    
    def updateWorkspace(self, 
                         name: str,                         
                         new_name: Optional[str]=None, 
                         branch: Optional[str]=None,
                         commit: Optional[str]= None,
                         ) ->  dict:
                        
        """
        Updates an existing workspace in the automation service.
        Allows updating the name of the workspace, the branch and the commit.
        If the branch or commit is to be changed, both, branch and commit need to be provided. To use the latest commit of the branch, set commit to "".
        Returns the name and URL of the updated workspace in a dictionary.

        Parameters:
        -----------
            name: str
                The name of the workspace to update
            newname: Optional[str]
                The new name of the workspace
            branch: Optional[str]
                The branch to use for the workspace
            commit: Optional[str]
                The commit to use for the workspace


        Example: 
        >>> client.Automation.updateWorkspace(name="myWorkspaceName", newname="myWorkspaceNameChanged", branch="main", commit="1234567890abcdef")
        >>> client.Automation.updateWorkspace(name="myWorkspaceName", newname="myWorkspaceNameChanged") # only change name      
        >>> client.Automation.updateWorkspace(name="myWorkspaceName", branch="main", commit="") # set to newest commit of main branch
        
        """
        
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            key = "updateWorkspace"

            # Check which parameters are set and create the input string accordingly
            update_info = ""
            input_string = f'name: "{name}", '

            if branch and commit is None:
                raise ValueError("To change the branch, the commit must also be provided. To use the latest commit of the branch, set commit to an empty string.")
            elif not branch and commit is not None:
                raise ValueError("To change the commit, the branch must also be provided. To use the latest commit of the branch, set commit to an empty string.")
            elif branch and commit is not None:
                input_string += f'branch: {{commit: "{commit}", name: "{branch}"}}'
                update_info += f'The branch is set to "{branch}" and the commit is set to "{commit}".'

            if new_name:
                input_string += f'newName: "{new_name}", '
                update_info += f'The name is set to "{new_name}". '


            logger.info(f"Updating workspace {name}. {update_info}")

            graphQLString = f'''mutation {key} {{
                {key}( 
                    input: {{{input_string}}}
                ) {{
                        name
                    }}
            }}
            '''
            
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            result = GraphQLUtil.validate_result_object(result)

            logger.info(f"Workspace {name} updated.")       

        return result
    
    
    def synchronizeWorkspace(self, name: str) -> dict:
        """
        Synchronizes an existing workspace in the automation service.        
        Returns the name of the synchronized workspace in a dictionary.

        Parameters:
        -----------
            name: str
                The name of the workspace to synchronize

        Example:
        ---------
        >>> client.Automation.synchronizeWorkspace(name="workspaceName")
        """
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            key = "synchronizeWorkspace"

            graphQLString = f'''mutation {key} {{
                {key}(
                    input: {{
                        name: "{name}"
                    }}
                ) {{
                        name
                    }}
            }}
            '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            result = GraphQLUtil.validate_result_object(result)

            logger.info(f"Workspace {name} synchronized.")       

        return result
    
        
    def deleteWorkspace(self, name: str) -> dict:
        """
        Deletes a workspace from the automation service.        
        Returns the name of the deleted workspace in a dictionary.

        Parameters:
        -----------
            name: str
                The name of the workspace to delete

        Example:
        >>> client.Automation.deleteWorkspace(name="workspaceName")
        """
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            key = "deleteWorkspace"

            graphQLString = f'''mutation {key} {{
                {key}(
                    input: {{
                        name: "{name}"
                    }}
                ) {{
                        name
                    }}
            }}
            '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            result = GraphQLUtil.validate_result_object(result)

            logger.info(f"Workspace {name} deleted.")       

        return result
    

    
    def automations(self,
                    fields:Union[list, str, None]=None,
                    where:Union[list,tuple,str,None]=None,
                    ) -> pd.DataFrame:
        
        """
        Returns all automations of the automation service in a DataFrame. 
        Returns for each automation the script path, description, workspace name, environment, 
        the input arguments and parallel execution setting.         

        Parameters:
        -----------
            fields: list, str, None
                The fields to return. If None, all fields are returned.
                Possible values: "path", "description", "workspaceName", "environment" and "allowParallelExecution"
                Note: "argumentDefinitions" are only returned if field parameter is None

            where: list, tuple, str, None
                The filter to apply to the automations. If None, no filter is applied.
                Possible values: "path", "description", "workspaceName", "environment" and "allowParallelExecution"
                Note: "argumentDefinitions" cannot be filtered

        Example:
        ---------
        >>> client.Automation.automations() # Returns all automations with all fields
        >>> client.Automation.automations(fields=["path","description","environment","allowParallelExecution"]) # only specific fields
        >>> client.Automation.automations(where=[f'workspaceName eq "myWorkspace"']) # filter by workspace name
        >>> client.Automation.automations(where=[f'path contains "price"'])  # filter on path 
        >>> client.Automation.automations(where=[f'allowParallelExecution eq true',f'environment eq "python_3.11"']) # note: true MUST be lowercase due to internal GraphQL syntax
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            # arguments
            _arguments = None            
            if where != None:
                resolved_where_filter = GraphQLUtil.resolve_where_automation(self.techStack, where)["topLevel"]
                _arguments = f'''(
                                {resolved_where_filter}
                                )
                            '''
            else:
                _arguments = ''


            # fields
            _fields = None

            if fields != None:
                if type(fields)!=list:
                    _fields = [fields]
                else:
                    _fields = GraphQLUtil.query_fields(field_list=fields,
                                                    array_type_fields=None,
                                                    array_page_size=None,
                                                    filter=None,
                                                    recursive=False)     
            else:
                _fields = '''path
                            description
                            workspaceName
                            argumentDefinitions {
                                name
                                description
                                mandatory
                            }
                            environment
                            allowParallelExecution
                            '''

            # Create GraphQL query string and invoke GraphQL API
            key = "automations"
            graphQLString = f'''query {key} {{
                {key} 
                    {_arguments}
                {{
                    nodes {{
                        {_fields}
                    }}
                }}
            }}
            '''  

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            result = GraphQLUtil.validate_result_object(result)

            if result[key] == None or len(result[key]) == 0:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.json_normalize(result[key]['nodes'])

        return df
    
    
    
    def executeAutomation(self,
                        automation_path: str,
                        workspace_name: str,
                        arguments: Optional[dict] = None,                      
                        initiatorReference: Optional[str] = None
                        ) -> str:
        """
        Executes an automation in the automation service.
        Returns the execution ID of the executed automation.
        

        Parameters:
        -----------
            automation_path: str
                The path to the automation script to execute
            workspace_name: str
                The name of the workspace
            arguments: Optional[dict]
                The arguments for the automation script. Formatted: {key1: value1, key2: value2,...}
            initiatorReference: Optional[str] = None
                A reference text for the execution. Default is None.

        Example:
        ---------
        >>> # execute automation with list of arguments, using all optional parameters            
        >>> execution_id  = client.Automation.executeAutomation(
                                    automation_path="/CurrentGridState.py",
                                    workspace_name="WSStromGedacht2",
                                    arguments={"zipCode":"76187","horizon":"short_term_calculation"},                                        
                                    initiatorReference='reference_text'
                                    )                                  
        >>> client.Automation.executions(where=[f'id eq "{execution_id}"']) # query status of execution  
        ---
        >>> # execute an automation that does not provide input arguments
        >>> execution_id = client.Automation.executeAutomation(
                                    automation_path="/pyweather/temperature.py",
                                    workspace_name="workspaceName"
                                    )
        ---
        """
        
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):              
            
            # create gql string and execute graphQL mutation
            key = "execute"

            input_string = f'automationPath: "{automation_path}"\n'
            input_string += f'workspaceName: "{workspace_name}"\n'
            
            if arguments != None: 
                arguments_str = GraphQLUtil.arguments_to_str(arguments)
                input_string += f'arguments: {arguments_str}\n'
            else:
                input_string += f'arguments: []\n'
                            
            input_string += f'initiatorType: {TriggerType.SCRIPT.value}\n'

            if initiatorReference != None:
                input_string += f'initiatorReference: "{initiatorReference}"\n'
            
            graphQLString = f'''mutation {key} {{
                {key}(
                    input: {{{input_string}}}
                ) {{                        
                    id
                }}
            }}
            '''

            logger.info(f'Executing automation {automation_path}...')
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            result = GraphQLUtil.validate_result_object(result)

            logger.info(f"Automation {automation_path} executed.")

            if result[key] == None or len(result[key]) == 0:
                id = ''
            else:
                id = result[key]['id']

        return id
            
    
    
    def createSchedule(self,
                    name: str,                    
                    automation_path: str,
                    workspace_name: str,                                        
                    cron: str,                    
                    arguments: Optional[dict] = None,
                    timezone: Optional[str] = 'Europe/Berlin',
                    description: Optional[str]="",
                    is_active: bool = True
                    ) -> dict:
        
        """
        Creates a new schedule to an existing automation". 
        Returns the name, automation path and and workspace name of the created schedule in a dictionary.
        Note: Unique key for a schedule is the combination of name, workspace and automation_path.

        Parameters:
        -----------
            name: str
                The name of the schedule
            automation_path: str
                The path to the automation script   
            workspace_name: str
                The name of the workspace
            cron: str
                The cron expression for the schedule
            arguments: Optional[dict] 
                The arguments for the automation script. Formatted: {key1: value1, key2: value2,...}
            timezone: Optional[str]
                The timezone of the schedule, default is 'Europe/Berlin'.
            descrption: Optional[str]
                The description of the schedule
            is_active: bool = True
                The active status of the schedule. Default is True.
            
        Examples:
        ---------
        >>> client.Automation.createSchedule(
                name="scheduleName",                
                automation_path="/pyweather/temperature.py",
                workspace_name="workspaceName",
                cron="0 0 12 * * ?",                
                arguments={"location": "Karlsruhe", "horizon": "short_term_calculation"},
                timezone="Europe/Berlin",
                description="regular calculation",
                is_active=True
                )
        """
        
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            key = "createSchedule"
           
            #Check parameters and create input string accordingly            
            if arguments != None: 
                arguments_str = GraphQLUtil.arguments_to_str(arguments)                
            else:
                arguments_str = '[]'

            active = GraphQLUtil.to_graphql(is_active)

            # create gql string and execute graphQL mutation
            input_string = f'''
                    name: "{name}"
                    description: "{description}"
                    workspaceName: "{workspace_name}"
                    cron: "{cron}"
                    automationPath: "{automation_path}"
                    timezone: "{timezone}"
                    active: {active}
                    arguments: {arguments_str}
                    '''
                    

            graphQLString = f'''mutation {key} {{
                {key}(
                    input: {{{input_string}}}
                ) {{
                    name
                    automationPath
                    workspaceName
                }}
            }}
            '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            result = GraphQLUtil.validate_result_object(result)
            if result is not None or result[key] is not None:
                result = result[key] 

            logger.info(f"Schedule {name} added.")

        return result


    def schedules(self,
                  where: Union[list,tuple,str,None]=None,
                  fields: Union[list, str, None]=None
                  ) -> pd.DataFrame:
        
        """
        Returns all schedules of automations in a DataFrame.
        Returns for each schedule the name, description, cron expression and active status .
        Returns also the name of the workspace.

        Parameters:
        -----------
            fields: list, str, None
                The fields to return. If None, all fields are returned.
                Possible values: "name", "automationPath", "description", "cron", 
                "timezone", "active" and "version".
                Note: "workspace" (name) and "argumentInstances" (name and value) and "nextFireTime" cannot be selected.

            where: list, tuple, str, None
                The filter to apply to the schedules. If None, no filter is applied.
                Possible values: see fields parameter.
                Note: "workspace" (name) and "argumentInstances" (name and value) and "nextFireTime" cannot be filtered.

        Example:
        ---------
        >>> client.Automation.schedules()
        >>> client.Automation.schedules(fields=["name","description","cron","active"]) # only specific fields
        >>> client.Automation.schedules(where=[f'automationPath eq "/CurrentGridState.py"'])
        >>> client.Automation.schedules(where=[f'name contains "Test"']) # filter on name
        >>> client.Automation.schedules(where=[f'active eq true',f'cron endsWith "* * ?"']) # filter on active schedules than run daily or more often
        >>> client.Automation.schedules(where=[f'active eq true',f'timezone neq "Europe/Berlin"']) # active schedules that are based on OTHER timezones than CET/CEST
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            # arguments
            _arguments = None            
            if where != None:
                resolved_where_filter = GraphQLUtil.resolve_where_automation(self.techStack, where)["topLevel"]
                _arguments = f'''(
                                {resolved_where_filter}
                                )
                            '''
            else:
                _arguments = ''
            
            # fields
            _fields = None

            if fields != None:
                if type(fields)!=list:
                    _fields = [fields]
                else:
                    _fields = GraphQLUtil.query_fields(field_list=fields,
                                                    array_type_fields=None,
                                                    array_page_size=None,
                                                    filter=None,
                                                    recursive=False)     
            else:
                _fields = '''name
                            automationPath
                            description
                            workspace {
                                name
                            }
                            cron
                            timezone
                            fireTimes(count: 1)
                            active
                            argumentInstances {
                                name
                                value
                            }
                            version'''

            
            # Create GraphQL query string and invoke GraphQL API
            key = "schedules"
            graphQLString = f'''query {key} {{
                {key} 
                    {_arguments}
                {{
                    nodes {{
                        {_fields}
                    }}
                }}
            }}
            '''    

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            result = GraphQLUtil.validate_result_object(result)

            if result[key] == None or len(result[key]) == 0:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.json_normalize(result[key]['nodes'])

            if df is None or df.empty:
                return pd.DataFrame()
            
            # Convert to datetime if date columns are in df
            if 'createdAt' in df.columns:	
                df['createdAt'] = pd.to_datetime(df['createdAt'], utc=True).dt.tz_convert('Europe/Berlin').dt.strftime("%Y-%m-%d %H:%M:%S%z")
            if 'fireTimes' in df.columns:                
                df.rename(columns={'fireTimes': 'nextFireTime'}, inplace=True)
                # Convert list of datetime to datetime 
                df['nextFireTime'] = df['nextFireTime'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)
                # Convert to datetime in 'Europe/Berlin' timezone 
                df['nextFireTime'] = pd.to_datetime(df['nextFireTime'], utc=True).dt.tz_convert('Europe/Berlin').dt.strftime("%Y-%m-%d %H:%M:%S%z")
                
        return df
    
      
    def nextFireTimes(self,
                        schedule_name: str,
                        fromTimepoint: Optional[str] = None,
                        toTimepoint: Optional[str] = None,
                        count: Optional[int] = 10,
                        ) -> pd.DataFrame:
        """
        Shows next fire times of a schedule.

        Returns the next fire time of the schedule in a DataFrame 
        together with the automation path and workspace name.

        If more than one schedule with the same name exists,
        the next fire times of all schedules with the same name are returned.

        Parameters:
        -----------
            schedule_name: str
                The name of the schedule to get the next fire times for.
            fromTimepoint: str, None
                The start date for the next fire times. If left out start date is set to now.
                Format: "YYYY-MM-DDTHH:MM:SS+02:00" or "YYYY-MM-DDTHH:MM:SSZ" or
                Format: "YYYY-MM-DD HH:MM:SS+02:00" or "YYYY-MM-DD HH:MM:SSZ"
            toTimepoint: str, None
                The end date for the next fire times.
                Format: "YYYY-MM-DDTHH:MM:SS+02:00" or "YYYY-MM-DDTHH:MM:SSZ" or
                Format: "YYYY-MM-DD HH:MM:SS+02:00" or "YYYY-MM-DD HH:MM:SSZ"
            count: int, None
                The number of next fire times to return. Default is 10.
        
        Example:
        ---------
        >>> # get the next fire times of a schedule with name "schedule_test_new_name" between fromTimepoint and toTimepoint
        >>> client.Automation.nextFireTimes(schedule_name="schedule_test_new_name",
        >>>                                  fromTimepoint="2030-05-04T00:00:00+02:00",
        >>>                                  toTimepoint="2030-05-05T23:59:59+02:00",
        >>>                                  count=5)
        >>> # get the next fire times of a schedule with name "schedule_test_new_name" without time filter
        >>> client.Automation.nextFireTimes(schedule_name="schedule_test_new_name",
        >>>                                  count=5)
        >>> # get the next fire times of a schedule with name "schedule_test_new_name" without time filter and count
        >>> client.Automation.nextFireTimes(schedule_name="schedule_test_new_name")
        >>> # get the next 100 fire times of a schedule with name "Alle15Minuten" starting from a specific timepoint
        >>> client.Automation.nextFireTimes(schedule_name="Alle15Minuten",
        >>>                                  fromTimepoint="2030-05-04T00:00:00+02:00",
        >>>                                  count=100)
        
        """
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            
            where_string = f'(where:{{name:{{eq:"{schedule_name}"}}}})'

            _arguments_firetimes = ''

            if fromTimepoint is not None:
                _fromTimepoint = f'from: "{fromTimepoint}"'                
                _arguments_firetimes += _fromTimepoint + ','
            
            if toTimepoint is not None:
                _toTimepoint = f'to: "{toTimepoint}"'
                _arguments_firetimes += _toTimepoint + ','

            if count is not None:
                _count = f'count: {count}'
                _arguments_firetimes += _count

            _fireTimes = f'''fireTimes({_arguments_firetimes})'''

            _fields = '''
                        automationPath
                        workspace {
                            name
                        }
                    '''

            # Create GraphQL query string and invoke GraphQL API
            key = "schedules"
            graphQLString = f'''query {key} {{
                {key} 
                    {where_string}
                {{
                    nodes {{
                        {_fireTimes}
                        {_fields}
                    }}
                }}
            }}
            '''    

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
            result = GraphQLUtil.validate_result_object(result)

            if result[key] == None or len(result[key]) == 0:
                return pd.DataFrame()
            
            df = pd.json_normalize(result[key]['nodes'])

            if df is None or df.empty:
                return pd.DataFrame()
            
            fire_times_list = []

            for _, row in df.iterrows():
                automationPath = row['automationPath']
                workspaceName = row['workspace.name']
                fire_times = row['fireTimes']
                for fire_time in fire_times:
                    fire_times_list.append({
                        'fireTimes': fire_time,
                        'automationPath': automationPath,
                        'workspace.name': workspaceName
                    })

            df_fire_times = pd.DataFrame(fire_times_list)
                     
            df_fire_times['fireTimes'] = pd.to_datetime(df_fire_times['fireTimes'], utc=True).dt.tz_convert('Europe/Berlin').dt.strftime("%Y-%m-%d %H:%M:%S%z")

        return  df_fire_times 
    
    
    def scheduledExecutions(self,                            
                            fromTimepoint: Optional[str],
                            toTimepoint: Optional[str],
                            fields:Union[list, str, None]=None,                                                    
                            top: int= 10,
                            pageSize:int=100, 
                            ) -> pd.DataFrame:
        """
        Shows the next fire times of scheduled executions in a DataFrame.
        Returns for each scheduled execution the calculated fire time, automationPath, schedule name, arguments the schedule will be executed with.
        Returns for the scheduled automation it's name, workspace and repository.
        Returns additional schedule information such as cron expression, timezone and description.

        Parameters:
        -----------

            fields: list, str, None
                The fields to return. If None, all fields are returned.
                Possible values: "fireTime", "automationPath", "name" (of the schedule), "cron", "description",
                 "active" and  "timezone" 
                Note: "workspace" (name), "repositoryName" and "argumentInstances" (name and value) cannot be selected

            fromTimepoint: str, None                    
                    The start date for the scheduled executions. 
                    Format: "YYYY-MM-DDTHH:MM:SS+02:00" or "YYYY-MM-DDTHH:MM:SSZ" or
                    Format: "YYYY-MM-DD HH:MM:SS+02:00" or "YYYY-MM-DD HH:MM:SSZ"

            toTimepoint: str, None
                    The end date for the scheduled executions
                    Format: "YYYY-MM-DDTHH:MM:SS+02:00" or "YYYY-MM-DDTHH:MM:SSZ" or
                    Format: "YYYY-MM-DD HH:MM:SS+02:00" or "YYYY-MM-DD HH:MM:SSZ"

            top: int, None
                Limits the returned number of scheduled executions per automation. Default is 10.

            pageSize:int=100 
                    The page size of scheduled executions that is used to retrieve a large number of items. Default is 100.
                

        Example:
        ---------
        >>> # return the next fire times between fromTimpoint and toTimepoint, all fields:
        >>> client.Automation.scheduledExecutions(fromTimepoint="2030-05-04T00:00:00+02:00",
        >>>                                       toTimepoint="2030-05-05T23:59:59+02:00")
        >>> # return the next 5 fire times, only specific fields:
        >>> client.Automation.scheduledExecutions(fields=["fireTime","automationPath","name","cron","description"],
        >>>                                       fromTimepoint="2030-05-04T00:00:00+02:00",
        >>>                                       toTimepoint="2030-05-05T23:59:59+02:00",
        >>>                                       top=5)             
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            # arguments
            _arguments = None

            _fromTimepoint = f'from: "{fromTimepoint}"'
            _toTimepoint = f'to: "{toTimepoint}"'

            _arguments = f'''
                {_fromTimepoint}
                {_toTimepoint}                                
            '''

            # fields
            _fields = None

            if fields != None:
                if type(fields)!=list:
                    _fields = [fields]
                else:
                    _fields = GraphQLUtil.query_fields(field_list=fields,
                                                    array_type_fields=None,
                                                    array_page_size=None,
                                                    filter=None,
                                                    recursive=False)     
            else:
                    _fields = '''
                            fireTime
                            automationPath
                            name
                            cron
                            description
                            argumentInstances {
                                name
                                value
                            }
                            workspace {
                                name
                                repositoryName
                            }
                            timezone
                        '''

            _pageInfoFields = f'''
                endCursor
                startCursor
                hasNextPage
                hasPreviousPage
                '''
            
            # Create GraphQL query string and invoke GraphQL API
            key = "scheduledExecutions"

            result = []
            count = 0
            hasNextPage = True
            endCursor = 'null' 
            stop = False

            while hasNextPage:   
                # Handling top (premature stop)
                if top != None:
                    loadedItems = pageSize * count
                    if top - loadedItems <= pageSize:
                        stop = True
                        pageSize = top - loadedItems

                # create the next query with the endCursor as after parameter
                graphQLString = f'''query {key} {{
                            {key} (
                                first: {pageSize}
                                after: {endCursor} 
                                {_arguments}              
                                ) {{
                                nodes {{
                                    {_fields}
                                }}
                                pageInfo {{
                                    {_pageInfoFields}
                                }}                           
                            }}
                        }}
                        '''

                _result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
                _result = GraphQLUtil.validate_result_object(_result)  
                
                if isinstance(_result[key]['nodes'],list): # only if 'node' is a list
                    hasNextPage = _result[key]['pageInfo']['hasNextPage'] 
                    endCursor = _result[key]['pageInfo']['endCursor']
                    endCursor = f'"{endCursor}"' # ensured to be a string, after first use of null
                    result += _result[key]['nodes'] 
                    count += 1
                else: # leave the loop if no more nodes are available
                    stop = True

                if stop == True:
                    break
            
            # Convert to DataFrame
            df = pd.json_normalize(result)	

            if df is None or df.empty:
                return pd.DataFrame()
            
            # Convert to datetime if date columns are in df
            if 'fireTime' in df.columns:	
                df['fireTime'] = pd.to_datetime(df['fireTime'], utc=True).dt.tz_convert('Europe/Berlin').dt.strftime("%Y-%m-%d %H:%M:%S%z")
            
        return df
                            


    def updateSchedule(self,
                        name: str,
                        workspace_name: str,
                        automation_path: str,
                        new_name: Optional[str] = None,
                        new_description: Optional[str] = None,
                        new_cron: Optional[str] = None,
                        new_arguments: Optional[dict] = None,
                        new_timezone: Optional[str] = None,
                        new_is_active: Optional[bool] = None
                        ) -> dict:
        """
        Updates an existing schedule in the automation service.
        The parameters name, workspace and automationPath are required for the identification of the schedule.
        Returns the name, automation path and and workspace name of the updated schedule in a dictionary.


        Parameters:
        -----------
            name: str
                The name of the schedule to update
            workspace_name: str
                The name of the workspace
            automation_path: str
                The path to the automation script
            new_name: Optional[str]
                The new name of the schedule
            new_description: Optional[str]
                The new description of the schedule
            new_cron: Optional[str]
                The new cron expression for the schedule
            new_arguments: Optional[dict]
                The new arguments for the automation script. Formatted: {key1: value1, key2: value2,...}
            new_timezone: Optional[str]
                The new timezone of the schedule
            new_is_active: Optional[bool]
                The active status of the schedule. Default is True.

        Examples:
        ---------
        >>> client.Automation.updateSchedule(
                name="scheduleName",
                workspace_name="myWorkspaceName",
                automation_path="/pyweather/temperature.py",
                new_name="newScheduleName",
                new_description="new_description",
                new_cron="0 0 * * * ?",
                new_arguments={"location": "Karlsruhe","horizon": "long_term_calculation"},
                new_timezone="UTC",
                new_is_active=True
                )

        """
        
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            key = "updateSchedule"

            input_string = f'''
                    name: "{name}"
                    workspaceName: "{workspace_name}"
                    automationPath: "{automation_path}"
                    '''
            
            if new_name:
                input_string += f'newName: "{new_name}"\n'
            if new_description:
                input_string += f'description: "{new_description}"\n'
            if new_cron:
                input_string += f'cron: "{new_cron}"\n'
            if new_arguments:
                arguments_str = GraphQLUtil.arguments_to_str(new_arguments)
                input_string += f'arguments: {arguments_str}\n'
            if new_timezone:
                input_string += f'timezone: "{new_timezone}"\n'
            if new_is_active is not None:
                active = GraphQLUtil.to_graphql(new_is_active)
                input_string += f'active: {active}\n'
            
            graphQLString = f'''mutation {key} {{
                {key}(
                    input: {{{input_string}}}
                ) {{
                    name
                    automationPath
                    workspaceName
                }}
            }}
            '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            result = GraphQLUtil.validate_result_object(result)
            if result is not None or result[key] is not None:
                result = result[key]

            logger.info(f"Schedule with name: {name}, workspace: {workspace_name}, automation_path: {automation_path} updated.")
            
        return result
        

    def deleteSchedule(self, name:str, automation_path:str, workspace_name: str) -> dict:
        """
        Deletes a schedule from the automation service.
        Returns the name, automation path and and workspace name of the deleted schedule in a dictionary.

        Parameters:
        -----------
            name: str
                The name of the schedule to delete
            automation_path: str
                The path to the automation script
            workspace_name: str
                The name of the workspace

        Examples:
        ---------
        >>> client.Automation.deleteSchedule(name="scheduleName", automation_path="/folder/script.py", workspace_name="myWorkspaceName")
        """
        
        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            key = "deleteSchedule"

            graphQLString = f'''mutation {key} {{
                {key}(
                    input: {{
                        name: "{name}"
                        automationPath: "{automation_path}"
                        workspaceName: "{workspace_name}"
                    }}
                ) {{
                    name
                    automationPath
                    workspaceName
                }}
            }}
            '''	

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
            result = GraphQLUtil.validate_result_object(result)
            if result is not None or result[key] is not None:
                result = result[key] 

            logger.info(f"Schedule {name} deleted.")
            
        return result
                       
    

    def executions(self,
                    fields:Union[list, str, None]=None,
                    where:Union[list,tuple,str,None]=None,
                    status: Union[ExecutionStatus,str,None]= None,
                    trigger: Union[TriggerType,str,None]= None,
                    limit: Union[LimitType,str,None]= 'NEWEST',
                    top: int= 1000,
                    pageSize:int=200, 
                    ) -> pd.DataFrame:
        """
        Returns all executed automations (executions) in a dataframe.
        Returns for each execution the name, description and active status.

        Parameters:
        -----------
            fields: list, str, None
                The fields to return. If None, all fields are returned.
                Possible values: "automationPath", "createdAt", "startedAt", 
                "finishedAt", "duration" ,"initiatorType" ,"initiatorReference"
                "argumentInstances" (name and value), "output", "status", "id", "environment"
                "workspaceName", "repositoryName", "branch", "commit", "repositoryUrl"
                Note: argumentInstances only returned if field parameter is None 

            where: list, tuple, str, None
                The filter to apply to the executions. If None, no filter is applied.
                Possible values: see fields parameter
                Note: argumentInstances cannot be filtered

            status: Union[ExecutionStatus,str,None]= None
                The status of the execution. If None, all statuses are returned.
                Possible values: "PENDING", "RUNNING" , "SUCCEEDED" and "FAILED"

            trigger: Union[TriggerType,str,None]= None
                The trigger type of the execution. If None, all trigger types are returned.
                Possible values: "MANUAL", "SCRIPT", "SCHEDULE"

            limit: Union[LimitType,str,None]= 'NEWEST'
                The limit type of the execution. Returns newest or oldest executions.
                Possible values: "NEWEST", "OLDEST"

            top: int= 1000
                Returns a restricted set of executions. Default is 1000.

            pageSize:int=200 
                The page size of executions that is used to retrieve a large number of items. Default is 200.
                
        Example:
        ---------
        >>> # return all executions (top = 1000 as default), all fields 
        >>> client.Automation.executions()    
        >>> # return one specific execution by id:
        >>> execution_id = '1508728c-45fc-41fa-9002-6fc4471acb42'
        >>> client.Automation.executions(where=[f'id eq "{execution_id}"'])
        >>> # return executions of specific workspace, automation
        >>> client.Automation.executions(where=[f'workspaceName eq "myWorkspace"'])     
        >>> client.Automation.executions(where=[f'automationPath eq "/CurrentGridState.py"',f'createdAt >= "2030-04-01T00:00:00+02:00"'])   
        >>> # query on status, use enum from seven2one.Automation:
        >>> client.Automation.executions(where=[f'createdAt >= "2030-04-01T00:00:00+01:00"'],status=client.Automation.ExecutionStatus.SUCCEEDED)
        >>> # query on status, import enum before using it:
        >>> from seven2one.automation import ExecutionStatus # provide enum values 
        >>> client.Automation.executions(where=[f'createdAt >= "2030-04-01T00:00:00+02:00"'],status=ExecutionStatus.SUCCEEDED) 
        >>> # query on status, use string for status query ('PENDING', 'RUNNING','SUCCEEDED','FAILED')
        >>> client.Automation.executions(where=[f'createdAt >= "2030-04-01T00:00:00+02:00"'],status='SUCCEEDED')
        >>> # query on several statuses using where-parameter: # status = (SUCCEEDED OR FAILED) AND createdAt >= "2030-04-01T00:00:00+02:00"
        >>> client.Automation.executions(where=[(f'status eq SUCCEEDED',f'status eq FAILED'),f'createdAt >= "2030-04-01T00:00:00+02:00"'])
        >>> # query on trigger types
        >>> from seven2one.automation import TriggerType 
        >>> client.Automation.executions(where=[f'createdAt >= "2030-04-01T00:00:00+02:00"'],trigger=TriggerType.SCHEDULE) # use enum for trigger
        >>> client.Automation.executions(where=[f'createdAt >= "2030-04-01T00:00:00+02:00"'],trigger='SCHEDULE') # use string for trigger
        >>> # query the OLDEST executions of a specific automation
        >>> from seven2one.automation import LimitType
        >>> client.Automation.executions(where=[f'automationPath eq "/pyweather/temperature.py"'],limit=LimitType.OLDEST,top=5) # use enum for limit	
        >>> client.Automation.executions(where=[f'automationPath eq "/pyweather/temperature.py"'],limit='OLDEST',top=5) # use string for limit
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):
            

            # check if status is set, then add to where-filter
            if status != None:
                if type(status) == str:
                    status = status
                elif type(status) == ExecutionStatus:
                    status = status.value
                else:
                    raise TypeError("status must be of type str or ExecutionStatus")

                if where != None:
                    # append status to where list
                    if type(where) == str:
                        where = [where] # how can I add it to the string?                            
                        where.append(f'status eq {status}')
                    elif type(where) == list:
                        where.append(f'status eq {status}')
                    elif type(where) == tuple:
                        where = list(where)
                        where.append(f'status eq {status}')
                    else:
                        raise TypeError("where must be of type str, list or tuple")
                else: # if where is None, set status as only where-filter criteria
                    where = [f'status eq {status}']  


            # check if trigger is set, then add to where-filter
            if trigger != None:
                if type(trigger) == str:
                    trigger = trigger
                elif type(trigger) == TriggerType:
                    trigger = trigger.value
                else:
                    raise TypeError("trigger must be of type str or TriggerType")

                if where != None:
                    # append TriggerType to where list
                    if type(where) == str:
                        where = [where]
                        where.append(f'initiatorType eq {trigger}') 
                    elif type(where) == list:
                        where.append(f'initiatorType eq {trigger}')
                    elif type(where) == tuple:
                        where = list(where)
                        where.append(f'initiatorType eq {trigger}')
                    else:
                        raise TypeError("where must be of type str, list or tuple")
                else: # if where is None, set trigger as only where-filter criteria
                    where = [f'initiatorType eq {trigger}']
                
            
            ##  arguments
            _arguments = None            
            if where != None:
                resolved_where_filter = GraphQLUtil.resolve_where_automation(self.techStack, where)["topLevel"]
                _arguments = f'''{resolved_where_filter}'''
            else:
                _arguments = ''


            ## limit
            # check if LimitType and number set
            if type(limit) == str:
                limit = limit
            elif type(limit) == LimitType:
                limit = limit.value
            else:
                raise TypeError("limit must be of type str or LimitType")
            
            
            if limit == LimitType.OLDEST.value:
                orderBy = '''order: { createdAt: ASC }'''
            else: # NEWEST
                orderBy = '''order: { createdAt: DESC }'''

            ## fields
            _fields = None

            if fields != None:
                if type(fields)!=list:
                    _fields = [fields]
                else:
                    _fields = GraphQLUtil.query_fields(field_list=fields,
                                                    array_type_fields=None,
                                                    array_page_size=None,
                                                    filter=None,
                                                    recursive=False)
            else:
                _fields = '''automationPath
                            createdAt
                            startedAt
                            finishedAt
                            duration
                            status
                            initiatorType
                            initiatorReference
                            argumentInstances {
                                name
                                value
                            }
                            output                            
                            id
                            environment
                            workspaceName
                            repositoryName
                            workspace {
                                name
                                repository {
                                    name
                                }
                            }
                            branch
                            commit
                            repositoryUrl'''  
                 
           
            _pageInfoFields = f'''
                            endCursor
                            startCursor
                            hasNextPage
                            hasPreviousPage
                            '''

            ## Create GraphQL query string and invoke GraphQL API
            key = "executions"

            result = []
            count = 0
            hasNextPage = True
            endCursor = 'null' 
            stop = False

            while hasNextPage:   
                # Handling top (premature stop)
                if top != None:
                    loadedItems = pageSize * count
                    if top - loadedItems <= pageSize:
                        stop = True
                        pageSize = top - loadedItems

                # create the next query with the endCursor as after parameter
                graphQLString = f'''query {key} {{
                            {key} (
                                first: {pageSize}
                                after: {endCursor} 
                                {_arguments}
                                {orderBy}                    
                                ) {{
                                nodes {{
                                    {_fields}
                                }}
                                pageInfo {{
                                    {_pageInfoFields}
                                }}                           
                            }}
                        }}
                        '''
                
                _result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId)
                _result = GraphQLUtil.validate_result_object(_result)  
                
                if isinstance(_result[key]['nodes'],list): # only if 'node' is a list
                    hasNextPage = _result[key]['pageInfo']['hasNextPage'] 
                    endCursor = _result[key]['pageInfo']['endCursor']
                    endCursor = f'"{endCursor}"' # ensured to be a string, after first use of null
                    result += _result[key]['nodes'] 
                    count += 1
                else: # leave the loop if no more nodes are available
                    stop = True

                if stop == True:
                    break        

            ## Convert to DataFrame and format columns
            df = pd.json_normalize(result)
            
            if df is None or df.empty:
                return pd.DataFrame()
            
            # Convert to datetime if date columns are in df
            if 'createdAt' in df.columns:	
                df['createdAt'] = pd.to_datetime(df['createdAt'], utc=True).dt.tz_convert('Europe/Berlin').dt.strftime("%Y-%m-%d %H:%M:%S%z")
            if 'startedAt' in df.columns:
                df['startedAt'] = pd.to_datetime(df['startedAt'], utc=True).dt.tz_convert('Europe/Berlin').dt.strftime("%Y-%m-%d %H:%M:%S%z")
            if 'finishedAt' in df.columns:
                df['finishedAt'] = pd.to_datetime(df['finishedAt'], utc=True).dt.tz_convert('Europe/Berlin').dt.strftime("%Y-%m-%d %H:%M:%S%z")
    
        return df