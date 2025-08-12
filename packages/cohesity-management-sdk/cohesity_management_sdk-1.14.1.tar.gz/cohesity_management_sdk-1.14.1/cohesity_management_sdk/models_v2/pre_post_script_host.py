# -*- coding: utf-8 -*-


class PrePostScriptHost(object):

    """Implementation of the 'Pre/Post Script Host' model.

    Specifies the params for the host of a pre / post script.

    Attributes:
        hostname (string): Specifies the Hostname or IP address of the host
            where the pre and post script will be run.
        username (string): Specifies the username for the host.
        host_type (HostTypeEnum): Specifies the Operating system type of the
            host.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "hostname":'hostname',
        "username":'username',
        "host_type":'hostType'
    }

    def __init__(self,
                 hostname=None,
                 username=None,
                 host_type=None):
        """Constructor for the PrePostScriptHost class"""

        # Initialize members of the class
        self.hostname = hostname
        self.username = username
        self.host_type = host_type


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
        hostname = dictionary.get('hostname')
        username = dictionary.get('username')
        host_type = dictionary.get('hostType')

        # Return an object of this model
        return cls(hostname,
                   username,
                   host_type)


