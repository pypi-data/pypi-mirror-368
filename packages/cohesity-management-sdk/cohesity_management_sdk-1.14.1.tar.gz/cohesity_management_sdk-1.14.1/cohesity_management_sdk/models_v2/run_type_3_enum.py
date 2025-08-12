# -*- coding: utf-8 -*-

class RunType3Enum(object):

    """Implementation of the 'RunType3' enum.

    The backup run type to which this extended retention applies to. If this
    is not set, the extended retention will be applicable to all non-log
    backup types. Currently, the only value that can be set here is Full.
    'Regular' indicates a incremental (CBT) backup. Incremental backups
    utilizing CBT (if supported) are captured of the target protection
    objects. The first run of a Regular schedule captures all the blocks.
    'Full' indicates a full (no CBT) backup. A complete backup (all blocks) of
    the target protection objects are always captured and Change Block
    Tracking (CBT) is not utilized.
    'Log' indicates a Database Log backup. Capture the database transaction
    logs to allow rolling back to a specific point in time.
    'System' indicates a system backup. System backups are used to do bare
    metal recovery of the system to a specific point in time.

    Attributes:
        REGULAR: TODO: type description here.
        FULL: TODO: type description here.
        LOG: TODO: type description here.
        SYSTEM: TODO: type description here.

    """

    REGULAR = 'Regular'

    FULL = 'Full'

    LOG = 'Log'

    SYSTEM = 'System'

