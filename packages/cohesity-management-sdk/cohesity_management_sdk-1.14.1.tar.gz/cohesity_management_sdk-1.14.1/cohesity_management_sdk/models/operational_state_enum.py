# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class OperationalStateEnum(object):
    """Implementation of the 'OperationalState' enum.

    Specifies the operational state of the replica.
    kFailedNoQuorum, kNull

    Attributes:
        KPENDINGFAILOVER: TODO: type description here.
        KPENDING: TODO: type description here.
        KONLINE: TODO: type description here.
        KOFFLINE: TODO: type description here.
        KFAILED: TODO: type description here.

    """

    KPENDINGFAILOVER = "kPendingFailover"

    KPENDING = "kPending"

    KONLINE = "kOnline"

    KOFFLINE = "kOffline"

    KFAILED = "kFailed"
