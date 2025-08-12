# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class LockedReasonEnum(object):

    """Implementation of the 'LockedReason' enum.

    Specifies the reason for locking the User.


    Attributes:
        NOTLOCKED: TODO: type description here.
        FAILEDLOGINATTEMPTS: TODO: type description here.
        LOCKEDBYADMIN: TODO: type description here.
        INACTIVITY: TODO: type description here.
        OTHERREASONS: TODO: type description here.

    """

    NOTLOCKED = 'NotLocked'

    FAILEDLOGINATTEMPTS = 'FailedLoginAttempts'

    LOCKEDBYADMIN = 'LockedByAdmin'

    INACTIVITY = 'Inactivity'

    OTHERREASONS = 'OtherReasons'