# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.certificate_object_with_metadata

class Office365AzureApplicationCredentials(object):

    """Implementation of the 'Office365AzureApplicationCredentials.' model.

    Specifies credentials for office365 azure registered applications,
      used for office 365 source registration.

    Attributes:
        client_certificate (CertificateObjectWithMetadata): Specifies Aag Backup
            Preference Type.
        client_id (string): Specifies the application ID that the registration portal (apps.dev.microsoft.com)
          assigned.
        client_secret (string): Specifies the application secret that was created in app registration
          portal.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "client_certificate":'clientCertificate',
        "client_id":'clientId',
        "client_secret":'clientSecret'
    }

    def __init__(self,
                 client_certificate=None,
                 client_id=None,
                 client_secret=None
                 ):
        """Constructor for the Office365AzureApplicationCredentials class"""

        # Initialize members of the class
        self.client_certificate = client_certificate
        self.client_id = client_id
        self.client_secret = client_secret


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
        client_certificate = cohesity_management_sdk.models_v2.certificate_object_with_metadata.CertificateObjectWithMetadata.from_dictionary(dictionary.get('clientCertificate')) if dictionary.get('clientCertificate') else None
        client_id = dictionary.get('clientId')
        client_secret =dictionary.get('clientSecret')

        # Return an object of this model
        return cls(client_certificate,
                   client_id,
                   client_secret)