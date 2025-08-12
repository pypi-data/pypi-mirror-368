# -*- coding: utf-8 -*-

class LockingProtocolEnum(object):

    """Implementation of the 'LockingProtocol' enum.

    Specifies the supported mechanisms to explicity lock a file from NFS/SMB
    interface. Supported locking protocols: SetReadOnly, SetAtime.
    'SetReadOnly' is compatible with Isilon/Netapp behaviour. This locks the
    file and the retention duration is determined in this order:
    1) atime, if set by user/application and within min and max retention
    duration.
    2) Min retention duration, if set.
    3) Otherwise, file is switched to expired data automatically.
    'SetAtime' is compatible with Data Domain behaviour.

    Attributes:
        SETREADONLY: TODO: type description here.
        SETATIME: TODO: type description here.

    """

    SETREADONLY = 'SetReadOnly'

    SETATIME = 'SetAtime'

