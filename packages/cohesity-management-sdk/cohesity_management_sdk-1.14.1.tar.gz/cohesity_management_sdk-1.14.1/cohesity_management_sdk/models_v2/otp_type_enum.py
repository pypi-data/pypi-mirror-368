# -*- coding: utf-8 -*-

class OtpTYpeEnum(object):

    """Implementation of the 'OtpTypeEnum' enum.

    Specifies OTP Type for MFA verification.

    Attributes:
        EMAIL: TODO: type description here.
        TOTP: TODO: type description here.
        SALESFORCE: TODO: type description here.

    """

    EMAIL = 'email'

    TOTP = 'totp'

    SALESFORCE = 'salesforce'