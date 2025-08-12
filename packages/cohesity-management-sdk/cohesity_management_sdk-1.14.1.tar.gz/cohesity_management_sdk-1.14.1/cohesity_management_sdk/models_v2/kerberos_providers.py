# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.kerberos_provider

class KerberosProviders(object):

    """Implementation of the 'KerberosProviders' model.

    Response of Kerberos Providers.

    Attributes:
        kerberos_providers (list of KerberosProvider): A list of registered
            Kerberos Providers.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "kerberos_providers":'kerberosProviders'
    }

    def __init__(self,
                 kerberos_providers=None):
        """Constructor for the KerberosProviders class"""

        # Initialize members of the class
        self.kerberos_providers = kerberos_providers


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
        kerberos_providers = None
        if dictionary.get("kerberosProviders") is not None:
            kerberos_providers = list()
            for structure in dictionary.get('kerberosProviders'):
                kerberos_providers.append(cohesity_management_sdk.models_v2.kerberos_provider.KerberosProvider.from_dictionary(structure))

        # Return an object of this model
        return cls(kerberos_providers)


