# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_pre_backup_script_params
import cohesity_management_sdk.models_v2.common_pre_post_script_params

class OracleCloneTask(object):

    """Implementation of the 'OracleCloneTask' model.

    Specifies the information about an Oracle clone task.

    Attributes:
        pre_script (CommonPreBackupScriptParams): Specifies the common params
            for PreBackup scripts.
        post_script (CommonPrePostScriptParams): Specifies the common params
            for PostBackup scripts.
        db_name (string): Specifies the name of the cloned database.
        home_folder (string): Specifies the home folder for the cloned
            database.
        base_folder (string): Specifies the base folder of Oracle installation
            on the target host.
        sga (string): Specifies the System Global Area (SGA) for the clone
            database.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "pre_script":'preScript',
        "post_script":'postScript',
        "db_name":'dbName',
        "home_folder":'homeFolder',
        "base_folder":'baseFolder',
        "sga":'sga'
    }

    def __init__(self,
                 pre_script=None,
                 post_script=None,
                 db_name=None,
                 home_folder=None,
                 base_folder=None,
                 sga=None):
        """Constructor for the OracleCloneTask class"""

        # Initialize members of the class
        self.pre_script = pre_script
        self.post_script = post_script
        self.db_name = db_name
        self.home_folder = home_folder
        self.base_folder = base_folder
        self.sga = sga


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
        db_name = dictionary.get('dbName')
        home_folder = dictionary.get('homeFolder')
        base_folder = dictionary.get('baseFolder')
        sga = dictionary.get('sga')

        # Return an object of this model
        return cls(pre_script,
                   post_script,
                   db_name,
                   home_folder,
                   base_folder,
                   sga)


