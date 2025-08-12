# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.credentials_to_connect_to_sql

class EnableSQLProtectionParameters(object):

    """Implementation of the 'Enable SQL protection parameters.' model.

    Specifies the parameters for enabling SQL protection.

    Attributes:
        use_installed_agent (bool): Specifies if agent is already installed.
        credentials (CredentialsToConnectToSQL): Specifies the credentials to
            connect to SQL.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "use_installed_agent":'useInstalledAgent',
        "credentials":'credentials'
    }

    def __init__(self,
                 use_installed_agent=None,
                 credentials=None):
        """Constructor for the EnableSQLProtectionParameters class"""

        # Initialize members of the class
        self.use_installed_agent = use_installed_agent
        self.credentials = credentials


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
        use_installed_agent = dictionary.get('useInstalledAgent')
        credentials = cohesity_management_sdk.models_v2.credentials_to_connect_to_sql.CredentialsToConnectToSQL.from_dictionary(dictionary.get('credentials')) if dictionary.get('credentials') else None

        # Return an object of this model
        return cls(use_installed_agent,
                   credentials)


