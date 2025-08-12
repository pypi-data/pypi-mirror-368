# -*- coding: utf-8 -*-


class SMBPermission(object):

    """Implementation of the 'SMB Permission.' model.

    Specifies information about a single SMB permission.

    Attributes:
        mtype (Type2Enum): Specifies the type of permission. 'Allow' indicates
            access is allowed. 'Deny' indicates access is denied.
            'SpecialType' indicates a type defined in the Access Control Entry
            (ACE) does not map to 'Allow' or 'Deny'.
        mode (ModeEnum): Specifies how the permission should be applied to
            folders and/or files. 'FolderSubFoldersAndFiles' indicates that
            permissions are applied to a Folder and it's sub folders and
            files. 'FolderAndSubFolders' indicates that permissions are
            applied to a Folder and it's sub folders. 'FolderAndSubFiles'
            indicates that permissions are applied to a Folder and it's sub
            files. 'FolderOnly' indicates that permsission are applied to
            folder only. 'SubFoldersAndFilesOnly' indicates that permissions
            are applied to sub folders and files only. 'SubFoldersOnly'
            indicates that permissiona are applied to sub folders only.
            'FilesOnly' indicates that permissions are applied to files only.
        access (AccessEnum): Specifies the read/write access to the SMB share.
            'ReadyOnly' indicates read only access to the SMB share.
            'ReadWrite' indicates read and write access to the SMB share.
            'FullControl' indicates full administrative control of the SMB
            share. 'SpecialAccess' indicates custom permissions to the SMB
            share using  access masks structures. 'SuperUser' indicates root
            permissions ignoring all SMB ACLs.
        sid (string): Specifies the security identifier (SID) of the
            principal.
        special_type (int): Specifies a custom type. When the type from the
            Access Control Entry (ACE) cannot be mapped to one of the enums in
            'type', this field is populated with the custom type derived from
            the ACE and 'type' is set to kSpecialType. This is a placeholder
            for storing an unmapped type and should not be set when creating
            and editing a View.
        special_access_mask (int): Specifies custom access permissions. When
            the access mask from the Access Control Entry (ACE) cannot be
            mapped to one of the enums in 'access', this field is populated
            with the custom mask derived from the ACE and 'access' is set to
            kSpecialAccess. This is a placeholder for storing an unmapped
            access permission and should not be set when creating and editing
            a View.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mtype":'type',
        "mode":'mode',
        "access":'access',
        "sid":'sid',
        "special_type":'specialType',
        "special_access_mask":'specialAccessMask'
    }

    def __init__(self,
                 mtype=None,
                 mode=None,
                 access=None,
                 sid=None,
                 special_type=None,
                 special_access_mask=None):
        """Constructor for the SMBPermission class"""

        # Initialize members of the class
        self.mtype = mtype
        self.mode = mode
        self.access = access
        self.sid = sid
        self.special_type = special_type
        self.special_access_mask = special_access_mask


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
        mtype = dictionary.get('type')
        mode = dictionary.get('mode')
        access = dictionary.get('access')
        sid = dictionary.get('sid')
        special_type = dictionary.get('specialType')
        special_access_mask = dictionary.get('specialAccessMask')

        # Return an object of this model
        return cls(mtype,
                   mode,
                   access,
                   sid,
                   special_type,
                   special_access_mask)


