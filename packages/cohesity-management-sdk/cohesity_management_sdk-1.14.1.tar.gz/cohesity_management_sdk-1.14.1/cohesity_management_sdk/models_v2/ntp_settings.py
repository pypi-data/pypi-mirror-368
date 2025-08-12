# -*- coding: utf-8 -*-


class NTPSettings(object):

    """Implementation of the 'NTPSettings' model.

    Specifies if the ntp/primary secondary scheme should be disabled

    Attributes:
        ntp_authentication_enabled (bool): Specifies if the cluster is using NTP with authentication.
        ntp_servers_internal (bool): Specifies if the NTP servers are on internal network or not.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "ntp_authentication_enabled":'ntpAuthenticationEnabled',
        "ntp_servers_internal":'ntpServersInternal'
    }

    def __init__(self,
                 ntp_authentication_enabled=None,
                 ntp_servers_internal=None
                 ):
        """Constructor for the NTPSettings class"""

        # Initialize members of the class
        self.ntp_authentication_enabled = ntp_authentication_enabled
        self.ntp_servers_internal = ntp_servers_internal


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
        ntp_authentication_enabled = dictionary.get('ntpAuthenticationEnabled')
        ntp_servers_internal = dictionary.get('ntpServersInternal')

        # Return an object of this model
        return cls(ntp_authentication_enabled,
                   ntp_servers_internal
                   )