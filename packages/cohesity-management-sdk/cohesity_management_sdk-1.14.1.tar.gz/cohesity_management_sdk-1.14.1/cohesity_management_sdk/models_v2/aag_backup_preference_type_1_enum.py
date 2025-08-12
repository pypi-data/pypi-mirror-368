# -*- coding: utf-8 -*-

class AagBackupPreferenceType1Enum(object):

    """Implementation of the 'AagBackupPreferenceType1' enum.

    Specifies the preference type for backing up databases that are part of an
    AAG. If not specified, then default preferences of the AAG server are
    applied. This field wont be applicable if user DB preference is set to
    skip AAG databases.

    Attributes:
        KPRIMARYREPLICAONLY: TODO: type description here.
        KSECONDARYREPLICAONLY: TODO: type description here.
        KPREFERSECONDARYREPLICA: TODO: type description here.
        KANYREPLICA: TODO: type description here.

    """

    KPRIMARYREPLICAONLY = 'kPrimaryReplicaOnly'

    KSECONDARYREPLICAONLY = 'kSecondaryReplicaOnly'

    KPREFERSECONDARYREPLICA = 'kPreferSecondaryReplica'

    KANYREPLICA = 'kAnyReplica'

