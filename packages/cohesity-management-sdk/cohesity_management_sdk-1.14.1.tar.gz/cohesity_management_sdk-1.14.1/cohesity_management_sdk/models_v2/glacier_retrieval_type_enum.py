# -*- coding: utf-8 -*-

class GlacierRetrievalTypeEnum(object):

    """Implementation of the 'GlacierRetrievalType' enum.

    Specifies the glacier retrieval type when restoring or downloding
          files or folders from a Glacier-based cloud snapshot.

    Attributes:
        KSTANDARD: TODO: type description here.
        KEXPEDITEDNOPCU: TODO: type description here.
        KEXPEDITEDWITHPCU: TODO: type description here.

    """

    KSTANDARD = 'kStandard'

    KEXPEDITEDNOPCU = 'kExpeditedNoPCU'

    KEXPEDITEDWITHPCU = 'kExpeditedWithPCU'