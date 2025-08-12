# -*- coding: utf-8 -*-


class CreateUserSessionRequestParams(object):

    """Implementation of the 'CreateUserSessionRequestParams' model.

    Specifies user session request parameters

    Attributes:
        certificate (string): Specifies the certificate for cert based authentication.
        username (string): Specifies the login name of the Cohesity user
        password (string): Specifies the password of the Cohesity user
        domain (string): Specifies the domain the user is logging in to. For a local user
          the domain is LOCAL. For LDAP/AD user, the domain will map to a LDAP connection
          string. A user is uniquely identified by a combination of username and domain.
          LOCAL is the default domain.
        otp_code (string): Specifies OTP code for MFA verification.
        otp_type (OtpTypeEnum): Specifies OTP Type for MFA verification.
        private_key (string): Specifies the private key for cert based authentication.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "certificate":'certificate',
        "username":'username',
        "password":'password',
        "domain":'domain',
        "otp_code":'otpCode',
        "otp_type":'otpType',
        "private_key":'privateKey'
    }

    def __init__(self,
                 certificate=None,
                 username=None,
                 password=None,
                 domain=None,
                 otp_code=None,
                 otp_type=None,
                 private_key=None):
        """Constructor for the CreateUserSessionRequestParams class"""

        # Initialize members of the class
        self.certificate = certificate
        self.username = username
        self.password = password
        self.domain = domain
        self.otp_code = otp_code
        self.otp_type = otp_type
        self.private_key = private_key

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
        username = dictionary.get('username')
        password = dictionary.get('password')
        domain = dictionary.get('domain')
        otp_code = dictionary.get('otpCode')
        otp_type = dictionary.egt('otpType')
        private_key = dictionary.get('privateKey')

        # Return an object of this model
        return cls(certificate,
                   username,
                   password,
                   domain,
                   otp_code,
                   otp_type,
                   private_key)