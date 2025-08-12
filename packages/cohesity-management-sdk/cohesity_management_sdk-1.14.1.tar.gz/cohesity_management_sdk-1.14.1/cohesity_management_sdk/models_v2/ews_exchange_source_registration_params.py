# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.credentials

class EwsExchangeSourceRegistrationParams(object):

    """Implementation of the 'EwsExchangeSourceRegistrationParams' model.

    Specifies the parameters to register an EWS Exchange source.

    Attributes:
        auth_method (AuthMethodEnum): Specifies the authentication method.
        ews_endpoint (string): Specifies the EWS endpoint of the Exchange server.
        service_account_credentials_list (list of Credentials): Specifies a list of service account credentials to be used to
          access the Exchange server.
        use_proxy (bool): Specifies whether to use the cluster proxy settings.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "auth_method":'authMethod',
        "ews_endpoint":'ewsEndpoint',
        "service_account_credentials_list":'serviceAccountCredentialsList',
        "use_proxy":'useProxy'
    }

    def __init__(self,
                 auth_method=None,
                 ews_endpoint=None,
                 service_account_credentials_list=None,
                 use_proxy=None):
        """Constructor for the EwsExchangeSourceRegistrationParams class"""

        # Initialize members of the class
        self.auth_method = auth_method
        self.ews_endpoint = ews_endpoint
        self.service_account_credentials_list = service_account_credentials_list
        self.use_proxy = use_proxy


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
        auth_method = dictionary.get('authMethod')
        ews_endpoint = dictionary.get('ewsEndpoint')
        service_account_credentials_list = None
        if dictionary.get('serviceAccountCredentialsList') is not None:
            service_account_credentials_list = list()
            for structure in dictionary.get('serviceAccountCredentialsList'):
                service_account_credentials_list.append(cohesity_management_sdk.models_v2.credentials.Credentials.from_dictionary(structure))
        use_proxy = dictionary.get('useProxy')

        # Return an object of this model
        return cls(auth_method,
                   ews_endpoint,
                   service_account_credentials_list,
                   use_proxy)