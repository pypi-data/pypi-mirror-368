# -*- coding: utf-8 -*-

class CdpStandbyStatusEnum(object):

    """Implementation of the 'CdpStandbyStatusEnum' enum.

    Specifies the current status of the standby object protected
            using continuous data protection policy.

    Attributes:
        INIT: TODO: type description here.
        VMCREATIONINPROGRESS: TODO: type description here.
        VMCREATED: TODO: type description here.
        LOGSTREAMINGINPROGRESS: TODO: type description here.
        REHYDRATIONREQUIRED: TODO: type description here.
        STEADY: TODO: type description here.
        DISABLED: TODO: type description here.
        RESTORECOMPLETE: TODO: type description here.

    """

    INIT = 'Init'

    VMCREATIONINPROGRESS = 'VmCreationInProgress'

    VMCREATED = 'VmCreated'

    LOGSTREAMINGINPROGRESS = 'LogStreamingInProgress'

    REHYDRATIONREQUIRED = 'RehydrationRequired'

    STEADY = 'Steady'

    DISABLED = 'Disabled'

    RESTORECOMPLETE = 'RestoreComplete'