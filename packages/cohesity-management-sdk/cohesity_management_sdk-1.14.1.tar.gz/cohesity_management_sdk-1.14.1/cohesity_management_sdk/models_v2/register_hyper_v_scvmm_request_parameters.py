# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.throttling_params

class HyperVSCVMMrequestparameters(object):

    """Implementation of the 'HyperV SCVMM request parameters' model.

    Specifies parameters to register HyperV SCVMM.

    Attributes:
        username (string): Specifies the username to access target entity.
        password (string): Specifies the password to access target entity.
        endpoint (string): Specifies the endpoint IPaddress, URL or hostname
            of the host.
        description (string): Specifies the description of the source being
            registered.
        agent_endpoint (string): Specifies the agent endpoint if it is different from the source
            endpoint.
        throttling_params (ThrottlingParams): Specifies the throttling params.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "username":'username',
        "password":'password',
        "endpoint":'endpoint',
        "description":'description',
        "agent_endpoint":'agentEndpoint',
        "throttling_params":'throttlingParams'
    }

    def __init__(self,
                 username=None,
                 password=None,
                 endpoint=None,
                 description=None,
                 agent_endpoint=None,
                 throttling_params=None):
        """Constructor for the HyperV SCVMM request parameters class"""

        # Initialize members of the class
        self.username = username
        self.password = password
        self.endpoint = endpoint
        self.description = description
        self.agent_endpoint = agent_endpoint
        self.throttling_params = throttling_params


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
        username = dictionary.get('username')
        password = dictionary.get('password')
        endpoint = dictionary.get('endpoint')
        description = dictionary.get('description')
        agent_endpoint = dictionary.get('agentEndpoint')
        throttling_params = cohesity_management_sdk.models_v2.throttling_params.ThrottlingParams.from_dictionary(dictionary.get('throttlingParams')) if dictionary.get('throttlingParams') else None

        # Return an object of this model
        return cls(username,
                   password,
                   endpoint,
                   description,
                   agent_endpoint,
                   throttling_params)