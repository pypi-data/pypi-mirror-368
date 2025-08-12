# -*- coding: utf-8 -*-

class ProtectionTypeEnum(object):

    """Implementation of the 'ProtectionType' enum.

    Specifies the AWS Protection Group type.

    Attributes:
        KAGENT: TODO: type description here.
        KNATIVE: TODO: type description here.
        KSNAPSHOTMANAGER: TODO: type description here.
        KRDSSNAPSHOTMANAGER: TODO: type description here.
        KAURORASNAPSHOTMANAGER: TODO: type description here.
        KAWSS3: TODO: type description here.
        KAWSRDSPOSTGRESBACKUP: TODO: type description here.

    """

    KAGENT = 'kAgent'

    KNATIVE = 'kNative'

    KSNAPSHOTMANAGER = 'kSnapshotManager'

    KRDSSNAPSHOTMANAGER = 'kRDSSnapshotManager'

    KAURORASNAPSHOTMANAGER = 'kAuroraSnapshotManager'

    KAWSS3 = 'kAwsS3'

    KAWSRDSPOSTGRESBACKUP = 'kAwsRDSPostgresBackup'