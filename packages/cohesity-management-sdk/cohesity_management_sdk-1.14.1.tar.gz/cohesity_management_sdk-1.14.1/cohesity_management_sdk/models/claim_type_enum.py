# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class ClaimTypeEnum(object):

    """Implementation of the 'ClaimType' enum.

    Specifies the type from which the cluster was claimed to Helios.
    'kCohesity' implies Cohesity cluster is claimed.
    'kIBMStroageProtect' implies IBM storage protect cluster is claimed.

    Attributes:
        KCOHESITY: TODO: type description here.
        KIBMSTORAGEPROTECT: TODO: type description here.

    """

    KCOHESITY = 'kCohesity'

    KIBMSTORAGEPROTECT = 'kIBMStorageProtect'


