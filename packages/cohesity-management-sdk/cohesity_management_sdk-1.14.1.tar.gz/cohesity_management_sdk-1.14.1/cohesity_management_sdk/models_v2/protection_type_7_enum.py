# -*- coding: utf-8 -*-

class ProtectionType7Enum(object):

    """Implementation of the 'ProtectionType7' enum.

    Specifies the Protection Group type. If not specified, then backup method
    is auto determined. Specifying RCT, will forcibly use RCT backup for all
    VMs in this Protection Group. Available only for VMs with hardware version
    8.0 and above, but is more efficient. Specifying VSS, will forcibly use
    VSS backup for all VMs in this Protection Group. Available for VMs with
    hardware version 5.0 and above but is slower than RCT backup.

    Attributes:
        KAUTO: TODO: type description here.
        KRCT: TODO: type description here.
        KVSS: TODO: type description here.

    """

    KAUTO = 'kAuto'

    KRCT = 'kRCT'

    KVSS = 'kVSS'

