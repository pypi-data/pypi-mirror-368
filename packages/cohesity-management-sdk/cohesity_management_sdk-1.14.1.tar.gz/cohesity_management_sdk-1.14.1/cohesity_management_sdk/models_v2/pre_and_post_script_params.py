# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_pre_backup_script_params
import cohesity_management_sdk.models_v2.common_pre_post_script_params

class PreAndPostScriptParams(object):

    """Implementation of the 'Pre and Post Script Params.' model.

    Specifies the params for pre and post scripts.

    Attributes:
        pre_script (CommonPreBackupScriptParams): Specifies the common params
            for PreBackup scripts.
        post_script (CommonPrePostScriptParams): Specifies the common params
            for PostBackup scripts.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "pre_script":'preScript',
        "post_script":'postScript'
    }

    def __init__(self,
                 pre_script=None,
                 post_script=None):
        """Constructor for the PreAndPostScriptParams class"""

        # Initialize members of the class
        self.pre_script = pre_script
        self.post_script = post_script


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
        pre_script = cohesity_management_sdk.models_v2.common_pre_backup_script_params.CommonPreBackupScriptParams.from_dictionary(dictionary.get('preScript')) if dictionary.get('preScript') else None
        post_script = cohesity_management_sdk.models_v2.common_pre_post_script_params.CommonPrePostScriptParams.from_dictionary(dictionary.get('postScript')) if dictionary.get('postScript') else None

        # Return an object of this model
        return cls(pre_script,
                   post_script)


