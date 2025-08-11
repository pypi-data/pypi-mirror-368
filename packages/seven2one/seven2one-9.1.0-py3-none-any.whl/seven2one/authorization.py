from typing import Optional, List
from uuid import uuid4
from numpy import empty
import pandas as pd
from loguru import logger

from .utils.ut_graphql import GraphQLUtil
from .utils.ut_error_handler import ErrorHandler

from seven2one.core_interface import ITechStack
from seven2one.dynamicobjects_interface import IDynamicObjects

class Authorization:

    def __init__(self, endpoint: str, techStack: ITechStack, dynamicObjects: IDynamicObjects) -> None:
        self.techStack = techStack
        self.endpoint = endpoint
        self.dynamicObjects = dynamicObjects

    def getVersion(self):
        """
        Returns name and version of the responsible micro service
        """

        return GraphQLUtil.get_service_version(self.techStack, self.endpoint, 'authorization')

    def _resolve_where(self, where: Optional[str]):
        resolvedFilter = ''
        if where != None: 
            resolvedFilter = f'({GraphQLUtil.resolve_where_dyno(self.techStack, self.dynamicObjects, where)["topLevel"]})'
        
        return resolvedFilter

    def roles(self, 
              nameFilter: Optional[str] = None,
              show_detailed_rights: Optional[bool] = False
              ) -> pd.DataFrame:
        """
        Returns a DataFrame of available roles.

        Parameters:
        -----------
        nameFilter : str, optional
            Filters the roles by role name.

        show_detailed_rights : bool, optional
            If True, the DataFrame will contain detailed rights information for each role about the 
            inventory and property permissions. Default is False.       

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with name, id and revision of the role. If show_detailed_rights is True, 
            the DataFrame will also contain detailed inventory and property permissions.

        Example:
        --------
        >>> client.Authorization.roles()
        >>> client.Authorization.roles(nameFilter='SpotMarketDataRole') # returns information about the role with name 'SpotMarketDataRole'
        >>> client.Authorization.roles(show_detailed_rights=True) # returns detailed rights information for each role
        """
        key = 'roles'


        ## fields
        if show_detailed_rights:
            _fields = '''
                    name
                    id
                    revision
                    rootInventoryPermission {
                        inventoryId
                        inventoryPermissions
                        properties {
                            accessPath
                            propertyId
                            propertyPermissions
                        }
                        referencedProperties {
                            accessPath
                            inventoryId
                            inventoryPermissions
                            propertyId
                            propertyPermissions
                        }
                    }
                    rules {
                        id
                        filter
                        filterJson
                        revision
                        group {
                            name
                            id
                        }
                    }
            '''
        else:
            _fields = '''
                        id
                        name
                        revision
                    '''
        
        ## where       
        where_string = "" 
        if nameFilter is not None:
            where_string = f'(where:{{name:{{eq:"{nameFilter}"}}}})'

        ## create graphQL query string and invoke GraphQL API
        graphQLString = f'''query roles {{
            {key} {where_string}
            {{ 
                {_fields}
            }}
        }}'''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        if (not isinstance(result, dict)):
            return pd.DataFrame()
        
        df = pd.json_normalize(result[key])

        return df
    

    def rules(
            self,
            fields:Optional[List[str]]=None, 
            rule_id:Optional[str]=None
            ) -> pd.DataFrame:
        """
        Returns a DataFrame of available rules

        Parameters:
        -----------
        fields : list, optional
            A list of fields to include in the returned DataFrame. If not specified, the default fields will be included.
            Default fields are: id, filter, filterJson, revision, role.id, role.name, group.id and group.name.

            
        rule_id : str, optional
            The ID of a specific rule to filter by. If None, all rules are returned.

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with rule information. Returns id, filter, filterJson, revision, role.id, role.name, group.id and group.name.
            If rule_id is specified, only the rule with that ID is returned.


        Example:
        --------
        >>> client.Authorization.rules()
        >>> client.Authorization.rules(fields=['id', 'filter', 'role.name', 'group.name'])
        >>> client.Authorization.rules(rule_id="hSedEjpSUK") # returns the rule with ID "hSedEjpSUK"

        """

        key = 'rules'

        ## fields
        if fields != None:            
            _fields = GraphQLUtil.query_fields(fields, recursive=True)   
        else:
            _fields ='''
                id
                filter
                filterJson
                revision
                role {
                    name
                    id
                }
                group {
                    name
                    id
                }
            ''' 


        ## where
        where_string = "" 
        if rule_id is not None:
            where_string = f'(where:{{id:{{eq:"{rule_id}"}}}})'


        ## create graphQL query string and invoke GraphQL API
        graphQLString = f'''query Rules {{
            {key}{where_string}  {{
                {_fields}
            }}
        }}
        '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)
        if result == None:
            return pd.DataFrame()
        elif not isinstance(result, dict):
            raise Exception("Result is not a dictionary")
        
        df = pd.json_normalize(result[key])
        return df
    
    

    def addUsers(self, 
                 provider_user_ids: List[str], 
                 fields: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Adds a list of users from Authentik via the provider_users_id to the Authorization-Service users list and returns a data frame with user information.
        Fields defines the values that are returned. By default id, providerSubject, providerUserId and userId are returned.

        Parameters:
        -----------
        provider_user_ids : List[str]
            A list of provider user IDs from Authentik to add into TechStack.

        fields: List[str], optional
            A list of fields to include in the returned DataFrame. If not specified, the default fields will be included.

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with user information (Default: id, providerSubject, providerUserId, userId).


        Example:
        --------
        >>> client.Authorization.addUsers(provider_user_ids=['96127306-98b8-48f1-962e-285cf3e8eab7', 'c88420b8-5b79-4f2c-8dbc-a1718ac372d6'])
        """

        if fields != None:
            _fields = GraphQLUtil.query_fields(fields, recursive=True)   
        else:
            _fields =f'''
                id
                providerSubject
                providerUserId
                userId
            ''' 

        correlation_id = str(uuid4())
        with logger.contextualize(correlation_id = correlation_id):
            key = 'addUsers'
            graphQLString = f'''mutation {key} {{
                {key}(input: {{
                    providerUserIds: ["{'", "'.join(provider_user_ids)}"]
                }}) {{
                    users {{
                        {_fields}
                    }}
                }}
            }}'''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlation_id)
            if result is None:
                return pd.DataFrame()
            elif not isinstance(result, dict):
                raise Exception("Result is not a dictionary")
            
            df = pd.json_normalize(result[key]['users'])

        return df
        

    
    def addUsersToGroups(self, 
                         ids: List[str], 
                         group_ids: List[str], 
                         fields: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Adds one or more users to one or more groups and returns a pandas DataFrame with user information.
        Fields defines the values that are returned. By default userId and groupIds are returned.

        Parameters:
        -----------
        ids : List[str]
            A list of user IDs to add to the groups.
        group_ids : List[str]
            A list of group IDs to add the users to.
        fields : List[str], optional
            A list of fields to include in the returned DataFrame. If not specified, the default fields will be included.

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with user and group information (Default:userId, groupIds).

        Example:
        --------
        >>> # Add a single user with id 'hfvPObAjhY' to two groups with group_ids 'hfwmWgGTpI' and 'hfwoRANI6y'
        >>> client.Authorization.addUsersToGroups(ids=['hfvPObAjhY'], group_ids=['hfwmWgGTpI', 'hfwoRANI6y'])
        >>> # Add each of the multiple users with ids 'hfvPObAjhZ' and 'hfvPObAjhA' to two groups with group_ids 'hfwmWgGTpI' and 'hfwoRANI6y'
        >>> client.Authorization.addUsersToGroups(ids=['hfvPObAjhZ','hfvPObAjhA'], group_ids=['hfwmWgGTpI', 'hfwoRANI6y'])

        """
        correlation_id = str(uuid4())

        if fields is not None:
            _fields = GraphQLUtil.query_fields(fields, recursive=True)
        else:
            _fields = '''
                userId
                groupIds
            '''

        with logger.contextualize(correlation_id=correlation_id):
            key = 'addUsersToGroups'

            user_inputs = []
            # Create a string representation of group_ids for each user
            group_ids_str = ', '.join([f'"{group_id}"' for group_id in group_ids])

            for user_id in ids:
                    user_inputs.append(f'{{ userId: "{user_id}", groupIds: [{group_ids_str}] }}')
            
            user_inputs_str = ', '.join(user_inputs)

            graphQLString = f'''mutation {{
                {key}(input: {{users: [{user_inputs_str}], }}) {{
                    users {{
                        {_fields}
                    }}
                }}
            }}'''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlation_id)

            if result is None:
                return pd.DataFrame()
            elif not isinstance(result, dict):
                raise Exception("Result is not a dictionary")
            
            users = result[key]['users']
            df = pd.DataFrame(users)

        return df



    def getAvailableUsers(self,
                          fields: Optional[List[str]] = None,
                          include_already_added: Optional[bool] = True) -> pd.DataFrame:
        """
        Retrieves available users, including all Users in Authentik, and returns a list with user information. Users can be filtered via the 'usernames' parameter.
        Fields defines the values that are returned. By default providerUserId, eMail and username are returned.
        The username will always be returned.

        Parameters:
        -----------
        
        fields : List[str], optional
            A list of fields to include in the returned DataFrame. If not specified, the default fields will be included.

        include_already_added : bool, optional
            If True, the function will include users that are already added from Authentik into the TechStack System. Default is True.

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with user and group information (Default:providerUserId, eMail).

        Example:
        --------
        >>> client.Authorization.getAvailableUsers() # all users with all fields
        >>> client.Authorization.getAvailableUsers(fields=['username,eMail,providerUserId,isActive,isServiceAccount']) # all users with specific fields
        >>> client.Authorization.getAvailableUsers(include_already_added=False) # only users in Authentik that are not added yet into the TechStack System
        """
        
        ## arguments
        _arguments = ''
        if include_already_added:
            _arguments = 'includeAlreadyAdded: true'
        else:
            _arguments = 'includeAlreadyAdded: false'
        
        ## fields
        if fields != None: 
            _fields = GraphQLUtil.query_fields(fields, recursive=True)   
        else:
            _fields ='''
                username
                eMail
                providerUserId
                isActive
                isServiceAccount
            ''' 

        ## create graphQL query string and invoke GraphQL API 
        correlation_id = str(uuid4())

        with logger.contextualize(correlation_id=correlation_id):
            key = 'availableUsers'
            graphQLString = f'''query {key} {{
                {key} (
                    {_arguments}
                ) 
                {{
                    {_fields}
                }}
            }}'''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlation_id)

            if not isinstance(result, dict):
                return pd.DataFrame()

            users = result[key]
            df = pd.json_normalize(users)

        return df



    def addGroups(self, group_names: List[str], fields: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Adds a list of groups and returns a pandas DataFrame with group information.
        Fields defines the values that are returned. By default name and id are returned

        Parameters:
        -----------
        group_names : List[str]
            A list of group names to add.
        fields : List[str], optional
            A list of fields to include in the results. If not specified, the default fields will be included.

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with group information (Default:name, id).

        Example:
        --------    
        >>> client.Authorization.addGroups(['Group1', 'Group2'])
        >>> client.Authorization.addGroups(['Group1', 'Group2'], fields=['name']) # returns only name of the groups

        """
        if fields is not None:
            _fields = GraphQLUtil.query_fields(fields, recursive=True)
        else:
            _fields = '''
                name
                id
            '''

        correlation_id = str(uuid4())

        with logger.contextualize(correlation_id=correlation_id):
            key = 'addGroups'
            graphQLString = f'''mutation {{
                {key}(input: {{names: ["{'", "'.join(group_names)}"] }}) {{
                    groups {{
                        {_fields}
                    }}
                }}
            }}'''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlation_id)

            if not isinstance(result, dict):
                return pd.DataFrame()

            groups = result[key]['groups']
            df = pd.DataFrame(groups)

        return df


    
    def serviceAccounts(self) -> pd.DataFrame:
        """
        Returns a DataFrame of available service accounts.
        Parameters:
        -----------
        None
        
        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with serviceAccount information. Returns username, eMail, id, userId, providerSubject, providerUserId, isActive, isServiceAccount and groups the user is member in.    

        Example:
        --------
        >>> client.Authorization.serviceAccounts()
        """

        # Get all users and filter for service accounts
        df_all_users = self.users()
        
        if not df_all_users.empty:
            df_service_accounts = pd.DataFrame(df_all_users[df_all_users['isServiceAccount'] == True])
        else:
            logger.info("No users found in the TechStack System.")
            return pd.DataFrame()

        return df_service_accounts        


    def users(
        self,
        fields: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Returns a DataFrame of users existing in the TechStack System.

        Parameters:
        -----------
        fields : List[str], optional
            A list of fields to include in the returned DataFrame. If not specified, the default fields will be included.
            Default fields are: username, eMail, id, userId, providerSubject, providerUserId, isActive, isServiceAccount and groups.
            Note: field "groups" is only returned with default fields, not supported in specific fields list.

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with user information. Returns username, eMail, id, userId, providerSubject, providerUserId, isActive, isServiceAccount and groups the user is member in.
            
        Example:
        --------
        >>> client.Authorization.users() # all users with default fields
        >>> client.Authorization.users(fields=['username,eMail,providerSubject,isActive']) # all users with specific fields
        """

        key = 'users'

        if fields != None:
            _fields = GraphQLUtil.query_fields(fields, recursive=True)   
        else:
            _fields ='''
                    username
                    eMail
                    id
                    userId
                    providerSubject
                    providerUserId
                    isActive
                    isServiceAccount
                    groups {
                        name
                        id
                    }
                '''       

        graphQLString = f'''query Users {{
            {key} {{
                {_fields}
            }}
        }}
        '''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)

        if result == None:
            return pd.DataFrame()
        elif not isinstance(result, dict):            
            raise Exception("Result is not a dictionary")
        else:
            df = pd.json_normalize(result[key])

        return df



    def userGroups(self, 
                   user_group: Optional[str] = None,
                   show_detailed_rights: Optional[bool] = False) -> pd.DataFrame:
        """
        Returns a DataFrame of available user groups with its user members and the roles that define the rights of the user group. 

        Parameters:
        -----------
        user_group : str, optional
            The name of one user group to filter by. If None, all user groups are returned.

        show_detailed_rights : bool, optional
            If True, the DataFrame will contain detailed rights information for each user group such as 
            user members, permissions, roles/rules and external rights. Default is False.
            If False, only the user group id and name, the usernames and role names are returned.

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with user group information.


        Example:
        --------
        >>> client.Authorization.userGroups() # returns all user groups with default fields
        >>> client.Authorization.userGroups(user_group='SuperAdmin', show_detailed_rights=True) # returns for a user group the detailed rights information
        """
        key = 'groups'

        ## fields
        if show_detailed_rights:
            _fields = '''
                name
                id
                users {
                    username
                    eMail
                    providerSubject
                    providerUserId
                    isServiceAccount
                    isActive
                }
                permissions {
                    type
                    permissions
                    revision
                }
                rules {
                    role {
                        name
                        rootInventoryPermission {
                            inventoryId
                            inventoryPermissions
                            properties {
                                propertyId
                                accessPath
                                propertyPermissions
                            }
                            referencedProperties {
                                inventoryId
                                accessPath
                                inventoryPermissions
                                propertyId
                                propertyPermissions
                            }
                        }
                    }
                }
                externalRights {
                    scope
                    rights {
                        right
                    }
                }
            '''
        else:
            _fields = '''
                id
                name
                users {
                    username
                }
                rules {
                    role {
                        name
                        }
                    }
            '''

        ## where
        where_string = "" 
        if user_group is not None:
            where_string = f'(where:{{name:{{eq:"{user_group}"}}}})'

        ## create graphQL query string and invoke GraphQL API
        graphQLString = f'''query userGroups {{
            {key}{where_string} {{
                {_fields}
            }}
        }}'''

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString)

        if result is None:
            return pd.DataFrame()
        elif not isinstance(result, dict):
            raise Exception("Result is not a dictionary")
        
        ## normalize the result into a pandas DataFrame
        df = pd.json_normalize(result[key])

        return df
    

    def updatePermissions(self, group: str, permissions: List[str], permissionType: str) -> pd.DataFrame:
        
        """
        Updates permissions of a group and returns a pandas DataFrame with permission information.

        Parameters:
        -----------
        group : str
            The name of the group to update the permissions of.
        permissions : List[str]
            A list of permissions to update. Permission are ["READ","ADD","UPDATE","DELETE"]
        permissionType : str
            The type of permission to update. PermissionTypes are "USERS", "USERS_GROUPS", "RULES", "ROLES", "DYNAMIC_OBJECT_TYPES", "SERVICE_ACCOUNTS", "EXTERNAL_RIGHTS" and "PERMISSIONS".

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with permission information. Returns groupId, type and id.

        Example:
        --------
        >>> client.Authorization.updatePermissions(group='myUserGroup', permissions=["READ","ADD","UPDATE","DELETE"], permissionType='USERS')
        >>> client.Authorization.updatePermissions(group='myUserGroup', permissions=["READ"], permissionType='EXTERNAL_RIGHTS')
        >>> client.Authorization.updatePermissions(group='myUserGroup', permissions=["READ","ADD","UPDATE"], permissionType='USERS_GROUPS')

        """
        correlation_id = str(uuid4())
       
        _fields = '''
            groupId
            type
            id
        '''

        # get the permissionId of the group and the groupId
        permission_df = self.getPermissionsOfGroups(group_name=group) 
        if permission_df.empty:
            raise Exception(f"No permissions found for group {group}")
        permissionId = permission_df.loc[permission_df["permissions.type"] == permissionType, "permissions.id"].iloc[0]
        groupId = permission_df.loc[0, "id"]

        # build permissions graphQL string
        permissions_enum = ','.join(permissions)

        with logger.contextualize(correlation_id=correlation_id):
            key = 'updatePermissions'

            graphQLString = f'''mutation {{
                {key}(input: {{permissions: {{groupId:"{groupId}", id:"{permissionId}", permissions: [{permissions_enum}], type: {permissionType}}}, }}) {{
                    permissions {{
                        {_fields}
                    }}
                }}
            }}'''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlation_id)
            if not isinstance(result, dict):
                raise Exception("Result is not a dictionary")
            
            df = pd.json_normalize(result[key]['permissions'], meta =  ['groupId', 'type', 'id'])
            
        return df


    def addPermissions(self, group: str, permissions: List[str], permissionType: str) -> pd.DataFrame: 
        """
        Adds one or more permissions to a group and returns a pandas DataFrame with permission information.

        Parameters:
        -----------
        group : str
            The name of the group to add the permissions to.
        permissions : List[str]
            A list of permissions to add to the group. Permission are ["ADD","DELETE","READ","UPDATE"]
        permissionType : str
            The type of permission to add to the group. PermissionTypes are "USERS", "USERS_GROUPS", "RULES", "ROLES", "DYNAMIC_OBJECT_TYPES", "SERVICE_ACCOUNTS", "EXTERNAL_RIGHTS" and "PERMISSIONS".

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame with permission information. Returns groupId, type and id.


        Example:
        --------
        >>> client.Authorization.addPermissions(group='myUserGroup', permissions=["READ","ADD","UPDATE","DELETE"], permissionType='USERS')
        >>> client.Authorization.addPermissions(group='myUserGroup', permissions=["READ"], permissionType='EXTERNAL_RIGHTS')
        >>> client.Authorization.addPermissions(group='myUserGroup', permissions=["READ","ADD","UPDATE"], permissionType='USERS_GROUPS')
        """
        correlation_id = str(uuid4())

    
        _fields = '''
            groupId
            type
            id
        '''

        # get item in _groups dataframe where name is equal to group
        _groups = self.userGroups()
        if _groups.empty:
            raise Exception(f"No user group found with name {group}")   
        if group not in _groups['name'].values:
            raise Exception(f"No user group found with name {group}") 
        else:
            # get groupId of the group            
            groupId = _groups.loc[_groups['name'] == group, "id"].iloc[0]  
            

        # build permissions graphQL string
        permissions_enum = ','.join(permissions)

        with logger.contextualize(correlation_id=correlation_id):
            
            key = 'addPermissions'
            graphQLString = f'''mutation {{
                {key}(input: {{permissions: {{groupId:"{groupId}", permissions: [{permissions_enum}], type: {permissionType}}}}}) {{
                    permissions {{
                        {_fields}
                    }}
                }}
            }}'''
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlation_id)
            if not isinstance(result, dict):
                raise Exception("Result is not a dictionary")
            
            df = pd.json_normalize(result[key]['permissions'], meta =  ['groupId', 'type', 'id'])

        return df

    
    def getPermissionsOfGroups(self, group_name: Optional[str] = None) -> pd.DataFrame: 
        """
        Retrieves all groups and their permissions, permissions can be filtered by group.

        Parameters:
        -----------
        group_name : str, optional  
            A group name to filter the results by.

        Returns:
        --------
        pd.DataFrame
            A pandas DataFrame about permissions and which user group they belong to. 
            Returns name and id of the group, as well as id, permissions, type and revision of the perimissions of each group

        Example:
        --------
        >>> client.Authorization.getPermissionsOfGroups()
        >>> client.Authorization.getPermissionsOfGroups(group_name='myUserGroup')
        """
       
        _fields =f'''
            name
            id
            permissions{{
                id
                permissions
                type
                revision
            }}
        ''' 

        correlation_id = str(uuid4())
        where_string = "" 
        if group_name is not None:
            where_string = f'(where:{{name:{{eq:"{group_name}"}}}})'
       
        with logger.contextualize(correlation_id=correlation_id):
            key = 'permissionsOfGroups'
            graphQLString = f'''query {key} 
                                {{groups {where_string}
                                    {{
                                        {_fields}
                                    }}
                                }}'''
            
            # execute GraphQL query
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlation_id)
            if not isinstance(result, dict):
                raise Exception("Result is not a dictionary")
            
            df = pd.json_normalize(result["groups"], 'permissions', ["name", "id"], record_prefix="permissions.")
            return df
        

    def addRole(
                self,
                inventoryName:str, 
                roleName:str,
                userGroups:Optional[List[str]] = None, 
                objectPermissions:List[str] = ['Create', 'Delete'], 
                propertiesPermissions:List[str] = ['Read', 'Update']
                ) -> None:

        """
        Adds a role for an inventory and sets all rights to all properties.
        Assigns the role to the specified user groups.

        Parameters:
        ----------
        inventoryName : str
            The name of the inventory for which the new role authorizes rights.
        roleName : str
            Name of the new role.
        userGroup : List[str] = None
            List of user group names. If None, the role will be created without attaching user groups.
        objectPermissions : List[str] = ['Create', 'Delete']
            Default is 'Create' and 'Delete' to allow creating and deleting items of the specified inventory.            
        propertiesPermissions : List[str] = ['Read', 'Update']
            Default is 'Read' and 'Update'. All properties will receive 
            the specified rights. Other entries are not allowed.
            Permissions are not extended on referenced inventories!

        Returns:
        ------- 
        None

        Example:
        --------        
        >>> client.Authorization.addRole(inventoryName='MarketData', roleName='MarketDataAdminRole', userGroups=['MarketDataAdmins'], objectPermissions=['Create', 'Delete'], propertiesPermissions=['Read', 'Update'])
        >>> client.Authorization.addRole(inventoryName='MarketData', roleName='MarketDataAdminRole_NotAllowedToModify', userGroups=['MarketDataManagers'], objectPermissions=['Create'], propertiesPermissions=['Read'])

        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            # Parameter validation
            try:
                self.techStack.metaData.structure[inventoryName]
            except:
                ErrorHandler.error(self.techStack.config.raiseException, f"Unknown inventory '{inventoryName}'")
                return
            
            try:
                roles = self.roles()
                if roleName in list(roles['name']):
                    ErrorHandler.error(self.techStack.config.raiseException, f"Role '{roleName}' already exists.")
                    return
            except:
                pass

            if isinstance(userGroups, str):
                userGroups = [userGroups]

            dfUserGroups = None
            if userGroups != None:
                # 'in' is not supported therefore load all groups
                dfUserGroups = self.userGroups()
                falseUserGroups = []
                for group in userGroups:
                    if group not in list(dfUserGroups['name']):
                        falseUserGroups.append(group)
                
                if falseUserGroups:
                    ErrorHandler.error(self.techStack.config.raiseException, f"Unknown user group(s) {falseUserGroups}")
                    return

            # Add role
            properties = self.techStack.metaData.structure[inventoryName]['properties']

            ppstring = '[' + ','.join(map(str.upper, propertiesPermissions)) + ']'
            props = '[\n'
            refProps = '[\n'
            for _, value in properties.items():
                if value["type"] == 'scalar':
                    props += f'{{ propertyId: {GraphQLUtil.to_graphql(value["propertyId"])}\n permissions: {ppstring} }}\n'
                elif value["type"] == 'reference':
                    refProps += f'{{ propertyId: {GraphQLUtil.to_graphql(value["propertyId"])}\n inventoryId: {GraphQLUtil.to_graphql(value["inventoryId"])}\n propertyPermissions: {ppstring}\n inventoryPermissions: [NONE]\n properties: []\n referencedProperties: []\n }}'
            props += ']'
            refProps += ']'
            
            graphQLString= f'''
            mutation AddRole($roleName: String!, $inventoryId: String!, $inventoryPermissions: [ObjectPermission!]!) {{ 
                addRoles (input: {{
                    roles: {{
                        name: $roleName
                        rootInventoryPermission: {{
                            inventoryId: $inventoryId
                            inventoryPermissions: $inventoryPermissions
                            properties: {props}
                            referencedProperties: {refProps}
                            }}
                        }}
                    }})
                    {{
                    roles {{
                        id
                    }}
                }}
            }}
            '''
            params = {
                "roleName": roleName,
                "inventoryId": self.techStack.metaData.structure[inventoryName]['inventoryId'],
                "inventoryPermissions": list(map(str.upper, objectPermissions)),
            }

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlationId, params=params)
            if result == None:
                return
            elif not isinstance(result, dict):
                raise Exception("Result is not a dictionary")

            logger.info(f"Role {roleName} created.")

            roleId = result['addRoles']['roles'][0]['id']

            # Add rules
            if userGroups != None:
                for groupname in userGroups:
                    if (dfUserGroups is None or dfUserGroups.empty):
                        raise Exception("No user groups found")
                    
                    groupId = dfUserGroups.set_index('name').to_dict(orient='index')[groupname]['id']
                    addRuleGqlString= f'''
                    mutation AddRule($roleId: String!, $groupId: String!) {{
                        addRules (input: {{
                            rules: {{
                                roleId: $roleId
                                groupId: $groupId
                                filter: ""
                                filterFormat: EXPRESSION
                                }}
                            }})
                            {{
                            rules {{
                                ruleId
                            }}
                        }}
                    }}
                    '''
                    result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, addRuleGqlString, correlationId, params={"roleId": roleId, "groupId": groupId})
                    if result != None:
                        logger.info(f"Rule for {roleName} and user group {groupname} added.")
                    else:
                        logger.error(f"Rule for {roleName} and user group {groupname} could not be added.")

            return

    def removeRole(self, role:str) -> None:
        """
        Deletes a role and all related rules.

        Parameters:
        -----------
        role : str
            The name of the role to delete.

        Returns:
        --------
        None

        Example:
        --------
        >>> client.Authorization.removeRole(role='MarketDataAdminRole')
        """

        correlationId = str(uuid4())
        with logger.contextualize(correlation_id=correlationId):

            # Get Id of the role
            rolesResult = self.roles()
            roles = rolesResult.set_index('name')
            roleId = roles.loc[role, 'id']

            # Get all rules of the role
            all_rules = self.rules()
            if (all_rules is None or all_rules.empty):
                raise Exception("No rules found")
            
            all_rules = all_rules.set_index('role.name')
            try:
                rules = all_rules.loc[[role], ['id']] # filter rules and ensure rules is dataframe even for 1 result row
                ruleIds = rules['id'].tolist()
            except:
                rules = None
                ruleIds = []

            # First delete all existing rules            
            if rules is not None:                           
                for ruleId in ruleIds:
                    removeRuleGraphQLString = f'''
                                mutation removeRules{{
                                    removeRules(input: {{
                                        ids: ["{ruleId}"]
                                    }}) 
                                }}
                                '''
                    
                    result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, removeRuleGraphQLString, correlationId)                    
                    if result != None:
                        logger.info(f"Rule {ruleId} of role {role} with id {ruleId} has been deleted.")
                    else:
                        ErrorHandler.error(self.techStack.config.raiseException, f"Rule {ruleId} of role {roleId} could not be deleted.")
                        return

            # After all rules have been deleted, delete the role            
            removeRoleGraphQLString = f'''
                    mutation removeRoles {{
                        removeRoles(input: {{
                            ids: ["{roleId}"]
                        }}) 
                    }}
            '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, removeRoleGraphQLString, correlationId)
            if result != None:
                logger.info(f"Role {role} with id {roleId} has been deleted.")
            else:
                ErrorHandler.error(self.techStack.config.raiseException, f"Role {roleId} could not be deleted.")
            
            return
        
    
    def addRule(self, role: str, group: str, filter: str) -> str:
        """
        Adds a rule connecting a role with usergroup and adds a filter to this rule.

        Parameters:
        -----------
        role : str
            The name of the role associated with the rule.
        group : str
            The name of the group to add the rule to.
        filter : str
            The filter to apply to the rule. The format must be:"Object.porpertyID=filter_value" 

        Returns:
        --------
        str
            The ID of the added rule.

        Example:
        --------
        >>> # Rule shall filter items for 'Region' = Germany, porperty 'Region'has propertyId 'hzxdAjlrFo'
        >>> client.Authorization.addRule(role='MarketDataAdminRole', group='MarketDataAdmins_CentralEurope', filter="Object.hzxdAjlrFo='DE'")
        >>> # Rule shall filter items with 'Compliance_Criticality' (propertyId is 'i1LD55SZ7o') = 3 (INT)
        >>> client.Authorization.addRule(role='MarketDataAdminRole', group='MarketDataAdmins_HighCriticality', filter="Object.i1LD55SZ7o=3")
        """
        # Get role id and group id
        try:
            roleId = self.roles(nameFilter =f'{role}')['id'].iloc[0]
        except Exception:
            ErrorHandler.error(self.techStack.config.raiseException, f"Role '{role}' not found.")
            return ''
        
        try:
            groupId = self.userGroups(user_group =f'{group}')['id'].iloc[0] 
        except Exception:
            ErrorHandler.error(self.techStack.config.raiseException, f"User group '{group}' not found.")
            return ''
        
        # Create GraphQL mutation string to add the rule
        graphqlString = '''
            mutation AddRule($roleId: String!, $groupId: String!, $filter: String!) {
                addRules(input: {
                    rules: {
                        roleId: $roleId
                        groupId: $groupId
                        filter: $filter
                        filterFormat: EXPRESSION
                    }
                }) {
                    rules {
                        ruleId
                    }
                }
            }
        '''

        params = {
            "roleId": roleId,
            "groupId": groupId,
            "filter": filter
        }

        result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphqlString, params=params)

        if isinstance(result, dict):
            rule_id = result['addRules']['rules'][0]['ruleId']
            logger.info(f"Rule for {role} and user group {groupId} added with ID {rule_id}.")
            return rule_id
        else:
            ErrorHandler.error(self.techStack.config.raiseException, f"Rule could not be added.")
            return ''



    def removeRules(self, rule_ids: List[str]) -> None:
        """
        Removes rules by their IDs.

        Parameters:
        -----------
        rule_ids : List[str]
            A list of rule IDs to remove.

        Returns:
        --------
        None

        Example:
        --------
        >>> client.Authorization.removeRules(['i1LPd7Othg', 'i1MA8Rcacy'])
        """
        
        correlation_id = str(uuid4())
        
        with logger.contextualize(correlation_id=correlation_id):
            # Create a string of rule IDs for the GraphQL mutation
            rule_ids_str = ', '.join([f'"{rule_id}"' for rule_id in rule_ids])

            # Create GraphQL mutation string to remove the rules
            graphQLString = f'''
                mutation removeRules {{
                    removeRules(input: {{ ids: [{rule_ids_str}] }}) 
                }}
            '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlation_id)

            if result is not None:
                logger.info(f"Removed rules with IDs: {', '.join(rule_ids)}")
            else:
                ErrorHandler.error(self.techStack.config.raiseException, "Failed to remove rules.")

    

    def removeUsers(self, ids: List[str]) -> None:
        """
        Removes users by their IDs.

        Parameters:
        -----------
        ids : List[str]
            A list of user IDs to remove.

        Returns:
        --------
        None

        Example:
        --------
        >>> client.Authorization.removeUsers(['userId1', 'userId2'])
        """
        
        correlation_id = str(uuid4())
        
        with logger.contextualize(correlation_id=correlation_id):
            # Create a string of user IDs for the GraphQL mutation
            user_ids_str = ', '.join([f'"{user_id}"' for user_id in ids])

            # Create GraphQL mutation string to remove the users
            graphQLString = f'''
                mutation removeUsers {{
                    removeUsers(input: {{ ids: [{user_ids_str}] }}) 
                }}
            '''

            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlation_id)

            if result is not None:
                logger.info(f"Removed users with IDs: {', '.join(ids)}")
            else:
                ErrorHandler.error(self.techStack.config.raiseException, "Failed to remove users.")


    def removeUsersFromGroups(self, ids: List[str], group_ids: List[str]) -> None:
        """
        Removes users from specified user groups.

        Parameters:
        -----------
        ids : List[str]
            A list of user IDs to remove from the groups.
        group_ids : List[str]
            A list of group IDs from which the users will be removed.

        Returns:
        --------
        None

        Example:
        --------
        >>> # Remove a single user from two groups
        >>> client.Authorization.removeUsersFromGroups(['i1GbEiSTPU'], ['hfvPObAjhY', 'hfvPObAjhZ'])
        >>> # Remove multiple users from multiple groups
        >>> client.Authorization.removeUsersFromGroups(['i1GbEiSTPU', 'i1GcOkb7ya'], ['hfvPObAjhY', 'hfvPObAjhZ', 'fWmCgL3cUi'])
        """
        
        correlation_id = str(uuid4())
        
        with logger.contextualize(correlation_id=correlation_id):
            
            # Create a list of user inputs for the GraphQL mutation
            user_inputs = []

            # Create a string of group IDs             
            group_ids_str = ', '.join([f'"{group_id}"' for group_id in group_ids])

            for user_id in ids:
                    user_inputs.append(f'{{ userId: "{user_id}", groupIds: [{group_ids_str}] }}')
            
            user_inputs_str = ', '.join(user_inputs)

            # Create GraphQL mutation string to remove the users from the groups
            graphQLString = f'''
                mutation removeUsersFromGroups {{
                    removeUsersFromGroups(input: {{users: [{user_inputs_str}], }}) 
                }}
            '''

            # Execute the GraphQL mutation
            result = GraphQLUtil.execute_GraphQL(self.techStack, self.endpoint, graphQLString, correlation_id)

            if result is not None:
                logger.info(f"Removed users {', '.join(ids)} from groups {', '.join(group_ids)}")
            else:
                ErrorHandler.error(self.techStack.config.raiseException, "Failed to remove users from groups.")
