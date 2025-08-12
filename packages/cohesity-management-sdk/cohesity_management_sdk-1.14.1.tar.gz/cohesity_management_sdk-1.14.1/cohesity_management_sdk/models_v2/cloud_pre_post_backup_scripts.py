# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_pre_post_cloud_script_params

class CloudPrePostBackupScripts(object):

    """Implementation of the 'CloudPrePostBackupScripts' model.

    Specifies params of a pre/post scripts to be executed before and
      after a backup run.

    Attributes:
        post_backup_script (CommonPrePostCloudScriptParams): Specifies the post backup script and its params.
        post_snapshot_script (CommonPrePostCloudScriptParams): Specifies the post snapshot script and its params.
        pre_backup_script (CommonPrePostCloudScriptParams): Specifies the pre script and its params.
    """

    # Create a mapping from Model property names to API property names
    _names = {"post_backup_script":'postBackupScript',
              "post_snapshot_script":'postSnapshotScript',
              "pre_backup_script":'preBackupScript'
    }

    def __init__(self,
                 post_backup_script=None,
                 post_snapshot_script=None,
                 pre_backup_script=None
                 ):
        """Constructor for the CloudPrePostBackupScripts class"""

        # Initialize members of the class
        self.post_backup_script = post_backup_script
        self.post_snapshot_script = post_snapshot_script
        self.pre_backup_script = pre_backup_script


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
        post_backup_script = cohesity_management_sdk.models_v2.common_pre_post_cloud_script_params.CommonPrePostCloudScriptParams.from_dictionary(dictionary.get('postBackupScript')) if dictionary.get('postBackupScript') else None
        post_snapshot_script = cohesity_management_sdk.models_v2.common_pre_post_cloud_script_params.CommonPrePostCloudScriptParams.from_dictionary(dictionary.get('postSnapshotScript')) if dictionary.get('postSnapshotScript') else None
        pre_backup_script = cohesity_management_sdk.models_v2.common_pre_post_cloud_script_params.CommonPrePostCloudScriptParams.from_dictionary(dictionary.get('preBackupScript')) if dictionary.get('preBackupScript') else None


        # Return an object of this model
        return cls(post_backup_script,
                   post_snapshot_script,
                   pre_backup_script)