# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class AccessTokenCredential(object):

    """Implementation of the 'AccessTokenCredential' model.

    Specifies the Cohesity credentials required for generating an access
    token.

    Attributes:
        certificate (string): Specifies the certificate for logging in the cert
            base auth cluster.
        domain (string): Specifies the domain the user is logging in to. For a
            Local user model, the domain is always LOCAL. For LDAP/AD user
            models, the domain will map to an LDAP connection string. A user
            is uniquely identified by a combination of username and domain. If
            this is not set, LOCAL is assumed.
        otp_code (string): Specifies OTP code for MFA verification.
        otp_type (list of OtpTypeEnum): Specifies OTP type for MFA verification.
            'Totp' implies the code is TOTP.
            'Email' implies the code is email OTP.
        password (string): Specifies the password of the Cohesity user
            account.
        private_key (string): Specifies the matching private key of the above
            certificate.
        username (string): Specifies the login name of the Cohesity user.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "certificate":'certificate',
        "otp_code":'otpCode',
        "otp_type":'otpType',
        "password":'password',
        "private_key":'privateKey',
        "username":'username',
        "domain":'domain'
    }

    def __init__(self,
                 certificate=None,
                 otp_code=None,
                 otp_type=None,
                 password=None,
                 private_key=None,
                 username=None,
                 domain=None):
        """Constructor for the AccessTokenCredential class"""

        # Initialize members of the class
        self.certificate = certificate
        self.otp_code = otp_code
        self.otp_type = otp_type
        self.domain = domain
        self.password = password
        self.private_key = private_key
        self.username = username


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        certificate = dictionary.get('certificate')
        otp_code = dictionary.get('otpCode')
        otp_type = dictionary.get('otpType')
        password = dictionary.get('password')
        private_key = dictionary.get('privateKey')
        username = dictionary.get('username')
        domain = dictionary.get('domain')

        # Return an object of this model
        return cls(certificate,
                   otp_code,
                   otp_type,
                   password,
                   private_key,
                   username,
                   domain)


