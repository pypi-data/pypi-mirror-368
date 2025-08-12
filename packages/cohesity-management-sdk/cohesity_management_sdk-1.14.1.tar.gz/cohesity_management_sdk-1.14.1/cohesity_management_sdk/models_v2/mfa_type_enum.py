# -*- coding: utf-8 -*-

class MfaTypeEnum(object):

    """Implementation of the 'MfaTypeEnum' enum.

    Specifies the mechanism to receive the OTP code.

    Attributes:
        EMAIL: TODO: type description here.
        TOTP: TODO: type description here.
        SALESFORCE: TODO: type description here.

    """

    EMAIL = 'Email'

    TOTP = 'TOTP'

    SALESFORCE = 'Salesforce'