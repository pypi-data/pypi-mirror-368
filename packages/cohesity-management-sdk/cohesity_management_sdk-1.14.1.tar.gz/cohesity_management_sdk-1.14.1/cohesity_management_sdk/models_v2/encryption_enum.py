# -*- coding: utf-8 -*-

class EncryptionEnum(object):

    """Implementation of the 'Encryption' enum.

    TODO: type enum description here.

    Attributes:
        DESCBCCRC: TODO: type description here.
        DESCBCMD5: TODO: type description here.
        RC4HMAC: TODO: type description here.
        AES128CTSHMACSHA196: TODO: type description here.
        AES256CTSHMACSHA196: TODO: type description here.

    """

    DESCBCCRC = 'DES-CBC-CRC'

    DESCBCMD5 = 'DES-CBC-MD5'

    RC4HMAC = 'RC4-HMAC'

    AES128CTSHMACSHA196 = 'AES128-CTS-HMAC-SHA1-96'

    AES256CTSHMACSHA196 = 'AES256-CTS-HMAC-SHA1-96'

