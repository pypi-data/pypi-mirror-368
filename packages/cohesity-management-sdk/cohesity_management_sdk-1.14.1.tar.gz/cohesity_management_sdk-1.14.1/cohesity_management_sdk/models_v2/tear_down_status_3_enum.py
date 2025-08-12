# -*- coding: utf-8 -*-

class TearDownStatus3Enum(object):

    """Implementation of the 'TearDownStatus3' enum.

    Specifies the status of the tear down operation. This is only set when the
    canTearDown is set to true. 'DestroyScheduled' indicates that the tear
    down is ready to schedule. 'Destroying' indicates that the tear down is
    still running. 'Destroyed' indicates that the tear down succeeded.
    'DestroyError' indicates that the tear down failed.

    Attributes:
        DESTROYSCHEDULED: TODO: type description here.
        DESTROYING: TODO: type description here.
        DESTROYED: TODO: type description here.
        DESTROYERROR: TODO: type description here.

    """

    DESTROYSCHEDULED = 'DestroyScheduled'

    DESTROYING = 'Destroying'

    DESTROYED = 'Destroyed'

    DESTROYERROR = 'DestroyError'

