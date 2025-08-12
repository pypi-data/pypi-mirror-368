# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class ExcludeAwsTypesEnum(object):

    """Implementation of the 'ExcludeAwsTypes' enum.

    Specifies the Object types to be filtered out for AWS that match the
    passed in types such as 'kEC2Instance', 'kRDSInstance', 'kAuroraCluster',
    'kTag', 'kAuroraTag', 'kRDSTag', kS3Bucket, kS3Tag.
    For example, set this parameter to 'kEC2Instance' to exclude ec2 instance
    from being returned.

    Attributes:
        KEC2INSTANCE: TODO: type description here.
        KRDSINSTANCE: TODO: type description here.
        KAURORACLUSTER: TODO: type description here.
        KS3BUCKET: TODO: type description here.
        KTAG: TODO: type description here.
        KRDSTAG: TODO: type description here.
        KAURORATAG: TODO: type description here.
        KS3TAG: TODO: type description here.

    """

    KEC2INSTANCE = 'kEC2Instance'

    KRDSINSTANCE = 'kRDSInstance'

    KAURORACLUSTER = 'kAuroraCluster'

    KS3BUCKET = 'kS3Bucket'

    KTAG = 'kTag'

    KRDSTAG = 'kRDSTag'

    KAURORATAG = 'kAuroraTag'

    KS3TAG = 'kS3Tag'
