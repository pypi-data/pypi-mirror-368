# -*- coding: utf-8 -*-

class Status3Enum(object):

    """Implementation of the 'Status3' enum.

    Status of the attempt for an object. 'Running' indicates that the run is
    still running. 'Canceled' indicates that the run has been canceled.
    'Canceling' indicates that the run is in the process of being canceled.
    'Failed' indicates that the run has failed. 'Missed' indicates that the
    run was unable to take place at the scheduled time because the previous
    run was still happening. 'Succeeded' indicates that the run has finished
    successfully. 'SucceededWithWarning' indicates that the run finished
    successfully, but there were some warning messages.

    Attributes:
        RUNNING: TODO: type description here.
        CANCELED: TODO: type description here.
        CANCELING: TODO: type description here.
        FAILED: TODO: type description here.
        MISSED: TODO: type description here.
        SUCCEEDED: TODO: type description here.
        SUCCEEDEDWITHWARNING: TODO: type description here.
        ONHOLD: TODO: type description here.

    """

    RUNNING = 'Running'

    CANCELED = 'Canceled'

    CANCELING = 'Canceling'

    FAILED = 'Failed'

    MISSED = 'Missed'

    SUCCEEDED = 'Succeeded'

    SUCCEEDEDWITHWARNING = 'SucceededWithWarning'

    ONHOLD = 'OnHold'

