# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class TypeNasProtectionSourceEnum(object):

    """Implementation of the 'Type_NasProtectionSource' enum.

    Specifies the type of a Protection Source Object in a generic NAS Source
    such as 'kGroup', or 'kHost'.
    Specifies the kind of NAS mount.
    'kGroup' indicates top level node that holds individual NAS hosts.
    'kHost' indicates a single NAS path that can be mounted.

    Attributes:
        KGROUP: TODO: type description here.
        KHOST: TODO: type description here.

    """

    KGROUP = 'kGroup'

    KHOST = 'kHost'
