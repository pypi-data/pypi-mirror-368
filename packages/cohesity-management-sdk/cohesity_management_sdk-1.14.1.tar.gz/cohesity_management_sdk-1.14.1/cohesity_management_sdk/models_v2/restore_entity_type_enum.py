# -*- coding: utf-8 -*-

class RestoreEntityTypeEnum(object):

    """Implementation of the 'RestoreEntityType' enum.

    Specifies the restore type (restore everything or ACLs only)
          when restoring or downloading files or folders from a Physical file based
          or block based backup snapshot.

    Attributes:
        KREGULAR: TODO: type description here.
        KACLONLY: TODO: type description here.

    """

    KREGULAR = 'kRegular'

    KACLONLY = 'kACLOnly'