# -*- coding: utf-8 -*-


class SupportMfaConfigInfo(object):

    """Implementation of the 'SupportMfaConfigInfo' model.

    Holds the MFA configuration to be returned or stored.

    Attributes:
        current_password (string): Specifies the current password of the support user, required
          for making updates to the configuration.
        email (string): Specifies email address of the support user. Used when MFA mode
          is email.
        enabled (bool): Specifies whether MFA is enabled for support user.
        mfa_code (string): MFA code that needs to be passed when disabling MFA or changing
          email address when email based MFA is configured.
        mfa_type (MfaTypeEnum): Specifies the mechanism to receive the OTP code.
        otp_verification_state (OtpVerificationStateEnum): Specifies the status of otp verification.
        requires_password_auth (bool): Specifies that this API requires current support user password
          for enabling/disabling MFA, and for updating mfaType and email.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "current_password":'currentPassword',
        "email":'email',
        "enabled":'enabled',
        "mfa_code":'mfaCode',
        "mfa_type":'mfaType',
        "otp_verification_state":'otpVerificationState',
        "requires_password_auth":'requiresPasswordAuth'
    }

    def __init__(self,
                 current_password=None,
                 email=None,
                 enabled=None,
                 mfa_code=None,
                 mfa_type=None,
                 otp_verification_state=None,
                 requires_password_auth=None):
        """Constructor for the SupportMfaConfigInfo class"""

        # Initialize members of the class
        self.current_password = current_password
        self.email = email
        self.enabled = enabled
        self.mfa_code = mfa_code
        self.mfa_type = mfa_type
        self.otp_verification_state = otp_verification_state
        self.requires_password_auth = requires_password_auth


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
        current_password = dictionary.get('currentPassword')
        email = dictionary.get('email')
        enabled = dictionary.get('enabled')
        mfa_code = dictionary.get('mfaCode')
        mfa_type = dictionary.get('mfaType')
        otp_verification_state = dictionary.get('otpVerificationState')
        requires_password_auth = dictionary.get('requiresPasswordAuth')

        # Return an object of this model
        return cls(current_password,
                   email,
                   enabled,
                   mfa_code,
                   mfa_type,
                   otp_verification_state,
                   requires_password_auth
                   )