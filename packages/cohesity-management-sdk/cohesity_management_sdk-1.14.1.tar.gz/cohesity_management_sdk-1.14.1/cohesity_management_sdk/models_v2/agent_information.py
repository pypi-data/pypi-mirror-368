# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.host_setting_check

class AgentInformation(object):

    """Implementation of the 'AgentInformation' model.

    Specifies the agent details.

    Attributes:
        connection_status (ConnectionStatusEnum): Specifies the status of
            agent connection.
        support_status (SupportStatusEnum): Specifies the whether agent
            version is compatible with cluster version ro use various
            features.
        agent_sw_version (string): Specifies the software version of the
            agent
        last_fetched_time_in_usecs (long|int): Specifies the time in usecs
            when the last agent info was fetched.
        host_setting_checks (list of HostSettingCheck): Specifies the list of
            host checks and its results.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "connection_status":'connectionStatus',
        "support_status":'supportStatus',
        "agent_sw_version":'agentSwVersion',
        "last_fetched_time_in_usecs":'lastFetchedTimeInUsecs',
        "host_setting_checks":'hostSettingChecks'
    }

    def __init__(self,
                 connection_status=None,
                 support_status=None,
                 agent_sw_version=None,
                 last_fetched_time_in_usecs=None,
                 host_setting_checks=None):
        """Constructor for the AgentInformation class"""

        # Initialize members of the class
        self.connection_status = connection_status
        self.support_status = support_status
        self.agent_sw_version = agent_sw_version
        self.last_fetched_time_in_usecs = last_fetched_time_in_usecs
        self.host_setting_checks = host_setting_checks


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
        connection_status = dictionary.get('connectionStatus')
        support_status = dictionary.get('supportStatus')
        agent_sw_version = dictionary.get('agentSwVersion')
        last_fetched_time_in_usecs = dictionary.get('lastFetchedTimeInUsecs')
        host_setting_checks = None
        if dictionary.get("hostSettingChecks") is not None:
            host_setting_checks = list()
            for structure in dictionary.get('hostSettingChecks'):
                host_setting_checks.append(cohesity_management_sdk.models_v2.host_setting_check.HostSettingCheck.from_dictionary(structure))

        # Return an object of this model
        return cls(connection_status,
                   support_status,
                   agent_sw_version,
                   last_fetched_time_in_usecs,
                   host_setting_checks)


