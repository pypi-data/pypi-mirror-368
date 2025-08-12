# -*- coding: utf-8 -*-

class AccessEnum(object):

    """Implementation of the 'Access' enum.

    Specifies the read/write access to the SMB share.
    'ReadyOnly' indicates read only access to the SMB share.
    'ReadWrite' indicates read and write access to the SMB share.
    'FullControl' indicates full administrative control of the SMB share.
    'SpecialAccess' indicates custom permissions to the SMB share using
     access masks structures.
    'SuperUser' indicates root permissions ignoring all SMB ACLs.

    Attributes:
        READONLY: TODO: type description here.
        READWRITE: TODO: type description here.
        MODIFY: TODO: type description here.
        FULLCONTROL: TODO: type description here.
        SPECIALACCESS: TODO: type description here.
        SUPERUSER: TODO: type description here.

    """

    READONLY = 'ReadOnly'

    READWRITE = 'ReadWrite'

    MODIFY = 'Modify'

    FULLCONTROL = 'FullControl'

    SPECIALACCESS = 'SpecialAccess'

    SUPERUSER = 'SuperUser'

