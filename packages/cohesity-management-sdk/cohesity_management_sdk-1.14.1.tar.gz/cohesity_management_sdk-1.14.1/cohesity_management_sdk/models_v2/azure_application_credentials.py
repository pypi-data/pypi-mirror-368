# -*- coding: utf-8 -*-


class AzureApplicationCredentials(object):

    """Implementation of the 'AzureApplicationCredentials.' model.

    Specifies the credentials of an application from Azure active directory.

    Attributes:
        application_id (string): Specifies the application id of an Azure active
           directory application.
        application_object_id (string): Specifies the application object id of an Azure active directory
          application.
        encrypted_application_key (string): Specifies the encrypted application key of an Azure active directory
          application.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "application_id":'applicationId',
        "application_object_id":'applicationObjectId',
        "encrypted_application_key":'encryptedApplicationKey'
    }

    def __init__(self,
                 application_id=None,
                 application_object_id=None,
                 encrypted_application_key=None
                 ):
        """Constructor for the AzureApplicationCredentials class"""

        # Initialize members of the class
        self.application_id = application_id
        self.application_object_id = application_object_id
        self.encrypted_application_key = encrypted_application_key


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
        application_id = dictionary.get('applicationId')
        application_object_id = dictionary.get('applicationObjectId')
        encrypted_application_key = dictionary.get('encryptedApplicationKey')

        # Return an object of this model
        return cls(application_id,
                   application_object_id,
                   encrypted_application_key)