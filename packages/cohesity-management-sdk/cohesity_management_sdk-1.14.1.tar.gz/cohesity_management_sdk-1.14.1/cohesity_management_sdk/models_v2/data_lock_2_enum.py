# -*- coding: utf-8 -*-

class DataLock2Enum(object):

    """Implementation of the 'DataLock2' enum.

    Specifies WORM retention type for the snapshots. When a WORM retention
    type is specified, the snapshots of the Protection Groups using this
    policy will be kept until the maximum of the snapshot retention time.
    During that time, the snapshots cannot be deleted. 
    'Compliance' implies WORM retention is set for compliance reason. 
    'Administrative' implies WORM retention is set for administrative
    purposes.

    Attributes:
        COMPLIANCE: TODO: type description here.
        ADMINISTRATIVE: TODO: type description here.

    """

    COMPLIANCE = 'Compliance'

    ADMINISTRATIVE = 'Administrative'

