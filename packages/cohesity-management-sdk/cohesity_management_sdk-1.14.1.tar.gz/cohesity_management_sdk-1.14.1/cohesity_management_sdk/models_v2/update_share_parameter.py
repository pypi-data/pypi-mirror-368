# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.alias_smb_config

class UpdateShareParameter(object):

    """Implementation of the 'UpdateShareParameter' model.

    Specifies the parameter to update a Share.

    Attributes:
        client_subnet_whitelist (list of Subnet): List of external client subnet IPs that are allowed to access
          the share.
        enable_filer_audit_logging (bool): This field is currently deprecated. Specifies if Filer Audit
          Logging is enabled for this Share.
        file_audit_logging_state (FileAuditLoggingStateEnum): Specifies the state of File Audit logging for this Share. Inherited:
          Audit log setting is inherited from the  View. Enabled: Audit log is enabled
          for this Share. Disabled: Audit log is disabled for this Share.
        smb_config (AliasSmbConfig): SMB config for the alias (share).

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "client_subnet_whitelist":'clientSubnetWhitelist',
        "enable_filer_audit_logging":'enableFilerAuditLogging',
        "file_audit_logging_state":'fileAuditLoggingState',
        "smb_config":'smbConfig'
    }

    def __init__(self,
                 client_subnet_whitelist=None,
                 enable_filer_audit_logging=None,
                 file_audit_logging_state=None,
                 smb_config=None):
        """Constructor for the UpdateShareParameter class"""

        # Initialize members of the class
        self.client_subnet_whitelist = client_subnet_whitelist
        self.enable_filer_audit_logging = enable_filer_audit_logging
        self.file_audit_logging_state = file_audit_logging_state
        self.smb_config = smb_config


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
        client_subnet_whitelist = dictionary.get('clientSubnetWhitelist')
        enable_filer_audit_logging = dictionary.get('enableFilerAuditLogging')
        file_audit_logging_state = dictionary.get('fileAuditLoggingState')
        smb_config = cohesity_management_sdk.models_v2.alias_smb_config.AliasSmbConfig.from_dictionary(dictionary.get('smbConfig')) if dictionary.get('smbConfig') else None


        # Return an object of this model
        return cls(client_subnet_whitelist,
                   enable_filer_audit_logging,
                   file_audit_logging_state,
                   smb_config
                   )