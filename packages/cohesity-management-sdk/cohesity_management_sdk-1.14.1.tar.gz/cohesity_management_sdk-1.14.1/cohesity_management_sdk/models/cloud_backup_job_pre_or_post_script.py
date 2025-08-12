# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.script_path_and_params

class CloudBackupJobPreOrPostScript(object):

    """Implementation of the 'CloudBackupJobPreOrPostScript' model.

    A message to encapsulate the pre-backup and post-backup and post-snapshot
    scripts for Cloud Adapter (AWS, Azure, GCP) based backups.

    Attributes:
        linux_script (ScriptPathAndParams): Specific for machines that are
            running the bash shell.
        windows_script (ScriptPathAndParams): Specific for machines that are
            running the powershell.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "linux_script": 'linuxScript',
        "windows_script": 'windowsScript'
    }

    def __init__(self,
                 linux_script=None,
                 windows_script=None):
        """Constructor for the CloudBackupJobPreOrPostScript class"""

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
        linux_script = cohesity_management_sdk.models.script_path_and_params.ScriptPathAndParams.from_dictionary(dictionary.get('linuxScript')) if dictionary.get('linuxScript') else None
        windows_script = cohesity_management_sdk.models.script_path_and_params.ScriptPathAndParams.from_dictionary(dictionary.get('windowsScript')) if dictionary.get('windowsScript') else None

        # Return an object of this model
        return cls(linux_script,
                   windows_script)


