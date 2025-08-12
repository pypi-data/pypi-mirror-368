# -*- coding: utf-8 -*-

class CurrentOperationEnum(object):

    """Implementation of the 'CurrentOperation' enum.

    Specifies the current Cluster-level operation in progress.

    Attributes:
        KREMOVENODE: TODO: type description here.
        KUPGRADE: TODO: type description here.
        KNONE: TODO: type description here.
        KDESTROY: TODO: type description here.
        KCLEAN: TODO:type description here.
        KRESTARTSERVICES: TODO:type description here
        KRESTARTSYSTEMSERVICES: TODO: type description here.
        KUPGRADEBASEOS: TODO: type description here.
        KCLUSTEREXPAND: TODO: type description here.
        KRUNUPGRADECHECKS: TODO: type description here.
        KPATCHAPPLYORCHESTRATION: TODO: type description here.
        KRUNPATCHPRECHECKS: TODO: type description here.
        KPATCHREVERTORCHESTRATION: TODO: type description here.

    """

    KREMOVENODE = 'kRemoveNode'

    KUPGRADE = 'kUpgrade'

    KNONE = 'kNone'

    KDESTROY = 'kDestroy'

    KCLEAN = 'kClean'

    KRESTARTSERVICES = 'kRestartServices'

    KRESTARTSYSTEMSERVICES = 'kRestartSystemServices'

    KUPGRADEBASEOS = 'kUpgradeBaseos'

    KCLUSTEREXPAND = 'kClusterExpand'

    KRUNUPGRADECHECKS = 'kRunUpgradeChecks'

    KPATCHAPPLYORCHESTRATION = 'kPatchApplyOrchestration'

    KRUNPATCHPRECHECKS = 'kRunPatchPrechecks'

    KPATCHREVERTORCHESTRATION = 'kPatchRevertOrchestration'