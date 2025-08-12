# -*- coding: utf-8 -*-

class Type42Enum(object):

    """Implementation of the 'Type42' enum.

    Specifies the encryption type of a machine account.

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

