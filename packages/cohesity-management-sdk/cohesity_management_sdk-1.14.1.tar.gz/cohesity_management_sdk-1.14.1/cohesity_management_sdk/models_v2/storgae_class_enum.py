# -*- coding: utf-8 -*-

class StorageClassEnum(object):

    """Implementation of the 'StorageClassEnum' enum.

    Specifies the AWS S3 Storage classes to backup.

    Attributes:
        AMAZONS3STANDARD: TODO: type description here.
        AMAZONS3INTELLIGENTTIERING: TODO: type description here.
        AMAZONS3STANDARDIA: TODO: type description here.
        AMAZONS3ONEZONEIA: TODO: type description here.

    """

    AMAZONS3STANDARD = 'kAmazonS3Standard'

    AMAZONS3INTELLIGENTTIERING = 'kAmazonS3IntelligentTiering'

    AMAZONS3STANDARDIA = 'kAmazonS3StandardIA'

    AMAZONS3ONEZONEIA = 'kAmazonS3OneZoneIA'