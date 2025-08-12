# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.enable_sql_protection_parameters

class VmwareAppProtectionParameters(object):

    """Implementation of the 'VMware app protection parameters.' model.

    Specifies the parameters to enable app protection on VMware.

    Attributes:
        app_type (AppTypeEnum): Specifies the app from which protection must
            be enabled.
        enable_sql_protection_params (EnableSQLProtectionParameters):
            Specifies the parameters for enabling SQL protection.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "app_type":'appType',
        "enable_sql_protection_params":'enableSqlProtectionParams'
    }

    def __init__(self,
                 app_type=None,
                 enable_sql_protection_params=None):
        """Constructor for the VmwareAppProtectionParameters class"""

        # Initialize members of the class
        self.app_type = app_type
        self.enable_sql_protection_params = enable_sql_protection_params


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
        app_type = dictionary.get('appType')
        enable_sql_protection_params = cohesity_management_sdk.models_v2.enable_sql_protection_parameters.EnableSQLProtectionParameters.from_dictionary(dictionary.get('enableSqlProtectionParams')) if dictionary.get('enableSqlProtectionParams') else None

        # Return an object of this model
        return cls(app_type,
                   enable_sql_protection_params)


