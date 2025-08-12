# -*- coding: utf-8 -*-

class UserDbBackupPreferenceTypeEnum(object):

    """Implementation of the 'UserDbBackupPreferenceType' enum.

    Specifies the preference type for backing up user databases on the host.

    Attributes:
        KBACKUPALLDATABASES: TODO: type description here.
        KBACKUPALLEXCEPTAAGDATABASES: TODO: type description here.
        KBACKUPONLYAAGDATABASES: TODO: type description here.

    """

    KBACKUPALLDATABASES = 'kBackupAllDatabases'

    KBACKUPALLEXCEPTAAGDATABASES = 'kBackupAllExceptAAGDatabases'

    KBACKUPONLYAAGDATABASES = 'kBackupOnlyAAGDatabases'

