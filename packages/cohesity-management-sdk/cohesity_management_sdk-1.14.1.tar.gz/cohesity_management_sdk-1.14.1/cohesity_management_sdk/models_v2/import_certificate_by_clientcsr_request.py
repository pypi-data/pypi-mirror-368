# -*- coding: utf-8 -*-


class ImportCertificateByClientcsrRequest(object):

    """Implementation of the 'ImportCertificateByClientcsrRequest' model.

    Specifies the request to import a certificate.

    Attributes:
        certificate_server (string): Specifies the server certificate to be
            imported.
        certificate_client (string): Specifies the client certificate to be
            imported.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "certificate_server":'certificateServer',
        "certificate_client":'certificateClient'
    }

    def __init__(self,
                 certificate_server=None,
                 certificate_client=None):
        """Constructor for the ImportCertificateByClientcsrRequest class"""

        # Initialize members of the class
        self.certificate_server = certificate_server
        self.certificate_client = certificate_client


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
        certificate_server = dictionary.get('certificateServer')
        certificate_client = dictionary.get('certificateClient')

        # Return an object of this model
        return cls(certificate_server,
                   certificate_client)


