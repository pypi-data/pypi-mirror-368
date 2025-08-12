# -*- coding: utf-8 -*-


class IPAddressPreference(object):

    """Implementation of the 'IP Address Preference' model.

    Preferred IP address mode of the cluster

    Attributes:
        ip_preference (IpPreference1Enum): Specifies the ip preference of
            cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "ip_preference":'ipPreference'
    }

    def __init__(self,
                 ip_preference=None):
        """Constructor for the IPAddressPreference class"""

        # Initialize members of the class
        self.ip_preference = ip_preference


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
        ip_preference = dictionary.get('ipPreference')

        # Return an object of this model
        return cls(ip_preference)


