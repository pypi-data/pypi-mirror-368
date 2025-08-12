# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.alias_smb_config
import cohesity_management_sdk.models_v2.subnet

class ViewAliasInformation(object):

    """Implementation of the 'View Alias Information.' model.

    View Alias Info is returned as part of list views.

    Attributes:
        alias_name (string): Alias name.
        view_path (string): View path for the alias.
        enable_filer_audit_log (bool): This field is currently deprecated. Specifies whether to enable
          filer audit log on this view alias. This is only used if filer audit logging
          is enabled in cluster config.
        file_audit_logging_state (FileAuditLoggingStateEnum): Specifies the state of File Audit logging for this Share. Supported
          types: [Inherited, Enabled, Disabled]. Inherited: Audit log setting is inherited
          from the  View. Enabled: Audit log is enabled for this Share. Disabled:
          Audit log is disabled for this Share.
        smb_config (AliasSmbConfig): Message defining SMB config for IRIS. SMB
            config contains SMB encryption flags, SMB discoverable flag and
            Share level permissions.
        client_subnet_whitelist (list of Subnet): List of external client
            subnet IPs that are allowed to access the share.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "alias_name":'aliasName',
        "view_path":'viewPath',
        "enable_filer_audit_log": 'enableFilerAuditLog',
        "file_audit_logging_state": 'fileAuditLoggingState',
        "smb_config":'smbConfig',
        "client_subnet_whitelist":'clientSubnetWhitelist'
    }

    def __init__(self,
                 alias_name=None,
                 view_path=None,
                 enable_filer_audit_log=None,
                 file_audit_logging_state=None,
                 smb_config=None,
                 client_subnet_whitelist=None):
        """Constructor for the ViewAliasInformation class"""

        # Initialize members of the class
        self.alias_name = alias_name
        self.view_path = view_path
        self.enable_filer_audit_log = enable_filer_audit_log
        self.file_audit_logging_state = file_audit_logging_state
        self.smb_config = smb_config
        self.client_subnet_whitelist = client_subnet_whitelist


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
        alias_name = dictionary.get('aliasName')
        view_path = dictionary.get('viewPath')
        enable_filer_audit_log = dictionary.get('enableFilerAuditLog')
        file_audit_logging_state = dictionary.get('fileAuditLoggingState')
        smb_config = cohesity_management_sdk.models_v2.alias_smb_config.AliasSmbConfig.from_dictionary(dictionary.get('smbConfig')) if dictionary.get('smbConfig') else None
        client_subnet_whitelist = None
        if dictionary.get("clientSubnetWhitelist") is not None:
            client_subnet_whitelist = list()
            for structure in dictionary.get('clientSubnetWhitelist'):
                client_subnet_whitelist.append(cohesity_management_sdk.models_v2.subnet.Subnet.from_dictionary(structure))

        # Return an object of this model
        return cls(alias_name,
                   view_path,
                   enable_filer_audit_log,
                   file_audit_logging_state,
                   smb_config,
                   client_subnet_whitelist)