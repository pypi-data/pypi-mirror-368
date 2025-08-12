# -*- coding: utf-8 -*-

class PhysicalTypeEnum(object):

    """Implementation of the 'PhysicalType' enum.

   Specifies the type of physical server.

    Attributes:
        KGROUP: TODO: type description here.
        KHOST: TODO: type description here.
        KWINDOWSCLUSTER: TODO: type description here.
        KORACLERACCLUSTER: TODO: type description here.
        KORACLEAPCLUSTER: TODO: type description here.
    """

    KGROUP = 'kGroup'

    KHOST = 'kHost'

    KWINDOWSCLUSTER = 'kWindowsCluster'

    KORACLERACCLUSTER = 'kOracleRACCluster'

    KORACLEAPCLUSTER = 'kOracleAPCluster'