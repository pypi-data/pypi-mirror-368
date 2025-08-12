# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.app_resource
import cohesity_management_sdk.models_v2.agent_information
import cohesity_management_sdk.models_v2.error
import cohesity_management_sdk.models_v2.sql_server_instance

class SQLServer(object):

    """Implementation of the 'SQLServer' model.

    Specifies the details of a SQL server.

    Attributes:
        id (string): Specifies the unique identifier of the SQL server host.
        resource_info (AppResource): Specifies the details about App
            Resource.
        agent_info (AgentInformation): Specifies the agent details.
        error (Error): Specifies the error object with error code and a
            message.
        is_primary (bool): Indicates whether this is a active node of a FCI
            cluster or hosts primary replica of a AAG group.
        instances (list of SQLServerInstance): Specifies the list of all sql
            instances running inside the current SQL host.
        is_selected_by_default (bool): Indicates to the UI whether this server
            should be selected by default

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "resource_info":'resourceInfo',
        "agent_info":'agentInfo',
        "error":'error',
        "is_primary":'isPrimary',
        "instances":'instances',
        "is_selected_by_default":'isSelectedByDefault'
    }

    def __init__(self,
                 id=None,
                 resource_info=None,
                 agent_info=None,
                 error=None,
                 is_primary=None,
                 instances=None,
                 is_selected_by_default=None):
        """Constructor for the SQLServer class"""

        # Initialize members of the class
        self.id = id
        self.resource_info = resource_info
        self.agent_info = agent_info
        self.error = error
        self.is_primary = is_primary
        self.instances = instances
        self.is_selected_by_default = is_selected_by_default


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        id = dictionary.get('id')
        resource_info = cohesity_management_sdk.models_v2.app_resource.AppResource.from_dictionary(dictionary.get('resourceInfo')) if dictionary.get('resourceInfo') else None
        agent_info = cohesity_management_sdk.models_v2.agent_information.AgentInformation.from_dictionary(dictionary.get('agentInfo')) if dictionary.get('agentInfo') else None
        error = cohesity_management_sdk.models_v2.error.Error.from_dictionary(dictionary.get('error')) if dictionary.get('error') else None
        is_primary = dictionary.get('isPrimary')
        instances = None
        if dictionary.get("instances") is not None:
            instances = list()
            for structure in dictionary.get('instances'):
                instances.append(cohesity_management_sdk.models_v2.sql_server_instance.SQLServerInstance.from_dictionary(structure))
        is_selected_by_default = dictionary.get('isSelectedByDefault')

        # Return an object of this model
        return cls(id,
                   resource_info,
                   agent_info,
                   error,
                   is_primary,
                   instances,
                   is_selected_by_default)


