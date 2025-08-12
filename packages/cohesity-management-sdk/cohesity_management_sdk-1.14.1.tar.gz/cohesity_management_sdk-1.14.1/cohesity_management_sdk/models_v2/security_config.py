# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.security_config_password_strength
import cohesity_management_sdk.models_v2.security_config_password_reuse
import cohesity_management_sdk.models_v2.security_config_password_lifetime
import cohesity_management_sdk.models_v2.security_config_account_lockout
import cohesity_management_sdk.models_v2.security_config_data_classification
import cohesity_management_sdk.models_v2.security_config_session_configuration
import cohesity_management_sdk.models_v2.security_config_certificate_based_auth

class SecurityConfig(object):

    """Implementation of the 'SecurityConfig' model.

    Specifies the fields of security settings.

    Attributes:
        password_strength (SecurityConfigPasswordStrength): Specifies security
            config for password strength.
        password_reuse (SecurityConfigPasswordReuse): Specifies security
            config for password reuse.
        password_lifetime (SecurityConfigPasswordLifetime): Specifies security
            config for password lifetime.
        account_lockout (SecurityConfigAccountLockout): Specifies security
            config for account lockout.
        data_classification (SecurityConfigDataClassification): Specifies
            security config for data classification.
        session_configuration (SecurityConfigSessionConfiguration): Specifies
            configuration for user sessions.
        certificate_based_auth (SecurityConfigCertificateBasedAuth): Specifies
            security config for certificate based authentication.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "password_strength":'passwordStrength',
        "password_reuse":'passwordReuse',
        "password_lifetime":'passwordLifetime',
        "account_lockout":'accountLockout',
        "data_classification":'dataClassification',
        "session_configuration":'sessionConfiguration',
        "certificate_based_auth":'certificateBasedAuth'
    }

    def __init__(self,
                 password_strength=None,
                 password_reuse=None,
                 password_lifetime=None,
                 account_lockout=None,
                 data_classification=None,
                 session_configuration=None,
                 certificate_based_auth=None):
        """Constructor for the SecurityConfig class"""

        # Initialize members of the class
        self.password_strength = password_strength
        self.password_reuse = password_reuse
        self.password_lifetime = password_lifetime
        self.account_lockout = account_lockout
        self.data_classification = data_classification
        self.session_configuration = session_configuration
        self.certificate_based_auth = certificate_based_auth


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
        password_strength = cohesity_management_sdk.models_v2.security_config_password_strength.SecurityConfigPasswordStrength.from_dictionary(dictionary.get('passwordStrength')) if dictionary.get('passwordStrength') else None
        password_reuse = cohesity_management_sdk.models_v2.security_config_password_reuse.SecurityConfigPasswordReuse.from_dictionary(dictionary.get('passwordReuse')) if dictionary.get('passwordReuse') else None
        password_lifetime = cohesity_management_sdk.models_v2.security_config_password_lifetime.SecurityConfigPasswordLifetime.from_dictionary(dictionary.get('passwordLifetime')) if dictionary.get('passwordLifetime') else None
        account_lockout = cohesity_management_sdk.models_v2.security_config_account_lockout.SecurityConfigAccountLockout.from_dictionary(dictionary.get('accountLockout')) if dictionary.get('accountLockout') else None
        data_classification = cohesity_management_sdk.models_v2.security_config_data_classification.SecurityConfigDataClassification.from_dictionary(dictionary.get('dataClassification')) if dictionary.get('dataClassification') else None
        session_configuration = cohesity_management_sdk.models_v2.security_config_session_configuration.SecurityConfigSessionConfiguration.from_dictionary(dictionary.get('sessionConfiguration')) if dictionary.get('sessionConfiguration') else None
        certificate_based_auth = cohesity_management_sdk.models_v2.security_config_certificate_based_auth.SecurityConfigCertificateBasedAuth.from_dictionary(dictionary.get('certificateBasedAuth')) if dictionary.get('certificateBasedAuth') else None

        # Return an object of this model
        return cls(password_strength,
                   password_reuse,
                   password_lifetime,
                   account_lockout,
                   data_classification,
                   session_configuration,
                   certificate_based_auth)


