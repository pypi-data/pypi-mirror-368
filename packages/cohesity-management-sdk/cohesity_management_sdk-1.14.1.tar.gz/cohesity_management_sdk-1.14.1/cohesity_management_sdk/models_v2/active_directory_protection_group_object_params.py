# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.active_directory_app_parameters

class ActiveDirectoryProtectionGroupObjectParams(object):

    """Implementation of the 'Active Directory Protection Group Object Params.' model.

    Specifies the object identifier to for the active directory protection
    group.

    Attributes:
        app_params (list of ActiveDirectoryAppParams): Specifies the specific parameters required for active directory
          app configuration.
        enable_system_backup (bool): Specifies whether to take bmr backup. If this is not specified,
          the bmr backup won't be enabled.
        source_id (long|int): Specifies the id of the registered active
            directory source.
        source_name (string): Specifies the name of the registered active
            directory source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "app_params":'appParams',
        "enable_system_backup":'enableSystemBackup',
        "source_id":'sourceId',
        "source_name":'sourceName',
    }

    def __init__(self,
                 app_params=None,
                 enable_system_backup=None,
                 source_id=None,
                 source_name=None,):
        """Constructor for the ActiveDirectoryProtectionGroupObjectParams class"""

        # Initialize members of the class
        self.app_params = app_params
        self.enable_system_backup = enable_system_backup
        self.source_id = source_id
        self.source_name = source_name


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
        app_params = None
        if dictionary.get("appParams") is not None:
            app_params = list()
            for structure in dictionary.get('appParams'):
                app_params.append(cohesity_management_sdk.models_v2.active_directory_app_parameters.ActiveDirectoryAppParameters.from_dictionary(structure))
        enable_system_backup = dictionary.get('enableSystemBackup')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')

        # Return an object of this model
        return cls(app_params,
                   enable_system_backup,
                   source_id,
                   source_name)