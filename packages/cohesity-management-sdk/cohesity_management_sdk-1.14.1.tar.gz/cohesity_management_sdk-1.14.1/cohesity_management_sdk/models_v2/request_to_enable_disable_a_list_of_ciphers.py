# -*- coding: utf-8 -*-


class RequestToEnableDisableAListOfCiphers(object):

    """Implementation of the 'Request to enable/disable a list of ciphers.' model.

    Specifies ciphers to enable/disable on the cluster.

    Attributes:
        enable (bool): If true, the ciphers passed in will be enabled on the
            cluster and all other ciphers will be disabled. If false, the
            ciphers specified will be disabled and all other ciphers on the
            cluster will be enabled.
        ciphers (list of string): Specifies a list of ciphers to
            enable/disable on the cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enable":'enable',
        "ciphers":'ciphers'
    }

    def __init__(self,
                 enable=None,
                 ciphers=None):
        """Constructor for the RequestToEnableDisableAListOfCiphers class"""

        # Initialize members of the class
        self.enable = enable
        self.ciphers = ciphers


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
        enable = dictionary.get('enable')
        ciphers = dictionary.get('ciphers')

        # Return an object of this model
        return cls(enable,
                   ciphers)


