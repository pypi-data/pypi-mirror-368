# -*- coding: utf-8 -*-

class CompressionEnum(object):

    """Implementation of the 'Compression' enum.

    Specifies the compression option supported by SQL package export
          command during Azure SQL backup.

    Attributes:
        NORMAL: TODO: type description here.
        MAXIMUM: TODO: type description here.
        FAST: TODO: type description here.
        SUPERFAST: TODO: type description here.
        NOTCOMPRESSED: TODO: type description here.
    """

    NORMAL = 'Normal'

    MAXIMUM = 'Maximum'

    FAST = 'Fast'

    SUPERFAST = 'SuperFast'

    NOTCOMPRESSED = 'NotCompressed'