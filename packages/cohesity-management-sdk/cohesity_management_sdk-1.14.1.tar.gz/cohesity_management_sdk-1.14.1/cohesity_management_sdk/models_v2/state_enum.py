# -*- coding: utf-8 -*-

class StateEnum(object):

    """Implementation of the 'State34' enum.

    Specifies the current state of licensing workflow.

    Attributes:
        KINPROGRESSNEWCLUSTER: TODO: type description here.
        KINPROGRESSOLDCLUSTER: TODO: type description here.
        KCLAIMED: TODO: type description here.
        KSKIPPED: TODO: type description here.
        KSTARTED: TODO: type description here.
    """

    KINPROGRESSNEWCLUSTER = 'kInProgressNewCluster'

    KINPROGRESSOLDCLUSTER = 'kInProgressOldCluster'

    KCLAIMED = 'kClaimed'

    KSKIPPED = 'kSkipped'

    KSTARTED = 'kStarted'