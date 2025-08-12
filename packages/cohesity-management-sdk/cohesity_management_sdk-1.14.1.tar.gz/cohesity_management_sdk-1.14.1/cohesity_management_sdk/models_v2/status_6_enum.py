# -*- coding: utf-8 -*-

class Status6Enum(object):

    """Implementation of the 'Status6' enum.

    Status of the Recovery. 'Running' indicates that the Recovery is still
    running. 'Canceled' indicates that the Recovery has been cancelled.
    'Canceling' indicates that the Recovery is in the process of being
    cancelled. 'Failed' indicates that the Recovery has failed. 'Succeeded'
    indicates that the Recovery has finished successfully.
    'SucceededWithWarning' indicates that the Recovery finished successfully,
    but there were some warning messages.

    Attributes:

        ACCEPTED: TODO: type description here.
        RUNNING: TODO: type description here.
        CANCELED: TODO: type description here.
        CANCELING: TODO: type description here.
        FAILED: TODO: type description here.
        MISSED: TODO: type description here.
        SUCCEEDED: TODO: type description here.
        SUCCEEDEDWITHWARNING: TODO: type description here.
        ONHOLD: TODO: type description here.

    """

    ACCEPTED = 'Accepted'

    RUNNING = 'Running'

    CANCELED = 'Canceled'

    CANCELING = 'Canceling'

    FAILED = 'Failed'

    MISSED = 'Missed'

    SUCCEEDED = 'Succeeded'

    SUCCEEDEDWITHWARNING = 'SucceededWithWarning'

    ONHOLD = 'OnHold'

