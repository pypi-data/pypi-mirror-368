# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.subnet
import cohesity_management_sdk.models_v2.alias_smb_config

class Share(object):

    """Implementation of the 'Share' model.

    Specifies the details of a Share.

    Attributes:
        client_subnet_whitelist (list of Subnet): List of external client subnet IPs that are allowed to access
          the share.
        enable_filer_audit_logging (bool): This field is currently deprecated. Specifies if Filer Audit
          Logging is enabled for this Share.
        file_audit_logging_state (FileAuditLoggingStateEnum): Specifies the state of File Audit logging for this Share. Inherited:
          Audit log setting is inherited from the  View. Enabled: Audit log is enabled
          for this Share. Disabled: Audit log is disabled for this Share.
        name (string): Specifies the Share name.
        nfs_mount_paths (list of string): Specifies the path for mounting this Share as an NFS share.
            If Kerberos Provider has multiple hostaliases, each host alias has its
            own path.
        s_3_access_path (string): Specifies the path to access this Share as an S3 share.
        smb_config (AliasSmbConfig): SMB config for the alias (share).
        smb_mount_paths (list of string): Specifies the possible paths that can be used to mount this
            Share as a SMB share. If Active Directory has multiple account names,
            each machine account has its own path.
        tenant_id (string): Specifies the tenant id who has access to this Share.
        view_id (long|int): Specifies the id of the View.
        view_name (string): Specifies the View name of this Share.
        view_path (string): Specifies the View path of this Share.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "client_subnet_whitelist":'clientSubnetWhitelist',
        "enable_filer_audit_logging":'enableFilerAuditLogging',
        "file_audit_logging_state":'fileAuditLoggingState',
        "name":'name',
        "nfs_mount_paths":'nfsMountPaths',
        "s_3_access_path":'s3AccessPath',
        "smb_config":'smbConfig',
        "smb_mount_paths":'smbMountPaths',
        "tenant_id":'tenantId',
        "view_id":'viewId',
        "view_name":'viewName',
        "view_path":'viewPath'
    }

    def __init__(self,
                 client_subnet_whitelist=None,
                 enable_filer_audit_logging=None,
                 file_audit_logging_state=None,
                 name=None,
                 nfs_mount_paths=None,
                 s_3_access_path=None,
                 smb_config=None,
                 smb_mount_paths=None,
                 tenant_id=None,
                 view_id=None,
                 view_name=None,
                 view_path=None):
        """Constructor for the Share class"""

        # Initialize members of the class
        self.client_subnet_whitelist = client_subnet_whitelist
        self.enable_filer_audit_logging = enable_filer_audit_logging
        self.file_audit_logging_state = file_audit_logging_state
        self.name = name
        self.nfs_mount_paths = nfs_mount_paths
        self.s_3_access_path = s_3_access_path
        self.smb_config = smb_config
        self.smb_mount_paths = smb_mount_paths
        self.tenant_id = tenant_id
        self.view_id = view_id
        self.view_name = view_name
        self.view_path = view_path


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
        client_subnet_whitelist = None
        if dictionary.get("clientSubnetWhitelist") is not None:
            client_subnet_whitelist = list()
            for structure in dictionary.get('clientSubnetWhitelist'):
                client_subnet_whitelist.append(cohesity_management_sdk.models_v2.subnet.Subnet.from_dictionary(structure))
        enable_filer_audit_logging = dictionary.get('enableFilerAuditLogging')
        file_audit_logging_state = dictionary.get('fileAuditLoggingState')
        name = dictionary.get('name')
        nfs_mount_paths = dictionary.get('nfsMountPaths')
        s_3_access_path = dictionary.get('s3AccessPath')
        smb_config = cohesity_management_sdk.models_v2.alias_smb_config.AliasSmbConfig.from_dictionary(dictionary.get('smbConfig')) if dictionary.get('smbConfig') else None
        smb_mount_paths = dictionary.get('smbMountPaths')
        tenant_id = dictionary.get('tenantId')
        view_id = dictionary.get('viewId')
        view_name = dictionary.get('viewName')
        view_path = dictionary.get('viewPath')


        # Return an object of this model
        return cls(client_subnet_whitelist,
                   enable_filer_audit_logging,
                   file_audit_logging_state,
                   name,
                   nfs_mount_paths,
                   s_3_access_path,
                   smb_config,
                   smb_mount_paths,
                   tenant_id,
                   view_id,
                   view_name,
                   view_path)