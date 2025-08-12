# -*- coding: utf-8 -*-


class UpdateCertificateByCsrRequest(object):

    """Implementation of the 'UpdateCertificateByCsrRequest' model.

    Specifies the request to update a certificate.

    Attributes:
        certificate (string): Specifies the certificate to be imported.
        csr_id (string): Specifies the id of the csr corresponding to the
            certificate.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "certificate":'certificate',
        "csr_id":'csrId'
    }

    def __init__(self,
                 certificate=None,
                 csr_id=None):
        """Constructor for the UpdateCertificateByCsrRequest class"""

        # Initialize members of the class
        self.certificate = certificate
        self.csr_id = csr_id


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
        csr_id = dictionary.get('csrId')

        # Return an object of this model
        return cls(certificate,
                   csr_id)


