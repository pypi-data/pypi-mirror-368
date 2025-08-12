# -*- coding: utf-8 -*-

class SecurityModeEnum(object):

    """Implementation of the 'SecurityMode' enum.

    Specifies the security mode used for this view.
    Currently we support the following modes: Native, Unified and NTFS style.
    'NativeMode' indicates a native security mode.
    'UnifiedMode' indicates a unified security mode.
    'NtfsMode' indicates a NTFS style security mode.

    Attributes:
        NATIVEMODE: TODO: type description here.
        UNIFIEDMODE: TODO: type description here.
        NTFSMODE: TODO: type description here.

    """

    NATIVEMODE = 'NativeMode'

    UNIFIEDMODE = 'UnifiedMode'

    NTFSMODE = 'NtfsMode'

