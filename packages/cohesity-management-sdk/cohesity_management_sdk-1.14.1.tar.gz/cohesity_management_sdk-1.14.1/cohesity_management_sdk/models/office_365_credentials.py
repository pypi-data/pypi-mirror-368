# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


import cohesity_management_sdk.models.certificate_object

class Office365Credentials(object):

    """Implementation of the 'Office365Credentials' model.

    Specifies the credentials to authenticate with Office365 account.

    Attributes:
        client_certificate (CertificateObject): Specifies the certificate attached to application.
        client_id (string): Specifies the application ID that the registration
            portal (apps.dev.microsoft.com) assigned.
        client_secret (string): Specifies the application secret that was
            created in app registration portal.
        grant_type (string): Specifies the application grant type. eg: For
            client credentials flow, set this to "client_credentials"; For
            refreshing access-token, set this to "refresh_token".
        scope (string): Specifies a space separated list of scopes/permissions
            for the user. eg: Incase of MS Graph APIs for Office365, scope is
            set to default: https://graph.microsoft.com/.default
        use_o_auth_for_exchange_online (bool): This field is deprecated from
            here and placed in RegisteredSourceInfo and
            ProtectionSourceParameters. deprecated: true

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "client_certificate":'clientCertificate',
        "client_id":'clientId',
        "client_secret":'clientSecret',
        "grant_type":'grantType',
        "scope":'scope',
        "use_o_auth_for_exchange_online":'useOAuthForExchangeOnline'
    }

    def __init__(self,
                 client_certificate=None,
                 client_id=None,
                 client_secret=None,
                 grant_type=None,
                 scope=None,
                 use_o_auth_for_exchange_online=None):
        """Constructor for the Office365Credentials class"""

        # Initialize members of the class
        self.client_certificate = client_certificate
        self.client_id = client_id
        self.client_secret = client_secret
        self.grant_type = grant_type
        self.scope = scope
        self.use_o_auth_for_exchange_online = use_o_auth_for_exchange_online


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
        client_certificate = cohesity_management_sdk.models.certificate_object.CertificateObject.from_dictionary(dictionary.get('clientCertificate')) if dictionary.get('clientCertificate') else None
        client_id = dictionary.get('clientId')
        client_secret = dictionary.get('clientSecret')
        grant_type = dictionary.get('grantType')
        scope = dictionary.get('scope')
        use_o_auth_for_exchange_online = dictionary.get('useOAuthForExchangeOnline')

        # Return an object of this model
        return cls(client_certificate,
                   client_id,
                   client_secret,
                   grant_type,
                   scope,
                   use_o_auth_for_exchange_online)