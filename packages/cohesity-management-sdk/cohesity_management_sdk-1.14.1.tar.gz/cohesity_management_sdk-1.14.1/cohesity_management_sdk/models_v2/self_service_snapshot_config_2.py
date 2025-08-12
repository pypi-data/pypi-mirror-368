# -*- coding: utf-8 -*-


class SelfServiceSnapshotConfig2(object):

    """Implementation of the 'SelfServiceSnapshotConfig2' model.

    Specifies self service config of this view.

    Attributes:
        enabled (bool): Specifies if self service snapshot feature is enabled.
            If this is set to true, the feature will also be enabled for NFS
            protocol. This field is deprecated.
        previous_versions_enabled (bool): Specifies if previouse versions
            feature is enabled with SMB protocol.
        nfs_access_enabled (bool): Specifies if self service snapshot feature
            is enabled for NFS protocol.
        smb_access_enabled (bool): Specifies if self service snapshot feature
            is enabled for SMB protocol.
        snapshot_directory_name (string): Specifies the directory name for the
            snapshots.
        alternate_snapshot_directory_name (string): Specifies the alternate
            directory name for the snapshots. If it is not set, this feature
            for SMB protocol will not work.
        allow_access_sids (list of string): Specifies a list of sids who has
            access to the snapshots.
        deny_access_sids (list of string): Specifies a list of sids who does
            not have access to the snapshots. This field overrides
            'allowAccessSids'.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enabled":'enabled',
        "previous_versions_enabled":'previousVersionsEnabled',
        "nfs_access_enabled":'nfsAccessEnabled',
        "smb_access_enabled":'smbAccessEnabled',
        "snapshot_directory_name":'snapshotDirectoryName',
        "alternate_snapshot_directory_name":'alternateSnapshotDirectoryName',
        "allow_access_sids":'allowAccessSids',
        "deny_access_sids":'denyAccessSids'
    }

    def __init__(self,
                 enabled=None,
                 previous_versions_enabled=None,
                 nfs_access_enabled=None,
                 smb_access_enabled=None,
                 snapshot_directory_name=None,
                 alternate_snapshot_directory_name=None,
                 allow_access_sids=None,
                 deny_access_sids=None):
        """Constructor for the SelfServiceSnapshotConfig2 class"""

        # Initialize members of the class
        self.enabled = enabled
        self.previous_versions_enabled = previous_versions_enabled
        self.nfs_access_enabled = nfs_access_enabled
        self.smb_access_enabled = smb_access_enabled
        self.snapshot_directory_name = snapshot_directory_name
        self.alternate_snapshot_directory_name = alternate_snapshot_directory_name
        self.allow_access_sids = allow_access_sids
        self.deny_access_sids = deny_access_sids


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
        enabled = dictionary.get('enabled')
        previous_versions_enabled = dictionary.get('previousVersionsEnabled')
        nfs_access_enabled = dictionary.get('nfsAccessEnabled')
        smb_access_enabled = dictionary.get('smbAccessEnabled')
        snapshot_directory_name = dictionary.get('snapshotDirectoryName')
        alternate_snapshot_directory_name = dictionary.get('alternateSnapshotDirectoryName')
        allow_access_sids = dictionary.get('allowAccessSids')
        deny_access_sids = dictionary.get('denyAccessSids')

        # Return an object of this model
        return cls(enabled,
                   previous_versions_enabled,
                   nfs_access_enabled,
                   smb_access_enabled,
                   snapshot_directory_name,
                   alternate_snapshot_directory_name,
                   allow_access_sids,
                   deny_access_sids)


