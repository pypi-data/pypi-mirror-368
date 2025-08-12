# -*- coding: utf-8 -*-


class SecurityConfigCertificateBasedAuth(object):

    """Implementation of the 'SecurityConfigCertificateBasedAuth' model.

    Specifies security config for certificate based authentication.

    Attributes:
        enable_mapping_based_authentication (bool): If true, certfication
            based authentication is done via configured mapping. Else it will
            proceed based on legacy serial number match.
        certificate_mapping (CertificateMappingEnum): Specifies the field to
            be used in certificate for authentication.
        ad_mapping (AdMappingEnum): Specifies the field to be used in AD user
            for authentication.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enable_mapping_based_authentication":'enableMappingBasedAuthentication',
        "certificate_mapping":'certificateMapping',
        "ad_mapping":'adMapping'
    }

    def __init__(self,
                 enable_mapping_based_authentication=None,
                 certificate_mapping=None,
                 ad_mapping=None):
        """Constructor for the SecurityConfigCertificateBasedAuth class"""

        # Initialize members of the class
        self.enable_mapping_based_authentication = enable_mapping_based_authentication
        self.certificate_mapping = certificate_mapping
        self.ad_mapping = ad_mapping


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
        enable_mapping_based_authentication = dictionary.get('enableMappingBasedAuthentication')
        certificate_mapping = dictionary.get('certificateMapping')
        ad_mapping = dictionary.get('adMapping')

        # Return an object of this model
        return cls(enable_mapping_based_authentication,
                   certificate_mapping,
                   ad_mapping)


