# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class UsageTypeKmsCreateRequestParametersEnum(object):

    """Implementation of the 'UsageTypeKmsCreateRequestParameters' enum.

    Specifies the usage type of the Vault.
    'kArchival' indicates the Vault provides archive storage for backup data.
    kRpaasArchival indicates this is used for RPaaS only.

    ''kArchival'' indicates an internal KMS object.
    ''kRpaasArchival'' indicates an Aws KMS object.

    Attributes:
        KARCHIVAL: TODO: type description here.
        KRPAASARCHIVAL: TODO: type description here.

    """

    KARCHIVAL = 'kArchival'

    KRPAASARCHIVAL = 'kRpaasArchival'
