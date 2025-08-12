# -*- coding: utf-8 -*-

class SourceTypeEnum(object):

    """Implementation of the 'SourceType' enum.

    Specifies the type of VMware source to which the VMs are being restored.

    Attributes:
        KVCENTER: TODO: type description here.
        KSTANDALONEHOST: TODO: type description here.
        KVCLOUDDIRECTOR: TODO: type description here.

    """

    KVCENTER = 'kVCenter'

    KSTANDALONEHOST = 'kStandaloneHost'

    K_VCLOUD_DIRECTOR = 'kvCloudDirector'

