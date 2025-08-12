# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.oracle_protection_group_sbt_host

class OracleProtectionGroupDatabaseHost(object):

    """Implementation of the 'Oracle Protection Group Database Host' model.

    Specifies details about an Oracle database host.

    Attributes:
        host_id (string): Specifies the id of the database host from which
            backup is allowed.
        channel_count (int): Specifies the number of channels to be created
            for this host. Default value for the number of channels will be
            calculated as the minimum of number of nodes in Cohesity cluster
            and 2 * number of CPU on the host.
        port (long|int): Specifies the port where the Database is listening.
        sbt_host_params (OracleProtectionGroupSBTHost): Specifies details
            about capturing Oracle SBT host info.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "host_id":'hostId',
        "channel_count":'channelCount',
        "port":'port',
        "sbt_host_params":'sbtHostParams'
    }

    def __init__(self,
                 host_id=None,
                 channel_count=None,
                 port=None,
                 sbt_host_params=None):
        """Constructor for the OracleProtectionGroupDatabaseHost class"""

        # Initialize members of the class
        self.host_id = host_id
        self.channel_count = channel_count
        self.port = port
        self.sbt_host_params = sbt_host_params


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
        host_id = dictionary.get('hostId')
        channel_count = dictionary.get('channelCount')
        port = dictionary.get('port')
        sbt_host_params = cohesity_management_sdk.models_v2.oracle_protection_group_sbt_host.OracleProtectionGroupSBTHost.from_dictionary(dictionary.get('sbtHostParams')) if dictionary.get('sbtHostParams') else None

        # Return an object of this model
        return cls(host_id,
                   channel_count,
                   port,
                   sbt_host_params)


