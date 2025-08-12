# -*- coding: utf-8 -*-


class UpdateCertificateResponse(object):

    """Implementation of the 'Update Certificate Response' model.

    Specifies the response to update a certificate.

    Attributes:
        certificate (string): Specifies the certificate.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "certificate":'certificate'
    }

    def __init__(self,
                 certificate=None):
        """Constructor for the UpdateCertificateResponse class"""

        # Initialize members of the class
        self.certificate = certificate


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

        # Return an object of this model
        return cls(certificate)


