# -*- coding: utf-8 -*-

class KeyTypeEnum(object):

    """Implementation of the 'KeyType' enum.

    Specifies the algorithm to be used to generate the key pair. RSA is the
    default value.

    Attributes:
        RSA: TODO: type description here.
        ECDSA: TODO: type description here.

    """

    RSA = 'rsa'

    ECDSA = 'ecdsa'

