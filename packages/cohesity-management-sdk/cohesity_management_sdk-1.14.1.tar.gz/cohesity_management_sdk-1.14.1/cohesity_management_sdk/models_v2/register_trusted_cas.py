# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.trusted_ca_request

class RegisterTrustedCas(object):

    """Implementation of the 'RegisterTrustedCas' model.

    Specifies the parameters to register a Certificate.

    Attributes:
        certificates (list of TrustedCaRequest): Specifies the certificates to
            be imported.
        only_validate (bool): Specifies if the certificates are only to be
            validated.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "certificates":'certificates',
        "only_validate":'onlyValidate'
    }

    def __init__(self,
                 certificates=None,
                 only_validate=None):
        """Constructor for the RegisterTrustedCas class"""

        # Initialize members of the class
        self.certificates = certificates
        self.only_validate = only_validate


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
        certificates = None
        if dictionary.get("certificates") is not None:
            certificates = list()
            for structure in dictionary.get('certificates'):
                certificates.append(cohesity_management_sdk.models_v2.trusted_ca_request.TrustedCaRequest.from_dictionary(structure))
        only_validate = dictionary.get('onlyValidate')

        # Return an object of this model
        return cls(certificates,
                   only_validate)


