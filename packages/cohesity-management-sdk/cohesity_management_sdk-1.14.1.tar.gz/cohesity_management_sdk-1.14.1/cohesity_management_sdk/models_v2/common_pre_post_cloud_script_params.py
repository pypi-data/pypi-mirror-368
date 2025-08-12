# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_pre_backup_script_params

class CommonPrePostCloudScriptParams(object):

    """Implementation of the 'CommonPrePostCloudScriptParams' model.

    Specifies the common params for PrePost backup scripts specific for
      cloud-adapters. They have two different scripts for the two different shell
      types - windows and linux

    Attributes:
        linux_script (CommonPreBackupScriptParams): Specifies the script details that will be specific to linux machines
          and executed on bash.
        windows_script (CommonPreBackupScriptParams): Specifies the script details that will be specific to windows
          machines and executed on powershell.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "linux_script":'linuxScript',
        "windows_script":'windowsScript'
    }

    def __init__(self,
                 linux_script=None,
                 windows_script=None):
        """Constructor for the CommonPrePostCloudScriptParams class"""

        # Initialize members of the class
        self.linux_script = linux_script
        self.windows_script = windows_script


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
        linux_script = cohesity_management_sdk.models_v2.common_pre_backup_script_params.CommonPreBackupScriptParams.from_dictionary(dictionary.get('linuxScript')) if dictionary.get('linuxScript') else None
        windows_script = cohesity_management_sdk.models_v2.common_pre_backup_script_params.CommonPreBackupScriptParams.from_dictionary(dictionary.get('windowsScript')) if dictionary.get('windowsScript') else None

        # Return an object of this model
        return cls(linux_script,
                   windows_script)