# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class StorageTierEnum(object):

    """Implementation of the 'StorageTier' enum.

    StorageTier is the type of StorageTier.
    StorageTierType represents the various values for the Storage Tier.
    'PCIeSSD' indicates storage tier type of Pci Solid State Drive.
    'SATAHDD' indicates storage tier type of SATA Solid State Drive.
    'SATAHDD' indicates storage tier type of SATA Hard Disk Drive.
    'CLOUD' indicates storage tier type of Cloud.

    Attributes:
        PCIESSD: TODO: type description here.
        SATASSD: TODO: type description here.
        SATAHDD: TODO: type description here.
        CLOUD: TODO: type description here.

    """

    PCIESSD = 'PCIeSSD'

    SATASSD = 'SATASSD'

    SATAHDD = 'SATAHDD'

    CLOUD = 'CLOUD'


