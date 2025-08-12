# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.syslog_server

class ListOfSyslogServers(object):

    """Implementation of the 'List of syslog servers' model.

    Specifies the list of syslog servers.

    Attributes:
        syslog_servers (list of SyslogServer): Specifies the list of syslog
            servers.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "syslog_servers":'syslogServers'
    }

    def __init__(self,
                 syslog_servers=None):
        """Constructor for the ListOfSyslogServers class"""

        # Initialize members of the class
        self.syslog_servers = syslog_servers


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
        syslog_servers = None
        if dictionary.get("syslogServers") is not None:
            syslog_servers = list()
            for structure in dictionary.get('syslogServers'):
                syslog_servers.append(cohesity_management_sdk.models_v2.syslog_server.SyslogServer.from_dictionary(structure))

        # Return an object of this model
        return cls(syslog_servers)


