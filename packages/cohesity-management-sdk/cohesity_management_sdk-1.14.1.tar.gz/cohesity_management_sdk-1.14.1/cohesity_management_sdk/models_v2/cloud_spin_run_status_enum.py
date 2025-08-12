# -*- coding: utf-8 -*-

class CloudSpinRunStatusEnum(object):

    """Implementation of the 'cloudSpinRunStatus' enum.

    TODO: type enum description here.

    Attributes:
        KINPROGRESS: TODO: type description here.
        KSUCCESSFUL: TODO: type description here.
        KFAILED: TODO: type description here.
        KWAITINGFORNEXTATTEMPT: TODO: type description here.
        KWARNING: TODO: type description here.
        KWAITINGFOROLDERBACKUPRUN: TODO: type description here.

    """

    KINPROGRESS = 'kInProgress'

    KSUCCESSFUL = 'kSuccessful'

    KFAILED = 'kFailed'

    KWAITINGFORNEXTATTEMPT = 'kWaitingForNextAttempt'

    KWARNING = 'kWarning'

    KWAITINGFOROLDERBACKUPRUN = 'kWaitingForOlderBackupRun'
