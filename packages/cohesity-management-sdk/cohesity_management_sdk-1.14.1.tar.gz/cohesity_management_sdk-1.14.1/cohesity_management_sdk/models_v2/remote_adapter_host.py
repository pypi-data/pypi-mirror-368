# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_pre_backup_script_params

class RemoteAdapterHost(object):

    """Implementation of the 'RemoteAdapterHost' model.

    Specifies params of the remote host.

    Attributes:
        hostname (string): Specifies the Hostname or IP address of the host
            where the pre and post script will be run.
        username (string): Specifies the username for the host.
        host_type (HostTypeEnum): Specifies the Operating system type of the
            host.
        incremental_backup_script (CommonPreBackupScriptParams): Specifies the
            common params for PreBackup scripts.
        full_backup_script (CommonPreBackupScriptParams): Specifies the common
            params for PreBackup scripts.
        log_backup_script (CommonPreBackupScriptParams): Specifies the common
            params for PreBackup scripts.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "hostname":'hostname',
        "username":'username',
        "host_type":'hostType',
        "incremental_backup_script":'incrementalBackupScript',
        "full_backup_script":'fullBackupScript',
        "log_backup_script":'logBackupScript'
    }

    def __init__(self,
                 hostname=None,
                 username=None,
                 host_type=None,
                 incremental_backup_script=None,
                 full_backup_script=None,
                 log_backup_script=None):
        """Constructor for the RemoteAdapterHost class"""

        # Initialize members of the class
        self.hostname = hostname
        self.username = username
        self.host_type = host_type
        self.incremental_backup_script = incremental_backup_script
        self.full_backup_script = full_backup_script
        self.log_backup_script = log_backup_script


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
        hostname = dictionary.get('hostname')
        username = dictionary.get('username')
        host_type = dictionary.get('hostType')
        incremental_backup_script = cohesity_management_sdk.models_v2.common_pre_backup_script_params.CommonPreBackupScriptParams.from_dictionary(dictionary.get('incrementalBackupScript')) if dictionary.get('incrementalBackupScript') else None
        full_backup_script = cohesity_management_sdk.models_v2.common_pre_backup_script_params.CommonPreBackupScriptParams.from_dictionary(dictionary.get('fullBackupScript')) if dictionary.get('fullBackupScript') else None
        log_backup_script = cohesity_management_sdk.models_v2.common_pre_backup_script_params.CommonPreBackupScriptParams.from_dictionary(dictionary.get('logBackupScript')) if dictionary.get('logBackupScript') else None

        # Return an object of this model
        return cls(hostname,
                   username,
                   host_type,
                   incremental_backup_script,
                   full_backup_script,
                   log_backup_script)


